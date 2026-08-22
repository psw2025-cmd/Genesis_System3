"""Pure request-authorization policy for the System3 public-readonly dashboard.

This module deliberately has no FastAPI, broker, model or data imports, so its
security boundary can be tested without loading the large application.

Dashboard API-key/login/session authority is permanently retired. Legacy auth
arguments remain in the function signature only for compatibility with older
callers; they cannot grant access. Safe reads are public, dedicated worker
pushes require the worker token, and every other mutation fails closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


PUBLIC_PREFIXES = ("/ui", "/assets")
PUBLIC_EXACT = {
    "/",
    "/api/health",
    "/health",
    "/healthz",
    "/api/auth/status",
    "/favicon.ico",
}
RETIRED_AUTH_PATHS = {
    "/api/auth/session",
    "/api/auth/logout",
}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
WORKER_PUSH_PATHS = {
    "/api/scheduler/health/push",
    "/api/chain/push",
}
AUTHORITY_REQUIRED_MUTATION_PATHS = {"/api/paper/tick"}


@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    status_code: int = 200
    detail: str = ""
    code: str = ""


def _has_public_prefix(path: str) -> bool:
    return any(
        path == prefix or path.startswith(prefix + "/")
        for prefix in PUBLIC_PREFIXES
    )


def evaluate_request(
    *,
    method: str,
    path: str,
    require_api_key: bool,
    api_key_configured: bool,
    dashboard_access: bool,
    worker_token_configured: bool = False,
    worker_token_valid: bool = False,
    header_api_key_present: bool = False,
    origin: str = "",
    same_origin: str = "",
    allowed_origins: Iterable[str] = (),
    idempotency_key_present: bool = False,
) -> SecurityDecision:
    """Evaluate one request under the permanent public-readonly contract.

    The legacy dashboard-auth parameters are intentionally ignored. Keeping the
    signature avoids breaking old internal callers while making it impossible
    for configuration drift or a supplied API key/session to restore mutation
    authority.
    """
    del (
        require_api_key,
        api_key_configured,
        dashboard_access,
        header_api_key_present,
        origin,
        same_origin,
        allowed_origins,
        idempotency_key_present,
    )

    method = method.upper()

    if method == "OPTIONS":
        return SecurityDecision(True)

    if path in RETIRED_AUTH_PATHS:
        return SecurityDecision(
            False,
            404,
            "Dashboard login/session authority is permanently retired",
            "DASHBOARD_AUTH_RETIRED",
        )

    if path in WORKER_PUSH_PATHS:
        if not worker_token_configured:
            return SecurityDecision(
                False,
                503,
                "WORKER_PUSH_TOKEN is required for worker ingestion",
                "WORKER_AUTH_NOT_CONFIGURED",
            )
        if not worker_token_valid:
            return SecurityDecision(
                False,
                401,
                "Invalid or missing X-Worker-Token",
                "WORKER_AUTH_INVALID",
            )
        return SecurityDecision(True)

    if method in SAFE_METHODS:
        return SecurityDecision(True)

    if path in AUTHORITY_REQUIRED_MUTATION_PATHS:
        return SecurityDecision(
            False,
            503,
            "Separate mutation authority is required but unavailable",
            "AUTH_REQUIRED_FOR_MUTATION",
        )

    return SecurityDecision(
        False,
        403,
        "Public dashboard is read-only; mutation authority is separate",
        "PUBLIC_DASHBOARD_READ_ONLY",
    )
