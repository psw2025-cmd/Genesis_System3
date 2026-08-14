"""Permanent public-readonly security boundary for Genesis System3.

Cloud Run launches this module. Dashboard viewing has no browser credential,
login-session, or dashboard-secret authority. Retired dashboard-auth environment
variables are scrubbed BEFORE importing the legacy application, so configuration
drift cannot reactivate that old code path.

Public visibility never becomes mutation authority. MutationPolicy owns every
write; UNKNOWN writes and all live mutation/approval capabilities fail closed.
Dedicated worker ingestion remains bound to its separate worker token.
"""
from __future__ import annotations

import asyncio
from collections import Counter
import hashlib
import json
import os

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Permanent architecture invariant: these retired dashboard-auth knobs have no
# runtime meaning. Scrub them before importing the legacy backend so even a
# manually drifted Cloud Run revision cannot activate its old compatibility
# middleware. The canonical deployer also removes them from revision metadata.
_RETIRED_DASHBOARD_ENV = (
    "REQUIRE_" + "API_KEY",
    "API_" + "KEY",
    "DASHBOARD_" + "API_KEY",
    "ENABLE_DASHBOARD_" + "AUTH",
    "DASHBOARD_SESSION_" + "MAX_AGE",
)
for _name in _RETIRED_DASHBOARD_ENV:
    os.environ.pop(_name, None)

from dashboard.backend import app as legacy  # noqa: E402
from dashboard.backend.mutation_policy import (  # noqa: E402
    Capability,
    assert_runtime_manifest,
    duplicate_write_routes,
    evaluate_runtime_mutation,
    inventory_write_routes,
    unclassified_write_routes,
)
from dashboard.backend.security_policy import SecurityDecision, evaluate_request  # noqa: E402
from dashboard.backend.traffic_shield import (  # noqa: E402
    retire_legacy_delay_middleware,
    traffic_shield_middleware,
    traffic_shield_status,
)


app = legacy.app

# The legacy "rate_limit_middleware" slept 50ms on every broker/chain request;
# it did not actually limit concurrency or honor Retry-After. Remove it from the
# Cloud Run serving stack before adding the real single-flight traffic shield.
_RETIRED_FIXED_DELAY_MIDDLEWARE_COUNT = retire_legacy_delay_middleware(
    app,
    getattr(legacy, "rate_limit_middleware", None),
)

# Belt-and-suspenders protection for the already-imported legacy compatibility
# globals. They are not authority and can never be changed by request input.
if hasattr(legacy, "_REQUIRE_API_KEY"):
    legacy._REQUIRE_API_KEY = False
if hasattr(legacy, "_API_KEY"):
    legacy._API_KEY = ""
if hasattr(legacy, "_has_dashboard_api_access"):
    legacy._has_dashboard_api_access = lambda _request: False

# Auth compatibility routes and the legacy file-backed paper GET are removed
# from the serving table.  The canonical /api/paper route below reads the
# durable Firestore paper ledger; local Cloud Run files are never production
# authority.
_RETIRED_AUTH_PATHS = {
    "/api/auth/" + "session",
    "/api/auth/" + "logout",
    "/api/auth/" + "status",
}


def _retire_serving_route(route) -> bool:
    path = getattr(route, "path", None)
    if path in _RETIRED_AUTH_PATHS:
        return True
    methods = set(getattr(route, "methods", None) or set())
    return path == "/api/paper" and "GET" in methods


app.router.routes = [route for route in app.router.routes if not _retire_serving_route(route)]


def _capability_aware_request_policy(**kwargs) -> SecurityDecision:
    """Apply MutationPolicy before the public-readonly request policy."""
    mutation = evaluate_runtime_mutation(
        kwargs.get("method", ""),
        kwargs.get("path", ""),
        worker_token_configured=bool(kwargs.get("worker_token_configured")),
        worker_token_valid=bool(kwargs.get("worker_token_valid")),
        control_authorized=False,
    )
    if mutation is None:
        return evaluate_request(**kwargs)

    if not mutation.allowed:
        return SecurityDecision(
            False,
            mutation.status_code,
            mutation.reason,
            mutation.code,
        )

    if mutation.capability is Capability.WORKER_INGEST:
        return SecurityDecision(True)

    return SecurityDecision(
        False,
        403,
        "Public dashboard is read-only; mutation authority is separate",
        "PUBLIC_DASHBOARD_READ_ONLY",
    )


# Existing legacy middleware resolves this symbol at request time. Replacing it
# keeps one middleware stack while removing the retired dashboard-auth model.
legacy.evaluate_request = _capability_aware_request_policy


@app.middleware("http")
async def strip_retired_dashboard_credentials(request: Request, call_next):
    """Make retired dashboard credential input inert before inner middleware."""
    headers = []
    retired_header = b"x-" + b"api-key"
    retired_cookie_name = "system3_dashboard_" + "session"

    for key, value in request.scope.get("headers", []):
        lower = key.lower()
        if lower == retired_header:
            continue
        if lower == b"cookie":
            try:
                parts = []
                for part in value.decode("latin-1").split(";"):
                    item = part.strip()
                    if not item:
                        continue
                    name = item.split("=", 1)[0].strip()
                    if name == retired_cookie_name:
                        continue
                    parts.append(item)
                if parts:
                    headers.append((key, "; ".join(parts).encode("latin-1")))
            except Exception:
                headers.append((key, value))
            continue
        headers.append((key, value))

    request.scope["headers"] = headers
    return await call_next(request)


