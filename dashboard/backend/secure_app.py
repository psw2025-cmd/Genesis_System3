"""Security boundary wrapper for the System3 FastAPI application.

Cloud Run launches this module. PAPER/ANALYZER dashboard viewing is public and
read-only; no dashboard API key is required for reads. SessionTruth routes are
retained as fail-closed compatibility surfaces but cannot create sessions while
REQUIRE_API_KEY is disabled.

This wrapper also installs the authoritative MutationPolicy decision function
used by the legacy request middleware. Public visibility never becomes mutation
authority. UNKNOWN writes and all live mutation/approval capabilities are hard
denied before legacy route logic. Dedicated worker ingestion remains bound to
its worker token. No broker order implementation exists in this module.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import hmac
import json

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from dashboard.backend import app as legacy
from dashboard.backend.mutation_policy import (
    Capability,
    assert_runtime_manifest,
    duplicate_write_routes,
    evaluate_runtime_mutation,
    inventory_write_routes,
    unclassified_write_routes,
)
from dashboard.backend.security_policy import SecurityDecision
from dashboard.backend.session_truth import get_session_truth_store


app = legacy.app
_SESSION_TRUTH = get_session_truth_store()
_AUTH_WINDOW_S = 300
_AUTH_MAX_FAILURES = 10
_AUTH_PATHS = {
    "/api/auth/session",
    "/api/auth/status",
    "/api/auth/logout",
}
_BASE_EVALUATE_REQUEST = legacy.evaluate_request


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def _enforce_login_throttle(request: Request) -> None:
    try:
        allowed, retry_after = _SESSION_TRUTH.login_allowed(
            _client_key(request),
            window_seconds=_AUTH_WINDOW_S,
            max_failures=_AUTH_MAX_FAILURES,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Dashboard session authority unavailable",
        ) from exc
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many failed dashboard login attempts; retry later",
            headers={"Retry-After": str(retry_after)},
        )


def _record_failed_login(request: Request) -> None:
    try:
        count = _SESSION_TRUTH.record_login_failure(
            _client_key(request),
            window_seconds=_AUTH_WINDOW_S,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Dashboard session authority unavailable",
        ) from exc
    if count >= _AUTH_MAX_FAILURES:
        raise HTTPException(
            status_code=429,
            detail="Too many failed dashboard login attempts; retry later",
            headers={"Retry-After": str(_AUTH_WINDOW_S)},
        )


def _clear_login_failures(request: Request) -> None:
    try:
        _SESSION_TRUTH.clear_login_failures(_client_key(request))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Dashboard session authority unavailable",
        ) from exc


def _forwarded_scheme(request: Request) -> str:
    return request.headers.get(
        "X-Forwarded-Proto", request.url.scheme
    ).split(",")[0].strip().lower()


def _forwarded_host(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-Host", "").split(",")[0].strip()
    return forwarded or request.headers.get("Host", "")


def _same_origin(request: Request) -> str:
    host = _forwarded_host(request)
    return f"{_forwarded_scheme(request)}://{host}" if host else ""


def _origin_allowed(request: Request) -> bool:
    origin = request.headers.get("Origin", "").rstrip("/")
    if not origin:
        return False
    allowed = {str(value).rstrip("/") for value in legacy._allowed_origins}
    return origin == _same_origin(request).rstrip("/") or origin in allowed


def _session_record(request: Request, *, surface_backend_error: bool = False):
    token = request.cookies.get(legacy._DASHBOARD_SESSION_COOKIE, "")
    if not token:
        return None
    try:
        return _SESSION_TRUTH.validate(token)
    except Exception as exc:
        if surface_backend_error:
            raise HTTPException(
                status_code=503,
                detail="Dashboard session authority unavailable",
            ) from exc
        return None


def _has_dashboard_api_access(request: Request) -> bool:
    """Compatibility access check. Public PAPER viewing never calls this authority."""
    if not legacy._REQUIRE_API_KEY or not legacy._API_KEY:
        return False
    header_key = request.headers.get("X-API-Key", "")
    if header_key and hmac.compare_digest(header_key, legacy._API_KEY):
        return True
    return _session_record(request) is not None


# Existing middleware resolves these globals at request time. Replacing the
# functions changes authority without duplicating/reordering the legacy
# RequestID/security middleware stack.
legacy._has_dashboard_api_access = _has_dashboard_api_access


def _capability_aware_request_policy(**kwargs) -> SecurityDecision:
    """Apply MutationPolicy before the legacy auth/origin policy.

    A separate browser/control mutation authority does not exist in the public
    PAPER dashboard, so `control_authorized` is deliberately False. This makes
    the product publicly readable but not publicly writable.
    """
    mutation = evaluate_runtime_mutation(
        kwargs.get("method", ""),
        kwargs.get("path", ""),
        worker_token_configured=bool(kwargs.get("worker_token_configured")),
        worker_token_valid=bool(kwargs.get("worker_token_valid")),
        control_authorized=False,
    )
    if mutation is None:
        return _BASE_EVALUATE_REQUEST(**kwargs)

    if not mutation.allowed:
        return SecurityDecision(
            False,
            mutation.status_code,
            mutation.reason,
            mutation.code,
        )

    # Worker authority is capability-specific and must not be forced through a
    # dashboard/session auth path. Handler schema/domain validation still runs.
    if mutation.capability is Capability.WORKER_INGEST:
        return SecurityDecision(True)

    # Session compatibility endpoints retain their existing endpoint policy.
    return _BASE_EVALUATE_REQUEST(**kwargs)


legacy.evaluate_request = _capability_aware_request_policy

# Remove the three legacy deterministic-cookie route objects before registering
# the authoritative versions below. All other app routes/startup hooks remain.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in _AUTH_PATHS
]


@app.post("/api/auth/session")
async def create_dashboard_session(payload: legacy.DashboardAuthRequest, request: Request):
    if not legacy._REQUIRE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Dashboard authentication is disabled; sessions cannot be created",
        )
    if not legacy._API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Dashboard API auth is required but API_KEY is not configured",
        )

    _enforce_login_throttle(request)
    supplied = (payload.api_key or "").strip()
    if not hmac.compare_digest(supplied, legacy._API_KEY):
        _record_failed_login(request)
        raise HTTPException(status_code=401, detail="Invalid dashboard API key")

    _clear_login_failures(request)
    try:
        token, session = _SESSION_TRUTH.issue(
            max_age_seconds=legacy._DASHBOARD_SESSION_MAX_AGE,
            principal="dashboard",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Dashboard session authority unavailable",
        ) from exc

    response = JSONResponse(
        {
            "ok": True,
            "authenticated": True,
            "mode": "opaque_server_session",
            "session_backend": _SESSION_TRUTH.backend_name,
            "session": session.public_dict(),
        }
    )
    response.set_cookie(
        legacy._DASHBOARD_SESSION_COOKIE,
        token,
        max_age=legacy._DASHBOARD_SESSION_MAX_AGE,
        httponly=True,
        secure=_forwarded_scheme(request) == "https",
        samesite="lax",
        path="/",
    )
    return response


@app.get("/api/auth/status")
async def dashboard_auth_status(request: Request):
    session = _session_record(request, surface_backend_error=True)
    header_key = request.headers.get("X-API-Key", "")
    header_ok = bool(
        legacy._REQUIRE_API_KEY
        and legacy._API_KEY
        and header_key
        and hmac.compare_digest(header_key, legacy._API_KEY)
    )
    return {
        "required": legacy._REQUIRE_API_KEY,
        "configured": bool(legacy._API_KEY),
        "authenticated": bool(session or header_ok),
        "mode": (
            "opaque_server_session"
            if session
            else "api_key_header"
            if header_ok
            else "session_cookie_or_header"
            if legacy._REQUIRE_API_KEY
            else "auth_disabled"
        ),
        "session_backend": _SESSION_TRUTH.backend_name,
        "session": session.public_dict() if session else None,
    }


@app.post("/api/auth/logout")
async def dashboard_auth_logout(request: Request):
    if request.cookies.get(legacy._DASHBOARD_SESSION_COOKIE) and not _origin_allowed(request):
        raise HTTPException(status_code=403, detail="Origin validation failed")
    token = request.cookies.get(legacy._DASHBOARD_SESSION_COOKIE, "")
    if token:
        try:
            revoked = _SESSION_TRUTH.revoke(token)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Dashboard session authority unavailable",
            ) from exc
    else:
        revoked = False
    response = JSONResponse(
        {
            "ok": True,
            "authenticated": False,
            "server_revoked": revoked,
            "session_backend": _SESSION_TRUTH.backend_name,
        }
    )
    response.delete_cookie(
        legacy._DASHBOARD_SESSION_COOKIE,
        path="/",
        samesite="lax",
        secure=_forwarded_scheme(request) == "https",
        httponly=True,
    )
    return response


def _sentinel_reached(capability: str) -> None:
    # These handlers have no mutation implementation. Runtime deployment probes
    # expect security middleware to stop the request before this function runs.
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


# Import/startup must fail if a newly added write route bypasses classification or
# duplicates an existing method/path owner. This is runtime authority, not only CI.
assert_runtime_manifest(app)
