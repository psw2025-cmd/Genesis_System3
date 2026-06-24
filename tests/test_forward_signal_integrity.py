"""
System3 Forward Signal Integrity Test Suite

Validates dhan_index_ai_signals_with_forward.csv integrity before PnL enrichment.
Tests critical columns: ts, side, no NaN in keys, file length.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FORWARD_SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"


def test_forward_signal_integrity() -> dict:
    """
    Test forward signals CSV integrity.

    Returns:
        dict: {
            "passed": bool,
            "total_tests": int,
            "tests": [
                {"name": str, "passed": bool, "details": str},
                ...
            ]
        }
    """
    results = []

    # Test 1: File exists and non-empty
    test1 = {"name": "File exists and readable", "passed": False, "details": ""}

    if not FORWARD_SIGNALS_CSV.exists():
        test1["details"] = f"File not found: {FORWARD_SIGNALS_CSV}"
        results.append(test1)
        return {"passed": False, "total_tests": 1, "tests": results}

    try:
        df = pd.read_csv(FORWARD_SIGNALS_CSV)
        file_size_mb = FORWARD_SIGNALS_CSV.stat().st_size / (1024 * 1024)
        test1["passed"] = len(df) > 0
        test1["details"] = f"✅ {len(df)} rows, {file_size_mb:.2f} MB" if test1["passed"] else "File is empty"
    except Exception as e:
        test1["details"] = f"Failed to read CSV: {e}"
        results.append(test1)
        return {"passed": False, "total_tests": 1, "tests": results}

    results.append(test1)

    # Test 2: ts column exists and is valid datetime
    test2 = {"name": "ts column is valid datetime", "passed": False, "details": ""}

    if "ts" not in df.columns:
        test2["details"] = "❌ ts column missing"
    else:
        ts_null_count = df["ts"].isna().sum()
        ts_null_pct = (ts_null_count / len(df) * 100) if len(df) > 0 else 100

        if ts_null_count == len(df):
            test2["details"] = f"❌ ts column is 100% NaN ({ts_null_count}/{len(df)})"
        elif ts_null_pct > 50:
            test2["passed"] = False
            test2["details"] = f"⚠️ ts column has {ts_null_pct:.1f}% NaN ({ts_null_count}/{len(df)})"
        else:
            # Try parsing as datetime
            try:
                df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
                valid_ts = df["ts"].notna().sum()
                test2["passed"] = valid_ts > len(df) * 0.9  # At least 90% valid
                test2["details"] = (
                    f"✅ {valid_ts}/{len(df)} valid timestamps ({100*valid_ts/len(df):.1f}%)"
                    if test2["passed"]
                    else f"⚠️ Only {valid_ts}/{len(df)} valid timestamps"
                )
            except Exception as e:
                test2["details"] = f"❌ Failed to parse ts as datetime: {e}"

    results.append(test2)

    # Test 3: side column contains only BUY/SELL/HOLD
    test3 = {"name": "side column is valid (BUY/SELL/HOLD)", "passed": False, "details": ""}

    if "side" not in df.columns:
        test3["details"] = "❌ side column missing"
    else:
        valid_sides = {"BUY", "SELL", "HOLD"}
        df["side"] = df["side"].astype(str).str.upper()
        unique_sides = set(df["side"].unique())
        invalid_sides = unique_sides - valid_sides

        if len(invalid_sides) > 0:
            test3["details"] = f"❌ Invalid side values: {invalid_sides}"
        else:
            side_dist = df["side"].value_counts().to_dict()
            test3["passed"] = True
            test3["details"] = f"✅ Valid sides: {side_dist}"

    results.append(test3)

    # Test 4: Key columns have no excessive NaN
    test4 = {"name": "Key columns integrity (underlying, strike, expiry)", "passed": False, "details": ""}

    key_cols = ["underlying", "strike", "expiry"]
    missing_cols = [col for col in key_cols if col not in df.columns]

    if missing_cols:
        test4["details"] = f"❌ Missing key columns: {missing_cols}"
    else:
        null_stats = {}
        for col in key_cols:
            null_count = df[col].isna().sum()
            null_pct = (null_count / len(df) * 100) if len(df) > 0 else 100
            null_stats[col] = f"{null_pct:.1f}%"

        # Pass if all key columns < 10% NaN
        max_null_pct = max([df[col].isna().sum() / len(df) * 100 for col in key_cols])
        test4["passed"] = max_null_pct < 10
        test4["details"] = f"{'✅' if test4['passed'] else '⚠️'} NaN %: {null_stats}"

    results.append(test4)

    # Test 5: Forward return columns exist and have data
    test5 = {"name": "Forward return columns exist and populated", "passed": False, "details": ""}

    fwd_cols = [col for col in df.columns if "fwd_ret" in col or "forward" in col.lower()]

    if len(fwd_cols) == 0:
        test5["details"] = "❌ No forward return columns found"
    else:
        fwd_stats = {}
        for col in fwd_cols[:3]:  # Check first 3
            notna_count = df[col].notna().sum()
            notna_pct = (notna_count / len(df) * 100) if len(df) > 0 else 0
            fwd_stats[col] = f"{notna_pct:.1f}%"

        # Pass if at least one forward return column has > 10% data
        max_data_pct = max([df[col].notna().sum() / len(df) * 100 for col in fwd_cols])
        test5["passed"] = max_data_pct > 10
        test5["details"] = f"{'✅' if test5['passed'] else '⚠️'} Forward returns populated: {fwd_stats}"

    results.append(test5)

    # Test 6: File length is reasonable (> 10 rows)
    test6 = {
        "name": "File has minimum row count",
        "passed": len(df) >= 10,
        "details": f"{'✅' if len(df) >= 10 else '❌'} {len(df)} rows (min: 10)",
    }
    results.append(test6)

    # Summary
    passed_count = sum(1 for test in results if test["passed"])
    all_passed = passed_count == len(results)

    return {"passed": all_passed, "total_tests": len(results), "passed_tests": passed_count, "tests": results}


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 FORWARD SIGNAL INTEGRITY TEST SUITE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"Testing: {FORWARD_SIGNALS_CSV}\n")

    result = test_forward_signal_integrity()

    print(f"Tests Run: {result['total_tests']}")
    print(f"Tests Passed: {result['passed_tests']}/{result['total_tests']}\n")

    for test in result["tests"]:
        status_icon = "✅" if test["passed"] else "❌"
        print(f"{status_icon} {test['name']}")
        print(f"   {test['details']}\n")

    print("=" * 70)
    if result["passed"]:
        print("✅ ALL TESTS PASSED - Forward signals CSV is valid")
        return 0
    else:
        print("❌ TESTS FAILED - Forward signals CSV has integrity issues")
        print("\nRecommendations:")
        print("  1. Run Phase 221 (forward returns calculator)")
        print("  2. Check for column corruption in Phase 225 (reconciliation)")
        print("  3. Verify ts and side columns in source data")
        return 1


if __name__ == "__main__":
    sys.exit(main())
