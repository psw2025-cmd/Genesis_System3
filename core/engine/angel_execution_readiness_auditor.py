"""
Angel One Index Options - Execution Readiness Auditor

Validates if system is safe to start (read-only).
SAFE MODE ONLY - Read-only validation.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
ULTRA_OBS_DIR = REPORTS_DIR / "ultra_obs"

ULTRA_OBS_DIR.mkdir(parents=True, exist_ok=True)


def audit_execution_readiness() -> Dict[str, Any]:
    """
    Audit system execution readiness.

    Read-only validation.

    Returns:
        Dict with audit results
    """
    print("=== ANGEL ONE INDEX OPTIONS - EXECUTION READINESS AUDITOR ===")
    print("[INFO] SAFE MODE - Read-only validation\n")

    audit_results = {
        "generated_at": datetime.utcnow().isoformat(),
        "checks": [],
        "overall_ready": False,
    }

    # Check 1: Models available
    expected_models = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
    models_ok = all((MODELS_DIR / f"{m}_model.pkl").exists() for m in expected_models)
    audit_results["checks"].append(
        {
            "check": "Models Available",
            "status": "PASS" if models_ok else "FAIL",
            "critical": True,
            "message": f"{len([m for m in expected_models if (MODELS_DIR / f'{m}_model.pkl').exists()])}/{len(expected_models)} models found",
        }
    )

    # Check 2: Safe mode active
    try:
        from core.engine.angel_automation_config import AUTOMATION_CONFIG

        safe_mode = not AUTOMATION_CONFIG.auto_execute_trades and not AUTOMATION_CONFIG.auto_simulate_pnl
    except Exception:
        safe_mode = False

    audit_results["checks"].append(
        {
            "check": "Safe Mode Active",
            "status": "PASS" if safe_mode else "FAIL",
            "critical": True,
            "message": "Auto-execute and auto-PnL disabled" if safe_mode else "Auto features may be enabled",
        }
    )

    # Check 3: Configuration loaded
    try:
        from core.engine.angel_trade_config import DEFAULT_THRESHOLDS

        config_ok = DEFAULT_THRESHOLDS.min_confidence > 0.0
    except Exception:
        config_ok = False

    audit_results["checks"].append(
        {
            "check": "Configuration Loaded",
            "status": "PASS" if config_ok else "FAIL",
            "critical": True,
            "message": "Trade thresholds available" if config_ok else "Configuration load failed",
        }
    )

    # Check 4: Directories exist
    required_dirs = [
        PROJECT_ROOT / "storage" / "live",
        PROJECT_ROOT / "storage" / "learning",
        PROJECT_ROOT / "storage" / "reports",
        PROJECT_ROOT / "storage" / "training",
    ]
    dirs_ok = all(d.exists() for d in required_dirs)
    audit_results["checks"].append(
        {
            "check": "Storage Directories",
            "status": "PASS" if dirs_ok else "FAIL",
            "critical": True,
            "message": f"{sum(1 for d in required_dirs if d.exists())}/{len(required_dirs)} directories exist",
        }
    )

    # Check 5: Training data available (optional)
    training_csv = PROJECT_ROOT / "storage" / "training" / "angel_index_options_training.csv"
    training_ok = training_csv.exists()
    audit_results["checks"].append(
        {
            "check": "Training Data Available",
            "status": "PASS" if training_ok else "WARN",
            "critical": False,
            "message": "Training CSV found" if training_ok else "Training CSV missing (optional)",
        }
    )

    # Overall readiness
    critical_checks = [c for c in audit_results["checks"] if c["critical"]]
    all_critical_pass = all(c["status"] == "PASS" for c in critical_checks)
    audit_results["overall_ready"] = all_critical_pass

    return audit_results


def save_audit_report(audit_results: Dict[str, Any]) -> Path:
    """
    Save audit report to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = ULTRA_OBS_DIR / f"execution_readiness_{today}.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    audit_results = audit_execution_readiness()

    print("=== EXECUTION READINESS AUDIT ===\n")

    for check in audit_results["checks"]:
        status_icon = "✅" if check["status"] == "PASS" else "⚠️" if check["status"] == "WARN" else "❌"
        critical_mark = " [CRITICAL]" if check["critical"] else ""
        print(f"{status_icon} {check['check']}{critical_mark}: {check['status']}")
        print(f"   {check['message']}")

    print(f"\n=== OVERALL READINESS ===")
    if audit_results["overall_ready"]:
        print("✅ System is READY for execution (safe mode)")
    else:
        print("❌ System is NOT READY. Critical checks failed.")

    # Save
    save_path = save_audit_report(audit_results)
    print(f"\n[SAVE] Audit report saved to: {save_path}")
    print("\n[NOTE] This is read-only validation. No changes made.")


if __name__ == "__main__":
    main()
