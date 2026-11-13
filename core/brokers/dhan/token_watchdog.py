"""Dhan proactive token watchdog.

Periodically monitors access token expiry and triggers pre-emptive canonical rotation
before expiry (default: 3 hours before expiry) so the system never halts or blocks.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any


def _get_token_hours() -> float | None:
    try:
        from core.utils.env_loader import get_dhan_token
        _, _, _, hours, _, _ = get_dhan_token(force_refresh=False)
        return hours
    except Exception:
        return None


def watchdog_cycle(proactive_hours: float | None = None) -> dict[str, Any]:
    """Execute one watchdog check and proactively rotate if near expiry or expired."""
    threshold = proactive_hours if proactive_hours is not None else float(
        os.getenv("DHAN_PROACTIVE_RENEWAL_HOURS", "3.0")
    )
    hours = _get_token_hours()
    result: dict[str, Any] = {
        "hours_remaining_before": hours,
        "threshold_hours": threshold,
        "action": "SKIPPED_HEALTHY",
        "rotated": False,
        "live_trading_enabled": False,
        "raw_token_exposed": False,
    }
    # If token is near expiry (<= threshold), expired (<= 0), or missing (None):
    if hours is None or hours <= threshold:
        try:
            from scripts.gcp_dhan_token_rotation_job import rotate_token
            rot = rotate_token(force=True)
            result["rotated"] = bool(rot.get("success"))
            result["action"] = "ROTATED_AND_VERIFIED" if rot.get("success") else "ROTATION_FAILED"
            result["status"] = rot.get("status")
            hours_after = _get_token_hours()
            result["hours_remaining_after"] = hours_after
        except Exception as exc:
            result["action"] = "ROTATION_EXCEPTION"
            result["error_type"] = type(exc).__name__
    return result


def run_watchdog_loop(interval_seconds: float = 900.0, stop_event: threading.Event | None = None) -> None:
    """Run persistent proactive renewal watchdog loop safely."""
    while stop_event is None or not stop_event.is_set():
        try:
            watchdog_cycle()
        except Exception:
            pass
        if stop_event:
            stop_event.wait(interval_seconds)
        else:
            time.sleep(interval_seconds)


def start_watchdog_thread(interval_seconds: float = 900.0) -> tuple[threading.Thread, threading.Event]:
    stop_event = threading.Event()
    thread = threading.Thread(
        target=run_watchdog_loop,
        args=(interval_seconds, stop_event),
        name="DhanTokenWatchdogThread",
        daemon=True,
    )
    thread.start()
    return thread, stop_event
