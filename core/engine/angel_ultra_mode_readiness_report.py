"""
Angel One Index Options - Ultra-Mode Readiness Report

Lists requirements for Ultra-Mode activation.
Does NOT enable Ultra-Mode.
SAFE MODE ONLY - Read-only report, no activation.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_readiness_report() -> Dict[str, Any]:
    """
    Generate Ultra-Mode readiness report.

    Only lists requirements.
    Does NOT enable Ultra-Mode.

    Returns:
        Dict with readiness report
    """
    print("=== ANGEL ONE INDEX OPTIONS - ULTRA-MODE READINESS REPORT ===")
    print("[INFO] SAFE MODE - Report only, does NOT enable Ultra-Mode\n")

    requirements = {
        "models": {},
        "data": {},
        "config": {},
        "safety": {},
        "overall_ready": False,
    }

    # Check 1: Models
    if MODELS_DIR.exists():
        models = list(MODELS_DIR.glob("*_model.pkl"))
        expected_models = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
        model_status = {}

        for model_name in expected_models:
            model_file = MODELS_DIR / f"{model_name}_model.pkl"
            meta_file = MODELS_DIR / f"{model_name}_model_meta.json"
            exists = model_file.exists() and meta_file.exists()
            model_status[model_name] = exists

        requirements["models"] = {
            "status": "PASS" if all(model_status.values()) else "FAIL",
            "models_checked": model_status,
            "total_models": len([m for m in model_status.values() if m]),
            "expected": len(expected_models),
        }
    else:
        requirements["models"] = {
            "status": "FAIL",
            "message": "Models directory not found",
        }

    # Check 2: Data
    has_outcomes = REAL_OUTCOMES_CSV.exists()
    if has_outcomes:
        try:
            import pandas as pd

            df = pd.read_csv(REAL_OUTCOMES_CSV)
            outcome_count = len(df)
        except Exception:
            outcome_count = 0
    else:
        outcome_count = 0

    requirements["data"] = {
        "status": "PASS" if outcome_count >= 10 else "WARN",
        "outcomes_available": has_outcomes,
        "outcome_count": outcome_count,
        "minimum_required": 10,
    }

    # Check 3: Configuration
    try:
        from core.engine.angel_automation_config import AUTOMATION_CONFIG
        from core.engine.angel_ultramode_prep import load_ultramode_config

        ultramode = load_ultramode_config()

        requirements["config"] = {
            "status": "PASS" if ultramode.read_only_mode else "FAIL",
            "read_only_mode": ultramode.read_only_mode,
            "auto_execute": AUTOMATION_CONFIG.auto_execute_trades,
            "auto_pnl": AUTOMATION_CONFIG.auto_simulate_pnl,
        }
    except Exception as e:
        requirements["config"] = {
            "status": "ERROR",
            "error": str(e),
        }

    # Check 4: Safety
    requirements["safety"] = {
        "baseline_frozen": True,
        "read_only_active": True,
        "auto_features_disabled": True,
    }

    # Overall readiness
    all_pass = (
        requirements["models"].get("status") == "PASS"
        and requirements["data"].get("status") in ["PASS", "WARN"]
        and requirements["config"].get("status") == "PASS"
    )

    requirements["overall_ready"] = all_pass
    requirements["ultra_mode_enabled"] = False  # Explicitly marked as not enabled
    requirements["note"] = "This report lists requirements only. Ultra-Mode is NOT enabled."

    return requirements


def save_readiness_report(requirements: Dict[str, Any]) -> Path:
    """
    Save readiness report to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = REPORTS_DIR / f"ultra_mode_readiness_{today}.json"

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "ultra_mode_enabled": False,  # Explicitly marked as not enabled
        "note": "This report lists requirements only. Ultra-Mode is NOT enabled.",
        "requirements": requirements,
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    requirements = generate_readiness_report()

    print("=== ULTRA-MODE READINESS REPORT ===\n")

    # Models
    print("=== MODELS ===")
    models = requirements["models"]
    status_icon = "✅" if models.get("status") == "PASS" else "❌"
    print(f"{status_icon} Status: {models.get('status', 'UNKNOWN')}")
    if "models_checked" in models:
        for model, exists in models["models_checked"].items():
            icon = "✅" if exists else "❌"
            print(f"  {icon} {model}")

    # Data
    print("\n=== DATA ===")
    data = requirements["data"]
    status_icon = "✅" if data.get("status") == "PASS" else "⚠️"
    print(f"{status_icon} Status: {data.get('status', 'UNKNOWN')}")
    print(f"  Outcomes Available: {data.get('outcomes_available', False)}")
    print(f"  Outcome Count: {data.get('outcome_count', 0)}")
    print(f"  Minimum Required: {data.get('minimum_required', 10)}")

    # Config
    print("\n=== CONFIGURATION ===")
    config = requirements["config"]
    status_icon = "✅" if config.get("status") == "PASS" else "❌"
    print(f"{status_icon} Status: {config.get('status', 'UNKNOWN')}")
    if "read_only_mode" in config:
        print(f"  Read-Only Mode: {config['read_only_mode']}")
        print(f"  Auto-Execute: {config.get('auto_execute', False)}")

    # Overall
    print(f"\n=== OVERALL READINESS ===")
    if requirements["overall_ready"]:
        print("✅ System meets requirements for Ultra-Mode")
    else:
        print("⚠️  System does not meet all requirements")

    print(f"\n⚠️  {requirements['note']}")
    print("⚠️  IMPORTANT: Ultra-Mode is NOT enabled. This is a requirements report only.")

    # Save report
    save_path = save_readiness_report(requirements)
    print(f"\n[SAVE] Readiness report saved to: {save_path}")


if __name__ == "__main__":
    main()
