"""
System3 Phase 112 - Session Loop Controller (One-Shot)

One-shot loop controller that orchestrates the full execution flow.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import phase functions
try:
    from core.engine.system3_phase111_live_session_brain import run_phase111
    from core.engine.system3_phase104_tradeplan_to_orders import run_phase104
    from core.engine.system3_phase105_ledger_integrity_check import run_phase105
    from core.engine.system3_phase109_intraday_risk_guard import run_phase109
    from core.engine.system3_phase106_dryrun_execution_bridge import run_phase106
    from core.engine.system3_phase107_live_execution_engine import run_phase107
    from core.engine.system3_phase113_kill_switch_monitor import run_phase113
except ImportError as e:
    print(f"[PH112] ERROR: Failed to import phase modules: {e}")
    sys.exit(1)

# Import config
try:
    from config.live_trade_config import USE_LIVE_EXECUTION_ENGINE
except ImportError:
    USE_LIVE_EXECUTION_ENGINE = False

# Paths
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "phase112_session_loop.log"


def log_cycle(cycle_num: int, message: str):
    """Log cycle message."""
    log_msg = f"[{datetime.now().isoformat()}] Cycle {cycle_num}: {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(log_msg)


def run_phase112(iterations: int = 1, sleep_seconds: int = 30, **kwargs) -> dict:
    """
    Run session loop for specified iterations.

    Args:
        iterations: Number of loop iterations (default: 1)
        sleep_seconds: Sleep between iterations (default: 30)

    Returns:
        dict: {
            "phase": 112,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    all_errors = []
    cycle_results = []

    log_cycle(0, f"Starting session loop: {iterations} iteration(s), {sleep_seconds}s interval")

    for i in range(1, iterations + 1):
        log_cycle(i, "Starting cycle")

        try:
            # Check kill switch
            kill_result = run_phase113()
            if kill_result.get("status") == "KILL":
                log_cycle(i, "Kill switch activated, aborting")
                all_errors.append("Kill switch activated")
                break

            # Run Phase 111 (pre-execution check)
            result_111 = run_phase111()
            if result_111.get("status") != "OK":
                log_cycle(i, f"Pre-execution check failed: {result_111.get('details')}")
                all_errors.extend(result_111.get("errors", []))
                cycle_results.append({"cycle": i, "status": "FAILED", "reason": "Pre-execution check failed"})
                continue

            # Run Phase 104 (build PLANNED orders)
            result_104 = run_phase104()

            # Run Phase 105 (integrity check)
            result_105 = run_phase105()
            if result_105.get("status") != "OK":
                log_cycle(i, f"Ledger integrity check failed: {result_105.get('details')}")
                all_errors.extend(result_105.get("errors", []))
                cycle_results.append({"cycle": i, "status": "FAILED", "reason": "Ledger integrity failed"})
                continue

            # Run Phase 109 (risk guard)
            result_109 = run_phase109()
            if result_109.get("status") == "BLOCK":
                log_cycle(i, f"Risk guard blocked: {result_109.get('details')}")
                cycle_results.append({"cycle": i, "status": "BLOCKED", "reason": result_109.get("details")})
                continue

            # Execute orders (DRY_RUN or LIVE)
            if USE_LIVE_EXECUTION_ENGINE:
                result_exec = run_phase107()
                log_cycle(i, f"LIVE execution: {result_exec.get('details')}")
            else:
                result_exec = run_phase106()
                log_cycle(i, f"DRY_RUN execution: {result_exec.get('details')}")

            cycle_results.append(
                {
                    "cycle": i,
                    "status": result_exec.get("status", "UNKNOWN"),
                    "execution_mode": "LIVE" if USE_LIVE_EXECUTION_ENGINE else "DRY_RUN",
                }
            )

            log_cycle(i, "Cycle completed")

        except Exception as e:
            error_msg = f"Cycle {i} failed: {e}"
            all_errors.append(error_msg)
            log_cycle(i, f"ERROR: {error_msg}")
            cycle_results.append({"cycle": i, "status": "ERROR", "error": str(e)})

        # Sleep between iterations (except last)
        if i < iterations:
            time.sleep(sleep_seconds)

    status = "OK" if not all_errors else "ERROR"
    details = f"Completed {len(cycle_results)} cycle(s)"

    return {
        "phase": 112,
        "status": status,
        "details": details,
        "outputs": {
            "iterations": iterations,
            "cycles_completed": len(cycle_results),
            "cycle_results": cycle_results,
        },
        "errors": all_errors,
    }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="System3 Phase 112 - Session Loop Controller")
    parser.add_argument("--iterations", type=int, default=1, help="Number of loop iterations")
    parser.add_argument("--sleep-seconds", type=int, default=30, help="Sleep between iterations")
    args = parser.parse_args()

    print("=" * 70)
    print("SYSTEM3 PHASE 112 - SESSION LOOP CONTROLLER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"Iterations: {args.iterations}")
    print(f"Sleep interval: {args.sleep_seconds}s\n")

    result = run_phase112(iterations=args.iterations, sleep_seconds=args.sleep_seconds)

    print(f"Phase112: {result['details']}")

    if result["outputs"].get("cycle_results"):
        print("\nCycle Results:")
        for cycle_result in result["outputs"]["cycle_results"]:
            print(f"  Cycle {cycle_result['cycle']}: {cycle_result['status']}")
            if "reason" in cycle_result:
                print(f"    Reason: {cycle_result['reason']}")

    if result.get("errors"):
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nLog: {LOG_FILE}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
