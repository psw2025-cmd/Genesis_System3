"""
Phase 391 XGBoost Test Runner
=============================

Functional test for Phase 391 (XGBoost Model Training).
Tests balanced dataset loading, model training, and output generation.

Usage:
    python tools/run_phase_391_xgb_test.py

Author: System3 AI Team
Date: 2025-12-08
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.engine.system3_phase391_xgboost_training import run_phase_391


def main():
    """Run Phase 391 test."""

    print("\n" + "=" * 80)
    print("PHASE 391 XGBOOST TEST - DRY-RUN")
    print("=" * 80)

    # Verify input dataset exists
    print("\n[TEST] Verifying input dataset...")
    csv_path = Path("storage/datasets/phase_390_balanced_features.csv")
    if not csv_path.exists():
        print(f"[FAIL] Input CSV not found: {csv_path}")
        return 1

    print(f"[OK] Input CSV found: {csv_path}")

    # Check file size
    size_mb = csv_path.stat().st_size / (1024 * 1024)
    print(f"  File size: {size_mb:.2f} MB")

    # Run Phase 391
    print("\n[TEST] Executing Phase 391...")
    result = run_phase_391()

    # Check results
    print("\n[TEST] Validating results...")

    success = True

    # 1. Check phase result status
    if not result["success"]:
        print(f"[FAIL] Phase 391 failed: {result['message']}")
        success = False
    else:
        print(f"[OK] Phase 391 executed successfully")

    # 2. Check models were trained
    if len(result["underlyings_trained"]) == 0:
        print(f"[FAIL] No models trained")
        success = False
    else:
        print(f"[OK] Models trained: {result['underlyings_trained']}")

    # 3. Check metrics JSON exists
    if result["metrics_path"]:
        metrics_path = Path(result["metrics_path"])
        if not metrics_path.exists():
            print(f"[FAIL] Metrics JSON not found: {result['metrics_path']}")
            success = False
        else:
            print(f"[OK] Metrics JSON exists: {result['metrics_path']}")

            # Verify JSON is valid
            try:
                with open(metrics_path, "r") as f:
                    metrics = json.load(f)
                print(f"  Size: {metrics_path.stat().st_size / 1024:.1f} KB")
                print(f"  Phase: {metrics.get('phase')}")
                print(f"  Status: {metrics.get('status')}")
            except Exception as e:
                print(f"[FAIL] Invalid metrics JSON: {str(e)}")
                success = False
    else:
        print(f"[FAIL] Metrics path not provided")
        success = False

    # 4. Check model directory exists
    if result["model_dir"]:
        model_dir = Path(result["model_dir"])
        if not model_dir.exists():
            print(f"[FAIL] Model directory not found: {result['model_dir']}")
            success = False
        else:
            print(f"[OK] Model directory exists: {result['model_dir']}")

            # Count model files
            model_files = list(model_dir.glob("*_xgb_model.pkl"))
            meta_files = list(model_dir.glob("*_xgb_meta.json"))
            print(f"  Model files: {len(model_files)}")
            print(f"  Metadata files: {len(meta_files)}")

            if len(model_files) != len(result["underlyings_trained"]):
                print(f"[WARN] Expected {len(result['underlyings_trained'])} models, found {len(model_files)}")
    else:
        print(f"[FAIL] Model directory not provided")
        success = False

    # 5. Check minimum number of underlyings trained
    min_underlyings = 3  # At least 3 underlyings should be trained
    if len(result["underlyings_trained"]) < min_underlyings:
        print(f"[WARN] Only {len(result['underlyings_trained'])} underlyings trained (expected >=3)")
        # This is a warning, not a failure

    # 6. Check safety flags
    print(f"\n[TEST] Safety verification:")

    if os.environ.get("LIVE_TRADING_ENABLED", "False").lower() == "true":
        print(f"[FAIL] LIVE_TRADING_ENABLED is True! Safety compromised.")
        success = False
    else:
        print(f"[OK] LIVE_TRADING_ENABLED = False (safe)")

    # 7. Per-underlying metrics
    print(f"\n[TEST] Per-underlying metrics:")

    if len(result["underlyings_trained"]) > 0:
        print(f"\n  Trained underlyings:")
        for underlying in result["underlyings_trained"]:
            print(f"    - {underlying}")

    if len(result["underlyings_skipped"]) > 0:
        print(f"\n  Skipped underlyings:")
        for underlying in result["underlyings_skipped"]:
            print(f"    - {underlying}")

    # Summary
    print(f"\n" + "=" * 80)
    if success:
        print("TEST RESULT: PASSED")
        print("=" * 80)
        print(f"\nPhase 391 is ready for production.")
        print(f"\nSummary:")
        print(
            f"  Models trained: {len(result['underlyings_trained'])}/{len(result['underlyings_trained']) + len(result['underlyings_skipped'])}"
        )
        print(f"  Output directory: {result['model_dir']}")
        print(f"  Metrics file: {result['metrics_path']}")
        print(f"  Duration: {result.get('duration_ms', 'N/A')} ms")

        if result["warnings"]:
            print(f"\n  Warnings:")
            for w in result["warnings"]:
                print(f"    - {w}")

        print("=" * 80 + "\n")
        return 0
    else:
        print("TEST RESULT: FAILED")
        print("=" * 80)
        print(f"\nDebug Info:")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        if result["warnings"]:
            print(f"  Warnings: {result['warnings']}")
        print("=" * 80 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
