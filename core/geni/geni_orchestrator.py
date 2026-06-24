"""
System3 GENI - Orchestrator

High-level coordinator for GENI operations.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .geni_config import (
    AUTO_EXECUTE_REAL_TRADES,
    AUTO_PROMOTE_MODELS,
    AUTO_UPDATE_CONFIGS,
    GENI_LAST_RUN_JSON,
    GENI_LAST_RUN_MD,
    GENI_ULTRA_LIVE_MODE,
    PATH_GENI_STORAGE,
    PROJECT_ROOT,
    validate_paths,
)
from .geni_state import GeniState, load_state, save_state
from .geni_tasks import get_all_tasks, get_task
from .geni_validator import ValidationResult, run_full_validation, run_quick_validation


def _run_task(task_name: str) -> Dict[str, Any]:
    """
    Run a registered task.

    Args:
        task_name: Name of task to run

    Returns:
        Dictionary with task execution results
    """
    task = get_task(task_name)
    if not task:
        return {
            "success": False,
            "error": f"Task not found: {task_name}",
        }

    print(f"[GENI] Running task: {task.description}")

    try:
        result = subprocess.run(
            task.command_line,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=task.estimated_runtime_sec * 2,  # 2x estimated time
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[:1000],  # First 1000 chars
            "stderr": result.stderr[:1000],
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Task {task_name} timed out",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Task {task_name} failed: {e}",
        }


def _write_summary(mode: str, results: Dict[str, Any]) -> None:
    """
    Write summary JSON and MD files.

    Args:
        mode: Operation mode
        results: Results dictionary
    """
    # Ensure directory exists
    PATH_GENI_STORAGE.mkdir(parents=True, exist_ok=True)

    # Write JSON
    summary_json = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        **results,
    }

    with GENI_LAST_RUN_JSON.open("w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2, ensure_ascii=False)

    # Write MD
    with GENI_LAST_RUN_MD.open("w", encoding="utf-8") as f:
        f.write(f"# System3 GENI Last Run – {mode.upper()}\n\n")
        f.write(f"- **Timestamp**: {summary_json['timestamp']}\n")
        f.write(f"- **Mode**: {mode}\n")
        f.write(f"- **Success**: {results.get('success', False)}\n")

        if "validation_result" in results:
            vr = results["validation_result"]
            f.write(f"- **Validation Passed**: {vr.get('success', False)}\n")
            f.write(f"- **Total Checks**: {vr.get('total_checks', 0)}\n")
            f.write(f"- **Passed**: {vr.get('passed', 0)}\n")
            f.write(f"- **Failed**: {vr.get('failed', 0)}\n")

        if results.get("warnings"):
            f.write("\n## Warnings\n\n")
            for warning in results["warnings"]:
                f.write(f"- {warning}\n")

        f.write("\n## Recommended Next Actions\n\n")
        f.write("- Review validation results\n")
        f.write("- Check pending issues in state file\n")
        f.write("- Run next scheduled operation\n")
        f.write("\n**Note**: All operations are SAFE MODE - no real trades, no auto-promotion.\n")


def run_geni_master(mode: str = "status") -> int:
    """
    Run GENI master orchestration.

    Args:
        mode: Operation mode
            - "status": Light status check
            - "full_validation": Run full validation
            - "daily_ultra": Run daily Ultra cycle
            - "panel_test": Run panel test
            - "all": Run combination of operations

    Returns:
        0 on success, non-zero on failure
    """
    print("=" * 70)
    print("System3 GENI Master – SAFE MODE (no real orders, no auto-promotion)")
    print("=" * 70)
    print()

    # Safety check
    if AUTO_EXECUTE_REAL_TRADES or AUTO_PROMOTE_MODELS or GENI_ULTRA_LIVE_MODE:
        print("[WARN] Safety flags should be False in production!")

    # Load state
    state = load_state()

    # Validate paths
    path_warnings = validate_paths()
    state.env_ok = len(path_warnings) == 0
    if path_warnings:
        state.pending_issues.extend(path_warnings)

    results: Dict[str, Any] = {
        "success": True,
        "warnings": path_warnings.copy(),
    }

    # Execute based on mode
    if mode == "status":
        print("[GENI] Mode: STATUS CHECK")
        print(f"[GENI] Environment OK: {state.env_ok}")
        print(f"[GENI] Last validation: {state.last_validation_summary}")
        print(f"[GENI] Pending issues: {len(state.pending_issues)}")

        # Quick validation if cheap
        if state.env_ok:
            validation_result = run_quick_validation()
            results["validation_result"] = {
                "success": validation_result.success,
                "total_checks": validation_result.total_checks,
                "passed": validation_result.passed,
                "failed": validation_result.failed,
            }
            results["warnings"].extend(validation_result.warnings)

    elif mode == "full_validation":
        print("[GENI] Mode: FULL VALIDATION")
        validation_result = run_full_validation()
        results["validation_result"] = {
            "success": validation_result.success,
            "total_checks": validation_result.total_checks,
            "passed": validation_result.passed,
            "failed": validation_result.failed,
        }
        results["warnings"].extend(validation_result.warnings)
        results["success"] = validation_result.success

    elif mode == "daily_ultra":
        print("[GENI] Mode: DAILY ULTRA")
        # Run daily runner
        daily_result = _run_task("run_daily_ultra")
        results["daily_ultra_result"] = daily_result

        # Then run validation
        validation_result = run_quick_validation()
        results["validation_result"] = {
            "success": validation_result.success,
            "total_checks": validation_result.total_checks,
            "passed": validation_result.passed,
            "failed": validation_result.failed,
        }
        results["warnings"].extend(validation_result.warnings)

        results["success"] = daily_result.get("success", False) and validation_result.success

    elif mode == "panel_test":
        print("[GENI] Mode: PANEL TEST")
        panel_result = _run_task("run_ultra_panel_test")
        results["panel_test_result"] = panel_result
        results["success"] = panel_result.get("success", False)

    elif mode == "all":
        print("[GENI] Mode: ALL OPERATIONS")

        # 1. Full validation
        print("\n[1/3] Running full validation...")
        validation_result = run_full_validation()
        results["validation_result"] = {
            "success": validation_result.success,
            "total_checks": validation_result.total_checks,
            "passed": validation_result.passed,
            "failed": validation_result.failed,
        }
        results["warnings"].extend(validation_result.warnings)

        # 2. Panel test
        print("\n[2/3] Running panel test...")
        panel_result = _run_task("run_ultra_panel_test")
        results["panel_test_result"] = panel_result

        # 3. Daily ultra
        print("\n[3/3] Running daily ultra...")
        daily_result = _run_task("run_daily_ultra")
        results["daily_ultra_result"] = daily_result

        results["success"] = (
            validation_result.success and panel_result.get("success", False) and daily_result.get("success", False)
        )

    else:
        print(f"[ERROR] Unknown mode: {mode}")
        return 1

    # Update state
    state.validation_passed = results.get("validation_result", {}).get("success", False)
    save_state(state)

    # Write summary
    _write_summary(mode, results)

    # Print summary
    print("\n" + "=" * 70)
    print("GENI Master Summary")
    print("=" * 70)
    print(f"Mode: {mode}")
    print(f"Success: {results['success']}")
    if "validation_result" in results:
        vr = results["validation_result"]
        print(f"Validation: {vr.get('passed', 0)}/{vr.get('total_checks', 0)} passed")
    print(f"Summary JSON: {GENI_LAST_RUN_JSON}")
    print(f"Summary MD: {GENI_LAST_RUN_MD}")
    print("=" * 70)

    return 0 if results["success"] else 1
