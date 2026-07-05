"""
System3 Phase 134 - Master DRY-RUN Session Plan

Builds session-level plan for DRY-RUN operations.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

MASTER_CONFIG_PATH = STORAGE_CONFIG / "system3_master_session_config.json"
SAFETY_STATE_PATH = STORAGE_CONFIG / "system3_master_safety_state.json"
OUTPUT_JSON_PATH = STORAGE_ULTRA / "phase134_master_session_plan.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase134_master_session_plan.md"

# Supported underlyings
SUPPORTED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def run_phase134_master_session_plan() -> Dict[str, Any]:
    """
    Build master DRY-RUN session plan.

    Returns:
        dict: {
            "phase": 134,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load master config
        master_config = {}
        if MASTER_CONFIG_PATH.exists():
            try:
                with MASTER_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    master_config = json.load(f)
            except Exception as e:
                errors.append(f"Error reading master config: {e}")

        # Load safety state
        safety_state = {}
        kill_switch_active = False
        if SAFETY_STATE_PATH.exists():
            try:
                with SAFETY_STATE_PATH.open("r", encoding="utf-8") as f:
                    safety_state = json.load(f)
                    kill_switch_active = safety_state.get("kill_switch_active", False)
            except Exception as e:
                errors.append(f"Error reading safety state: {e}")

        # Build session plan
        if kill_switch_active:
            plan_status = "ABORTED"
            plan_details = "Kill switch is active"
        else:
            plan_status = "READY"
            plan_details = "System ready for DRY-RUN session"

        # Get limits from config
        max_daily_trades = master_config.get("max_daily_trades", 10)
        max_trades_per_underlying = master_config.get("max_trades_per_underlying", 3)

        # Build underlying configs
        underlyings_config = {}
        for underlying in SUPPORTED_UNDERLYINGS:
            # Default all enabled (can be overridden by config)
            enabled = master_config.get("underlyings", {}).get(underlying, {}).get("enabled", True)
            underlyings_config[underlying] = {
                "enabled": enabled,
                "max_trades": max_trades_per_underlying,
            }

        # Build session plan
        session_plan = {
            "status": plan_status,
            "dry_run": True,  # Always True
            "timestamp": datetime.now().isoformat(),
            "underlyings": underlyings_config,
            "max_trades_per_underlying": max_trades_per_underlying,
            "max_daily_trades": max_daily_trades,
            "session_limits": {
                "max_cycles": 100,  # Default max cycles
                "max_indices_to_watch": len([u for u in underlyings_config.values() if u["enabled"]]),
            },
        }

        # Save JSON
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(session_plan, f, indent=2)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Master Session Plan\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Session Status\n\n")
            f.write(f"- **Status**: {plan_status}\n")
            f.write(f"- **Details**: {plan_details}\n")
            f.write(f"- **DRY_RUN**: {session_plan['dry_run']} ✅\n\n")

            f.write("## Session Limits\n\n")
            f.write(f"- **Max Daily Trades**: {max_daily_trades}\n")
            f.write(f"- **Max Trades per Underlying**: {max_trades_per_underlying}\n")
            f.write(f"- **Max Cycles**: {session_plan['session_limits']['max_cycles']}\n")
            f.write(f"- **Max Indices to Watch**: {session_plan['session_limits']['max_indices_to_watch']}\n\n")

            f.write("## Underlyings Configuration\n\n")
            f.write("| Underlying | Enabled | Max Trades |\n")
            f.write("|------------|---------|------------|\n")
            for underlying, config in underlyings_config.items():
                enabled_str = "✅ YES" if config["enabled"] else "❌ NO"
                f.write(f"| {underlying} | {enabled_str} | {config['max_trades']} |\n")

        status = "OK" if not errors else "ERROR"
        details = f"Session plan created: {plan_status}"

        return {
            "phase": 134,
            "status": status,
            "details": details,
            "outputs": {
                "json_path": str(OUTPUT_JSON_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "plan_status": plan_status,
                "dry_run": session_plan["dry_run"],
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 134,
            "status": "ERROR",
            "details": f"Phase 134 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 134 - MASTER DRY-RUN SESSION PLAN")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase134_master_session_plan()

    print(f"Phase134: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nPlan Status: {result['outputs']['plan_status']}")
        print(f"DRY_RUN: {result['outputs']['dry_run']}")
        print(f"JSON: {result['outputs']['json_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
