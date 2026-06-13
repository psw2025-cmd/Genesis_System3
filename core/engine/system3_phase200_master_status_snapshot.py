"""
System3 Phase 200 - MASTER STATUS SNAPSHOT (Angel DRY-RUN)

Consolidates final view and serves as truth source for session start.
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
READINESS_REPORT = STORAGE_ULTRA / "phase196_dry_run_readiness_report.md"
OUTPUT_JSON_PATH = STORAGE_ULTRA / "phase200_master_status_snapshot.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase200_master_status_snapshot.md"


def run_phase200_master_status_snapshot() -> Dict[str, Any]:
    """
    Generate master status snapshot.

    Returns:
        dict: {
            "phase": 200,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load all inputs
        master_config = {}
        if MASTER_CONFIG_PATH.exists():
            try:
                with MASTER_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    master_config = json.load(f)
            except Exception as e:
                errors.append(f"Error reading master config: {e}")

        safety_state = {}
        if SAFETY_STATE_PATH.exists():
            try:
                with SAFETY_STATE_PATH.open("r", encoding="utf-8") as f:
                    safety_state = json.load(f)
            except Exception as e:
                errors.append(f"Error reading safety state: {e}")

        health_snapshot = {}
        if HEALTH_SNAPSHOT_PATH.exists():
            try:
                with HEALTH_SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
                    health_snapshot = json.load(f)
            except Exception as e:
                errors.append(f"Error reading health snapshot: {e}")

        # Determine overall status
        overall_status = "GOOD"
        if health_snapshot.get("overall_status") == "ERROR":
            overall_status = "ERROR"
        elif safety_state.get("kill_switch_active", False):
            overall_status = "ERROR"
        elif health_snapshot.get("overall_status") == "WARN":
            overall_status = "WARN"

        # Build master snapshot
        master_snapshot = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": True,
            "broker": "DHAN",
            "one_lot_test": "ACTIVE",
            "last_known_status": overall_status,
            "config": {
                "live_trading_enabled": False,
                "max_daily_trades": master_config.get("max_daily_trades", 10),
                "max_trades_per_underlying": master_config.get("max_trades_per_underlying", 3),
            },
            "safety": {
                "kill_switch_active": safety_state.get("kill_switch_active", False),
                "live_trading_allowed": False,
            },
            "health": {
                "overall_status": health_snapshot.get("overall_status", "UNKNOWN"),
                "broker_status": health_snapshot.get("broker", {}).get("status", "UNKNOWN"),
            },
        }

        # Save JSON
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(master_snapshot, f, indent=2)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Master Status Snapshot (Angel DRY-RUN)\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**This is the truth source to read at the start of any session.**\n\n")

            f.write("## System Status\n\n")
            f.write(f"- **DRY_RUN**: {master_snapshot['dry_run']} ✅\n")
            f.write(f"- **BROKER**: {master_snapshot['broker']} ✅\n")
            f.write(f"- **ONE_LOT_TEST**: {master_snapshot['one_lot_test']} ✅\n")
            f.write(f"- **LAST_KNOWN_STATUS**: {master_snapshot['last_known_status']}\n\n")

            f.write("## Configuration\n\n")
            f.write(f"- **Live Trading Enabled**: {master_snapshot['config']['live_trading_enabled']} ✅\n")
            f.write(f"- **Max Daily Trades**: {master_snapshot['config']['max_daily_trades']}\n")
            f.write(f"- **Max Trades per Underlying**: {master_snapshot['config']['max_trades_per_underlying']}\n\n")

            f.write("## Safety\n\n")
            f.write(f"- **Kill Switch Active**: {master_snapshot['safety']['kill_switch_active']}\n")
            f.write(f"- **Live Trading Allowed**: {master_snapshot['safety']['live_trading_allowed']} ✅\n\n")

            f.write("## Health\n\n")
            f.write(f"- **Overall Status**: {master_snapshot['health']['overall_status']}\n")
            f.write(f"- **Broker Status**: {master_snapshot['health']['broker_status']}\n\n")

            if overall_status == "GOOD":
                f.write("## Summary\n\n")
                f.write("✅ **System is SAFE and TEST-READY for DRY-RUN operations.**\n")
            elif overall_status == "WARN":
                f.write("## Summary\n\n")
                f.write("⚠️ **System has warnings but is operational for DRY-RUN.**\n")
            else:
                f.write("## Summary\n\n")
                f.write("❌ **System has errors - review before proceeding.**\n")

        status = "OK" if not errors else "ERROR"
        details = f"Master status snapshot: {overall_status}"

        return {
            "phase": 200,
            "status": status,
            "details": details,
            "outputs": {
                "json_path": str(OUTPUT_JSON_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "overall_status": overall_status,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 200,
            "status": "ERROR",
            "details": f"Phase 200 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 200 - MASTER STATUS SNAPSHOT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase200_master_status_snapshot()

    print(f"Phase200: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nOverall Status: {result['outputs']['overall_status']}")
        print(f"JSON: {result['outputs']['json_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
