"""Canonical write-route capability classification and runtime authority policy.

Every HTTP mutation route must map to exactly one capability. UNKNOWN is a
runtime/CI blocker. LIVE_MUTATION and LIVE_APPROVAL are hard denied in the
current ANALYZER/PAPER runtime regardless of UI state, environment drift or
legacy route behavior.

The public dashboard is intentionally read-only. Except for self-session routes
and authenticated worker ingestion, control/paper/risk/scheduler/analyzer writes
remain denied until a separate mutation control authority is implemented.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class Capability(str, Enum):
    SESSION_CREATE = "SESSION_CREATE"
    SESSION_REVOKE_SELF = "SESSION_REVOKE_SELF"
    WORKER_INGEST = "WORKER_INGEST"
    PAPER_MUTATION = "PAPER_MUTATION"
    RISK_POLICY_WRITE = "RISK_POLICY_WRITE"
    SAFETY_CONTROL = "SAFETY_CONTROL"
    SCHEDULER_CONTROL = "SCHEDULER_CONTROL"
    PREFERENCE_WRITE = "PREFERENCE_WRITE"
    ANALYZER_COMMAND = "ANALYZER_COMMAND"
    LIVE_APPROVAL = "LIVE_APPROVAL"
    LIVE_MUTATION = "LIVE_MUTATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MutationRoute:
    method: str
    path: str
    capability: Capability


@dataclass(frozen=True)
class RuntimeMutationDecision:
    allowed: bool
    capability: Capability
    state: str
    status_code: int
    code: str
    reason: str
    authority: str

    def public_dict(self) -> Dict[str, object]:
        return {
            "allowed": self.allowed,
            "capability": self.capability.value,
            "state": self.state,
            "status_code": self.status_code,
            "code": self.code,
            "reason": self.reason,
            "authority": self.authority,
        }


def classify_mutation(method: str, path: str) -> Optional[Capability]:
    method = method.upper()
    if method not in WRITE_METHODS:
        return None

    p = path.rstrip("/") or "/"

    # Safe runtime proof sentinels. Their handlers never mutate state and raise
    # if reached, so deployment tests can prove middleware enforcement without
    # touching paper state or any broker/order implementation.
    if p == "/api/security/mutation-policy/probe/live":
        return Capability.LIVE_MUTATION
    if p == "/api/security/mutation-policy/probe/worker":
        return Capability.WORKER_INGEST
    if p == "/api/security/mutation-policy/probe/paper":
        return Capability.PAPER_MUTATION

    if p == "/api/auth/session":
        return Capability.SESSION_CREATE
    if p == "/api/auth/logout":
        return Capability.SESSION_REVOKE_SELF

    if p in {"/api/scheduler/health/push", "/api/chain/push"}:
        return Capability.WORKER_INGEST
    if p.startswith((
        "/api/worker/",
        "/api/gcp/runtime/",
        "/api/runtime/push",
    )):
        return Capability.WORKER_INGEST

    if p.startswith("/api/live-trading/approve"):
        return Capability.LIVE_APPROVAL
    if p.startswith((
        "/api/live-trading/",
        "/api/orders/",
        "/place-order",
        "/modify-order",
        "/cancel-order",
    )):
        return Capability.LIVE_MUTATION

    if p == "/api/paper/tick" or p.startswith("/api/paper/"):
        return Capability.PAPER_MUTATION
    if p.startswith("/api/positions/") and p.endswith("/close"):
        return Capability.PAPER_MUTATION

    if p.startswith(("/api/kill-switch", "/api/safety/", "/api/security/")):
        return Capability.SAFETY_CONTROL
    if p.startswith(("/api/risk/", "/api/risk-management/")):
        return Capability.RISK_POLICY_WRITE
    if p.startswith(("/api/scheduler/", "/api/schedules/")):
        return Capability.SCHEDULER_CONTROL

    if p.startswith(("/api/settings/", "/api/preferences/", "/api/alerts/")):
        return Capability.PREFERENCE_WRITE

    if p.startswith((
        "/api/analyzer/",
        "/api/analysis/",
        "/api/backtest/",
        "/api/simulation/",
        "/api/scanner/",
        "/api/ml/",
        "/api/model/",
        "/api/prediction/",
        "/api/retrain/",
    )):
        return Capability.ANALYZER_COMMAND

    return Capability.UNKNOWN


def inventory_write_routes(app) -> List[MutationRoute]:
    rows: List[MutationRoute] = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods: Iterable[str] = getattr(route, "methods", set()) or set()
        for method in sorted(methods):
            if method.upper() not in WRITE_METHODS:
                continue
            capability = classify_mutation(method, path) or Capability.UNKNOWN
            rows.append(MutationRoute(method.upper(), path, capability))
    return sorted(rows, key=lambda row: (row.path, row.method))


def unclassified_write_routes(app) -> List[MutationRoute]:
    return [row for row in inventory_write_routes(app) if row.capability is Capability.UNKNOWN]


def duplicate_write_routes(app) -> List[Tuple[str, str]]:
    counts: Dict[Tuple[str, str], int] = {}
    for row in inventory_write_routes(app):
        key = (row.method, row.path)
        counts[key] = counts.get(key, 0) + 1
    return sorted(key for key, count in counts.items() if count > 1)


def assert_runtime_manifest(app) -> None:
    """Fail application startup/import if mutation ownership is ambiguous."""
    unknown = unclassified_write_routes(app)
    duplicates = duplicate_write_routes(app)
    if unknown or duplicates:
        unknown_text = ", ".join(
            f"{row.method} {row.path}" for row in unknown
        ) or "none"
        duplicate_text = ", ".join(
            f"{method} {path}" for method, path in duplicates
        ) or "none"
        raise RuntimeError(
            "MUTATION_MANIFEST_INVALID "
            f"unknown=[{unknown_text}] duplicates=[{duplicate_text}]"
        )


def capability_for_request(method: str, path: str) -> Capability:
    return classify_mutation(method, path) or Capability.UNKNOWN


def evaluate_runtime_mutation(
    method: str,
    path: str,
    *,
    worker_token_configured: bool = False,
    worker_token_valid: bool = False,
    control_authorized: bool = False,
) -> Optional[RuntimeMutationDecision]:
    """Return the authoritative runtime mutation decision.

    `control_authorized` is intentionally False in the current public PAPER
    dashboard. It exists only as an explicit future integration point for a
    separate control-plane authority; dashboard viewing never sets it True.
    """
    capability = classify_mutation(method, path)
    if capability is None:
        return None

    if capability is Capability.UNKNOWN:
        return RuntimeMutationDecision(
            False,
            capability,
            "DENY",
            403,
            "MUTATION_CAPABILITY_UNKNOWN",
            "Write request has no approved mutation capability",
            "NONE",
        )

    if capability is Capability.LIVE_MUTATION:
        return RuntimeMutationDecision(
            False,
            capability,
            "DENY",
            423,
            "LIVE_MUTATION_LOCKED",
            "Live mutation is hard locked in ANALYZER/PAPER runtime",
            "HARD_LIVE_LOCK",
        )

    if capability is Capability.LIVE_APPROVAL:
        return RuntimeMutationDecision(
            False,
            capability,
            "DENY",
            423,
            "LIVE_APPROVAL_LOCKED",
            "Live approval cannot become execution authority in ANALYZER/PAPER",
            "HARD_LIVE_LOCK",
        )

    if capability is Capability.WORKER_INGEST:
        if not worker_token_configured:
            return RuntimeMutationDecision(
                False,
                capability,
                "DENY",
                503,
                "WORKER_AUTH_NOT_CONFIGURED",
                "Worker ingestion token is not configured",
                "WORKER_TOKEN",
            )
        if not worker_token_valid:
            return RuntimeMutationDecision(
                False,
                capability,
                "DENY",
                401,
                "WORKER_AUTH_INVALID",
                "Worker ingestion requires a valid dedicated worker token",
                "WORKER_TOKEN",
            )
        return RuntimeMutationDecision(
            True,
            capability,
            "ALLOW",
            200,
            "WORKER_AUTH_ACCEPTED",
            "Dedicated worker authority accepted; handler validation still applies",
            "WORKER_TOKEN",
        )

    if capability in {Capability.SESSION_CREATE, Capability.SESSION_REVOKE_SELF}:
        return RuntimeMutationDecision(
            True,
            capability,
            "ALLOW_DOWNSTREAM",
            200,
            "SESSION_ROUTE",
            "Session route may reach its own endpoint-specific policy",
            "SESSION_ROUTE",
        )

    if not control_authorized:
        return RuntimeMutationDecision(
            False,
            capability,
            "DENY",
            403,
            f"{capability.value}_AUTHORITY_REQUIRED",
            "Public PAPER dashboard is read-only; separate mutation authority is required",
            "CONTROL_PLANE",
        )

    return RuntimeMutationDecision(
        True,
        capability,
        "ALLOW_DOWNSTREAM",
        200,
        f"{capability.value}_AUTHORITY_ACCEPTED",
        "Mutation control authority accepted; downstream domain/idempotency gates still apply",
        "CONTROL_PLANE",
    )
