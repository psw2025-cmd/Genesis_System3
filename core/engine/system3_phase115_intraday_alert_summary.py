"""
System3 Phase 115 - Intraday Alert Summary (Text Only)

Generate plain text summary for WhatsApp/Email integration later.
No sending; only content creation.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import phase functions
try:
    from core.engine.system3_phase114_live_session_health import run_phase114
except ImportError as e:
    print(f"[PH115] ERROR: Failed to import phase modules: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

OUTPUT_TXT = STORAGE_LIVE / "phase115_intraday_alert_summary.txt"


def run_phase115(**kwargs) -> dict:
    """
    Generate intraday alert summary text.

    Returns:
        dict: {
            "phase": 115,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Get session health data
        health_result = run_phase114()
        health_outputs = health_result.get("outputs", {})

        # Generate text summary
        with OUTPUT_TXT.open("w", encoding="utf-8") as f:
            f.write("SYSTEM3 INTRADAY ALERT SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("TRADES TODAY:\n")
            f.write(f"  Total: {health_outputs.get('trades_today', 0)}\n")
            f.write(f"  PLANNED: {health_outputs.get('planned', 0)}\n")
            f.write(f"  SENT: {health_outputs.get('sent', 0)}\n")
            f.write(f"  FILLED: {health_outputs.get('filled', 0)}\n\n")

            f.write("RISK STATUS:\n")
            f.write(f"  Status: {health_outputs.get('risk_guard_status', 'UNKNOWN')}\n\n")

            f.write("KILL SWITCH:\n")
            kill_active = health_outputs.get("kill_switch_active", False)
            f.write(f"  Active: {'YES' if kill_active else 'NO'}\n\n")

            if kill_active:
                f.write("⚠️ WARNING: Kill switch is ACTIVE\n")

            if health_outputs.get("risk_guard_status") == "BLOCK":
                f.write("⚠️ WARNING: Risk guard has BLOCKED trading\n")

        status = "OK"
        details = "Intraday alert summary generated"

        return {
            "phase": 115,
            "status": status,
            "details": details,
            "outputs": {
                "summary_path": str(OUTPUT_TXT),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 115,
            "status": "ERROR",
            "details": f"Phase 115 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 115 - INTRADAY ALERT SUMMARY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase115()

    print(f"Phase115: {result['details']}")
    if result["outputs"]:
        print(f"Summary file: {result['outputs']['summary_path']}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
