"""Install Cloud Run-safe Dhan read-only wrappers before the FastAPI app loads.

The wrappers retry a read-only broker call once after reloading the newest
Secret Manager token. They never place, modify, cancel, or route orders.
"""
from __future__ import annotations

import threading
from typing import Any, Callable

from core.brokers.dhan.cloud_token_provider import (
    force_reload,
    get_access_token,
    token_metadata,
)

_INSTALL_LOCK = threading.Lock()
_INSTALLED = False


def _text_blob(value: Any) -> str:
    try:
        if isinstance(value, dict):
            parts = []
            for key, item in value.items():
                if key.lower() in {"access_token", "token", "authorization"}:
                    continue
                parts.append(f"{key}={_text_blob(item)}")
            return " ".join(parts)
        if isinstance(value, (list, tuple)):
            return " ".join(_text_blob(v) for v in value)
        return str(value or "")
    except Exception:
        return ""


def _auth_failed(result: Any) -> bool:
    blob = _text_blob(result).lower()
    return any(
        marker in blob
        for marker in (
            "token_expired_or_invalid",
            "invalid token",
            "dh-906",
            "unauthorized",
            "http_401",
            "status_code=401",
        )
    )


def _clear_status_cache(module: Any) -> None:
    try:
        module._STATUS_RESULT_CACHE = None
        module._STATUS_RESULT_CACHE_AT = 0.0
    except Exception:
        pass


def _wrap_read(module: Any, name: str, original: Callable[..., Any]) -> Callable[..., Any]:
    def wrapped(*args, **kwargs):
        get_access_token(reason=f"pre_{name}")
        result = original(*args, **kwargs)
        reload_attempted = False
        reload_success = False
        if _auth_failed(result):
            reload_attempted = True
            reload_success = force_reload(reason=f"{name}_auth_failure")
            _clear_status_cache(module)
            if reload_success:
                result = original(*args, **kwargs)
        if isinstance(result, dict):
            result = dict(result)
            result["token_reload"] = {
                "attempted": reload_attempted,
                "success": reload_success,
                "raw_token_exposed": False,
            }
            if name == "get_status":
                result["token_proof"] = token_metadata()
                result["cloud_runtime_patch"] = True
        return result

    wrapped.__name__ = getattr(original, "__name__", name)
    wrapped.__doc__ = getattr(original, "__doc__", None)
    return wrapped


def install() -> dict[str, Any]:
    """Patch the read-only adapter once and return non-secret install proof."""
    global _INSTALLED
    with _INSTALL_LOCK:
        if _INSTALLED:
            return {
                "installed": True,
                "already_installed": True,
                "live_trading_enabled": False,
            }

        get_access_token(force_refresh=True, reason="cloud_runtime_startup")

        from core.brokers.dhan import dhan_readonly as module

        patched = []
        for name in (
            "get_status",
            "get_profile",
            "get_funds",
            "get_holdings",
            "get_positions",
            "get_orders_readonly",
        ):
            original = getattr(module, name, None)
            if callable(original) and not getattr(original, "_system3_cloud_wrapped", False):
                wrapped = _wrap_read(module, name, original)
                setattr(wrapped, "_system3_cloud_wrapped", True)
                setattr(module, name, wrapped)
                patched.append(name)

        _INSTALLED = True
        return {
            "installed": True,
            "patched": patched,
            "token_source": token_metadata().get("source"),
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "raw_token_exposed": False,
        }
