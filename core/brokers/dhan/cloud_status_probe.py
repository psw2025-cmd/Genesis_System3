"""Deterministic Cloud Run Dhan broker status probe.

Safety: read-only profile GET only; no order APIs; no raw token output.
Legacy ``error`` values are preserved for confirmed auth failures;
``auth_classification`` adds explicit clock-vs-upstream rejection semantics.
The first affirmative upstream auth rejection is latched with safe metadata before
any Secret Manager reload/recovery can obscure event ordering.
"""
from __future__ import annotations

import base64
import json
import re
import time
from datetime import datetime, timezone
from typing import Any

from core.brokers.dhan.first_rejection_trace import record_auth_rejection, snapshot


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
    for pattern in (r'"code"\s*:\s*(\d{3,5})', r"\bcode\s+(\d{3,5})\b", r"\bdh-(\d{3,5})\b"):
        match = re.search(pattern, blob, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def _http_auth_failure(status_code: Any, blob: str) -> bool:
    """Return true only for affirmative upstream authentication evidence.

    Dhan DH-906 is an order/request error, not an authentication code. Dhan 805
    is rate limiting. Neither may invalidate the token or increment the first
    authentication-rejection latch. Dhan 808 and HTTP 401 remain affirmative
    authentication evidence.
    """
    if status_code == 401:
        return True
    if _safe_upstream_code(blob) == 808:
        return True
    auth_markers = (
        "invalid token",
        "invalid access token",
        "token expired",
        "token is expired",
        "authentication failed",
        "authentication error",
    )
    return status_code == 400 and any(marker in blob for marker in auth_markers)


def _non_auth_upstream_classification(status_code: Any, blob: str) -> tuple[str | None, str | None]:
    """Classify known non-auth Dhan failures without changing auth state."""
    code = _safe_upstream_code(blob)
    if code == 805 or status_code == 429:
        return "DHAN_RATE_LIMITED", "DHAN_RATE_LIMITED"
    if code == 906:
        return "DHAN_REQUEST_REJECTED_906", "DHAN_REQUEST_REJECTED_906"
    return None, None


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
        "probe_timeout_s": float(timeout_s),
        "auth_rejection_trace": snapshot(),
    }
    if not client_id or not access_token:
        return {
            **base,
            "connected": False,
            "error": "CONFIG_MISSING",
            "auth_classification": "CONFIG_MISSING",
            "latency_ms": 0,
        }
    started = time.monotonic()
    try:
        data = module._rest_get(
            module._DHAN_PROFILE_URL,
            access_token,
            client_id,
            timeout=max(1, min(float(timeout_s), 8.0)),
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        if module._auth_failure_payload(data):
            classification = _auth_classification(access_token)
            trace = _record_rejection(access_token, 401, str(data or "").lower())
            return {
                **base,
                "connected": False,
                "error": "TOKEN_EXPIRED_OR_INVALID",
                "auth_classification": classification,
                "auth_rejection_trace": trace,
                "latency_ms": latency_ms,
            }
        result = {
            **base,
            "connected": True,
            "error": None,
            "auth_classification": "AUTH_OK",
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
        classification = None
        trace = snapshot()
        if _http_auth_failure(status_code, blob):
            error = "TOKEN_EXPIRED_OR_INVALID"
            classification = _auth_classification(access_token)
            trace = _record_rejection(access_token, status_code, blob)
        else:
            non_auth_error, non_auth_classification = _non_auth_upstream_classification(status_code, blob)
            if non_auth_error:
                error = non_auth_error
                classification = non_auth_classification
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
            "auth_rejection_trace": trace,
            "latency_ms": latency_ms,
        }
