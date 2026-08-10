"""Pure request-authorization policy for the System3 dashboard.

This module deliberately has no FastAPI, broker, model or data imports, so its
security boundary can be tested without loading the large application.
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
    "/api/auth/session",
    "/api/auth/status",
    "/api/auth/logout",
    "/favicon.ico",
}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
WORKER_PUSH_PATHS = {
    "/api/scheduler/health/push",
    "/api/chain/push",
}
IDEMPOTENCY_REQUIRED_PATHS = {
    "/api/orders/create",
    "/place-order",
}


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
    method = method.upper()

    if (
        method == "OPTIONS"
        or path in PUBLIC_EXACT
        or _has_public_prefix(path)
    ):
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

    is_mutation = method not in SAFE_METHODS

    if not require_api_key:
        if is_mutation:
            return SecurityDecision(
                False,
                503,
                "Authentication must be enabled before mutation routes can be used",
                "AUTH_REQUIRED_FOR_MUTATION",
            )
        return SecurityDecision(True)

    if not api_key_configured:
        return SecurityDecision(
            False,
            503,
            "Dashboard authentication is required but API_KEY is not configured",
            "AUTH_NOT_CONFIGURED",
        )

    if not dashboard_access:
        return SecurityDecision(
            False,
            401,
            "Missing or invalid dashboard API session",
            "AUTH_INVALID",
        )

    if is_mutation:
        if not header_api_key_present:
            allowed = set(allowed_origins)
            if (
                not origin
                or (
                    origin != same_origin
                    and origin not in allowed
                )
            ):
                return SecurityDecision(
                    False,
                    403,
                    "Origin validation failed",
                    "CSRF_ORIGIN_REJECTED",
                )

        if (
            path in IDEMPOTENCY_REQUIRED_PATHS
            and not idempotency_key_present
        ):
            return SecurityDecision(
                False,
                428,
                "Idempotency-Key header is required for this operation",
                "IDEMPOTENCY_KEY_REQUIRED",
            )

    return SecurityDecision(True)
