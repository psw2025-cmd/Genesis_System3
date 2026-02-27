"""
System3 Phase 133 - Master Safety & Kill-Switch

Computes safety flags and kill-switch state.
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
SAFETY_CONFIG_PATH = STORAGE_CONFIG / "system3_safety_config.json"
OUTPUT_JSON_PATH = STORAGE_CONFIG / "system3_master_safety_state.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase133_master_safety_report.md"


def run_phase133_master_safety_guard() -> Dict[str, Any]:
    """
    Compute master safety flags and kill-switch state.

    Returns:
        dict: {
            "phase": 133,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    kill_switch_reasons = []

    try:
        # Load master config
        master_config = {}
        if MASTER_CONFIG_PATH.exists():
            try:
                with MASTER_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    master_config = json.load(f)
            except Exception as e:
                errors.append(f"Error reading master config: {e}")

        # Load health snapshot
        health_snapshot = {}
        if HEALTH_SNAPSHOT_PATH.exists():
            try:
                with HEALTH_SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
                    health_snapshot = json.load(f)
            except Exception as e:
                errors.append(f"Error reading health snapshot: {e}")

        # Load safety config (optional)
        safety_config = {}
        if SAFETY_CONFIG_PATH.exists():
            try:
                with SAFETY_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    safety_config = json.load(f)
            except Exception:
                pass  # Optional file

        # Compute safety flags
        kill_switch_active = False

        # Check health status
        if health_snapshot.get("overall_status") == "ERROR":
            kill_switch_active = True
            kill_switch_reasons.append("Health snapshot shows ERROR status")

        # Check broker status
        broker_status = health_snapshot.get("broker", {}).get("status", "UNKNOWN")
        if broker_status == "ERROR":
            kill_switch_active = True
            kill_switch_reasons.append("Broker connectivity ERROR")

        # Check config flags
        live_trading_enabled = master_config.get("live_trading_enabled", False)
        if live_trading_enabled:
            # Force to False and note it
            kill_switch_reasons.append("Config attempted to enable live trading (clamped to False)")

        # Get max risk from config or default
        max_risk_percent_per_day = master_config.get("max_loss_percent", 1.0)
        if max_risk_percent_per_day > 5.0:
            kill_switch_active = True
            kill_switch_reasons.append(f"Max risk percent too high: {max_risk_percent_per_day}%")

        # Build safety state
        safety_state = {
            "timestamp": datetime.now().isoformat(),
            "kill_switch_active": kill_switch_active,
            "live_trading_allowed": False,  # MUST remain False
            "max_risk_percent_per_day": max_risk_percent_per_day,
            "kill_switch_reasons": kill_switch_reasons if kill_switch_active else [],
            "safety_flags": {
                "dry_run_only": True,
                "angel_one_only": True,
                "one_lot_only": True,
            },
        }

        # Save JSON
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(safety_state, f, indent=2)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Master Safety Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Safety Flags\n\n")
            f.write(f"- **kill_switch_active**: {kill_switch_active}\n")
            f.write(f"- **live_trading_allowed**: FALSE (MASTER MODE)\n")
            f.write(f"- **max_risk_percent_per_day**: {max_risk_percent_per_day}%\n")
            f.write(f"- **dry_run_only**: {safety_state['safety_flags']['dry_run_only']}\n")
            f.write(f"- **angel_one_only**: {safety_state['safety_flags']['angel_one_only']}\n")
            f.write(f"- **one_lot_only**: {safety_state['safety_flags']['one_lot_only']}\n")

            if kill_switch_reasons:
                f.write("\n## Kill-Switch Reasons\n\n")
                for reason in kill_switch_reasons:
                    f.write(f"- ⚠️ {reason}\n")
            else:
                f.write("\n## Kill-Switch Reasons\n\n")
                f.write("- None (system is safe)\n")

            f.write("\n## Summary\n\n")
            f.write("**LIVE_TRADING_ALLOWED: FALSE (MASTER MODE)**\n\n")
            if kill_switch_active:
                f.write("⚠️ **KILL SWITCH ACTIVE** - Future live trading (if ever enabled) should be blocked.\n")
            else:
                f.write("✅ **KILL SWITCH INACTIVE** - System is safe for DRY-RUN operations.\n")

        status = "OK" if not errors else "ERROR"
        details = f"Safety state computed: kill_switch={'ACTIVE' if kill_switch_active else 'INACTIVE'}"

        return {
            "phase": 133,
            "status": status,
            "details": details,
            "outputs": {
                "json_path": str(OUTPUT_JSON_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "kill_switch_active": kill_switch_active,
                "live_trading_allowed": False,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 133,
            "status": "ERROR",
            "details": f"Phase 133 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 133 - MASTER SAFETY & KILL-SWITCH")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase133_master_safety_guard()

    print(f"Phase133: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nKill Switch: {'ACTIVE' if result['outputs']['kill_switch_active'] else 'INACTIVE'}")
        print(f"Live Trading Allowed: {result['outputs']['live_trading_allowed']}")
        print(f"JSON: {result['outputs']['json_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
