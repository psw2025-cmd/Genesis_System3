"""SYS3-BLK-001: Broker connection stability tracker.

Distinguishes real outages from transient blips (latency spike, rate limit,
single failed probe). A disconnect is only "confirmed" after 3 consecutive
failures; within a 120s grace window after the last good probe the state is
DEGRADED, not DOWN. Shared singleton — sampled by every status caller.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime, timezone

FAILURE_THRESHOLD = 3
GRACE_WINDOW_S = 120.0


class ConnectionStabilityTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._last_connected_epoch = 0.0
        self._last_disconnected_epoch = 0.0
        self._last_error = None
        self._flap_count = 0
        self._last_raw_state = None
        self._samples = deque(maxlen=200)

    def record(self, connected: bool, error: str | None = None) -> dict:
        with self._lock:
            now = time.time()
            connected = bool(connected)
            if self._last_raw_state is not None and connected != self._last_raw_state:
                self._flap_count += 1
            self._last_raw_state = connected
            self._samples.append((now, connected))
            if connected:
                self._consecutive_failures = 0
                self._consecutive_successes += 1
                self._last_connected_epoch = now
                self._last_error = None
            else:
                self._consecutive_successes = 0
                self._consecutive_failures += 1
                self._last_disconnected_epoch = now
                if error:
                    self._last_error = str(error)[:200]
            return self._snapshot_locked()

    def snapshot(self) -> dict:
        with self._lock:
            return self._snapshot_locked()

    def _snapshot_locked(self) -> dict:
        now = time.time()
        since_good = (now - self._last_connected_epoch) if self._last_connected_epoch else None
        raw = bool(self._last_raw_state)
        confirmed_down = self._consecutive_failures >= FAILURE_THRESHOLD
        grace_active = (
            not raw
            and not confirmed_down
            and since_good is not None
            and since_good <= GRACE_WINDOW_S
        )
        if raw:
            state = "CONNECTED"
        elif grace_active:
            state = "DEGRADED"
        elif confirmed_down:
            state = "DOWN_CONFIRMED"
        else:
            state = "DOWN_UNCONFIRMED"
        window = [s for s in self._samples if now - s[0] <= 3600]
        uptime_pct = (
            round(sum(1 for _, ok in window if ok) / len(window) * 100, 1) if window else None
        )
        return {
            "state": state,
            "raw_connected": raw,
            "stable_connected": raw or grace_active,
            "consecutive_failures": self._consecutive_failures,
            "consecutive_successes": self._consecutive_successes,
            "failure_threshold": FAILURE_THRESHOLD,
            "grace_window_s": GRACE_WINDOW_S,
            "grace_active": grace_active,
            "seconds_since_last_good": round(since_good, 1) if since_good is not None else None,
            "last_connected_at_utc": (
                datetime.fromtimestamp(self._last_connected_epoch, tz=timezone.utc).isoformat()
                if self._last_connected_epoch
                else None
            ),
            "last_error": self._last_error,
            "flap_count": self._flap_count,
            "uptime_pct_1h": uptime_pct,
            "samples_1h": len(window),
        }


_TRACKER = ConnectionStabilityTracker()


def get_connection_tracker() -> ConnectionStabilityTracker:
    return _TRACKER
