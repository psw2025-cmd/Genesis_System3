"""
System3 Phase 114 - Live Session Health Snapshot

Summarize session health: PLANNED/SENT/FILLED trades, risk guard, kill switch.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import phase functions
try:
    from core.engine.system3_phase109_intraday_risk_guard import run_phase109
    from core.engine.system3_phase113_kill_switch_monitor import run_phase113
except ImportError as e:
    print(f"[PH114] ERROR: Failed to import phase modules: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
OUTPUT_MD = STORAGE_LIVE / "phase114_live_session_health.md"


def run_phase114(**kwargs) -> dict:
    """
    Generate live session health snapshot.

    Returns:
        dict: {
            "phase": 114,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Read ledger
        if LEDGER_CSV.exists():
            df = pd.read_csv(LEDGER_CSV)

            # Filter today's trades
            today_trades = df[df["timestamp"].astype(str).str.contains(today)]

            # Count by status
            status_counts = today_trades["status"].value_counts().to_dict()

            planned_count = status_counts.get("PLANNED", 0)
            sent_count = status_counts.get("SENT", 0)
            filled_count = status_counts.get("FILLED", 0)
            total_today = len(today_trades)
        else:
            status_counts = {}
            planned_count = 0
            sent_count = 0
            filled_count = 0
            total_today = 0

        # Get risk guard status
        try:
            risk_result = run_phase109()
            risk_status = risk_result.get("status", "UNKNOWN")
            risk_details = risk_result.get("details", "")
        except Exception as e:
            risk_status = "ERROR"
            risk_details = f"Risk guard check failed: {e}"
            errors.append(str(e))

        # Get kill switch status
        try:
            kill_result = run_phase113()
            kill_status = kill_result.get("status", "UNKNOWN")
            kill_active = kill_result.get("outputs", {}).get("kill_active", False)
        except Exception as e:
            kill_status = "ERROR"
            kill_active = True  # Assume active on error
            errors.append(str(e))

        # Generate Markdown report
        with OUTPUT_MD.open("w", encoding="utf-8") as f:
            f.write("# System3 Live Session Health Snapshot\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Today's Trades\n\n")
            f.write(f"- **Total Trades**: {total_today}\n")
            f.write(f"- **PLANNED**: {planned_count}\n")
            f.write(f"- **SENT**: {sent_count}\n")
            f.write(f"- **FILLED**: {filled_count}\n\n")

            f.write("## Risk Guard Status\n\n")
            f.write(f"- **Status**: {risk_status}\n")
            f.write(f"- **Details**: {risk_details}\n\n")

            f.write("## Kill Switch Status\n\n")
            f.write(f"- **Status**: {kill_status}\n")
            f.write(f"- **Active**: {kill_active}\n\n")

            if status_counts:
                f.write("## Status Distribution\n\n")
                f.write("| Status | Count |\n")
                f.write("|-------|-------|\n")
                for status, count in sorted(status_counts.items()):
                    f.write(f"| {status} | {count} |\n")
                f.write("\n")

        status = "OK" if not errors else "ERROR"
        details = f"Session health snapshot generated: {total_today} trades today"

        return {
            "phase": 114,
            "status": status,
            "details": details,
            "outputs": {
                "snapshot_path": str(OUTPUT_MD),
                "trades_today": total_today,
                "planned": planned_count,
                "sent": sent_count,
                "filled": filled_count,
                "risk_guard_status": risk_status,
                "kill_switch_active": kill_active,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 114,
            "status": "ERROR",
            "details": f"Phase 114 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 114 - LIVE SESSION HEALTH")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase114()

    print(f"Phase114: {result['details']}")

    if result["outputs"]:
        print(f"\nTrades today: {result['outputs']['trades_today']}")
        print(f"  PLANNED: {result['outputs']['planned']}")
        print(f"  SENT: {result['outputs']['sent']}")
        print(f"  FILLED: {result['outputs']['filled']}")
        print(f"\nRisk guard: {result['outputs']['risk_guard_status']}")
        print(f"Kill switch: {'ACTIVE' if result['outputs']['kill_switch_active'] else 'INACTIVE'}")
        print(f"\nSnapshot: {result['outputs']['snapshot_path']}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
