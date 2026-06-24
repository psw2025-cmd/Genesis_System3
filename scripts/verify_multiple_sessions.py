"""
Verify Multiple Sessions - Test system across multiple sessions
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.multi_session_handler import MultiSessionHandler


def test_session_1():
    """Test first session."""
    print("\n" + "=" * 80)
    print("  SESSION 1 TEST")
    print("=" * 80 + "\n")

    handler = MultiSessionHandler()

    # Update state
    state = handler.update_multi_session_state()

    print(f"Session ID: {handler.get_current_session_id()}")
    print(f"Total Days: {state.get('total_days', 0)}")
    print(f"Total Trades: {state.get('total_trades_all_sessions', 0)}")
    print(f"Total PnL: Rs {state.get('total_pnl_all_sessions', 0):.2f}")

    return True


def test_session_2():
    """Test second session (simulated)."""
    print("\n" + "=" * 80)
    print("  SESSION 2 TEST (Simulated)")
    print("=" * 80 + "\n")

    handler = MultiSessionHandler()

    # Simulate new session by updating state
    state = handler.update_multi_session_state()

    print(f"Session ID: {handler.get_current_session_id()}")
    print(f"Total Days: {state.get('total_days', 0)}")
    print(f"Total Trades: {state.get('total_trades_all_sessions', 0)}")
    print(f"Total PnL: Rs {state.get('total_pnl_all_sessions', 0):.2f}")

    # Get summary
    summary = handler.get_multi_session_summary()
    print(f"\nMulti-Session Summary:")
    print(f"  Sessions: {list(summary['sessions'].keys())}")

    return True


def main():
    """Test multiple sessions."""
    print("\n" + "=" * 80)
    print("  MULTI-SESSION VERIFICATION")
    print("=" * 80)

    # Test session 1
    test_session_1()

    # Wait a bit
    print("\nWaiting 5 seconds...")
    time.sleep(5)

    # Test session 2
    test_session_2()

    # Final summary
    handler = MultiSessionHandler()
    summary = handler.get_multi_session_summary()

    print("\n" + "=" * 80)
    print("  FINAL MULTI-SESSION SUMMARY")
    print("=" * 80)
    print(f"  Total Days: {summary['total_days']}")
    print(f"  Total Trades (All): {summary['total_trades']}")
    print(f"  Total PnL (All): Rs {summary['total_pnl']:.2f}")
    print(f"  Sessions: {len(summary['sessions'])}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
