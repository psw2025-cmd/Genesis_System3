"""Canonical write-route capability classification for Genesis System3.

The policy is intentionally fail-closed: every HTTP mutation route must map to
one capability. UNKNOWN is a CI/runtime blocker. LIVE_MUTATION is denied in the
current analyzer/paper runtime regardless of UI state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional


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


def classify_mutation(method: str, path: str) -> Optional[Capability]:
    method = method.upper()
    if method not in WRITE_METHODS:
        return None

    p = path.rstrip("/") or "/"

    if p == "/api/auth/session":
        return Capability.SESSION_CREATE
    if p == "/api/auth/logout":
        return Capability.SESSION_REVOKE_SELF

    if p.startswith(("/api/worker/", "/api/gcp/runtime/", "/api/runtime/push")):
        return Capability.WORKER_INGEST

    if p.startswith("/api/live-trading/approve"):
        return Capability.LIVE_APPROVAL
    if p.startswith(("/api/live-trading/", "/api/orders/", "/place-order", "/modify-order", "/cancel-order")):
        return Capability.LIVE_MUTATION

    if p == "/api/paper/tick" or p.startswith("/api/paper/"):
        return Capability.PAPER_MUTATION
    if p.startswith("/api/positions/") and p.endswith("/close"):
        return Capability.PAPER_MUTATION

    if p.startswith(("/api/kill-switch", "/api/safety/")):
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


def capability_for_request(method: str, path: str) -> Capability:
    return classify_mutation(method, path) or Capability.UNKNOWN
