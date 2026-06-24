"""
Dhan Index Options - Failure Point Predictor

Predict weak points in pipeline.
Read-only analysis.
SAFE MODE ONLY - No changes, prediction only.
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


def predict_failure_points() -> Dict[str, Any]:
    """
    Predict weak points in pipeline.

    Read-only analysis.

    Returns:
        Dict with failure point predictions
    """
    print("=== ANGEL ONE INDEX OPTIONS - FAILURE POINT PREDICTOR ===")
    print("[INFO] SAFE MODE - Read-only prediction\n")

    failure_points = []

    # Check 1: Model availability
    expected_models = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
    missing_models = []
    for model_name in expected_models:
        model_file = MODELS_DIR / f"{model_name}_model.pkl"
        if not model_file.exists():
            missing_models.append(model_name)

    if missing_models:
        failure_points.append(
            {
                "component": "MODELS",
                "risk_level": "HIGH",
                "issue": f"Missing models: {', '.join(missing_models)}",
                "impact": "Prediction failures for affected underlyings",
                "recommendation": "Retrain missing models",
            }
        )

    # Check 2: Data pipeline continuity
    training_csv = PROJECT_ROOT / "storage" / "training" / "dhan_index_options_training.csv"
    signals_csv = LIVE_DIR / "dhan_index_ai_signals.csv"

    if not training_csv.exists():
        failure_points.append(
            {
                "component": "DATA_PIPELINE",
                "risk_level": "MEDIUM",
                "issue": "Training data CSV missing",
                "impact": "Cannot retrain models",
                "recommendation": "Regenerate training data",
            }
        )

    if not signals_csv.exists():
        failure_points.append(
            {
                "component": "LIVE_SYSTEM",
                "risk_level": "MEDIUM",
                "issue": "Signals CSV missing",
                "impact": "No signal history available",
                "recommendation": "Start live signal collection",
            }
        )

    # Check 3: Learning system data
    outcomes_csv = LEARNING_DIR / "real_outcomes.csv"
    if not outcomes_csv.exists():
        failure_points.append(
            {
                "component": "LEARNING_SYSTEM",
                "risk_level": "LOW",
                "issue": "Outcomes CSV missing",
                "impact": "Cannot analyze real performance",
                "recommendation": "Start outcome logging",
            }
        )

    # Check 4: Configuration consistency
    try:
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG

        if AUTOMATION_CONFIG.auto_execute_trades:
            failure_points.append(
                {
                    "component": "CONFIGURATION",
                    "risk_level": "CRITICAL",
                    "issue": "Auto-execute enabled (not in safe mode)",
                    "impact": "Real trades may execute automatically",
                    "recommendation": "Disable auto-execute for safe mode",
                }
            )
    except Exception as e:
        failure_points.append(
            {
                "component": "CONFIGURATION",
                "risk_level": "MEDIUM",
                "issue": f"Configuration load error: {e}",
                "impact": "Cannot verify safe mode status",
                "recommendation": "Check configuration files",
            }
        )

    # Check 5: File system health
    critical_dirs = [
        MODELS_DIR,
        LIVE_DIR,
        LEARNING_DIR,
        REPORTS_DIR,
    ]

    for dir_path in critical_dirs:
        if not dir_path.exists():
            failure_points.append(
                {
                    "component": "FILE_SYSTEM",
                    "risk_level": "HIGH",
                    "issue": f"Directory missing: {dir_path.name}",
                    "impact": "System cannot write data",
                    "recommendation": f"Create directory: {dir_path}",
                }
            )

    # Risk summary
    risk_counts = {
        "CRITICAL": len([fp for fp in failure_points if fp["risk_level"] == "CRITICAL"]),
        "HIGH": len([fp for fp in failure_points if fp["risk_level"] == "HIGH"]),
        "MEDIUM": len([fp for fp in failure_points if fp["risk_level"] == "MEDIUM"]),
        "LOW": len([fp for fp in failure_points if fp["risk_level"] == "LOW"]),
    }

    overall_risk = (
        "CRITICAL"
        if risk_counts["CRITICAL"] > 0
        else (
            "HIGH"
            if risk_counts["HIGH"] > 0
            else "MEDIUM" if risk_counts["MEDIUM"] > 0 else "LOW" if risk_counts["LOW"] > 0 else "NONE"
        )
    )

    return {
        "status": "SUCCESS",
        "overall_risk": overall_risk,
        "risk_counts": risk_counts,
        "failure_points": failure_points,
        "total_issues": len(failure_points),
    }


def save_failure_point_analysis(analysis: Dict[str, Any]) -> Path:
    """
    Save failure point analysis to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = ULTRA_OBS_DIR / f"failure_points_{today}.json"

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "analysis": analysis,
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    analysis = predict_failure_points()

    print("=== FAILURE POINT PREDICTION ===\n")

    print(f"Overall Risk: {analysis['overall_risk']}")
    print(f"Total Issues: {analysis['total_issues']}")

    print("\n=== RISK BREAKDOWN ===")
    for risk_level, count in analysis["risk_counts"].items():
        if count > 0:
            print(f"{risk_level}: {count}")

    if analysis["failure_points"]:
        print("\n=== FAILURE POINTS ===")
        for i, fp in enumerate(analysis["failure_points"], 1):
            risk_icon = (
                "🔴"
                if fp["risk_level"] == "CRITICAL"
                else "🟠" if fp["risk_level"] == "HIGH" else "🟡" if fp["risk_level"] == "MEDIUM" else "🟢"
            )
            print(f"\n{risk_icon} {i}. {fp['component']} ({fp['risk_level']})")
            print(f"   Issue: {fp['issue']}")
            print(f"   Impact: {fp['impact']}")
            print(f"   Recommendation: {fp['recommendation']}")
    else:
        print("\n✅ No failure points detected. System appears healthy.")

    # Save
    save_path = save_failure_point_analysis(analysis)
    print(f"\n[SAVE] Failure point analysis saved to: {save_path}")
    print("\n[NOTE] This is read-only prediction. No changes made.")


if __name__ == "__main__":
    main()
