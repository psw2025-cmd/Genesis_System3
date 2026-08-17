"""Deterministic Cloud Run Dhan broker status probe.

Safety: read-only profile GET only; no order APIs; no raw token output.
Legacy ``error`` values are preserved for confirmed token/auth failures;
``auth_classification`` adds explicit clock-vs-upstream rejection semantics.
Known non-token-recovery upstream failures use ``upstream_classification``
instead of polluting authentication state. The first affirmative upstream auth
rejection is latched with safe metadata before any Secret Manager reload/recovery
can obscure event ordering.
"""
from __future__ import annotations

import base64
import json
import re
import time
from datetime import datetime, timezone
from typing import Any

from core.brokers.dhan.first_rejection_trace import record_auth_rejection, snapshot


_TOKEN_AUTH_CODES = {901, 807, 808, 809}
_RATE_LIMIT_CODES = {904, 805}
_CLIENT_ID_INVALID_CODES = {810}
_REQUEST_REJECTED_CODES = {906}


def _clock_expired(token: str) -> bool | None:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        exp = json.loads(base64.urlsafe_b64decode(payload.encode("ascii"))).get("exp")
        if exp is None:
            return None
        return float(exp) <= datetime.now(timezone.utc).timestamp()
    except Exception:
        return None


def _auth_classification(token: str) -> str:
    expired = _clock_expired(token)
    if expired is True:
        return "TOKEN_CLOCK_EXPIRED"
    if expired is False:
        return "DHAN_TOKEN_REJECTED"
    return "DHAN_TOKEN_REJECTED_CLOCK_UNKNOWN"


