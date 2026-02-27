"""
Block Test for System3 Phases 389-400
======================================

Executes all 12 phases sequentially and generates pass/fail summary.

Usage:
    python tools/run_phases_389_400_block_test.py

Author: System3 AI Team
Date: 2025-12-08
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
import json

# Import phase functions
from core.engine.ai_model.feature_engineering_v2 import run_phase_389
from core.engine.ai_model.smote_balancer import run_phase_390
from core.engine.ai_model.xgboost_trainer import run_phase_391
from core.engine.ensemble_predictor import run_phase_392
from core.engine.system3_phases_393_400 import (
    run_phase_393,
    run_phase_394,
    run_phase_395,
    run_phase_396,
    run_phase_397,
    run_phase_398,
    run_phase_399,
    run_phase_400,
    verify_safety_configs,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


PHASE_FUNCTIONS = [
    (389, "Feature Engineering Upgrade", run_phase_389),
    (390, "SMOTE Data Balancing", run_phase_390),
    (391, "XGBoost Model Training", run_phase_391),
    (392, "Ultra + ML + Delta Ensemble", run_phase_392),
    (393, "Score Normalization Engine", run_phase_393),
    (394, "Real PnL Outcome Learning", run_phase_394),
    (395, "Drift Detector Upgrade", run_phase_395),
    (396, "Daily Auto-Retraining Engine", run_phase_396),
    (397, "Probability-Based Risk Controller", run_phase_397),
    (398, "Paper Trading Validation Loop", run_phase_398),
    (399, "Scoring Telemetry v2.0", run_phase_399),
    (400, "Production-Readiness Report", run_phase_400),
]


def run_block_test_389_400():
    """Run all phases 389-400 and generate summary."""
    print("=" * 80)
    print("SYSTEM3 PHASES 389-400 BLOCK TEST")
    print("ML Pipeline Upgrade - Production Grade")
    print("=" * 80)
    print()

    # Safety check
    print("Verifying safety configurations...")
    if not verify_safety_configs():
        print("[FAIL] SAFETY CHECK FAILED: Live trading may be enabled!")
        print("Aborting block test.")
        return 1
    print("[OK] Safety check passed: LIVE_TRADING_ENABLED = False\n")

    results = []
    start_time = datetime.now()

    for phase_id, phase_name, phase_func in PHASE_FUNCTIONS:
        phase_label = f"Phase {phase_id}: {phase_name}"
        print(f"{phase_label}".ljust(60), end=" ")

        try:
            result = phase_func()
            status = result.get("status", "error")
            message = result.get("message", "")

            if status == "ok":
                print("[OK]")
                results.append({"phase": phase_id, "name": phase_name, "status": "PASS", "message": message})
            elif status == "warn":
                print("[WARN]")
                results.append({"phase": phase_id, "name": phase_name, "status": "WARN", "message": message})
            else:
                print("[FAIL]")
                results.append({"phase": phase_id, "name": phase_name, "status": "FAIL", "message": message})

        except Exception as e:
            print(f"[ERROR]")
            results.append({"phase": phase_id, "name": phase_name, "status": "ERROR", "message": str(e)})
            logger.error(f"Phase {phase_id} error: {e}", exc_info=True)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Summary
    print()
    print("=" * 80)
    print("BLOCK TEST SUMMARY")
    print("=" * 80)

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    warn_count = sum(1 for r in results if r["status"] == "WARN")
    fail_count = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])

    print(f"\nResults: {pass_count}/12 PASS, {warn_count}/12 WARN, {fail_count}/12 FAIL")
    print(f"Duration: {duration:.2f} seconds")

    # Details for non-passing phases
    if warn_count > 0 or fail_count > 0:
        print("\n[!] Issues Detected:")
        for r in results:
            if r["status"] in ["WARN", "FAIL", "ERROR"]:
                print(f"  Phase {r['phase']}: {r['status']} - {r['message']}")

    # Final safety check
    print("\nFinal safety verification...")
    if verify_safety_configs():
        print("[OK] Safety configs remain unchanged: LIVE_TRADING_ENABLED = False")
    else:
        print("[WARN] WARNING: Safety configs may have changed!")

    # Overall status
    print()
    if fail_count == 0 and warn_count == 0:
        print("[SUCCESS] STATUS: ALL PHASES COMPLETE - READY FOR PRODUCTION")
        overall_status = "complete"
        exit_code = 0
    elif fail_count == 0:
        print("[WARN] STATUS: PHASES COMPLETE WITH WARNINGS - REVIEW BEFORE PRODUCTION")
        overall_status = "complete_with_warnings"
        exit_code = 0
    else:
        print("[FAIL] STATUS: SOME PHASES FAILED - FIX ISSUES BEFORE PRODUCTION")
        overall_status = "failed"
        exit_code = 1

    # Save block test results
    block_test_summary = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "overall_status": overall_status,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "total_phases": len(PHASE_FUNCTIONS),
        "phase_results": results,
        "safety_check": verify_safety_configs(),
    }

    summary_path = Path("storage/metrics/block_test_389_400_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(block_test_summary, f, indent=2)

    print(f"\nBlock test summary saved: {summary_path}")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    exit_code = run_block_test_389_400()
    sys.exit(exit_code)