@app.middleware("http")
async def public_read_traffic_shield(request: Request, call_next):
    """Coalesce expensive public GETs and fail over to recent good snapshots.

    This never wraps write methods. MutationPolicy therefore remains the only
    mutation authority and LIVE remains hard-disabled.
    """
    return await traffic_shield_middleware(request, call_next)


@app.get("/api/auth/status")
async def dashboard_auth_status():
    """Stable non-secret proof that dashboard credential authority is absent."""
    return {
        "required": False,
        "configured": False,
        "authenticated": False,
        "mode": "public_readonly",
        "credential_surface": "REMOVED",
        "session": None,
    }


@app.get("/api/traffic/health")
async def traffic_health_status():
    """Non-secret 429/self-healing evidence for monitoring and runtime proof."""
    return {
        **traffic_shield_status(),
        "legacy_fixed_delay_middleware_retired": _RETIRED_FIXED_DELAY_MIDDLEWARE_COUNT == 1,
        "legacy_fixed_delay_middleware_removed_count": _RETIRED_FIXED_DELAY_MIDDLEWARE_COUNT,
        "client_contract": "RETRY_AFTER_EXPONENTIAL_BACKOFF_JITTER",
        "websocket_preferred": True,
        "durable_truth": "FIRESTORE_AND_BROKER_READ_ONLY",
        "public_dashboard_read_only": True,
    }


@app.get("/api/paper")
async def durable_paper_status():
    """Single self-contained public truth endpoint for the Paper Trades tab.

    Reads only Firestore.  It never invokes Dhan, scanner, order, mutation or
    local-file code, so dashboard rendering cannot trigger broker fan-out or
    depend on the lifetime of a Cloud Run container.
    """
    try:
        from dashboard.backend.paper_ledger_backend import FirestorePaperLedgerBackend

        payload = await asyncio.wait_for(
            asyncio.to_thread(FirestorePaperLedgerBackend().public_snapshot),
            timeout=8.0,
        )
        payload["api_contract"] = "paper_public_truth_v1"
        payload["public_dashboard_read_only"] = True
        return JSONResponse(payload, status_code=200, headers={"Cache-Control": "no-store"})
    except Exception as exc:
        # A durable ledger outage is not represented as an empty/zero portfolio.
        # Fail visibly so semantic browser proof blocks deployment acceptance.
        payload = {
            "status": "UNAVAILABLE",
            "mode": "PAPER",
            "engine": "cloud_paper_firestore_v1",
            "positions_source": "FIRESTORE_PAPER_LEDGER",
            "data_source": "DURABLE_LEDGER_UNAVAILABLE",
            "positions": {"positions": [], "open_positions": [], "open_count": 0},
            "pnl": {"summary": {}, "closed_positions": []},
            "trades": {"entries": [], "exits": [], "count": 0},
            "paper_truth": {
                "ledger_source": "FIRESTORE_PAPER_LEDGER",
                "durable": True,
                "available": False,
                "broker_order_endpoints_called": False,
                "order_endpoints_label": "INTENTIONALLY_NOT_CALLED_PAPER_SAFE",
                "error_type": type(exc).__name__,
            },
            "broker_order_endpoints_called": False,
            "live_trading_enabled": False,
            "api_contract": "paper_public_truth_v1",
            "public_dashboard_read_only": True,
        }
        return JSONResponse(payload, status_code=503, headers={"Cache-Control": "no-store"})


def _sentinel_reached(capability: str) -> None:
    raise HTTPException(
        status_code=500,
        detail=f"MUTATION_POLICY_BYPASSED_{capability}",
    )


@app.post("/api/security/mutation-policy/probe/paper", include_in_schema=False)
async def mutation_policy_probe_paper():
    _sentinel_reached("PAPER_MUTATION")


@app.post("/api/security/mutation-policy/probe/live", include_in_schema=False)
async def mutation_policy_probe_live():
    _sentinel_reached("LIVE_MUTATION")


@app.post("/api/security/mutation-policy/probe/worker", include_in_schema=False)
async def mutation_policy_probe_worker():
    _sentinel_reached("WORKER_INGEST")


@app.get("/api/security/mutation-policy")
async def mutation_policy_status():
    """Non-secret runtime evidence for the active mutation boundary."""
    rows = inventory_write_routes(app)
    unknown = unclassified_write_routes(app)
    duplicates = duplicate_write_routes(app)
    counts = Counter(row.capability.value for row in rows)
    manifest_rows = [
        {"method": row.method, "path": row.path, "capability": row.capability.value}
        for row in rows
    ]
    manifest_hash = hashlib.sha256(
        json.dumps(manifest_rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "state": "ENFORCED" if not unknown and not duplicates else "INVALID",
        "runtime_mode": "ANALYZER_PAPER",
        "public_dashboard_read_only": True,
        "dashboard_credential_authority": "REMOVED",
        "control_authority_configured": False,
        "live_mutation": "HARD_DENY",
        "live_approval": "HARD_DENY",
        "worker_authority": "DEDICATED_WORKER_TOKEN",
        "write_route_count": len(rows),
        "unknown_count": len(unknown),
        "duplicate_count": len(duplicates),
        "capability_counts": dict(sorted(counts.items())),
        "manifest_sha256": manifest_hash,
        "secret_values_exposed": False,
    }


# Startup/import fails if any newly added write route bypasses classification or
# duplicates an existing method/path owner.
assert_runtime_manifest(app)
