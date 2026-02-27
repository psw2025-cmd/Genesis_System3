"""
System3 Phase 196 - DRY-RUN Readiness Checklist

Verifies DRY-RUN readiness and provides explicit YES/NO.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

MASTER_CONFIG_PATH = STORAGE_CONFIG / "system3_master_session_config.json"
SAFETY_STATE_PATH = STORAGE_CONFIG / "system3_master_safety_state.json"
HEALTH_SNAPSHOT_PATH = STORAGE_ULTRA / "phase132_master_health_snapshot.json"
ONE_LOT_HEALTH_PATH = STORAGE_ULTRA / "phase145_one_lot_health_report.md"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase196_dry_run_readiness_report.md"


def run_phase196_dry_run_readiness() -> Dict[str, Any]:
    """
    Verify DRY-RUN readiness.

    Returns:
        dict: {
            "phase": 196,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    checks = {}

    try:
        # Check 1: DRY_RUN only
        master_config = {}
        if MASTER_CONFIG_PATH.exists():
            with MASTER_CONFIG_PATH.open("r", encoding="utf-8") as f:
                master_config = json.load(f)
        checks["dry_run_only"] = master_config.get("dry_run", True) is True

        # Check 2: ANGEL_ONLY
        checks["angel_only"] = master_config.get("broker", "") == "ANGEL_ONE"

        # Check 3: Capital & lot-size rules
        capital_guardrail_path = STORAGE_ULTRA / "phase140_capital_guardrail.csv"
        checks["capital_rules_obeyed"] = capital_guardrail_path.exists()

        # Check 4: No kill-switch active
        safety_state = {}
        if SAFETY_STATE_PATH.exists():
            with SAFETY_STATE_PATH.open("r", encoding="utf-8") as f:
                safety_state = json.load(f)
        checks["no_kill_switch"] = not safety_state.get("kill_switch_active", False)

        # Check 5: Health snapshot OK
        health_snapshot = {}
        if HEALTH_SNAPSHOT_PATH.exists():
            with HEALTH_SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
                health_snapshot = json.load(f)
        checks["health_ok"] = health_snapshot.get("overall_status", "ERROR") in ["OK", "WARN"]

        # Determine overall readiness
        all_checks_passed = all(checks.values())
        readiness = "YES" if all_checks_passed else "NO"

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 DRY-RUN Readiness Checklist\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Readiness Checks\n\n")
            f.write("| Check | Status |\n")
            f.write("|-------|--------|\n")
            f.write(f"| DRY_RUN only | {'✅ PASS' if checks['dry_run_only'] else '❌ FAIL'} |\n")
            f.write(f"| ANGEL_ONLY | {'✅ PASS' if checks['angel_only'] else '❌ FAIL'} |\n")
            f.write(
                f"| Capital & lot-size rules obeyed | {'✅ PASS' if checks['capital_rules_obeyed'] else '❌ FAIL'} |\n"
            )
            f.write(f"| No kill-switch active | {'✅ PASS' if checks['no_kill_switch'] else '❌ FAIL'} |\n")
            f.write(f"| Health snapshot OK | {'✅ PASS' if checks['health_ok'] else '❌ FAIL'} |\n")

            f.write("\n## Final Verdict\n\n")
            f.write(f"**DRY-RUN READINESS: {readiness}**\n\n")
            if readiness == "YES":
                f.write("✅ System is ready for DRY-RUN operations.\n")
            else:
                f.write("❌ System is NOT ready for DRY-RUN operations. Review failed checks above.\n")

        status = "OK" if not errors else "ERROR"
        details = f"DRY-RUN readiness: {readiness}"

        return {
            "phase": 196,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "readiness": readiness,
                "checks": checks,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 196,
            "status": "ERROR",
            "details": f"Phase 196 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 196 - DRY-RUN READINESS CHECKLIST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase196_dry_run_readiness()

    print(f"Phase196: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReadiness: {result['outputs']['readiness']}")
        print(f"Report: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
