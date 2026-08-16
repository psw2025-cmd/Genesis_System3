"""Deterministic Cloud Run Dhan broker status probe.

The normal read-only adapter prefers the SDK and then falls back to REST. That
is useful for interactive/local reads, but a health/status endpoint has a hard
request deadline and cannot safely spend that deadline on two sequential
network strategies. Cloud Run therefore uses one bounded REST profile probe for
connectivity truth. Token reload/rotation remains owned by cloud_runtime_patch.

Safety: read-only profile GET only; no order APIs; no raw token output.
"""
from __future__ import annotations

import time
from typing import Any


def get_cloud_status(module: Any, *, timeout_s: float = 5.0) -> dict[str, Any]:
    """Return bounded Dhan connectivity truth using exactly one REST profile GET."""
    now = time.time()
    cache = getattr(module, "_STATUS_RESULT_CACHE", None)
    cache_at = float(getattr(module, "_STATUS_RESULT_CACHE_AT", 0.0) or 0.0)
    ttl = float(getattr(module, "_STATUS_RESULT_TTL_S", 25.0) or 25.0)
    if cache and (now - cache_at) < ttl and cache.get("connected") is True:
        out = dict(cache)
        out["cache_hit"] = True
        out["cache_age_s"] = round(now - cache_at, 1)
        out["probe_strategy"] = "cloud_rest_profile_bounded"
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
        return {**base, "connected": False, "error": "CONFIG_MISSING", "latency_ms": 0}

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
            return {
                **base,
                "connected": False,
                "error": "TOKEN_EXPIRED_OR_INVALID",
                "latency_ms": latency_ms,
            }
        result = {
            **base,
            "connected": True,
            "error": None,
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
        body = ""
        if response is not None:
            try:
                body = str(getattr(response, "text", "") or "")[:160]
            except Exception:
                body = ""
        blob = f"{status_code or ''} {body} {exc}".lower()
        if status_code in (400, 401) or "dh-906" in blob or "invalid token" in blob:
            error = "TOKEN_EXPIRED_OR_INVALID"
        elif status_code == 403 or "forbidden" in blob:
            error = "ACCESS_FORBIDDEN"
        elif status_code:
            error = f"HTTP_{status_code}"
        else:
            error = f"NETWORK_ERROR:{type(exc).__name__}"
        return {**base, "connected": False, "error": error, "latency_ms": latency_ms}
