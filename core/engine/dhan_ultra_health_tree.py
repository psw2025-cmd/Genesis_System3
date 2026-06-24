"""
Dhan Index Options - Ultra Health Tree

System dependency + health map.
Read-only health visualization.
SAFE MODE ONLY - No changes, observation only.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
ULTRA_OBS_DIR = REPORTS_DIR / "ultra_obs"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"

ULTRA_OBS_DIR.mkdir(parents=True, exist_ok=True)


def build_health_tree() -> Dict[str, Any]:
    """
    Build system health tree with dependencies.

    Read-only health visualization.

    Returns:
        Dict with health tree structure
    """
    print("=== ANGEL ONE INDEX OPTIONS - ULTRA HEALTH TREE ===")
    print("[INFO] SAFE MODE - Read-only health map\n")

    health_tree = {
        "generated_at": datetime.utcnow().isoformat(),
        "system_status": "SAFE_MODE",
        "components": {},
    }

    # Component 1: Models
    models_status = _check_models_health()
    health_tree["components"]["models"] = models_status

    # Component 2: Data Pipeline
    data_status = _check_data_pipeline_health()
    health_tree["components"]["data_pipeline"] = data_status

    # Component 3: Learning System
    learning_status = _check_learning_system_health()
    health_tree["components"]["learning_system"] = learning_status

    # Component 4: Live System
    live_status = _check_live_system_health()
    health_tree["components"]["live_system"] = live_status

    # Component 5: Configuration
    config_status = _check_config_health()
    health_tree["components"]["configuration"] = config_status

    # Overall health score
    all_scores = []
    for comp_name, comp_data in health_tree["components"].items():
        if "health_score" in comp_data:
            all_scores.append(comp_data["health_score"])

    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
    health_tree["overall_health_score"] = overall_score
    health_tree["overall_status"] = _classify_health_status(overall_score)

    return health_tree


def _check_models_health() -> Dict[str, Any]:
    """Check models health."""
    expected_models = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
    models_found = []
    models_missing = []

    for model_name in expected_models:
        model_file = MODELS_DIR / f"{model_name}_model.pkl"
        meta_file = MODELS_DIR / f"{model_name}_model_meta.json"
        if model_file.exists() and meta_file.exists():
            models_found.append(model_name)
        else:
            models_missing.append(model_name)

    health_score = len(models_found) / len(expected_models) * 100.0

    return {
        "status": "HEALTHY" if health_score == 100.0 else "DEGRADED",
        "health_score": health_score,
        "models_found": models_found,
        "models_missing": models_missing,
        "total_expected": len(expected_models),
        "total_found": len(models_found),
    }


def _check_data_pipeline_health() -> Dict[str, Any]:
    """Check data pipeline health."""
    training_csv = PROJECT_ROOT / "storage" / "training" / "dhan_index_options_training.csv"
    signals_csv = LIVE_DIR / "dhan_index_ai_signals.csv"
    trades_csv = LIVE_DIR / "dhan_index_ai_trades_plan.csv"

    checks = {
        "training_data": training_csv.exists(),
        "signals_data": signals_csv.exists(),
        "trades_data": trades_csv.exists(),
    }

    health_score = sum(checks.values()) / len(checks) * 100.0

    return {
        "status": "HEALTHY" if health_score == 100.0 else "DEGRADED",
        "health_score": health_score,
        "checks": checks,
    }


def _check_learning_system_health() -> Dict[str, Any]:
    """Check learning system health."""
    outcomes_csv = LEARNING_DIR / "real_outcomes.csv"
    signals_raw_csv = LEARNING_DIR / "real_signals_raw.csv"
    regime_log_csv = LEARNING_DIR / "market_regime_log.csv"

    checks = {
        "outcomes_log": outcomes_csv.exists(),
        "signals_raw": signals_raw_csv.exists(),
        "regime_log": regime_log_csv.exists(),
    }

    health_score = sum(checks.values()) / len(checks) * 100.0

    return {
        "status": "HEALTHY" if health_score >= 66.0 else "DEGRADED",
        "health_score": health_score,
        "checks": checks,
    }


def _check_live_system_health() -> Dict[str, Any]:
    """Check live system health."""
    try:
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG

        auto_execute = AUTOMATION_CONFIG.auto_execute_trades
        auto_pnl = AUTOMATION_CONFIG.auto_simulate_pnl
    except Exception:
        auto_execute = False
        auto_pnl = False

    # In safe mode, auto features should be disabled
    safe_mode_active = not auto_execute and not auto_pnl
    health_score = 100.0 if safe_mode_active else 50.0

    return {
        "status": "HEALTHY" if safe_mode_active else "WARNING",
        "health_score": health_score,
        "auto_execute": auto_execute,
        "auto_pnl": auto_pnl,
        "safe_mode_active": safe_mode_active,
    }


def _check_config_health() -> Dict[str, Any]:
    """Check configuration health."""
    try:
        from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS

        thresholds_ok = DEFAULT_THRESHOLDS.min_confidence > 0.0 and DEFAULT_THRESHOLDS.min_abs_score > 0.0
    except Exception:
        thresholds_ok = False

    health_score = 100.0 if thresholds_ok else 0.0

    return {
        "status": "HEALTHY" if thresholds_ok else "ERROR",
        "health_score": health_score,
        "thresholds_available": thresholds_ok,
    }


def _classify_health_status(score: float) -> str:
    """Classify overall health status."""
    if score >= 90.0:
        return "EXCELLENT"
    elif score >= 75.0:
        return "GOOD"
    elif score >= 50.0:
        return "FAIR"
    else:
        return "POOR"


def save_health_tree(health_tree: Dict[str, Any]) -> Path:
    """
    Save health tree to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = ULTRA_OBS_DIR / f"health_tree_{today}.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(health_tree, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    health_tree = build_health_tree()

    print("=== SYSTEM HEALTH TREE ===\n")

    # Overall
    print(f"Overall Health Score: {health_tree['overall_health_score']:.1f}%")
    print(f"Overall Status: {health_tree['overall_status']}")
    print(f"System Mode: {health_tree['system_status']}")

    # Components
    print("\n=== COMPONENT HEALTH ===")
    for comp_name, comp_data in health_tree["components"].items():
        status_icon = "✅" if comp_data.get("status") == "HEALTHY" else "⚠️"
        print(f"\n{status_icon} {comp_name.upper()}:")
        print(f"  Status: {comp_data.get('status', 'UNKNOWN')}")
        print(f"  Health Score: {comp_data.get('health_score', 0):.1f}%")

        if "models_found" in comp_data:
            print(f"  Models Found: {len(comp_data['models_found'])}/{comp_data['total_expected']}")
        if "checks" in comp_data:
            for check_name, check_value in comp_data["checks"].items():
                icon = "✅" if check_value else "❌"
                print(f"  {icon} {check_name}: {check_value}")

    # Save
    save_path = save_health_tree(health_tree)
    print(f"\n[SAVE] Health tree saved to: {save_path}")
    print("\n[NOTE] This is a read-only health map. No changes made.")


if __name__ == "__main__":
    main()
