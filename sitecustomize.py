"""
Genesis System3 cloud startup compatibility hooks.

Safety:
- Analyzer/read-only only.
- No broker order placement, modification, cancellation, or live trading.
- No secrets are read or printed.
"""

from __future__ import annotations

import asyncio
import builtins
import os


async def _system3_background_data_refresh_fallback() -> None:
    """Non-fatal no-op background refresh loop for cloud startup stability."""
    interval_s = int(os.getenv("BACKGROUND_DATA_REFRESH_INTERVAL_S", "300") or "300")
    print("[startup-compat] background_data_refresh fallback active (no-op)")
    while True:
        await asyncio.sleep(max(60, interval_s))


def _install_status_alias() -> None:
    """Expose the legacy status helper expected by the broker router."""
    try:
        from core.brokers.dhan import token_manager as _tm
    except Exception as exc:
        print(f"[startup-compat] status alias skipped: {exc}")
        return

    if hasattr(_tm, "get_token_status"):
        return

    def get_token_status() -> dict:
        try:
            status = _tm.verify_token()
            return {
                "valid": bool(status.get("valid", False)),
                "reason": status.get("reason"),
                "expires_at": status.get("expires_at"),
                "hours_remaining": status.get("hours_remaining"),
                "source": "verify_token_alias",
            }
        except Exception as exc:
            return {"valid": False, "reason": str(exc)[:120], "source": "verify_token_alias_error"}

    _tm.get_token_status = get_token_status
    print("[startup-compat] installed broker status alias")


if not hasattr(builtins, "background_data_refresh"):
    builtins.background_data_refresh = _system3_background_data_refresh_fallback

_install_status_alias()
