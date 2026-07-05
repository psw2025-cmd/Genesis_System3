"""
System3 Phase 119 - Safety Audit for Live Trading

Comprehensive safety check: LIVE_TRADING_ENABLED, risk guard, kill switch, trade counts.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import config
try:
    from config.live_trade_config import LIVE_TRADING_ENABLED, MAX_LIVE_TRADES_PER_DAY
except ImportError as e:
    print(f"[PH119] ERROR: Failed to import live_trade_config: {e}")
    sys.exit(1)

# Import phase functions
try:
    from core.engine.system3_phase109_intraday_risk_guard import run_phase109
    from core.engine.system3_phase113_kill_switch_monitor import run_phase113
except ImportError as e:
    print(f"[PH119] ERROR: Failed to import phase modules: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

OUTPUT_MD = STORAGE_LIVE / "phase119_live_safety_audit.md"


def run_phase119(**kwargs) -> dict:
    """
    Perform comprehensive safety audit.

    Returns:
        dict: {
            "phase": 119,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    warnings = []
    audit_items = {}

    try:
        # Check LIVE_TRADING_ENABLED
        audit_items["live_trading_enabled"] = LIVE_TRADING_ENABLED
        if LIVE_TRADING_ENABLED:
            warnings.append("LIVE_TRADING_ENABLED is True - real trading is active")
        else:
            audit_items["live_trading_status"] = "SAFE (disabled)"

        # Check risk guard
        try:
            risk_result = run_phase109()
            audit_items["risk_guard_status"] = risk_result.get("status", "UNKNOWN")
            audit_items["risk_guard_details"] = risk_result.get("details", "")
            audit_items["trades_today"] = risk_result.get("outputs", {}).get("trades_today", 0)
            audit_items["max_trades_per_day"] = MAX_LIVE_TRADES_PER_DAY

            if risk_result.get("status") == "BLOCK":
                warnings.append(f"Risk guard blocked: {risk_result.get('details')}")
        except Exception as e:
            errors.append(f"Risk guard check failed: {e}")
            audit_items["risk_guard_status"] = "ERROR"

        # Check kill switch
        try:
            kill_result = run_phase113()
            audit_items["kill_switch_active"] = kill_result.get("outputs", {}).get("kill_active", False)
            audit_items["kill_switch_status"] = kill_result.get("status", "UNKNOWN")

            if audit_items["kill_switch_active"]:
                warnings.append("Kill switch is ACTIVE")
        except Exception as e:
            errors.append(f"Kill switch check failed: {e}")
            audit_items["kill_switch_status"] = "ERROR"

        # Generate Markdown report
        with OUTPUT_MD.open("w", encoding="utf-8") as f:
            f.write("# System3 Live Trading Safety Audit\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Configuration\n\n")
            f.write(f"- **LIVE_TRADING_ENABLED**: {LIVE_TRADING_ENABLED}\n")
            f.write(f"- **Status**: {'⚠️ ACTIVE' if LIVE_TRADING_ENABLED else '✅ SAFE (disabled)'}\n\n")

            f.write("## Risk Guard\n\n")
            f.write(f"- **Status**: {audit_items.get('risk_guard_status', 'UNKNOWN')}\n")
            f.write(f"- **Details**: {audit_items.get('risk_guard_details', 'N/A')}\n")
            f.write(
                f"- **Trades Today**: {audit_items.get('trades_today', 0)} / {audit_items.get('max_trades_per_day', 0)}\n\n"
            )

            f.write("## Kill Switch\n\n")
            f.write(f"- **Status**: {audit_items.get('kill_switch_status', 'UNKNOWN')}\n")
            f.write(f"- **Active**: {'⚠️ YES' if audit_items.get('kill_switch_active', False) else '✅ NO'}\n\n")

            if warnings:
                f.write("## Warnings\n\n")
                for warning in warnings:
                    f.write(f"- ⚠️ {warning}\n")
                f.write("\n")

            if errors:
                f.write("## Errors\n\n")
                for error in errors:
                    f.write(f"- ❌ {error}\n")
                f.write("\n")

            # Overall assessment
            f.write("## Overall Assessment\n\n")
            if (
                LIVE_TRADING_ENABLED
                and not audit_items.get("kill_switch_active", False)
                and audit_items.get("risk_guard_status") != "BLOCK"
            ):
                f.write("✅ **System is OPERATIONAL**\n")
            elif LIVE_TRADING_ENABLED:
                f.write("⚠️ **System is OPERATIONAL but with SAFETY WARNINGS**\n")
            else:
                f.write("✅ **System is SAFE (live trading disabled)**\n")

        status = "OK" if not errors else "ERROR"
        details = "Safety audit completed"
        if warnings:
            details += f" with {len(warnings)} warning(s)"

        return {
            "phase": 119,
            "status": status,
            "details": details,
            "outputs": {
                "audit_path": str(OUTPUT_MD),
                "live_trading_enabled": LIVE_TRADING_ENABLED,
                "risk_guard_status": audit_items.get("risk_guard_status", "UNKNOWN"),
                "kill_switch_active": audit_items.get("kill_switch_active", False),
                "warnings": warnings,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 119,
            "status": "ERROR",
            "details": f"Phase 119 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 119 - LIVE SAFETY AUDIT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase119()

    print(f"Phase119: {result['details']}")
    print(f"\nLive trading: {'ENABLED' if result['outputs']['live_trading_enabled'] else 'DISABLED'}")
    print(f"Risk guard: {result['outputs']['risk_guard_status']}")
    print(f"Kill switch: {'ACTIVE' if result['outputs']['kill_switch_active'] else 'INACTIVE'}")

    if result["outputs"].get("warnings"):
        print(f"\nWarnings ({len(result['outputs']['warnings'])}):")
        for warning in result["outputs"]["warnings"]:
            print(f"  [WARN] {warning}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nAudit report: {result['outputs']['audit_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
