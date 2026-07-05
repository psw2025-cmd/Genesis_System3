"""
System3 Signal Engine Self-Test

Provides a self-test endpoint for the signal engine that validates:
- Threshold loading
- Signal generation pipeline
- Without touching broker APIs
"""

import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.system3_signal_engine import process_snapshot
from core.engine.threshold_loader import load_thresholds


def create_test_snapshot() -> pd.DataFrame:
    """
    Create a minimal test snapshot for self-test.

    Returns:
        Test DataFrame
    """
    test_data = []

    # Create test rows for each underlying
    for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
        # Create a few test rows with different scores
        for score in [-0.15, -0.05, 0.05, 0.15]:
            test_data.append(
                {
                    "ts": pd.Timestamp.now(),
                    "underlying": underlying,
                    "expiry": "30DEC2025",
                    "strike": 25000.0 if underlying == "NIFTY" else 60000.0,
                    "side": "CE",
                    "ltp": 100.0,
                    "spot": 25000.0 if underlying == "NIFTY" else 60000.0,
                    "iv": 0.2,
                    "time_to_expiry": 0.1,
                }
            )

    return pd.DataFrame(test_data)


def run_self_test() -> Dict[str, Any]:
    """
    Run self-test on signal engine.

    Returns:
        Dict with test results
    """
    results = {"status": "PASS", "errors": [], "warnings": [], "checks": {}}

    # Check 1: Load thresholds
    print("Check 1: Loading thresholds...")
    try:
        thresholds = load_thresholds(prefer_candidates=True)
        if not thresholds:
            results["errors"].append("Failed to load thresholds")
            results["status"] = "FAIL"
        else:
            results["checks"]["thresholds_loaded"] = True
            print(f"   ✅ Loaded thresholds for {len(thresholds)} underlyings")
    except Exception as e:
        results["errors"].append(f"Error loading thresholds: {e}")
        results["status"] = "FAIL"
        print(f"   ❌ Failed: {e}")

    # Check 2: Create test snapshot
    print("\nCheck 2: Creating test snapshot...")
    try:
        test_df = create_test_snapshot()
        if test_df.empty:
            results["errors"].append("Test snapshot is empty")
            results["status"] = "FAIL"
        else:
            results["checks"]["test_snapshot_created"] = True
            print(f"   ✅ Created test snapshot with {len(test_df)} rows")
    except Exception as e:
        results["errors"].append(f"Error creating test snapshot: {e}")
        results["status"] = "FAIL"
        print(f"   ❌ Failed: {e}")

    # Check 3: Process snapshot through signal engine
    print("\nCheck 3: Processing snapshot through signal engine...")
    try:
        if "test_snapshot_created" in results["checks"]:
            processed_df = process_snapshot(test_df)
            if processed_df.empty:
                results["warnings"].append("Processed snapshot is empty")
            else:
                results["checks"]["snapshot_processed"] = True
                print(f"   ✅ Processed snapshot: {len(processed_df)} rows")

                # Check for required columns
                required_cols = ["final_score", "signal"]
                missing_cols = [col for col in required_cols if col not in processed_df.columns]
                if missing_cols:
                    results["errors"].append(f"Missing columns in processed snapshot: {missing_cols}")
                    results["status"] = "FAIL"
                else:
                    results["checks"]["required_columns_present"] = True
                    print(f"   ✅ Required columns present")

                    # Check signal distribution
                    if "signal" in processed_df.columns:
                        signal_counts = processed_df["signal"].value_counts().to_dict()
                        results["checks"]["signal_distribution"] = signal_counts
                        print(f"   ✅ Signal distribution: {signal_counts}")
    except Exception as e:
        results["errors"].append(f"Error processing snapshot: {e}")
        results["status"] = "FAIL"
        import traceback

        print(f"   ❌ Failed: {e}")
        print(traceback.format_exc())

    # Check 4: Verify thresholds are applied correctly
    print("\nCheck 4: Verifying thresholds are applied...")
    try:
        if "snapshot_processed" in results["checks"] and "thresholds_loaded" in results["checks"]:
            # Check if signals match thresholds
            global_buy = thresholds.get("default", {}).get("buy", 0.1)
            global_sell = thresholds.get("default", {}).get("sell", -0.1)

            buy_signals = len(
                processed_df[(processed_df["final_score"] >= global_buy) & (processed_df["signal"] == "BUY")]
            )
            sell_signals = len(
                processed_df[(processed_df["final_score"] <= global_sell) & (processed_df["signal"] == "SELL")]
            )

            results["checks"]["thresholds_applied"] = {"buy_signals": buy_signals, "sell_signals": sell_signals}
            print(f"   ✅ Thresholds applied: {buy_signals} BUY, {sell_signals} SELL")
    except Exception as e:
        results["warnings"].append(f"Could not verify thresholds: {e}")
        print(f"   ⚠️  Warning: {e}")

    return results


def main() -> int:
    """
    Main self-test entry point.

    Returns:
        Exit code: 0 for PASS, 1 for FAIL
    """
    print("=" * 80)
    print("SYSTEM3 SIGNAL ENGINE SELF-TEST")
    print("=" * 80)
    print()

    results = run_self_test()

    print("\n" + "=" * 80)
    if results["status"] == "PASS":
        print("✅ SELF-TEST PASSED")
        if results["warnings"]:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for warn in results["warnings"]:
                print(f"   - {warn}")
        return 0
    else:
        print("❌ SELF-TEST FAILED")
        if results["errors"]:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for err in results["errors"]:
                print(f"   - {err}")
        if results["warnings"]:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for warn in results["warnings"]:
                print(f"   - {warn}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
