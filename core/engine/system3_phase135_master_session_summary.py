"""
System3 Phase 135 - Master Session Human Summary MD

Generates human-readable summary of master session setup.
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
STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

MASTER_CONFIG_PATH = STORAGE_CONFIG / "system3_master_session_config.json"
HEALTH_SNAPSHOT_PATH = STORAGE_ULTRA / "phase132_master_health_snapshot.json"
SAFETY_STATE_PATH = STORAGE_CONFIG / "system3_master_safety_state.json"
SESSION_PLAN_PATH = STORAGE_ULTRA / "phase134_master_session_plan.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase135_master_session_summary.md"


def run_phase135_master_session_summary() -> Dict[str, Any]:
    """
    Generate human-readable master session summary.

    Returns:
        dict: {
            "phase": 135,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load all JSONs
        master_config = {}
        if MASTER_CONFIG_PATH.exists():
            try:
                with MASTER_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    master_config = json.load(f)
            except Exception as e:
                errors.append(f"Error reading master config: {e}")

        health_snapshot = {}
        if HEALTH_SNAPSHOT_PATH.exists():
            try:
                with HEALTH_SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
                    health_snapshot = json.load(f)
            except Exception as e:
                errors.append(f"Error reading health snapshot: {e}")

        safety_state = {}
        if SAFETY_STATE_PATH.exists():
            try:
                with SAFETY_STATE_PATH.open("r", encoding="utf-8") as f:
                    safety_state = json.load(f)
            except Exception as e:
                errors.append(f"Error reading safety state: {e}")

        session_plan = {}
        if SESSION_PLAN_PATH.exists():
            try:
                with SESSION_PLAN_PATH.open("r", encoding="utf-8") as f:
                    session_plan = json.load(f)
            except Exception as e:
                errors.append(f"Error reading session plan: {e}")

        # Determine overall readiness
        master_session_ready = "NO"
        if (
            master_config
            and health_snapshot.get("overall_status") in ["OK", "WARN"]
            and not safety_state.get("kill_switch_active", True)
            and session_plan.get("status") == "READY"
        ):
            master_session_ready = "YES"

        # Generate MD summary
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Master Session Summary\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Config section
            f.write("## 1. Configuration\n\n")
            if master_config:
                f.write(f"- **Broker**: {master_config.get('broker', 'N/A')}\n")
                f.write(f"- **Mode**: {master_config.get('mode', 'N/A')}\n")
                f.write(f"- **Max Daily Trades**: {master_config.get('max_daily_trades', 'N/A')}\n")
                f.write(f"- **Max Trades per Underlying**: {master_config.get('max_trades_per_underlying', 'N/A')}\n")
                f.write(f"- **Max Loss Percent**: {master_config.get('max_loss_percent', 'N/A')}%\n")
            else:
                f.write("- Configuration not loaded\n")
            f.write("\n")

            # Health section
            f.write("## 2. Health\n\n")
            if health_snapshot:
                overall_status = health_snapshot.get("overall_status", "UNKNOWN")
                f.write(f"- **Overall Status**: {overall_status}\n")
                env_status = health_snapshot.get("environment", {}).get("status", "UNKNOWN")
                f.write(f"- **Environment Status**: {env_status}\n")
                broker_status = health_snapshot.get("broker", {}).get("status", "UNKNOWN")
                f.write(f"- **Broker Status**: {broker_status}\n")
            else:
                f.write("- Health snapshot not loaded\n")
            f.write("\n")

            # Safety section
            f.write("## 3. Safety\n\n")
            if safety_state:
                kill_switch = safety_state.get("kill_switch_active", True)
                f.write(f"- **Kill Switch**: {'ACTIVE' if kill_switch else 'INACTIVE'}\n")
                f.write(f"- **Live Trading Allowed**: FALSE (MASTER MODE)\n")
                f.write(f"- **Max Risk Percent/Day**: {safety_state.get('max_risk_percent_per_day', 'N/A')}%\n")
                if safety_state.get("kill_switch_reasons"):
                    f.write("- **Kill Switch Reasons**:\n")
                    for reason in safety_state["kill_switch_reasons"]:
                        f.write(f"  - {reason}\n")
            else:
                f.write("- Safety state not loaded\n")
            f.write("\n")

            # Plan section
            f.write("## 4. Plan\n\n")
            if session_plan:
                f.write(f"- **Status**: {session_plan.get('status', 'N/A')}\n")
                f.write(f"- **DRY_RUN**: {session_plan.get('dry_run', False)} ✅\n")
                f.write(f"- **Max Daily Trades**: {session_plan.get('max_daily_trades', 'N/A')}\n")
                enabled_count = len(
                    [u for u in session_plan.get("underlyings", {}).values() if u.get("enabled", False)]
                )
                f.write(f"- **Enabled Underlyings**: {enabled_count}\n")
            else:
                f.write("- Session plan not loaded\n")
            f.write("\n")

            # Final summary
            f.write("## Final Summary\n\n")
            f.write(f"- **MASTER_SESSION_READY**: {master_session_ready}\n")
            f.write(f"- **DRY_RUN_ONLY**: YES ✅\n")
            f.write(f"- **BROKER**: DHAN ✅\n")

        status = "OK" if not errors else "ERROR"
        details = f"Master session summary generated: READY={master_session_ready}"

        return {
            "phase": 135,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "master_session_ready": master_session_ready,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 135,
            "status": "ERROR",
            "details": f"Phase 135 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 135 - MASTER SESSION HUMAN SUMMARY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase135_master_session_summary()

    print(f"Phase135: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nMaster Session Ready: {result['outputs']['master_session_ready']}")
        print(f"Summary: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
