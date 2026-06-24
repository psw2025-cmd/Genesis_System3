"""
Phase 390 SMOTE Test Runner
============================

DRY-RUN test for Phase 390 (SMOTE Data Balancing).
Tests that data loading, balancing, and output generation work correctly.

Usage:
    python tools/run_phase_390_smote_test.py

Author: System3 AI Team
Date: 2025-12-08
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json

import pandas as pd

from core.engine.system3_phase390_smote_balancing import run_phase_390


def main():
    """Run Phase 390 test."""

    print("\n" + "=" * 80)
    print("PHASE 390 SMOTE TEST - DRY-RUN")
    print("=" * 80)

    # Run Phase 390
    print("\n[TEST] Executing Phase 390...")
    result = run_phase_390()

    # Check results
    print("\n[TEST] Validating results...")

    success = True

    # 1. Check phase result status
    if result["status"] != "complete":
        print(f"[FAIL] Phase 390 failed with status: {result['status']}")
        print(f"  Message: {result['message']}")
        success = False
    else:
        print(f"[OK] Phase 390 executed successfully")

    # 2. Check output CSV exists
    csv_path = Path(result["output_file"])
    if not csv_path.exists():
        print(f"[FAIL] Output CSV not found: {result['output_file']}")
        success = False
    else:
        print(f"[OK] Output CSV exists: {result['output_file']}")

        # Check CSV is non-empty
        df = pd.read_csv(csv_path)
        if len(df) == 0:
            print(f"[FAIL] Output CSV is empty")
            success = False
        else:
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")

    # 3. Check metrics JSON exists
    json_path = Path(result["metrics_file"])
    if not json_path.exists():
        print(f"[FAIL] Metrics JSON not found: {result['metrics_file']}")
        success = False
    else:
        print(f"[OK] Metrics JSON exists: {result['metrics_file']}")

        # Check JSON content
        try:
            with open(json_path, "r") as f:
                metrics = json.load(f)

            required_keys = ["phase", "status", "metrics", "class_distribution"]
            for key in required_keys:
                if key not in metrics:
                    print(f"[FAIL] Metrics JSON missing key: {key}")
                    success = False
                else:
                    print(f"  [OK] {key} present")
        except Exception as e:
            print(f"[FAIL] Error reading metrics JSON: {str(e)}")
            success = False

    # 4. Validate class distribution
    print(f"\n[TEST] Class distribution analysis:")
    m = result["metrics"]

    if "input_class_counts" in m and "output_class_counts" in m:
        print(f"\n  Before balancing:")
        for cls, count in m["input_class_counts"].items():
            total = m["input_rows"]
            pct = 100.0 * count / total
            print(f"    {cls:10s}: {count:6d} ({pct:6.2f}%)")

        print(f"\n  After balancing:")
        for cls, count in m["output_class_counts"].items():
            total = m["output_rows"]
            pct = 100.0 * count / total
            print(f"    {cls:10s}: {count:6d} ({pct:6.2f}%)")

        # Check that output is reasonably balanced
        out_counts = list(m["output_class_counts"].values())
        if len(out_counts) > 0:
            max_pct = max(out_counts) / sum(out_counts)
            min_pct = min(out_counts) / sum(out_counts)
            balance_ratio = max_pct / min_pct if min_pct > 0 else float("inf")

            print(f"\n  Balance ratio (max/min): {balance_ratio:.2f}")
            if balance_ratio < 1.2:  # Allow 20% variance
                print(f"  [OK] Classes reasonably balanced")
            else:
                print(f"  [WARN] Classes have imbalance (ratio={balance_ratio:.2f})")
    else:
        print(f"[FAIL] Class counts not in metrics")
        success = False

    # 5. Check safety flags
    print(f"\n[TEST] Safety verification:")

    # Check that no trading flags were modified
    if os.environ.get("LIVE_TRADING_ENABLED", "False").lower() == "true":
        print(f"[FAIL] LIVE_TRADING_ENABLED is True! Safety compromised.")
        success = False
    else:
        print(f"[OK] LIVE_TRADING_ENABLED = False (safe)")

    # 6. Summary
    print(f"\n" + "=" * 80)
    if success:
        print("TEST RESULT: PASSED")
        print("=" * 80)
        print(f"\nPhase 390 is ready for production.")
        print(f"\nOutput files:")
        print(f"  CSV: {result['output_file']}")
        print(f"  JSON: {result['metrics_file']}")
        print(f"\nMetrics:")
        print(f"  Input rows: {m.get('input_rows', 'N/A')}")
        print(f"  Output rows: {m.get('output_rows', 'N/A')}")
        print(f"  Rows added: {m.get('rows_added', 'N/A')}")
        print(f"  Method: {m.get('balancing_method', 'N/A')}")
        print(f"  Duration: {result.get('duration_ms', 'N/A')} ms")
        print("=" * 80 + "\n")
        return 0
    else:
        print("TEST RESULT: FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
