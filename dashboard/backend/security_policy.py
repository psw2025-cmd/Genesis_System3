"""Pure request-authorization policy for the System3 public PAPER dashboard.

Dashboard visibility is permanently credential-free. This policy contains no
browser/dashboard credential authority. Safe reads are public; authenticated
worker ingestion is bound only to the dedicated worker token; every other write
remains fail-closed unless MutationPolicy supplies a separate control authority.
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
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
WORKER_PUSH_PATHS = {
    "/api/scheduler/health/push",
    "/api/chain/push",
}


@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    status_code: int = 200
    detail: str = ""
    code: str = ""


def _has_public_prefix(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in PUBLIC_PREFIXES)


def evaluate_request(
    *,
    method: str,
    path: str,
    worker_token_configured: bool = False,
    worker_token_valid: bool = False,
    origin: str = "",
    same_origin: str = "",
    allowed_origins: Iterable[str] = (),
    idempotency_key_present: bool = False,
    **_obsolete_dashboard_credential_fields,
) -> SecurityDecision:
    """Authorize public reads and dedicated worker ingestion only.

    Extra keyword fields are ignored solely so an older inner middleware cannot
    reactivate the retired dashboard credential model. They grant no authority.
    """
    del origin, same_origin, allowed_origins, idempotency_key_present
    method = method.upper()

    if method == "OPTIONS" or path in PUBLIC_EXACT or _has_public_prefix(path):
        return SecurityDecision(True)

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

    return SecurityDecision(
        False,
        403,
        "Public dashboard is read-only; mutation authority is separate",
        "PUBLIC_DASHBOARD_READ_ONLY",
    )
