"""
BLK-001 FIX: Broker Alert Deduplication Service
Prevents false BROKER_DISCONNECTED alert loop with state tracking and debounce.

Issue: BROKER_DISCONNECTED alert was firing every sync cycle even when broker
was actually connected, causing user confusion.

Fix: 
1. Track last alert state (was it already active?)
2. Only upsert if state actually changes (dedupe)
3. Increase consecutive failure threshold from 1 to 3
4. Add timestamp tracking for alert lifecycle
5. Clear false alerts immediately when broker status changes to connected
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import pytz

IST = pytz.timezone("Asia/Kolkata")


def _emit_log(logger: Any, level: str, message: str) -> None:
    """Support stdlib loggers and simple callables (e.g. print)."""
    if logger is None:
        return
    sink = getattr(logger, level, None)
    if callable(sink):
        sink(message)
        return
    if callable(logger):
        logger(message)


class BrokerAlertDeduplicator:
    """Manages broker connectivity alert state to prevent false alert loops."""
    
    def __init__(self):
        # Track last alert state to prevent redundant upserts
        self.last_alert_state = None  # None | "ACTIVE" | "RESOLVED"
        self.last_alert_timestamp = None
        self.consecutive_failures = 0
        self.failure_threshold = 3  # Require 3 consecutive disconnects before alert
        self.last_connected_state = True  # Assume connected initially
        self.dedupe_window_seconds = 10  # Don't re-alert within 10s
        
    def should_alert_on_disconnect(self, broker_connected: bool) -> tuple[bool, str]:
        """
        Determine if we should emit a BROKER_DISCONNECTED alert.
        
        Returns (should_alert, reason)
        """
        now = datetime.now(IST)
        
        # Immediate resolution if broker came back online
        if broker_connected and not self.last_connected_state:
            self.last_connected_state = True
            self.consecutive_failures = 0
            return False, "BROKER_RECOVERED"
        
        # Track connection state
        self.last_connected_state = broker_connected
        
        # Count consecutive failures
        if not broker_connected:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0
            return False, "BROKER_CONNECTED"
        
        # Only alert after threshold breached
        if self.consecutive_failures < self.failure_threshold:
            return False, f"COUNTING_FAILURES ({self.consecutive_failures}/{self.failure_threshold})"
        
        # Check dedupe window — don't re-alert within 10s
        if self.last_alert_state == "ACTIVE" and self.last_alert_timestamp:
            time_since_alert = (now - self.last_alert_timestamp).total_seconds()
            if time_since_alert < self.dedupe_window_seconds:
                return False, f"DEDUPE_WINDOW ({time_since_alert:.1f}s < {self.dedupe_window_seconds}s)"
        
        # State transition: from RESOLVED/None to ACTIVE
        if self.last_alert_state != "ACTIVE":
            self.last_alert_state = "ACTIVE"
            self.last_alert_timestamp = now
            return True, "ALERT_ACTIVE"
        
        # Already active, don't re-upsert
        return False, "ALREADY_ACTIVE"
    
    def should_resolve_alert(self, broker_connected: bool) -> tuple[bool, str]:
        """
        Determine if we should resolve (clear) a BROKER_DISCONNECTED alert.
        
        Returns (should_resolve, reason)
        """
        now = datetime.now(IST)
        
        if not broker_connected:
            return False, "BROKER_STILL_DISCONNECTED"
        
        # Only resolve if alert was actually active
        if self.last_alert_state != "ACTIVE":
            return False, "ALERT_NOT_ACTIVE"
        
        self.last_alert_state = "RESOLVED"
        self.last_alert_timestamp = now
        self.consecutive_failures = 0
        return True, "ALERT_RESOLVED"
    
    def get_state(self) -> Dict:
        """Return current deduplicator state for debugging/logging."""
        return {
            "last_alert_state": self.last_alert_state,
            "last_alert_timestamp": self.last_alert_timestamp.isoformat() if self.last_alert_timestamp else None,
            "consecutive_failures": self.consecutive_failures,
            "failure_threshold": self.failure_threshold,
            "last_connected_state": self.last_connected_state,
        }


# Singleton instance
_deduplicator_instance = BrokerAlertDeduplicator()


def get_broker_alert_deduplicator() -> BrokerAlertDeduplicator:
    """Get singleton deduplicator instance."""
    return _deduplicator_instance


def process_broker_alert(
    broker_connected: bool,
    state_store,
    logger=None
) -> Dict[str, Any]:
    """
    Process broker connectivity and emit/resolve alerts appropriately.
    
    Args:
        broker_connected: Current broker connection status
        state_store: State store to upsert/resolve alerts
        logger: Optional logger
        
    Returns:
        Action taken: {"action": "UPSERT|RESOLVE|NONE", "reason": "...", "state": {...}}
    """
    dedup = get_broker_alert_deduplicator()
    
    # Check if we should resolve
    should_resolve, resolve_reason = dedup.should_resolve_alert(broker_connected)
    if should_resolve:
        state_store.resolve_alert("BROKER_DISCONNECTED")
        _emit_log(logger, "info", f"Resolved BROKER_DISCONNECTED: {resolve_reason}")
        return {
            "action": "RESOLVE",
            "reason": resolve_reason,
            "state": dedup.get_state()
        }
    
    # Check if we should alert
    should_alert, alert_reason = dedup.should_alert_on_disconnect(broker_connected)
    if should_alert:
        state_store.upsert_alert(
            "WARN",
            "BROKER_DISCONNECTED",
            f"Broker connection lost ({dedup.consecutive_failures} consecutive failures)"
        )
        _emit_log(logger, "warning", f"Upserted BROKER_DISCONNECTED: {alert_reason}")
        return {
            "action": "UPSERT",
            "reason": alert_reason,
            "state": dedup.get_state()
        }
    
    # No action needed
    if alert_reason not in ["ALREADY_ACTIVE", "COUNTING_FAILURES"]:
        _emit_log(logger, "debug", f"No alert action: {alert_reason}")
    
    return {
        "action": "NONE",
        "reason": alert_reason,
        "state": dedup.get_state()
    }


if __name__ == "__main__":
    # Test the deduplicator
    print("Testing BrokerAlertDeduplicator...")
    dedup = BrokerAlertDeduplicator()
    
    # Simulate 3 consecutive disconnects then reconnect
    test_states = [
        (False, "1st disconnect"),
        (False, "2nd disconnect"),
        (False, "3rd disconnect — should alert now"),
        (False, "4th disconnect — dedupe"),
        (True, "Reconnected — should resolve"),
        (True, "Still connected"),
    ]
    
    for connected, label in test_states:
        should_alert, alert_reason = dedup.should_alert_on_disconnect(connected)
        should_resolve, resolve_reason = dedup.should_resolve_alert(connected)
        
        action = "ALERT" if should_alert else ("RESOLVE" if should_resolve else "NONE")
        reason = alert_reason if should_alert else resolve_reason
        print(f"{label:40} → {action:10} ({reason})")
    
    print("\nFinal state:", json.dumps(dedup.get_state(), indent=2, default=str))
