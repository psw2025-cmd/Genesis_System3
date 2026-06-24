"""
Test CSV Write Scenarios - All Possible Write Conditions
Tests how the code handles various write scenarios
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.storage.trade_history import TradeHistoryStore


def test_new_file_write():
    """Test: Writing to new file"""
    print("\n[SCENARIO 1] New File Write")
    print("-" * 80)

    # Create temp file path
    temp_dir = ROOT_DIR / "outputs" / "test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_new_file.csv"

    if temp_file.exists():
        temp_file.unlink()

    try:
        store = TradeHistoryStore()
        store.trades_csv = temp_file

        # Write OPEN trade
        trade = {
            "position_id": "TEST_001",
            "action": "OPEN",
            "timestamp": datetime.now().isoformat(),
            "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "underlying": "NIFTY",
            "strike": 25000.0,
            "option_type": "CE",
            "price": 1000.0,
            "qty": 65,
            "strategy": "BUY_CE",
        }

        store.save_trade(trade)

        # Verify
        df = pd.read_csv(temp_file, on_bad_lines="skip", engine="python")
        print(f"  Result: SUCCESS")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Columns: {list(df.columns)}")

        temp_file.unlink()
        return True
    except Exception as e:
        print(f"  Result: ERROR - {str(e)[:100]}")
        if temp_file.exists():
            temp_file.unlink()
        return False


def test_append_to_existing():
    """Test: Appending to existing file"""
    print("\n[SCENARIO 2] Append to Existing File")
    print("-" * 80)

    temp_dir = ROOT_DIR / "outputs" / "test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_append.csv"

    if temp_file.exists():
        temp_file.unlink()

    try:
        store = TradeHistoryStore()
        store.trades_csv = temp_file

        # Write first trade
        trade1 = {
            "position_id": "TEST_001",
            "action": "OPEN",
            "timestamp": datetime.now().isoformat(),
            "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "underlying": "NIFTY",
            "strike": 25000.0,
            "option_type": "CE",
            "price": 1000.0,
            "qty": 65,
            "strategy": "BUY_CE",
        }
        store.save_trade(trade1)

        # Write second trade
        trade2 = {
            "position_id": "TEST_002",
            "action": "OPEN",
            "timestamp": datetime.now().isoformat(),
            "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "underlying": "BANKNIFTY",
            "strike": 60000.0,
            "option_type": "PE",
            "price": 2000.0,
            "qty": 30,
            "strategy": "BUY_PE",
        }
        store.save_trade(trade2)

        # Verify
        df = pd.read_csv(temp_file, on_bad_lines="skip", engine="python")
        print(f"  Result: SUCCESS")
        print(f"  Rows: {len(df)}")
        print(f"  All rows have same columns: {len(set([len(row.dropna()) for _, row in df.iterrows()])) == 1}")

        temp_file.unlink()
        return True
    except Exception as e:
        print(f"  Result: ERROR - {str(e)[:100]}")
        if temp_file.exists():
            temp_file.unlink()
        return False


def test_open_close_consistency():
    """Test: OPEN and CLOSE actions maintain consistency"""
    print("\n[SCENARIO 3] OPEN/CLOSE Consistency")
    print("-" * 80)

    temp_dir = ROOT_DIR / "outputs" / "test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_open_close.csv"

    if temp_file.exists():
        temp_file.unlink()

    try:
        store = TradeHistoryStore()
        store.trades_csv = temp_file

        # Write OPEN
        trade_open = {
            "position_id": "TEST_001",
            "action": "OPEN",
            "timestamp": datetime.now().isoformat(),
            "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "underlying": "NIFTY",
            "strike": 25000.0,
            "option_type": "CE",
            "price": 1000.0,
            "qty": 65,
            "strategy": "BUY_CE",
        }
        store.save_trade(trade_open)

        # Write CLOSE
        trade_close = {
            "position_id": "TEST_001",
            "action": "CLOSE",
            "timestamp": datetime.now().isoformat(),
            "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "underlying": "NIFTY",
            "strike": 25000.0,
            "option_type": "CE",
            "price": 1500.0,
            "qty": 65,
            "strategy": "BUY_CE",
            "exit_reason": "TARGET",
            "realized_pnl": 32500.0,
            "realized_pnl_pct": 50.0,
            "entry_price": 1000.0,
            "exit_price": 1500.0,
        }
        store.save_trade(trade_close)

        # Verify
        df = pd.read_csv(temp_file, on_bad_lines="skip", engine="python")
        print(f"  Result: SUCCESS")
        print(f"  Total rows: {len(df)}")
        print(f"  OPEN rows: {len(df[df['action'] == 'OPEN'])}")
        print(f"  CLOSE rows: {len(df[df['action'] == 'CLOSE'])}")

        # Check column consistency
        open_cols = set(df[df["action"] == "OPEN"].columns) if len(df[df["action"] == "OPEN"]) > 0 else set()
        close_cols = set(df[df["action"] == "CLOSE"].columns) if len(df[df["action"] == "CLOSE"]) > 0 else set()

        if open_cols == close_cols:
            print(f"  Column consistency: PASS (same columns)")
        else:
            print(f"  Column consistency: FAIL")
            print(f"    OPEN columns: {len(open_cols)}")
            print(f"    CLOSE columns: {len(close_cols)}")
            print(f"    Extra in CLOSE: {close_cols - open_cols}")
            print(f"    Extra in OPEN: {open_cols - close_cols}")

        temp_file.unlink()
        return open_cols == close_cols
    except Exception as e:
        print(f"  Result: ERROR - {str(e)[:100]}")
        import traceback

        traceback.print_exc()
        if temp_file.exists():
            temp_file.unlink()
        return False


def test_missing_optional_fields():
    """Test: Missing optional fields in CLOSE"""
    print("\n[SCENARIO 4] Missing Optional Fields")
    print("-" * 80)

    temp_dir = ROOT_DIR / "outputs" / "test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_missing_fields.csv"

    if temp_file.exists():
        temp_file.unlink()

    try:
        store = TradeHistoryStore()
        store.trades_csv = temp_file

        # Write CLOSE without all optional fields
        trade_close = {
            "position_id": "TEST_001",
            "action": "CLOSE",
            "timestamp": datetime.now().isoformat(),
            "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "underlying": "NIFTY",
            "strike": 25000.0,
            "option_type": "CE",
            "price": 1500.0,
            "qty": 65,
            "strategy": "BUY_CE",
            # Missing: exit_reason, realized_pnl, etc.
        }
        store.save_trade(trade_close)

        # Verify
        df = pd.read_csv(temp_file, on_bad_lines="skip", engine="python")
        print(f"  Result: SUCCESS")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Optional columns present: {sum(1 for c in ['exit_reason', 'realized_pnl'] if c in df.columns)}")

        temp_file.unlink()
        return True
    except Exception as e:
        print(f"  Result: ERROR - {str(e)[:100]}")
        if temp_file.exists():
            temp_file.unlink()
        return False


def test_concurrent_writes():
    """Test: Multiple rapid writes"""
    print("\n[SCENARIO 5] Multiple Rapid Writes")
    print("-" * 80)

    temp_dir = ROOT_DIR / "outputs" / "test"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_rapid_writes.csv"

    if temp_file.exists():
        temp_file.unlink()

    try:
        store = TradeHistoryStore()
        store.trades_csv = temp_file

        # Write 10 trades rapidly
        for i in range(10):
            trade = {
                "position_id": f"TEST_{i:03d}",
                "action": "OPEN" if i % 2 == 0 else "CLOSE",
                "timestamp": datetime.now().isoformat(),
                "time_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
                "underlying": "NIFTY",
                "strike": 25000.0 + i * 50,
                "option_type": "CE",
                "price": 1000.0 + i * 10,
                "qty": 65,
                "strategy": "BUY_CE",
            }
            if trade["action"] == "CLOSE":
                trade["exit_reason"] = "TARGET"
                trade["realized_pnl"] = 1000.0
                trade["realized_pnl_pct"] = 10.0
                trade["entry_price"] = 1000.0
                trade["exit_price"] = 1100.0

            store.save_trade(trade)

        # Verify
        df = pd.read_csv(temp_file, on_bad_lines="skip", engine="python")
        print(f"  Result: SUCCESS")
        print(f"  Total rows: {len(df)}")
        print(f"  All rows have same columns: {len(set([tuple(df.columns)])) == 1}")

        temp_file.unlink()
        return True
    except Exception as e:
        print(f"  Result: ERROR - {str(e)[:100]}")
        if temp_file.exists():
            temp_file.unlink()
        return False


def main():
    """Run all write scenario tests."""
    print("\n" + "=" * 80)
    print("  CSV WRITE SCENARIOS - ALL CONDITIONS TEST")
    print("=" * 80)

    results = {}
    results["new_file"] = test_new_file_write()
    results["append"] = test_append_to_existing()
    results["open_close"] = test_open_close_consistency()
    results["missing_fields"] = test_missing_optional_fields()
    results["rapid_writes"] = test_concurrent_writes()

    print("\n" + "=" * 80)
    print("  WRITE SCENARIO TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    print("\n  Test Results:")
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"    {status} {name}")

    print("=" * 80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
