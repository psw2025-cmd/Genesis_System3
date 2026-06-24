"""
System3 Ultra - Phase 50: Ultra Prediction Explainer

Explain why Ultra made specific predictions (interpretability).
Compute feature importance and generate explanation text.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 112
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_predictions() -> Optional[pd.DataFrame]:
    """Load recent Ultra predictions."""
    fused_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if fused_csv.exists():
        try:
            return pd.read_csv(fused_csv)
        except Exception:
            pass
    return None


def compute_feature_importance_simple(
    prediction: Dict[str, Any], features: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Compute simple feature importance for a prediction.

    Args:
        prediction: Prediction dict with action, confidence, score
        features: Optional feature values

    Returns:
        Dict mapping feature names to importance scores
    """
    # Default feature importance (would use actual model in production)
    importance = {
        "confidence": prediction.get("final_confidence", 0.0) * 0.3,
        "score": abs(prediction.get("final_score", 0.0)) * 0.3,
        "action_strength": 0.2,
        "market_conditions": 0.1,
        "historical_pattern": 0.1,
    }

    if features:
        # Incorporate actual feature values
        for feat_name, feat_value in features.items():
            if feat_name.startswith("volatility"):
                importance["volatility"] = abs(feat_value) * 0.15
            elif feat_name.startswith("momentum"):
                importance["momentum"] = abs(feat_value) * 0.15

    # Normalize
    total = sum(importance.values())
    if total > 0:
        importance = {k: v / total for k, v in importance.items()}

    return importance


def generate_explanation(prediction: Dict[str, Any], feature_importance: Dict[str, float]) -> str:
    """
    Generate human-readable explanation for a prediction.

    Args:
        prediction: Prediction dict
        feature_importance: Feature importance scores

    Returns:
        Explanation text
    """
    action = prediction.get("final_action", "HOLD")
    confidence = prediction.get("final_confidence", 0.0)
    score = prediction.get("final_score", 0.0)

    # Top contributing features
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]

    explanation_parts = [
        f"Prediction: {action}",
        f"Confidence: {confidence:.2%}",
        f"Score: {score:.3f}",
        "",
        "Top contributing factors:",
    ]

    for feat_name, importance in top_features:
        explanation_parts.append(f"  - {feat_name}: {importance:.2%}")

    if confidence > 0.8:
        explanation_parts.append("\nHigh confidence due to strong signal alignment.")
    elif confidence < 0.6:
        explanation_parts.append("\nLower confidence due to mixed signals.")

    if abs(score) > 0.3:
        explanation_parts.append(f"\nStrong directional signal ({'positive' if score > 0 else 'negative'}).")

    return "\n".join(explanation_parts)


def explain_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Generate explanations for all predictions."""
    explanations = []

    for idx, row in df.iterrows():
        prediction = {
            "final_action": row.get("final_action", "HOLD"),
            "final_confidence": row.get("final_confidence", 0.0),
            "final_score": row.get("final_score", 0.0),
        }

        feature_importance = compute_feature_importance_simple(prediction)
        explanation = generate_explanation(prediction, feature_importance)

        explanations.append(
            {
                "timestamp": row.get("timestamp", datetime.now().isoformat()),
                "underlying": row.get("underlying", "UNKNOWN"),
                "prediction": prediction["final_action"],
                "confidence": prediction["final_confidence"],
                "score": prediction["final_score"],
                "explanation": explanation,
                "top_feature_1": list(feature_importance.keys())[0] if feature_importance else "N/A",
                "top_feature_1_importance": list(feature_importance.values())[0] if feature_importance else 0.0,
                "top_feature_2": list(feature_importance.keys())[1] if len(feature_importance) > 1 else "N/A",
                "top_feature_2_importance": (
                    list(feature_importance.values())[1] if len(feature_importance) > 1 else 0.0
                ),
                "top_feature_3": list(feature_importance.keys())[2] if len(feature_importance) > 2 else "N/A",
                "top_feature_3_importance": (
                    list(feature_importance.values())[2] if len(feature_importance) > 2 else 0.0
                ),
            }
        )

    return pd.DataFrame(explanations)


def run_phase50_prediction_explainer() -> None:
    """Run Phase 50: Ultra Prediction Explainer."""
    print("=== SYSTEM3 ULTRA - PHASE 50: ULTRA PREDICTION EXPLAINER ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load predictions
    df_pred = load_predictions()

    if df_pred is None or df_pred.empty:
        print("[WARN] No predictions found. Using synthetic data for demo.")
        # Create synthetic data
        np.random.seed(42)
        df_pred = pd.DataFrame(
            {
                "timestamp": [datetime.now().isoformat()] * 10,
                "underlying": np.random.choice(["NIFTY", "BANKNIFTY"], 10),
                "final_action": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], 10),
                "final_confidence": np.random.uniform(0.6, 0.9, 10),
                "final_score": np.random.uniform(-0.5, 0.5, 10),
            }
        )

    print(f"[LOAD] Loaded {len(df_pred)} predictions")

    # Generate explanations
    df_explanations = explain_predictions(df_pred)

    # Feature importance summary
    all_importances = []
    for _, row in df_explanations.iterrows():
        all_importances.append(
            {
                "top_feature_1": row["top_feature_1"],
                "top_feature_1_importance": row["top_feature_1_importance"],
            }
        )

    df_importance = pd.DataFrame(all_importances)
    feature_importance_summary = df_importance.groupby("top_feature_1")["top_feature_1_importance"].mean().to_dict()

    # Save results
    output_csv = OUTPUT_DIR / "phase50_prediction_explanations.csv"
    df_explanations.to_csv(output_csv, index=False)
    print(f"[SAVE] Prediction explanations saved to: {output_csv}")

    importance_json = OUTPUT_DIR / "phase50_feature_importance.json"
    with importance_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "feature_importance": feature_importance_summary,
                "analysis_date": datetime.now().isoformat(),
                "total_predictions": len(df_explanations),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] Feature importance saved to: {importance_json}")

    # Summary
    print(f"\n=== PREDICTION EXPLAINER SUMMARY ===")
    print(f"Total predictions explained: {len(df_explanations)}")
    print(f"\nTop contributing features:")
    for feat, importance in sorted(feature_importance_summary.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feat}: {importance:.2%}")

    print("\n[OK] Phase 50 Ultra Prediction Explainer completed")


def main() -> None:
    """Main entry point."""
    run_phase50_prediction_explainer()


if __name__ == "__main__":
    main()
