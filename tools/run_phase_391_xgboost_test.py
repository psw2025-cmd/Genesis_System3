"""
Phase 391 XGBoost Test Runner
==============================

DRY-RUN test for Phase 391 (XGBoost Model Training).
Tests that data loading, model training, and output generation work correctly.

Usage:
    python tools/run_phase_391_xgboost_test.py

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

from core.engine.system3_phase391_xgboost_training import run_phase_391


def main():
    """Run Phase 391 test."""

    print("\n" + "=" * 80)
    print("PHASE 391 XGBOOST TEST - DRY-RUN")
    print("=" * 80)

    # Run Phase 391
    print("\n[TEST] Executing Phase 391...")
    result = run_phase_391()

    # Check results
    print("\n[TEST] Validating results...")

    success = True

    # 1. Check phase result status
    if result["status"] != "complete":
        print(f"✗ Phase 391 failed with status: {result['status']}")
        print(f"  Message: {result['message']}")
        success = False
    else:
        print(f"[OK] Phase 391 executed successfully")

    # 2. Check that at least one model was trained
    if len(result["models_trained"]) == 0:
        print(f"✗ No models trained")
        success = False
    else:
        print(f"✓ Models trained: {len(result['models_trained'])}")
        for underlying in result["models_trained"].keys():
            print(f"  ✓ {underlying}")

    # 3. Check model files exist
    print(f"\n[TEST] Checking model files...")
    model_dir = Path("storage/models/xgboost/phase_391")
    for underlying in result["models_trained"].keys():
        model_file = model_dir / f"{underlying}_xgb_model_391.pkl"
        if not model_file.exists():
            print(f"✗ Model file not found: {model_file}")
            success = False
        else:
            size_mb = model_file.stat().st_size / (1024**2)
            print(f"  ✓ {underlying}: {size_mb:.2f} MB")

    # 4. Check metrics JSON
    print(f"\n[TEST] Checking metrics JSON...")
    json_path = Path("storage/metrics/phase_391_xgboost_training_summary.json")
    if not json_path.exists():
        print(f"✗ Metrics JSON not found: {json_path}")
        success = False
    else:
        print(f"✓ Metrics JSON exists: {json_path}")

        # Check JSON validity
        try:
            with open(json_path, "r") as f:
                metrics = json.load(f)

            required_keys = ["phase", "status", "class_mapping", "per_underlying_metrics"]
            for key in required_keys:
                if key not in metrics:
                    print(f"✗ Metrics JSON missing key: {key}")
                    success = False
                else:
                    print(f"  ✓ {key} present")
        except Exception as e:
            print(f"✗ Error reading metrics JSON: {str(e)}")
            success = False

    # 5. Print training metrics
    print(f"\n[TEST] Training metrics:")
    if "models_trained" in result and result["models_trained"]:
        for underlying, data in result["models_trained"].items():
            acc = data["metrics"]["accuracy"]
            precision = data["metrics"]["precision"]
            recall = data["metrics"]["recall"]
            f1 = data["metrics"]["f1_score"]
            print(f"\n  {underlying}:")
            print(f"    Accuracy:  {acc:.4f}")
            print(f"    Precision: {precision:.4f}")
            print(f"    Recall:    {recall:.4f}")
            print(f"    F1-Score:  {f1:.4f}")

    # 6. Print skipped models
    if "models_skipped" in result and result["models_skipped"]:
        print(f"\n[TEST] Skipped models:")
        for underlying, reason in result["models_skipped"].items():
            print(f"  ⚠ {underlying}: {reason}")

    # 7. Check safety flags
    print(f"\n[TEST] Safety verification:")
    if os.environ.get("LIVE_TRADING_ENABLED", "False").lower() == "true":
        print(f"✗ LIVE_TRADING_ENABLED is True! Safety compromised.")
        success = False
    else:
        print(f"✓ LIVE_TRADING_ENABLED = False (safe)")

    # 8. Summary
    print(f"\n" + "=" * 80)
    if success:
        print("TEST RESULT: ✓ PASSED")
        print("=" * 80)
        print(f"\nPhase 391 is ready for production.")
        print(f"\nOutput files:")
        print(f"  Models: storage/models/xgboost/phase_391/")
        print(f"  Metrics: storage/metrics/phase_391_xgboost_training_summary.json")
        print(f"\nModels trained: {len(result['models_trained'])}")
        if result["models_trained"]:
            for underlying, data in result["models_trained"].items():
                acc = data["metrics"]["accuracy"]
                print(f"  {underlying}: {acc:.4f}")
        print("=" * 80 + "\n")
        return 0
    else:
        print("TEST RESULT: ✗ FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
