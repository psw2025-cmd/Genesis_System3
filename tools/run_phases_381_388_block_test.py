"""
Block Test for System3 Phases 381-388

Executes all 8 phases sequentially and generates pass/fail summary.

Usage:
    C:/Genesis_System3/venv/Scripts/python.exe tools/run_phases_381_388_block_test.py

Safety:
    - DRY-RUN only
    - No live trading
    - No safety config modifications
    - Uses venv Python interpreter
"""

import sys
from pathlib import Path
from datetime import datetime
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

# Import all phase modules
from core.engine.system3_phase381_ultra_models_scanner import run_phase_381
from core.engine.system3_phase382_ultra_models_validator import run_phase_382
from core.engine.system3_phase383_ultra_backtest_sampler import run_phase_383
from core.engine.system3_phase384_ultra_health_summary import run_phase_384
from core.engine.system3_phase385_scoring_telemetry import run_phase_385
from core.engine.system3_phase386_failsafe_guard import run_phase_386
from core.engine.system3_phase387_impact_preview import run_phase_387
from core.engine.system3_phase388_health_gate import run_phase_388
from core.engine.system3_phases_381_388_registry import PHASES_381_388

# Output paths
STORAGE_DIR = ROOT_DIR / "storage"
METRICS_DIR = STORAGE_DIR / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"


def verify_python_venv():
    """Verify running in venv."""
    venv_marker = ROOT_DIR / "venv"
    if not venv_marker.exists():
        logger.warning("venv directory not found")
        return False

    if sys.prefix == sys.base_prefix:
        logger.warning("Not running in virtual environment")
        return False

    logger.info(f"✓ Running in venv: {sys.prefix}")
    return True


def verify_safety_configs():
    """Verify safety configs are unchanged."""
    config_dir = ROOT_DIR / "core" / "config"
    safety_verified = True

    # Check live_trade_config.py
    live_config = config_dir / "live_trade_config.py"
    if live_config.exists():
        with open(live_config, "r") as f:
            content = f.read()
            if "LIVE_TRADING_ENABLED = False" in content or "LIVE_TRADING_ENABLED=False" in content:
                logger.info("✓ live_trade_config.py: LIVE_TRADING_ENABLED = False")
            else:
                logger.error("❌ live_trade_config.py: LIVE_TRADING_ENABLED is NOT False")
                safety_verified = False

    # Check dhan_automation_config.json
    dhan_config = config_dir / "dhan_automation_config.json"
    if dhan_config.exists():
        with open(dhan_config, "r") as f:
            config = json.load(f)
            dry_run = config.get("DRY_RUN", config.get("dry_run"))
            if dry_run is True:
                logger.info("✓ dhan_automation_config.json: DRY_RUN = true")
            else:
                logger.error("❌ dhan_automation_config.json: DRY_RUN is NOT true")
                safety_verified = False

    return safety_verified


def run_block_test():
    """Run all phases 381-388 and generate summary."""
    print("=" * 60)
    print("PHASE 381-388 BLOCK TEST")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version.split()[0]}")
    print()

    # Verify venv
    print("Verifying Python environment...")
    if not verify_python_venv():
        print("⚠️ WARNING: Not running in venv (proceeding anyway)")
    print()

    # Phase execution mapping
    phase_functions = [
        (381, "Scanner", run_phase_381),
        (382, "Validator", run_phase_382),
        (383, "Backtest", run_phase_383),
        (384, "Health Summary", run_phase_384),
        (385, "Telemetry", run_phase_385),
        (386, "Fail-Safe", run_phase_386),
        (387, "Impact Preview", run_phase_387),
        (388, "Health Gate", run_phase_388),
    ]

    results = []

    # Run each phase
    for phase_id, phase_name, phase_func in phase_functions:
        print(f"Phase {phase_id} ({phase_name})".ljust(40), end="")

        try:
            result = phase_func()
            status = result.get("status", "error")
            message = result.get("message", "Unknown")

            if status == "ok":
                print(f": ✅ PASS ({message})")
                results.append({"phase": phase_id, "name": phase_name, "status": "PASS", "message": message})
            elif status == "warn":
                print(f": ⚠️ WARN ({message})")
                results.append({"phase": phase_id, "name": phase_name, "status": "WARN", "message": message})
            else:
                print(f": ❌ FAIL ({message})")
                results.append({"phase": phase_id, "name": phase_name, "status": "FAIL", "message": message})

        except Exception as e:
            print(f": ❌ ERROR ({str(e)})")
            results.append({"phase": phase_id, "name": phase_name, "status": "ERROR", "message": str(e)})

    # Summary
    print()
    print("=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    warn_count = sum(1 for r in results if r["status"] == "WARN")
    fail_count = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])
    total_count = len(results)

    print(f"Total Phases: {total_count}")
    print(f"✅ PASS: {pass_count}")
    print(f"⚠️ WARN: {warn_count}")
    print(f"❌ FAIL: {fail_count}")
    print()

    if fail_count == 0 and warn_count == 0:
        print("✅ OVERALL: ALL PHASES PASSED")
        overall_status = "PASS"
    elif fail_count == 0:
        print("⚠️ OVERALL: PASSED WITH WARNINGS")
        overall_status = "WARN"
    else:
        print("❌ OVERALL: SOME PHASES FAILED")
        overall_status = "FAIL"

    print()
    print("=" * 60)
    print("SAFETY VERIFICATION")
    print("=" * 60)

    safety_ok = verify_safety_configs()
    if safety_ok:
        print("✅ All safety configs verified (DRY-RUN enforced)")
    else:
        print("❌ Safety config verification FAILED")
        overall_status = "FAIL"

    print()
    print("=" * 60)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Write summary to file
    summary_file = REPORTS_DIR / "PHASE_381_388_BLOCK_TEST_RESULTS.md"
    with open(summary_file, "w") as f:
        f.write("# PHASE 381-388 BLOCK TEST RESULTS\n\n")
        f.write(f"**Test Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Python:** {sys.executable}\n")
        f.write(f"**Overall Status:** {overall_status}\n\n")

        f.write("## Phase Results\n\n")
        f.write("| Phase | Name | Status | Message |\n")
        f.write("|-------|------|--------|----------|\n")

        for r in results:
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "ERROR": "❌"}[r["status"]]
            f.write(f"| {r['phase']} | {r['name']} | {status_icon} {r['status']} | {r['message']} |\n")

        f.write("\n## Summary\n\n")
        f.write(f"- **Total Phases:** {total_count}\n")
        f.write(f"- **Passed:** {pass_count}\n")
        f.write(f"- **Warnings:** {warn_count}\n")
        f.write(f"- **Failed:** {fail_count}\n\n")

        f.write("## Safety Verification\n\n")
        if safety_ok:
            f.write("✅ **All safety configs verified:**\n")
            f.write("- LIVE_TRADING_ENABLED = False\n")
            f.write("- DRY_RUN = true\n")
        else:
            f.write("❌ **Safety verification FAILED**\n")

    logger.info(f"Block test results written: {summary_file}")

    # Return exit code
    return 0 if overall_status in ["PASS", "WARN"] else 1


if __name__ == "__main__":
    exit_code = run_block_test()
    sys.exit(exit_code)
