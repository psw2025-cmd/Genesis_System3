"""
System3 Phase 120 - End-of-Day Live Summary Pack

Combine outputs from 114, 118, 119 into one report.
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
    from core.engine.system3_phase114_live_session_health import run_phase114
    from core.engine.system3_phase118_daily_live_pnl_snapshot import run_phase118
    from core.engine.system3_phase119_live_safety_audit import run_phase119
except ImportError as e:
    print(f"[PH120] ERROR: Failed to import phase modules: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

OUTPUT_MD = STORAGE_LIVE / "phase120_eod_live_summary_pack.md"


def run_phase120(**kwargs) -> dict:
    """
    Generate end-of-day summary pack.

    Returns:
        dict: {
            "phase": 120,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    child_results = {}

    try:
        # Run Phase 114 (session health)
        try:
            result_114 = run_phase114()
            child_results["phase114"] = result_114
        except Exception as e:
            errors.append(f"Phase 114 failed: {e}")
            child_results["phase114"] = {"status": "ERROR", "error": str(e)}

        # Run Phase 118 (daily PnL)
        try:
            result_118 = run_phase118()
            child_results["phase118"] = result_118
        except Exception as e:
            errors.append(f"Phase 118 failed: {e}")
            child_results["phase118"] = {"status": "ERROR", "error": str(e)}

        # Run Phase 119 (safety audit)
        try:
            result_119 = run_phase119()
            child_results["phase119"] = result_119
        except Exception as e:
            errors.append(f"Phase 119 failed: {e}")
            child_results["phase119"] = {"status": "ERROR", "error": str(e)}

        # Generate combined report
        with OUTPUT_MD.open("w", encoding="utf-8") as f:
            f.write("# System3 End-of-Day Live Summary Pack\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Overview\n\n")
            f.write("This report combines:\n")
            f.write("- Phase 114: Live Session Health\n")
            f.write("- Phase 118: Daily Live PnL Snapshot\n")
            f.write("- Phase 119: Live Safety Audit\n\n")

            # Session Health Summary
            if child_results.get("phase114", {}).get("status") == "OK":
                f.write("## Session Health Summary\n\n")
                outputs_114 = child_results["phase114"].get("outputs", {})
                f.write(f"- **Trades Today**: {outputs_114.get('trades_today', 0)}\n")
                f.write(f"  - PLANNED: {outputs_114.get('planned', 0)}\n")
                f.write(f"  - SENT: {outputs_114.get('sent', 0)}\n")
                f.write(f"  - FILLED: {outputs_114.get('filled', 0)}\n")
                f.write(f"- **Risk Guard**: {outputs_114.get('risk_guard_status', 'UNKNOWN')}\n")
                f.write(
                    f"- **Kill Switch**: {'ACTIVE' if outputs_114.get('kill_switch_active', False) else 'INACTIVE'}\n\n"
                )
                f.write(f"*Full report: {outputs_114.get('snapshot_path', 'N/A')}*\n\n")

            # PnL Summary
            if child_results.get("phase118", {}).get("status") == "OK":
                f.write("## Daily PnL Summary\n\n")
                outputs_118 = child_results["phase118"].get("outputs", {})
                f.write(f"- **Total Trades**: {outputs_118.get('total_trades', 0)}\n")
                f.write(f"- **Filled Trades**: {outputs_118.get('filled_trades', 0)}\n")
                f.write(f"- **Total PnL**: ₹{outputs_118.get('total_pnl_absolute', 0):.2f}\n")
                f.write(f"- **Total PnL %**: {outputs_118.get('total_pnl_percent', 0):.2f}%\n\n")
                f.write(f"*Full report: {outputs_118.get('snapshot_path', 'N/A')}*\n\n")

            # Safety Audit Summary
            if child_results.get("phase119", {}).get("status") == "OK":
                f.write("## Safety Audit Summary\n\n")
                outputs_119 = child_results["phase119"].get("outputs", {})
                f.write(
                    f"- **Live Trading**: {'ENABLED' if outputs_119.get('live_trading_enabled', False) else 'DISABLED'}\n"
                )
                f.write(f"- **Risk Guard**: {outputs_119.get('risk_guard_status', 'UNKNOWN')}\n")
                f.write(
                    f"- **Kill Switch**: {'ACTIVE' if outputs_119.get('kill_switch_active', False) else 'INACTIVE'}\n\n"
                )
                if outputs_119.get("warnings"):
                    f.write("**Warnings**:\n")
                    for warning in outputs_119["warnings"]:
                        f.write(f"- ⚠️ {warning}\n")
                    f.write("\n")
                f.write(f"*Full report: {outputs_119.get('audit_path', 'N/A')}*\n\n")

            # Errors
            if errors:
                f.write("## Errors\n\n")
                for error in errors:
                    f.write(f"- ❌ {error}\n")
                f.write("\n")

        status = "OK" if not errors else "ERROR"
        details = "End-of-day summary pack generated"

        return {
            "phase": 120,
            "status": status,
            "details": details,
            "outputs": {
                "summary_path": str(OUTPUT_MD),
                "child_results": {
                    "phase114": child_results.get("phase114", {}).get("status", "UNKNOWN"),
                    "phase118": child_results.get("phase118", {}).get("status", "UNKNOWN"),
                    "phase119": child_results.get("phase119", {}).get("status", "UNKNOWN"),
                },
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 120,
            "status": "ERROR",
            "details": f"Phase 120 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 120 - END-OF-DAY LIVE SUMMARY PACK")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase120()

    print(f"Phase120: {result['details']}")

    if result["outputs"].get("child_results"):
        print("\nChild Phase Results:")
        for phase, status in result["outputs"]["child_results"].items():
            print(f"  {phase}: {status}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nSummary pack: {result['outputs']['summary_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
