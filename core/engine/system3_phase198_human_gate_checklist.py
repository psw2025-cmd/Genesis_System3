"""
System3 Phase 198 - Human Gate Checklist (Manual Only)

Generates human-readable checklist for manual confirmation.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

READINESS_REPORT = STORAGE_ULTRA / "phase196_dry_run_readiness_report.md"
TEST_PLAN = STORAGE_ULTRA / "phase197_micro_capital_test_plan.md"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase198_human_gate_checklist.md"


def run_phase198_human_gate_checklist() -> Dict[str, Any]:
    """
    Generate human gate checklist.

    Returns:
        dict: {
            "phase": 198,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Generate MD checklist
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Human Gate Checklist (Manual Confirmation Required)\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(
                "**IMPORTANT**: This checklist must be manually reviewed and confirmed before any future live mode.\n\n"
            )

            f.write("## Pre-Live Mode Checklist\n\n")
            f.write("Please confirm each item manually:\n\n")
            f.write("- [ ] DRY-RUN testing completed successfully for at least 30 days\n")
            f.write("- [ ] All safety mechanisms verified and operational\n")
            f.write("- [ ] Capital guardrails tested and validated\n")
            f.write("- [ ] Kill switch tested and confirmed working\n")
            f.write("- [ ] Risk limits reviewed and approved\n")
            f.write("- [ ] One-lot-only mode tested and validated\n")
            f.write("- [ ] Execution quality acceptable (slippage, fills)\n")
            f.write("- [ ] PnL analysis shows acceptable performance\n")
            f.write("- [ ] All phases 131-200 operational\n")
            f.write("- [ ] Backup and recovery procedures tested\n")
            f.write("- [ ] Operator override procedures understood\n")
            f.write("- [ ] Emergency stop procedures documented and tested\n")
            f.write("- [ ] Live trading explicitly enabled in config (after all checks pass)\n\n")

            f.write("## Notes\n\n")
            f.write("- **NO AUTOMATION**: This checklist requires manual confirmation.\n")
            f.write("- **NO FLAG TOGGLING**: No code path automatically enables live trading.\n")
            f.write("- **SAFETY FIRST**: All items must be checked before considering live mode.\n")

        status = "OK"
        details = "Human gate checklist generated"

        return {
            "phase": 198,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 198,
            "status": "ERROR",
            "details": f"Phase 198 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 198 - HUMAN GATE CHECKLIST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase198_human_gate_checklist()

    print(f"Phase198: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nChecklist: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