def _safe_upstream_code(blob: str) -> int | None:
    """Extract only a numeric Dhan error code; never return response text."""
    text = str(blob or "")
    for pattern in (
        r'"(?:error[_-]?code|code)"\s*:\s*"?(?:dh-)?(\d{3,5})',
        r"\b(?:error[_-]?code|code)\s*[=: ]\s*(?:dh-)?(\d{3,5})\b",
        r"\bdh-(\d{3,5})\b",
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def _http_auth_failure(status_code: Any, blob: str) -> bool:
    """Return true only for affirmative token/authentication evidence.

    Current Dhan documentation distinguishes:
    - trading auth: DH-901;
    - data auth/token: 807/808/809;
    - invalid client id: 810 (configuration, not token recovery);
    - rate limiting: DH-904/805;
    - request/order rejection: DH-906.
    Numeric codes override ambiguous free text.
    """
    code = _safe_upstream_code(blob)
    if code in _RATE_LIMIT_CODES | _REQUEST_REJECTED_CODES | _CLIENT_ID_INVALID_CODES:
        return False
    if status_code == 401 or code in _TOKEN_AUTH_CODES:
        return True
    auth_markers = (
        "invalid token",
        "invalid access token",
        "access token is expired",
        "token expired",
        "token is expired",
        "authentication failed",
        "invalid authentication",
    )
    return status_code == 400 and any(marker in blob for marker in auth_markers)


def _non_auth_upstream_classification(status_code: Any, blob: str) -> str | None:
    """Classify failures that must not trigger token recovery."""
    code = _safe_upstream_code(blob)
    if code in _RATE_LIMIT_CODES or status_code == 429:
        return "DHAN_RATE_LIMITED"
    if code in _REQUEST_REJECTED_CODES:
        return "DHAN_REQUEST_REJECTED_906"
    if code in _CLIENT_ID_INVALID_CODES:
        return "DHAN_CLIENT_ID_INVALID"
    return None


def _payload_blob(data: Any) -> str:
    try:
        return json.dumps(data, sort_keys=True, default=str).lower()
    except Exception:
        return str(data or "").lower()


def _payload_failure(data: Any) -> tuple[str | None, str | None, int | None]:
    """Classify a JSON payload returned with HTTP success semantics.

    Returns ``(error, upstream_classification, upstream_code)``. ``None`` error
    means no failure evidence was present.
    """
    if not isinstance(data, dict):
        return None, None, None
    blob = _payload_blob(data)
    code = _safe_upstream_code(blob)
    status = str(data.get("status") or "").strip().lower()

    if code in _TOKEN_AUTH_CODES:
        return "TOKEN_EXPIRED_OR_INVALID", None, code
    if code in _CLIENT_ID_INVALID_CODES:
        return "CLIENT_ID_INVALID", "DHAN_CLIENT_ID_INVALID", code
    if code in _RATE_LIMIT_CODES:
        return "DHAN_RATE_LIMITED", "DHAN_RATE_LIMITED", code
    if code in _REQUEST_REJECTED_CODES:
        return "DHAN_REQUEST_REJECTED_906", "DHAN_REQUEST_REJECTED_906", code

    auth_markers = (
        "invalid token",
        "invalid access token",
        "access token is expired",
        "token expired",
        "token is expired",
        "authentication failed",
        "invalid authentication",
    )
    if any(marker in blob for marker in auth_markers):
        return "TOKEN_EXPIRED_OR_INVALID", None, code
    if status in {"failure", "failed", "error"}:
        return "DHAN_UPSTREAM_FAILURE", "DHAN_UPSTREAM_FAILURE", code
    return None, None, code


def _secret_version() -> str | None:
    try:
        from core.brokers.dhan.cloud_token_provider import token_metadata

        return str(token_metadata().get("secret_version") or "") or None
    except Exception:
        return None


def _record_rejection(token: str, status_code: int | None, blob: str) -> dict[str, Any]:
    classification = _auth_classification(token)
    return record_auth_rejection(
        secret_version=_secret_version(),
        auth_classification=classification,
        http_status=status_code,
        upstream_code=_safe_upstream_code(blob),
    )


def get_cloud_status(module: Any, *, timeout_s: float = 5.0) -> dict[str, Any]:
    now = time.time()
    cache = getattr(module, "_STATUS_RESULT_CACHE", None)
    cache_at = float(getattr(module, "_STATUS_RESULT_CACHE_AT", 0.0) or 0.0)
    ttl = float(getattr(module, "_STATUS_RESULT_TTL_S", 25.0) or 25.0)
    if cache and (now - cache_at) < ttl and cache.get("connected") is True:
        out = dict(cache)
        out.update(
            cache_hit=True,
            cache_age_s=round(now - cache_at, 1),
            probe_strategy="cloud_rest_profile_bounded",
            auth_rejection_trace=snapshot(),
        )
        return out

    creds = module.get_dhan_credentials()
    client_id = str(creds.get("client_id") or "").strip().lstrip("\ufeff")
    access_token = str(creds.get("access_token") or "").strip().lstrip("\ufeff")
    base = {
        "broker": "dhan",
        "mode": "ANALYZER",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "client_id_present": bool(client_id),
        "access_token_present": bool(access_token),
        "credentials_present": bool(client_id and access_token),
        "sdk_available": bool(getattr(module, "_DHAN_SDK_OK", False)),
        "env_source": getattr(module, "_ENV_LOADED_VIA", "unknown"),
        "cache_hit": False,
        "probe_strategy": "cloud_rest_profile_bounded",
        "probe_header_contract": "access-token-only",
        "probe_timeout_s": float(timeout_s),
        "auth_rejection_trace": snapshot(),
    }
    if not client_id or not access_token:
        return {
            **base,
            "connected": False,
            "error": "CONFIG_MISSING",
            "auth_classification": "CONFIG_MISSING",
            "upstream_classification": None,
            "upstream_code": None,
            "latency_ms": 0,
        }

    started = time.monotonic()
    try:
        # Dhan User Profile is documented as access-token-only. The existing
        # client id remains available from Secret Manager for endpoints that
        # explicitly require it (for example Option Chain / Market Quote).
        data = module._rest_get(
            module._DHAN_PROFILE_URL,
            access_token,
            client_id,
            timeout=max(1, min(float(timeout_s), 8.0)),
            include_client_id=False,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        payload_error, upstream_classification, upstream_code = _payload_failure(data)
        if payload_error == "TOKEN_EXPIRED_OR_INVALID":
            trace = _record_rejection(access_token, None, _payload_blob(data))
            return {
                **base,
                "connected": False,
                "error": payload_error,
                "auth_classification": _auth_classification(access_token),
                "upstream_classification": None,
                "upstream_code": upstream_code,
                "auth_rejection_trace": trace,
                "latency_ms": latency_ms,
            }
        if payload_error:
            return {
                **base,
                "connected": False,
                "error": payload_error,
                "auth_classification": None,
                "upstream_classification": upstream_classification,
                "upstream_code": upstream_code,
                "auth_rejection_trace": snapshot(),
                "latency_ms": latency_ms,
            }

        result = {
            **base,
            "connected": True,
            "error": None,
            "auth_classification": "AUTH_OK",
            "upstream_classification": None,
            "upstream_code": None,
            "auth_rejection_trace": snapshot(),
            "latency_ms": latency_ms,
            "profile_source": "rest",
        }
        module._STATUS_RESULT_CACHE = dict(result)
        module._STATUS_RESULT_CACHE_AT = time.time()
        return result
    except Exception as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None) if response is not None else None
        try:
            body = str(getattr(response, "text", "") or "")[:160] if response is not None else ""
        except Exception:
            body = ""
        blob = f"{status_code or ''} {body} {exc}".lower()
        upstream_code = _safe_upstream_code(blob)
        classification = None
        upstream_classification = None
        trace = snapshot()
        if _http_auth_failure(status_code, blob):
            error = "TOKEN_EXPIRED_OR_INVALID"
            classification = _auth_classification(access_token)
            trace = _record_rejection(access_token, status_code, blob)
        else:
            upstream_classification = _non_auth_upstream_classification(status_code, blob)
            if upstream_classification == "DHAN_REQUEST_REJECTED_906":
                error = "DHAN_REQUEST_REJECTED_906"
            elif upstream_classification == "DHAN_RATE_LIMITED":
                error = "DHAN_RATE_LIMITED"
            elif upstream_classification == "DHAN_CLIENT_ID_INVALID":
                error = "CLIENT_ID_INVALID"
            elif status_code == 403 or "forbidden" in blob:
                error = "ACCESS_FORBIDDEN"
            elif status_code:
                error = f"HTTP_{status_code}"
            else:
                error = f"NETWORK_ERROR:{type(exc).__name__}"
        return {
            **base,
            "connected": False,
            "error": error,
            "auth_classification": classification,
            "upstream_classification": upstream_classification,
            "upstream_code": upstream_code,
            "auth_rejection_trace": trace,
            "latency_ms": latency_ms,
        }
