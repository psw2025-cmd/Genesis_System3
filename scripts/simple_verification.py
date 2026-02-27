"""
Simple Verification Script - Produces visible output and proof
"""

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Fix Unicode
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def test_imports():
    """Test critical imports."""
    print("  Testing imports...")
    try:
        from src.trading.paper_executor import PaperExecutor
        from src.trading.pnl_tracker import PnLTracker
        from src.storage.trade_history import TradeHistoryStore

        print("    [OK] All imports successful")
        return True
    except Exception as e:
        print(f"    [FAIL] Import error: {e}")
        return False


def test_components():
    """Test component initialization."""
    print("  Testing components...")
    try:
        from src.trading.paper_executor import PaperExecutor

        executor = PaperExecutor()
        summary = executor.get_positions_summary()
        print("    [OK] Paper executor working")

        from src.trading.pnl_tracker import PnLTracker

        tracker = PnLTracker()
        print("    [OK] PnL tracker working")

        from src.storage.trade_history import TradeHistoryStore

        store = TradeHistoryStore()
        print("    [OK] Trade history working")

        return True
    except Exception as e:
        print(f"    [FAIL] Component error: {e}")
        return False


def test_data_files():
    """Test data file operations."""
    print("  Testing data files...")
    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    test_data = {"test": True, "timestamp": datetime.now().isoformat()}
    test_file = outputs_dir / "verification_test.json"

    try:
        # Write
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        print("    [OK] Write operation successful")

        # Read
        with open(test_file, "r", encoding="utf-8") as f:
            read_data = json.load(f)
        print("    [OK] Read operation successful")

        # Cleanup
        test_file.unlink()
        print("    [OK] Data file operations verified")
        return True
    except Exception as e:
        print(f"    [FAIL] Data file error: {e}")
        return False


def main():
    """Main verification."""
    print("=" * 80)
    print("  SIMPLE VERIFICATION - ULTRA-MICRO LEVEL")
    print("=" * 80)
    print()

    results = {"timestamp": datetime.now().isoformat(), "tests": {}}

    # Test 1: Imports
    print("[TEST 1] Import System")
    results["tests"]["imports"] = test_imports()
    print()

    # Test 2: Components
    print("[TEST 2] Component Initialization")
    results["tests"]["components"] = test_components()
    print()

    # Test 3: Data Files
    print("[TEST 3] Data File Operations")
    results["tests"]["data_files"] = test_data_files()
    print()

    # Summary
    print("=" * 80)
    print("  VERIFICATION SUMMARY")
    print("=" * 80)
    print()

    total = len(results["tests"])
    passed = sum(1 for v in results["tests"].values() if v)
    failed = total - passed

    print(f"  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Pass Rate: {(passed/total*100):.1f}%")
    print()

    status = "PASS" if failed == 0 else "FAIL"
    print(f"  Status: {status}")
    print()

    # Save report
    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    report_file = outputs_dir / "simple_verification_report.json"

    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 1),
        "status": status,
    }

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"  [OK] Report saved: {report_file}")
    except Exception as e:
        print(f"  [ERROR] Failed to save report: {e}")

    print()
    print("=" * 80)

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
