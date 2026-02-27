"""
System3 Phase 113 - Kill Switch Monitor

Monitor kill switch file and return status.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

KILL_SWITCH_JSON = STORAGE_LIVE / "kill_switch.json"


def run_phase113(**kwargs) -> dict:
    """
    Check kill switch status.

    Returns:
        dict: {
            "phase": 113,
            "status": "OK" or "KILL",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    try:
        if KILL_SWITCH_JSON.exists():
            with KILL_SWITCH_JSON.open("r", encoding="utf-8") as f:
                kill_data = json.load(f)

            if kill_data.get("kill", False):
                return {
                    "phase": 113,
                    "status": "KILL",
                    "details": "Kill switch activated",
                    "outputs": {
                        "kill_switch_path": str(KILL_SWITCH_JSON),
                        "kill_active": True,
                    },
                    "errors": [],
                }

        return {
            "phase": 113,
            "status": "OK",
            "details": "Kill switch not activated",
            "outputs": {
                "kill_switch_path": str(KILL_SWITCH_JSON),
                "kill_active": False,
            },
            "errors": [],
        }

    except Exception as e:
        return {
            "phase": 113,
            "status": "KILL",  # Default to KILL on error for safety
            "details": f"Kill switch check failed: {e}",
            "outputs": {
                "kill_switch_path": str(KILL_SWITCH_JSON),
                "kill_active": True,  # Assume active on error
            },
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 113 - KILL SWITCH MONITOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase113()

    print(f"Phase113: {result['details']}")
    print(f"Status: {result['status']}")
    print(f"Kill switch active: {result['outputs']['kill_active']}")

    if result["status"] == "KILL":
        print("\n[WARNING] Kill switch is ACTIVE - execution should be aborted")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
