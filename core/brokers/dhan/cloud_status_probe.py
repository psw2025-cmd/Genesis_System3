"""Deterministic Cloud Run Dhan broker status probe.

Safety: read-only profile GET only; no order APIs; no raw token output.
Legacy ``error`` values are preserved for confirmed auth failures;
``auth_classification`` adds explicit clock-vs-upstream rejection semantics.
"""
from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timezone
from typing import Any


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


def _http_auth_failure(status_code: Any, blob: str) -> bool:
    """Return true only for an HTTP exception with affirmative auth evidence.

    Dhan profile HTTP 401 is authentication failure by boundary. HTTP 400 is
    deliberately *not* sufficient on its own: only known auth markers/codes
    may promote a 400 to token-invalid. This prevents malformed/non-auth 400s
    from being mislabeled as premature Dhan token rejection.
    """
    if status_code == 401:
        return True
    auth_markers = (
        "dh-906",
        "code 808",
        '"code":808',
        '"code": 808',
        "invalid token",
        "invalid access token",
        "token expired",
        "token is expired",
        "authentication failed",
        "authentication error",
    )
    return status_code == 400 and any(marker in blob for marker in auth_markers)


def get_cloud_status(module: Any, *, timeout_s: float = 5.0) -> dict[str, Any]:
    now = time.time()
    cache = getattr(module, "_STATUS_RESULT_CACHE", None)
    cache_at = float(getattr(module, "_STATUS_RESULT_CACHE_AT", 0.0) or 0.0)
    ttl = float(getattr(module, "_STATUS_RESULT_TTL_S", 25.0) or 25.0)
    if cache and (now - cache_at) < ttl and cache.get("connected") is True:
        out = dict(cache)
        out.update(cache_hit=True, cache_age_s=round(now - cache_at, 1), probe_strategy="cloud_rest_profile_bounded")
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
    }
    if not client_id or not access_token:
        return {**base, "connected": False, "error": "CONFIG_MISSING", "auth_classification": "CONFIG_MISSING", "latency_ms": 0}
    started = time.monotonic()
    try:
        data = module._rest_get(module._DHAN_PROFILE_URL, access_token, client_id, timeout=max(1, min(float(timeout_s), 8.0)))
        latency_ms = int((time.monotonic() - started) * 1000)
        if module._auth_failure_payload(data):
            return {**base, "connected": False, "error": "TOKEN_EXPIRED_OR_INVALID", "auth_classification": _auth_classification(access_token), "latency_ms": latency_ms}
        result = {**base, "connected": True, "error": None, "auth_classification": "AUTH_OK", "latency_ms": latency_ms, "profile_source": "rest"}
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
        if _http_auth_failure(status_code, blob):
            error = "TOKEN_EXPIRED_OR_INVALID"
            classification = _auth_classification(access_token)
        elif status_code == 403 or "forbidden" in blob:
            error = "ACCESS_FORBIDDEN"
        elif status_code:
            error = f"HTTP_{status_code}"
        else:
            error = f"NETWORK_ERROR:{type(exc).__name__}"
        return {**base, "connected": False, "error": error, "auth_classification": classification, "latency_ms": latency_ms}
