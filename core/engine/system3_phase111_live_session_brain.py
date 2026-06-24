"""
System3 Phase 111 - Live Signal Session Orchestrator (Skeleton)

Orchestrates phases: 101, 102, 104, 105, 109.
Returns combined status for a pre-execution check.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import phase functions
try:
    from core.engine.system3_phase101_live_trade_config_check import run_phase101
    from core.engine.system3_phase102_order_ledger_schema import run_phase102
    from core.engine.system3_phase104_tradeplan_to_orders import run_phase104
    from core.engine.system3_phase105_ledger_integrity_check import run_phase105
    from core.engine.system3_phase109_intraday_risk_guard import run_phase109
except ImportError as e:
    print(f"[PH111] ERROR: Failed to import phase modules: {e}")
    sys.exit(1)


def run_phase111(**kwargs) -> dict:
    """
    Orchestrate pre-execution checks.

    Returns:
        dict: {
            "phase": 111,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    child_results = {}
    all_errors = []

    # Run Phase 101: Config check
    try:
        result_101 = run_phase101()
        child_results["phase101"] = result_101
        if result_101.get("status") != "OK":
            all_errors.extend(result_101.get("errors", []))
    except Exception as e:
        all_errors.append(f"Phase 101 failed: {e}")
        child_results["phase101"] = {"status": "ERROR", "error": str(e)}

    # Run Phase 102: Ledger schema
    try:
        result_102 = run_phase102()
        child_results["phase102"] = result_102
        if result_102.get("status") != "OK":
            all_errors.extend(result_102.get("errors", []))
    except Exception as e:
        all_errors.append(f"Phase 102 failed: {e}")
        child_results["phase102"] = {"status": "ERROR", "error": str(e)}

    # Run Phase 104: Trade plan to orders
    try:
        result_104 = run_phase104()
        child_results["phase104"] = result_104
        if result_104.get("status") != "OK":
            all_errors.extend(result_104.get("errors", []))
    except Exception as e:
        all_errors.append(f"Phase 104 failed: {e}")
        child_results["phase104"] = {"status": "ERROR", "error": str(e)}

    # Run Phase 105: Ledger integrity
    try:
        result_105 = run_phase105()
        child_results["phase105"] = result_105
        if result_105.get("status") != "OK":
            all_errors.extend(result_105.get("errors", []))
    except Exception as e:
        all_errors.append(f"Phase 105 failed: {e}")
        child_results["phase105"] = {"status": "ERROR", "error": str(e)}

    # Run Phase 109: Risk guard
    try:
        result_109 = run_phase109()
        child_results["phase109"] = result_109
        if result_109.get("status") == "BLOCK":
            all_errors.append(f"Risk guard blocked: {result_109.get('details')}")
    except Exception as e:
        all_errors.append(f"Phase 109 failed: {e}")
        child_results["phase109"] = {"status": "ERROR", "error": str(e)}

    # Determine overall status
    if all_errors:
        status = "ERROR"
        details = f"Pre-execution check failed: {len(all_errors)} issue(s)"
    else:
        # Check if risk guard blocked
        if child_results.get("phase109", {}).get("status") == "BLOCK":
            status = "BLOCK"
            details = "Pre-execution check OK, but risk guard blocked"
        else:
            status = "OK"
            details = "Pre-execution check passed"

    return {
        "phase": 111,
        "status": status,
        "details": details,
        "outputs": {
            "child_results": child_results,
            "summary": {
                "config_check": child_results.get("phase101", {}).get("status", "UNKNOWN"),
                "ledger_schema": child_results.get("phase102", {}).get("status", "UNKNOWN"),
                "trade_plan_conversion": child_results.get("phase104", {}).get("status", "UNKNOWN"),
                "ledger_integrity": child_results.get("phase105", {}).get("status", "UNKNOWN"),
                "risk_guard": child_results.get("phase109", {}).get("status", "UNKNOWN"),
            },
        },
        "errors": all_errors,
    }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 111 - LIVE SESSION BRAIN")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase111()

    print(f"Phase111: {result['details']}")

    print("\nChild Phase Results:")
    summary = result["outputs"]["summary"]
    for phase, status in summary.items():
        print(f"  {phase}: {status}")

    if result.get("errors"):
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
