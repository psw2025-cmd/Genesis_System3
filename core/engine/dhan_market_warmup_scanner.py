"""
Dhan Index Options - Market Warmup Scanner

Pre-market diagnostics and validation.
SAFE MODE ONLY - Read-only checks, no changes, no execution.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent


def scan_market_warmup() -> Dict[str, Any]:
    """
    Scan and validate system readiness for market open.

    Returns:
        Dict with warmup scan results
    """
    print("=== ANGEL ONE INDEX OPTIONS - MARKET WARMUP SCANNER ===")
    print("[INFO] SAFE MODE - Read-only validation, no changes\n")

    scan_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "status": "PASS",
        "warnings": [],
        "errors": [],
    }

    # Check 1: Directory structure
    required_dirs = [
        "core/engine",
        "core/models/dhan",
        "storage/live",
        "storage/training",
        "storage/config",
        "storage/reports",
        "storage/learning",
    ]

    dir_checks = {}
    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        exists = full_path.exists()
        dir_checks[dir_path] = exists
        if not exists:
            scan_results["warnings"].append(f"Directory missing: {dir_path}")

    scan_results["checks"]["directories"] = {
        "status": "PASS" if all(dir_checks.values()) else "WARN",
        "checked": dir_checks,
    }

    # Check 2: Model presence
    models_dir = PROJECT_ROOT / "core" / "models" / "dhan"
    expected_models = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
    model_checks = {}

    if models_dir.exists():
        for model_name in expected_models:
            model_file = models_dir / f"{model_name}_model.pkl"
            meta_file = models_dir / f"{model_name}_model_meta.json"
            exists = model_file.exists() and meta_file.exists()
            model_checks[model_name] = exists
            if not exists:
                scan_results["warnings"].append(f"Model missing: {model_name}")
    else:
        for model_name in expected_models:
            model_checks[model_name] = False
        scan_results["errors"].append("Models directory not found")
        scan_results["status"] = "FAIL"

    scan_results["checks"]["models"] = {
        "status": "PASS" if all(model_checks.values()) else "FAIL",
        "checked": model_checks,
    }

    # Check 3: Key files
    key_files = [
        "run_system3.py",
        "core/engine/dhan_live_ai_signals.py",
        "core/engine/dhan_trade_decision.py",
        "storage/training/dhan_index_options_training.csv",
    ]

    file_checks = {}
    for file_path in key_files:
        full_path = PROJECT_ROOT / file_path
        exists = full_path.exists()
        file_checks[file_path] = exists
        if not exists:
            scan_results["errors"].append(f"Key file missing: {file_path}")
            scan_results["status"] = "FAIL"

    scan_results["checks"]["key_files"] = {
        "status": "PASS" if all(file_checks.values()) else "FAIL",
        "checked": file_checks,
    }

    # Check 4: Configuration safety
    try:
        from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG
        from core.engine.dhan_ultramode_prep import load_ultramode_config

        ultramode = load_ultramode_config()

        config_safe = (
            not AUTOMATION_CONFIG.auto_execute_trades
            and not AUTOMATION_CONFIG.auto_simulate_pnl
            and ultramode.read_only_mode
            and not ultramode.auto_trade_execution
        )

        scan_results["checks"]["configuration"] = {
            "status": "PASS" if config_safe else "FAIL",
            "auto_execute": AUTOMATION_CONFIG.auto_execute_trades,
            "auto_pnl": AUTOMATION_CONFIG.auto_simulate_pnl,
            "read_only": ultramode.read_only_mode,
        }

        if not config_safe:
            scan_results["errors"].append("Configuration not in safe mode")
            scan_results["status"] = "FAIL"
    except Exception as e:
        scan_results["checks"]["configuration"] = {"status": "ERROR", "error": str(e)}
        scan_results["errors"].append(f"Config check failed: {e}")
        scan_results["status"] = "FAIL"

    # Print results
    print("=== WARMUP SCAN RESULTS ===\n")
    for check_name, check_result in scan_results["checks"].items():
        status = check_result.get("status", "UNKNOWN")
        icon = "[OK]" if status == "PASS" else "[WARN]" if status == "WARN" else "[FAIL]"
        print(f"{icon} {check_name.upper()}: {status}")

    if scan_results["warnings"]:
        print("\n=== WARNINGS ===")
        for warning in scan_results["warnings"]:
            print(f"[WARN] {warning}")

    if scan_results["errors"]:
        print("\n=== ERRORS ===")
        for error in scan_results["errors"]:
            print(f"[ERROR] {error}")

    print(f"\n=== OVERALL STATUS: {scan_results['status']} ===")

    return scan_results


def main() -> None:
    """Main entry point."""
    result = scan_market_warmup()

    if result["status"] == "FAIL":
        print("\n[WARN] SYSTEM NOT READY - FIX ERRORS ABOVE")
    elif result["warnings"]:
        print("\n[WARN] SYSTEM READY WITH WARNINGS - REVIEW ABOVE")
    else:
        print("\n[OK] SYSTEM READY FOR MARKET OPEN (SAFE MODE)")


if __name__ == "__main__":
    main()
