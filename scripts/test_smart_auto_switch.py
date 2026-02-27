"""
Test Smart Auto-Switch System
Quick test to verify auto-switching works
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.market_hours import is_market_open, get_market_status

IST = pytz.timezone("Asia/Kolkata")


def test_market_detection():
    """Test market detection."""
    print("=" * 80)
    print("  SMART AUTO-SWITCH - MARKET DETECTION TEST")
    print("=" * 80)
    print()

    now = datetime.now(IST)
    is_open, reason = is_market_open(now)
    status = get_market_status(now)

    print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()
    print(f"Market Status: {'OPEN' if is_open else 'CLOSED'}")
    print(f"Reason: {reason}")
    print()

    if is_open:
        print("✅ Market is OPEN")
        print("   → System will use LIVE data")
        print("   → Real API calls will be made")
    else:
        print("⚠️  Market is CLOSED")
        print("   → System will use VIRTUAL data")
        print("   → Simulation mode will be used")
        if status.get("next_open"):
            print(f"   → Next market open: {status['next_open']}")

    print()
    print("=" * 80)
    print()

    return is_open


if __name__ == "__main__":
    test_market_detection()
