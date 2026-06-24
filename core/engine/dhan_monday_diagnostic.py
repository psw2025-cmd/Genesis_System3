"""
Dhan Index Options - Monday Morning Pre-Market Diagnostic

Runs comprehensive pre-market diagnostics before trading.
SAFE MODE ONLY - Read-only checks, no actions.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_pre_market_diagnostic() -> Dict[str, Any]:
    """
    Run comprehensive pre-market diagnostic.

    Returns:
        Dict with diagnostic results
    """
    print("=== ANGEL ONE INDEX OPTIONS - MONDAY MORNING PRE-MARKET DIAGNOSTIC ===")
    print("[INFO] SAFE MODE - Read-only checks only\n")

    diagnostics = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "status": "PASS",
        "warnings": [],
        "errors": [],
    }

    # Check 1: Models exist
    models_dir = PROJECT_ROOT / "core" / "models" / "dhan"
    models = list(models_dir.glob("*_model.pkl")) if models_dir.exists() else []
    diagnostics["checks"]["models"] = {
        "status": "PASS" if len(models) == 5 else "FAIL",
        "count": len(models),
        "expected": 5,
    }
    if len(models) != 5:
        diagnostics["warnings"].append(f"Expected 5 models, found {len(models)}")

    # Check 2: Configuration
    try:
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG
        from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS

        diagnostics["checks"]["config"] = {
            "status": "PASS",
            "confidence": DEFAULT_THRESHOLDS.min_confidence,
            "score": DEFAULT_THRESHOLDS.min_abs_score,
            "auto_execute": AUTOMATION_CONFIG.auto_execute_trades,
            "auto_pnl": AUTOMATION_CONFIG.auto_simulate_pnl,
        }
        if AUTOMATION_CONFIG.auto_execute_trades:
            diagnostics["errors"].append("AUTO-EXECUTE IS ENABLED - DISABLE BEFORE TRADING")
            diagnostics["status"] = "FAIL"
    except Exception as e:
        diagnostics["checks"]["config"] = {"status": "FAIL", "error": str(e)}
        diagnostics["errors"].append(f"Config check failed: {e}")
        diagnostics["status"] = "FAIL"

    # Check 3: Ultra-Mode status
    try:
        from core.engine.dhan_ultramode_prep import load_ultramode_config

        config = load_ultramode_config()
        diagnostics["checks"]["ultramode"] = {
            "status": "PASS" if config.read_only_mode and not config.auto_trade_execution else "FAIL",
            "read_only": config.read_only_mode,
            "auto_trade": config.auto_trade_execution,
        }
        if not config.read_only_mode or config.auto_trade_execution:
            diagnostics["errors"].append("ULTRA-MODE NOT IN SAFE MODE")
            diagnostics["status"] = "FAIL"
    except Exception as e:
        diagnostics["checks"]["ultramode"] = {"status": "WARN", "error": str(e)}
        diagnostics["warnings"].append(f"Ultra-Mode check failed: {e}")

    # Check 4: Data files
    signals_csv = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
    diagnostics["checks"]["data_files"] = {
        "status": "PASS" if signals_csv.exists() else "WARN",
        "signals_exists": signals_csv.exists(),
    }

    # Check 5: Broker connection — disabled (Dhan-only mode)
    diagnostics["checks"]["broker"] = {
        "status": "DISABLED",
        "available": False,
        "reason": "Dhan broker path disabled — System3 is Dhan-only",
    }
    diagnostics["warnings"].append("Dhan broker check skipped — Dhan-only mode")

    # Print results
    print("=== DIAGNOSTIC RESULTS ===\n")
    for check_name, check_result in diagnostics["checks"].items():
        status_icon = (
            "[OK]"
            if check_result.get("status") == "PASS"
            else "[WARN]" if check_result.get("status") == "WARN" else "[FAIL]"
        )
        print(f"{status_icon} {check_name.upper()}: {check_result.get('status', 'UNKNOWN')}")

    if diagnostics["warnings"]:
        print("\n=== WARNINGS ===")
        for warning in diagnostics["warnings"]:
            print(f"[WARN] {warning}")

    if diagnostics["errors"]:
        print("\n=== ERRORS ===")
        for error in diagnostics["errors"]:
            print(f"[ERROR] {error}")

    print(f"\n=== OVERALL STATUS: {diagnostics['status']} ===")

    return diagnostics


def main() -> None:
    """Main entry point."""
    result = run_pre_market_diagnostic()

    if result["status"] == "FAIL":
        print("\n[WARN] SYSTEM NOT READY FOR TRADING - FIX ERRORS ABOVE")
    else:
        print("\n[OK] SYSTEM READY FOR TRADING (DRY RUN MODE)")


if __name__ == "__main__":
    main()
