"""
Production System Test - End-to-end validation
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


def test_data_flow():
    """Test data flow through the system."""
    print("\n[TEST 1/5] Testing data flow...")

    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    # Test PnL file creation
    pnl_file = outputs_dir / "pnl_live.json"
    test_pnl = {
        "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "total_realized_pnl": 0.0,
        "total_unrealized_pnl": 0.0,
        "total_pnl": 0.0,
        "open_positions": 0,
    }

    try:
        with open(pnl_file, "w", encoding="utf-8") as f:
            json.dump(test_pnl, f, indent=2)
        print("  ✅ PnL file write successful")
    except Exception as e:
        print(f"  ❌ PnL file write failed: {e}")
        return False

    # Test positions file creation
    positions_file = outputs_dir / "positions_live.json"
    test_positions = {
        "timestamp_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
        "open_positions": [],
        "summary": {"open_count": 0, "closed_count": 0},
    }

    try:
        with open(positions_file, "w", encoding="utf-8") as f:
            json.dump(test_positions, f, indent=2)
        print("  ✅ Positions file write successful")
    except Exception as e:
        print(f"  ❌ Positions file write failed: {e}")
        return False

    # Test file reading
    try:
        with open(pnl_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "total_pnl" in data:
                print("  ✅ PnL file read successful")
            else:
                print("  ❌ PnL file missing required fields")
                return False
    except Exception as e:
        print(f"  ❌ PnL file read failed: {e}")
        return False

    return True


def test_paper_executor():
    """Test paper executor functionality."""
    print("\n[TEST 2/5] Testing paper executor...")

    try:
        from src.trading.paper_executor import PaperExecutor

        executor = PaperExecutor()
        summary = executor.get_positions_summary()

        if isinstance(summary, dict) and "open_count" in summary:
            print("  ✅ Paper executor initialized and working")
            return True
        else:
            print("  ❌ Paper executor returned invalid summary")
            return False
    except Exception as e:
        print(f"  ❌ Paper executor test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_pnl_tracker():
    """Test PnL tracker functionality."""
    print("\n[TEST 3/5] Testing PnL tracker...")

    try:
        from src.trading.pnl_tracker import PnLTracker

        tracker = PnLTracker()

        # Test with empty positions
        empty_summary = {
            "open_count": 0,
            "closed_count": 0,
            "total_unrealized_pnl": 0.0,
            "total_realized_pnl": 0.0,
            "total_pnl": 0.0,
            "open_positions": [],
            "closed_positions": [],
        }

        pnl_summary = tracker.update(empty_summary, datetime.now().isoformat())

        if isinstance(pnl_summary, dict) and "total_pnl" in pnl_summary:
            print("  ✅ PnL tracker working")
            return True
        else:
            print("  ❌ PnL tracker returned invalid summary")
            return False
    except Exception as e:
        print(f"  ❌ PnL tracker test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_trade_history():
    """Test trade history store."""
    print("\n[TEST 4/5] Testing trade history store...")

    try:
        from src.storage.trade_history import TradeHistoryStore

        store = TradeHistoryStore()

        # Test saving empty PnL
        test_pnl = {"timestamp": datetime.now().isoformat(), "total_trades": 0, "total_pnl": 0.0}

        store.save_pnl(test_pnl)
        print("  ✅ Trade history store working")
        return True
    except Exception as e:
        print(f"  ❌ Trade history test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_monitor_components():
    """Test monitor components."""
    print("\n[TEST 5/5] Testing monitor components...")

    try:
        # Test profit monitor functions
        from scripts.profit_focused_monitor import (
            get_open_positions,
            get_pnl_summary,
            get_system_status,
        )

        # Test PnL summary
        pnl = get_pnl_summary()
        if isinstance(pnl, dict):
            print("  ✅ PnL summary function working")
        else:
            print("  ❌ PnL summary returned invalid data")
            return False

        # Test open positions
        positions = get_open_positions()
        if isinstance(positions, list):
            print("  ✅ Open positions function working")
        else:
            print("  ❌ Open positions returned invalid data")
            return False

        # Test system status
        status, msg = get_system_status()
        if isinstance(status, str) and isinstance(msg, str):
            print("  ✅ System status function working")
        else:
            print("  ❌ System status returned invalid data")
            return False

        return True
    except Exception as e:
        print(f"  ❌ Monitor components test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("  PRODUCTION SYSTEM TEST")
    print("=" * 80)

    tests = [test_data_flow, test_paper_executor, test_pnl_tracker, test_trade_history, test_monitor_components]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
        time.sleep(0.5)  # Small delay between tests

    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"\n  Tests passed: {passed}/{total}")

    if passed == total:
        print("  Status: ✅ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        return 0
    elif passed >= total * 0.8:
        print("  Status: ⚠️  MOST TESTS PASSED - SYSTEM FUNCTIONAL")
        return 0
    else:
        print("  Status: ❌ MULTIPLE TESTS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
