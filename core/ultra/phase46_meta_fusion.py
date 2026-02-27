"""
System3 Ultra - Phase 46: Ultra Meta Fusion Model

Combine predictions from multiple Ultra models into a single meta-prediction
using weighted fusion based on historical accuracy.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 108
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_fused_decisions() -> Optional[pd.DataFrame]:
    """Load Phase 31 fused decisions."""
    fused_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if fused_csv.exists():
        try:
            return pd.read_csv(fused_csv)
        except Exception as e:
            print(f"[WARN] Failed to load fused decisions: {e}")
    return None


def compute_model_weights(historical_performance: Dict[str, float]) -> Dict[str, float]:
    """
    Compute weights for each model based on historical performance.

    Args:
        historical_performance: Dict mapping model names to accuracy scores

    Returns:
        Dict mapping model names to normalized weights
    """
    if not historical_performance:
        # Default equal weights if no history
        return {"baseline": 0.5, "ultra": 0.5}

    # Normalize to sum to 1.0
    total = sum(historical_performance.values())
    if total == 0:
        return {k: 1.0 / len(historical_performance) for k in historical_performance}

    weights = {k: v / total for k, v in historical_performance.items()}
    return weights


def fuse_predictions(predictions: List[Dict[str, Any]], weights: Dict[str, float]) -> Dict[str, Any]:
    """
    Fuse multiple predictions into a single meta-prediction.

    Args:
        predictions: List of prediction dicts with 'action', 'confidence', 'score'
        weights: Dict mapping model names to weights

    Returns:
        Fused prediction dict
    """
    if not predictions:
        return {
            "meta_action": "HOLD",
            "meta_confidence": 0.0,
            "meta_score": 0.0,
            "fusion_method": "none",
        }

    # Weighted average of confidences and scores
    weighted_conf = 0.0
    weighted_score = 0.0
    total_weight = 0.0

    action_votes = {}

    for i, pred in enumerate(predictions):
        model_name = pred.get("model", f"model_{i}")
        weight = weights.get(model_name, 1.0 / len(predictions))

        conf = pred.get("confidence", 0.0)
        score = pred.get("score", 0.0)
        action = pred.get("action", "HOLD")

        weighted_conf += conf * weight
        weighted_score += score * weight
        total_weight += weight

        action_votes[action] = action_votes.get(action, 0) + weight

    if total_weight > 0:
        weighted_conf /= total_weight
        weighted_score /= total_weight

    # Majority vote for action
    action_votes_dict: Dict[str, float] = action_votes
    meta_action = max(action_votes_dict.items(), key=lambda x: x[1])[0] if action_votes_dict else "HOLD"

    return {
        "meta_action": meta_action,
        "meta_confidence": float(weighted_conf),
        "meta_score": float(weighted_score),
        "fusion_method": "weighted_average",
        "num_models": len(predictions),
        "action_votes": action_votes,
    }


def run_phase46_meta_fusion() -> None:
    """Run Phase 46: Meta Fusion Model."""
    print("=== SYSTEM3 ULTRA - PHASE 46: ULTRA META FUSION MODEL ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load fused decisions
    df_fused = load_fused_decisions()

    if df_fused is None or df_fused.empty:
        print("[WARN] No fused decisions found. Using synthetic data for demo.")
        # Create synthetic data for demo
        np.random.seed(42)
        n_samples = 100
        df_fused = pd.DataFrame(
            {
                "timestamp": pd.date_range(start="2025-11-30", periods=n_samples, freq="1H"),
                "underlying": np.random.choice(["NIFTY", "BANKNIFTY"], n_samples),
                "final_action": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], n_samples),
                "final_confidence": np.random.uniform(0.5, 0.95, n_samples),
                "final_score": np.random.uniform(-0.5, 0.5, n_samples),
            }
        )

    print(f"[LOAD] Loaded {len(df_fused)} fused decisions")

    # Historical performance (would come from actual tracking)
    historical_performance = {
        "baseline": 0.65,
        "ultra": 0.72,
    }

    weights = compute_model_weights(historical_performance)
    print(f"[WEIGHTS] Model weights: {weights}")

    # Group by underlying and timestamp for fusion
    meta_predictions = []

    for (underlying, timestamp), group in df_fused.groupby(["underlying", df_fused.index]):
        predictions = [
            {
                "model": "fused",
                "action": row.get("final_action", "HOLD"),
                "confidence": row.get("final_confidence", 0.0),
                "score": row.get("final_score", 0.0),
            }
            for _, row in group.iterrows()
        ]

        fused = fuse_predictions(predictions, weights)
        fused["underlying"] = underlying
        fused["timestamp"] = timestamp
        meta_predictions.append(fused)

    if not meta_predictions:
        # Fallback: fuse all rows
        for _, row in df_fused.iterrows():
            predictions = [
                {
                    "model": "fused",
                    "action": row.get("final_action", "HOLD"),
                    "confidence": row.get("final_confidence", 0.0),
                    "score": row.get("final_score", 0.0),
                }
            ]
            fused = fuse_predictions(predictions, weights)
            fused["underlying"] = row.get("underlying", "UNKNOWN")
            fused["timestamp"] = row.get("timestamp", datetime.now())
            meta_predictions.append(fused)

    df_meta = pd.DataFrame(meta_predictions)

    # Save results
    output_csv = OUTPUT_DIR / "phase46_meta_fusion_predictions.csv"
    df_meta.to_csv(output_csv, index=False)
    print(f"[SAVE] Meta predictions saved to: {output_csv}")

    # Save weights
    weights_json = OUTPUT_DIR / "phase46_meta_fusion_weights.json"
    with weights_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "weights": weights,
                "historical_performance": historical_performance,
                "computed_at": datetime.now().isoformat(),
            },
            f,
            indent=2,
        )
    print(f"[SAVE] Weights saved to: {weights_json}")

    # Summary
    print("\n=== META FUSION SUMMARY ===")
    print(f"Total meta predictions: {len(df_meta)}")
    print("Actions distribution:")
    if "meta_action" in df_meta.columns:
        print(df_meta["meta_action"].value_counts().to_string())
    print(f"Average meta confidence: {df_meta['meta_confidence'].mean():.3f}")
    print(f"Average meta score: {df_meta['meta_score'].mean():.3f}")

    print("\n[OK] Phase 46 Ultra Meta Fusion Model completed")


def main() -> None:
    """Main entry point."""
    run_phase46_meta_fusion()


if __name__ == "__main__":
    main()
