"""
System3 Live Runtime Safety Guard

Provides hard safety limits and logging for live signal generation.
Tracks signal rates, position limits, and logs safety trips.
"""

import sys
from collections import defaultdict, deque
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
LOGS_DIR = PROJECT_ROOT / "storage" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Safety limits (configurable)
MAX_SIGNALS_PER_MINUTE_PER_UNDERLYING = 10
MAX_TOTAL_OPEN_POSITIONS = 50
MAX_PENDING_SIGNALS = 100

# Global state for tracking
# Last 60 seconds
_signal_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=60))
_total_open_positions = 0
_pending_signals = 0
_safety_trip_log: List[str] = []


def reset_counters():
    """Reset all counters (call at start of each day)."""
    global _signal_counters
    global _total_open_positions
    global _pending_signals
    global _safety_trip_log
    _signal_counters.clear()
    _total_open_positions = 0
    _pending_signals = 0
    _safety_trip_log = []


def check_signal_rate_limit(underlying: str) -> Tuple[bool, Optional[str]]:
    """
    Check if signal rate limit is exceeded for an underlying.

    Args:
        underlying: Underlying symbol

    Returns:
        Tuple of (is_safe, error_message)
    """
    now = datetime.now()
    current_minute = now.replace(second=0, microsecond=0)

    # Count signals in last minute
    signals_in_minute = sum(1 for timestamp in _signal_counters[underlying] if timestamp >= current_minute)

    if signals_in_minute >= MAX_SIGNALS_PER_MINUTE_PER_UNDERLYING:
        error_msg = (
            f"Signal rate limit exceeded for {underlying}: "
            f"{signals_in_minute} signals in last minute "
            f"(limit: {MAX_SIGNALS_PER_MINUTE_PER_UNDERLYING})"
        )
        return False, error_msg

    # Record this signal
    _signal_counters[underlying].append(now)
    return True, None


def check_position_limits(open_positions: int, pending_signals: int) -> Tuple[bool, Optional[str]]:
    """
    Check if position limits are exceeded.

    Args:
        open_positions: Current number of open positions
        pending_signals: Current number of pending signals

    Returns:
        Tuple of (is_safe, error_message)
    """
    global _total_open_positions, _pending_signals

    _total_open_positions = open_positions
    _pending_signals = pending_signals

    if open_positions >= MAX_TOTAL_OPEN_POSITIONS:
        error_msg = (
            f"Total open positions limit exceeded: " f"{open_positions} positions (limit: {MAX_TOTAL_OPEN_POSITIONS})"
        )
        return False, error_msg

    if pending_signals >= MAX_PENDING_SIGNALS:
        error_msg = f"Pending signals limit exceeded: " f"{pending_signals} signals (limit: {MAX_PENDING_SIGNALS})"
        return False, error_msg

    return True, None


def log_safety_trip(
    reason: str,
    underlying: Optional[str] = None,
    signal_count: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a safety trip event.

    Args:
        reason: Reason for safety trip
        underlying: Underlying symbol (if applicable)
        signal_count: Number of signals (if applicable)
        details: Additional details
    """
    today = date.today().strftime("%Y%m%d")
    log_file = LOGS_DIR / f"system3_live_safety_trips_{today}.log"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"[{timestamp}] SAFETY_TRIP: {reason}"
    if underlying:
        log_entry += f" | Underlying: {underlying}"
    if signal_count is not None:
        log_entry += f" | Signal Count: {signal_count}"
    if details:
        log_entry += f" | Details: {details}"
    log_entry += "\n"

    _safety_trip_log.append(log_entry)

    try:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        # Don't fail if logging fails
        pass


def check_signal_safety(
    underlying: str, signal_count: int, open_positions: int = 0, pending_signals: int = 0
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive safety check for signal generation.

    Args:
        underlying: Underlying symbol
        signal_count: Number of signals being generated
        open_positions: Current open positions
        pending_signals: Current pending signals

    Returns:
        Tuple of (is_safe, error_message)
    """
    # Check signal rate limit
    is_safe, error = check_signal_rate_limit(underlying)
    if not is_safe:
        log_safety_trip("Signal rate limit exceeded", underlying=underlying, signal_count=signal_count)
        return False, error

    # Check position limits
    is_safe, error = check_position_limits(open_positions, pending_signals)
    if not is_safe:
        log_safety_trip(
            "Position limit exceeded",
            underlying=underlying,
            signal_count=signal_count,
            details={"open_positions": open_positions, "pending_signals": pending_signals},
        )
        return False, error

    return True, None


def get_safety_status() -> Dict[str, Any]:
    """
    Get current safety status.

    Returns:
        Dict with safety status information
    """
    now = datetime.now()
    current_minute = now.replace(second=0, microsecond=0)

    signals_per_underlying = {}
    for underlying, timestamps in _signal_counters.items():
        signals_in_minute = sum(1 for timestamp in timestamps if timestamp >= current_minute)
        signals_per_underlying[underlying] = signals_in_minute

    return {
        "signals_per_underlying_last_minute": signals_per_underlying,
        "total_open_positions": _total_open_positions,
        "pending_signals": _pending_signals,
        "safety_trips_today": len(_safety_trip_log),
        "limits": {
            "max_signals_per_minute_per_underlying": (MAX_SIGNALS_PER_MINUTE_PER_UNDERLYING),
            "max_total_open_positions": MAX_TOTAL_OPEN_POSITIONS,
            "max_pending_signals": MAX_PENDING_SIGNALS,
        },
    }


if __name__ == "__main__":
    # Test safety guard
    reset_counters()

    # Test signal rate limit
    for i in range(12):
        is_safe, error = check_signal_rate_limit("NIFTY")
        if not is_safe:
            print(f"Safety trip at signal {i+1}: {error}")
            break

    # Test position limits
    is_safe, error = check_position_limits(51, 0)
    if not is_safe:
        print(f"Position limit trip: {error}")

    # Get status
    status = get_safety_status()
    print(f"Safety status: {status}")
