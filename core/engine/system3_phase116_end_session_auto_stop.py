"""
System3 Phase 116 - End-of-Session Auto Stop

Automatically set kill switch at market close.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import config
try:
    from config.live_trade_config import MARKET_CLOSE_TIME
except ImportError:
    MARKET_CLOSE_TIME = "15:30"

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

KILL_SWITCH_JSON = STORAGE_LIVE / "kill_switch.json"


def run_phase116(market_close_time_str: str = None, **kwargs) -> dict:
    """
    Check if market is closed and set kill switch if needed.

    Args:
        market_close_time_str: Market close time in HH:MM format (default from config)

    Returns:
        dict: {
            "phase": 116,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        close_time = market_close_time_str or MARKET_CLOSE_TIME

        # Parse close time
        close_hour, close_minute = map(int, close_time.split(":"))

        # Get current time
        now = datetime.now()
        current_time = now.time()
        close_time_obj = datetime.strptime(close_time, "%H:%M").time()

        # Check if market is closed
        if current_time >= close_time_obj:
            # Set kill switch
            kill_data = {
                "kill": True,
                "timestamp": now.isoformat(),
                "reason": f"Market closed at {close_time}",
            }

            with KILL_SWITCH_JSON.open("w", encoding="utf-8") as f:
                json.dump(kill_data, f, indent=2)

            status = "OK"
            details = f"Market closed - kill switch activated"
        else:
            status = "OK"
            details = f"Market still open (closes at {close_time})"

        return {
            "phase": 116,
            "status": status,
            "details": details,
            "outputs": {
                "kill_switch_path": str(KILL_SWITCH_JSON),
                "market_closed": current_time >= close_time_obj,
                "current_time": current_time.strftime("%H:%M:%S"),
                "close_time": close_time,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 116,
            "status": "ERROR",
            "details": f"Phase 116 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="System3 Phase 116 - End-of-Session Auto Stop")
    parser.add_argument("--market-close-time", type=str, default=None, help="Market close time (HH:MM)")
    args = parser.parse_args()

    print("=" * 70)
    print("SYSTEM3 PHASE 116 - END-OF-SESSION AUTO STOP")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase116(market_close_time_str=args.market_close_time)

    print(f"Phase116: {result['details']}")
    print(f"Current time: {result['outputs']['current_time']}")
    print(f"Close time: {result['outputs']['close_time']}")
    print(f"Market closed: {result['outputs']['market_closed']}")

    if result["outputs"]["market_closed"]:
        print(f"\n[INFO] Kill switch activated: {result['outputs']['kill_switch_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
