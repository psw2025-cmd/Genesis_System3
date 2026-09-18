"""Measured telemetry for the existing market-top loop; no worker or broker I/O."""
import time
from datetime import datetime, timezone


class ScannerTelemetry:
    def __init__(self):
        self.cycles = 0
        self.errors = 0
        self.last_monotonic = None
        self.last_observed_at = None
        self.duration = None
        self.rows = 0
        self.error = None

    def observe(self, duration, rows=0, error=None):
        self.cycles += 1
        self.errors += int(error is not None)
        self.last_monotonic = time.monotonic()
        self.last_observed_at = datetime.now(timezone.utc).isoformat()
        self.duration = max(0.0, float(duration))
        self.rows = max(0, int(rows))
        self.error = type(error).__name__ if error is not None else None

    def snapshot(self, market_open, max_age=90.0):
        age = None if self.last_monotonic is None else max(0.0, time.monotonic() - self.last_monotonic)
        if age is None:
            status = 'STARTING'
        elif age > max_age:
            status = 'STALLED'
        elif self.error:
            status = 'ERROR'
        elif not market_open:
            status = 'MARKET_CLOSED'
        else:
            status = 'ACTIVE' if self.rows else 'WAITING_FOR_DATA'
        return {
            'status': status, 'cycle_count': self.cycles, 'error_count': self.errors,
            'observed_at': self.last_observed_at, 'heartbeat_age_seconds': age,
            'rows': self.rows, 'error_type': self.error,
            'performance_sla': {
                'scope': 'scanner_cache_refresh_only',
                'cycle_duration_sec': self.duration,
                'limit_seconds': 60.0,
                'sla_pass': None if age is None or age > max_age else self.error is None and self.duration <= 60.0,
            },
        }
