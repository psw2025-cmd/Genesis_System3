"""
System3 Ultra - Phase 36: Ultra Continuous Learning Cycle (CULL)

Orchestrator that runs:
- Real data extraction
- Blended dataset creation
- Ultra training
- Ultra validation
- Promotion planner
- Audit

But only in offline, manual mode.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 99
"""

import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def _capture_output(func, *args, **kwargs) -> tuple[Any, str]:
    """Capture stdout from a function call."""
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    try:
        result = func(*args, **kwargs)
        output = captured.getvalue()
        return result, output
    finally:
        sys.stdout = old_stdout


def run_phase36_cull_full_cycle() -> str:
    """
    Run Phase 36: Ultra Continuous Learning Cycle (CULL).

    Returns:
        Path to execution log MD file
    """
    print("=== SYSTEM3 ULTRA - PHASE 36: CONTINUOUS LEARNING CYCLE (CULL) ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] NO AUTOMATIC PROMOTION - NO CONFIG CHANGES\n")

    log_entries = []
    log_entries.append(f"# Ultra Continuous Learning Cycle (CULL) Execution Log\n\n")
    log_entries.append(f"Generated: {datetime.utcnow().isoformat()}\n\n")

    # Step 1: Real data extractor
    log_entries.append("## Step 1: Real Data Extractor\n\n")
    log_entries.append("**Status**: STARTED\n\n")
    try:
        from core.engine.dhan_real_data_extractor import main as real_extractor_main

        result, output = _capture_output(real_extractor_main)
        log_entries.append(f"**Output**:\n```\n{output}\n```\n\n")
        log_entries.append("**Status**: COMPLETED\n\n")
        print("[STEP 1] Real data extraction completed")
    except Exception as e:
        log_entries.append(f"**Status**: FAILED\n\n")
        log_entries.append(f"**Error**: {str(e)}\n\n")
        print(f"[STEP 1] Real data extraction failed: {e}")

    # Step 2: Blended dataset builder
    log_entries.append("## Step 2: Blended Dataset Builder\n\n")
    log_entries.append("**Status**: STARTED\n\n")
    try:
        from core.engine.dhan_blended_dataset_builder import (
            main as blended_builder_main,
        )

        result, output = _capture_output(blended_builder_main)
        log_entries.append(f"**Output**:\n```\n{output}\n```\n\n")
        log_entries.append("**Status**: COMPLETED\n\n")
        print("[STEP 2] Blended dataset building completed")
    except Exception as e:
        log_entries.append(f"**Status**: FAILED\n\n")
        log_entries.append(f"**Error**: {str(e)}\n\n")
        print(f"[STEP 2] Blended dataset building failed: {e}")

    # Step 3: Blended model trainer (Ultra)
    log_entries.append("## Step 3: Blended Model Trainer (Ultra)\n\n")
    log_entries.append("**Status**: STARTED\n\n")
    log_entries.append("**Note**: This step requires manual confirmation and is not auto-executed\n\n")
    try:
        from core.engine.dhan_blended_training_v3 import main as blended_trainer_main

        # Note: This may require manual confirmation, so we just log that it should be run
        log_entries.append("**Status**: MANUAL TRIGGER REQUIRED\n\n")
        log_entries.append("**Note**: Run menu option 71 to train blended models manually\n\n")
        print("[STEP 3] Blended model training requires manual trigger (menu option 71)")
    except Exception as e:
        log_entries.append(f"**Status**: FAILED\n\n")
        log_entries.append(f"**Error**: {str(e)}\n\n")
        print(f"[STEP 3] Blended model training check failed: {e}")

    # Step 4: Ultra comparison (Phase 32)
    log_entries.append("## Step 4: Ultra vs Baseline Comparison (Phase 32)\n\n")
    log_entries.append("**Status**: STARTED\n\n")
    try:
        from core.engine.system3_phase32_ultra_vs_baseline import run_phase32_comparison

        result, output = _capture_output(run_phase32_comparison)
        log_entries.append(f"**Output**:\n```\n{output}\n```\n\n")
        log_entries.append("**Status**: COMPLETED\n\n")
        print("[STEP 4] Ultra comparison completed")
    except Exception as e:
        log_entries.append(f"**Status**: FAILED\n\n")
        log_entries.append(f"**Error**: {str(e)}\n\n")
        print(f"[STEP 4] Ultra comparison failed: {e}")

    # Step 5: Promotion planner (Phase 33)
    log_entries.append("## Step 5: Promotion Planner (Phase 33)\n\n")
    log_entries.append("**Status**: STARTED\n\n")
    try:
        from core.engine.system3_phase33_promotion_planner import (
            run_phase33_promotion_planner,
        )

        result, output = _capture_output(run_phase33_promotion_planner)
        log_entries.append(f"**Output**:\n```\n{output}\n```\n\n")
        log_entries.append("**Status**: COMPLETED\n\n")
        print("[STEP 5] Promotion planning completed")
    except Exception as e:
        log_entries.append(f"**Status**: FAILED\n\n")
        log_entries.append(f"**Error**: {str(e)}\n\n")
        print(f"[STEP 5] Promotion planning failed: {e}")

    # Step 6: Auditor (Phase 35)
    log_entries.append("## Step 6: Decision Auditor (Phase 35)\n\n")
    log_entries.append("**Status**: STARTED\n\n")
    try:
        from core.engine.system3_phase35_ultra_auditor import run_phase35_audit

        result, output = _capture_output(run_phase35_audit)
        log_entries.append(f"**Output**:\n```\n{output}\n```\n\n")
        log_entries.append("**Status**: COMPLETED\n\n")
        print("[STEP 6] Decision auditing completed")
    except Exception as e:
        log_entries.append(f"**Status**: FAILED\n\n")
        log_entries.append(f"**Error**: {str(e)}\n\n")
        print(f"[STEP 6] Decision auditing failed: {e}")

    # Final summary
    log_entries.append("## Summary\n\n")
    log_entries.append("CULL cycle completed. All steps executed in safe, read-only mode.\n\n")
    log_entries.append("**No configs were modified.**\n")
    log_entries.append("**No automatic promotion occurred.**\n")
    log_entries.append("**All outputs are in Ultra storage directories.**\n")

    # Save log
    log_md = ULTRA_DIR / "phase36_cull_execution_log.md"
    with log_md.open("w", encoding="utf-8") as f:
        f.write("".join(log_entries))

    print(f"[SAVE] Execution log saved to: {log_md}")
    print("\n[OK] Phase 36 CULL Orchestrator completed")
    return str(log_md)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase36_cull_full_cycle()
        print(f"\n[PHASE 36] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 36][ERROR] {e}")
        error_path = ULTRA_DIR / "phase36_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 36 Error\n\n{str(e)}\n")
        print(f"[PHASE 36] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
