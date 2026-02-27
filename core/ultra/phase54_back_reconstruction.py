"""
System3 Ultra - Phase 54: Real Outcome Back-Reconstruction

Reconstruct what should have happened based on actual outcomes.
Compare actual vs optimal decisions and generate "what-if" analysis.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 116
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_predictions_and_outcomes() -> Optional[pd.DataFrame]:
    """Load predictions and actual outcomes."""
    # Load predictions
    predictions_path = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    df_pred = None
    if predictions_path.exists():
        try:
            df_pred = pd.read_csv(predictions_path)
        except Exception:
            pass

    # Load outcomes
    outcomes_path = LEARNING_DIR / "real_outcomes.csv"
    df_outcomes = None
    if outcomes_path.exists():
        try:
            df_outcomes = pd.read_csv(outcomes_path)
        except Exception:
            pass

    # Merge if both exist
    if df_pred is not None and df_outcomes is not None and not df_outcomes.empty:
        # Simple merge on timestamp or index
        if "timestamp" in df_pred.columns and "timestamp" in df_outcomes.columns:
            df_pred["timestamp"] = pd.to_datetime(df_pred["timestamp"])
            df_outcomes["timestamp"] = pd.to_datetime(df_outcomes["timestamp"])
            df_merged = pd.merge_asof(
                df_pred.sort_values("timestamp"),
                df_outcomes.sort_values("timestamp"),
                on="timestamp",
                direction="nearest",
                suffixes=("_pred", "_outcome"),
            )
            return df_merged

    return df_pred if df_pred is not None else df_outcomes


def reconstruct_optimal_decision(
    prediction: str, outcome: str, confidence: float, actual_pnl: Optional[float] = None
) -> Dict[str, Any]:
    """
    Reconstruct what the optimal decision should have been.

    Args:
        prediction: What was predicted
        outcome: What actually happened
        confidence: Prediction confidence
        actual_pnl: Actual PnL (if available)

    Returns:
        Reconstruction dict with optimal decision
    """
    # If outcome is known, optimal decision is clear
    if outcome in ["BUY_CE", "BUY_PE"]:
        optimal_action = outcome
        optimal_confidence = 1.0 if actual_pnl and actual_pnl > 0 else 0.8
    elif outcome == "HOLD":
        optimal_action = "HOLD"
        optimal_confidence = 0.7
    else:
        # Unknown outcome - keep prediction
        optimal_action = prediction
        optimal_confidence = confidence

    # Compare actual vs optimal
    was_correct = prediction == optimal_action
    confidence_gap = abs(confidence - optimal_confidence)

    return {
        "predicted_action": prediction,
        "optimal_action": optimal_action,
        "actual_outcome": outcome,
        "was_correct": was_correct,
        "predicted_confidence": confidence,
        "optimal_confidence": optimal_confidence,
        "confidence_gap": confidence_gap,
        "actual_pnl": actual_pnl if actual_pnl is not None else None,
        "reconstruction_note": "Optimal decision based on known outcome" if outcome != "UNKNOWN" else "Outcome unknown",
    }


def run_phase54_back_reconstruction() -> None:
    """Run Phase 54: Real Outcome Back-Reconstruction."""
    print("=== SYSTEM3 ULTRA - PHASE 54: REAL OUTCOME BACK-RECONSTRUCTION ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load predictions and outcomes
    df_data = load_predictions_and_outcomes()

    if df_data is None or df_data.empty:
        print("[WARN] No prediction/outcome data found. Using synthetic data for demo.")
        # Create synthetic data
        np.random.seed(42)
        df_data = pd.DataFrame(
            {
                "final_action": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], 20),
                "final_confidence": np.random.uniform(0.6, 0.9, 20),
                "outcome": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], 20),
                "pnl_pct": np.random.uniform(-2, 3, 20),
            }
        )

    print(f"[LOAD] Loaded {len(df_data)} prediction/outcome pairs")

    # Reconstruct optimal decisions
    reconstructions = []
    what_if_scenarios = []

    for idx, row in df_data.iterrows():
        prediction = row.get("final_action", row.get("predicted_action", "HOLD"))
        outcome = row.get("outcome", row.get("actual_outcome", "UNKNOWN"))
        confidence = row.get("final_confidence", row.get("predicted_confidence", 0.0))
        pnl = row.get("pnl_pct", row.get("actual_pnl", None))

        reconstruction = reconstruct_optimal_decision(prediction, outcome, confidence, pnl)
        reconstruction["timestamp"] = row.get("timestamp", datetime.now().isoformat())
        reconstruction["underlying"] = row.get("underlying", "UNKNOWN")
        reconstructions.append(reconstruction)

        # What-if scenario
        if not reconstruction["was_correct"]:
            what_if_scenarios.append(
                {
                    "timestamp": reconstruction["timestamp"],
                    "underlying": reconstruction["underlying"],
                    "what_actually_happened": f"Predicted {prediction}, but optimal was {reconstruction['optimal_action']}",
                    "what_if_we_had_optimal": f"Would have predicted {reconstruction['optimal_action']} with {reconstruction['optimal_confidence']:.2%} confidence",
                    "potential_improvement": (
                        "Correct prediction" if reconstruction["was_correct"] else "Better decision possible"
                    ),
                }
            )

    df_reconstruction = pd.DataFrame(reconstructions)

    # Save results
    output_csv = OUTPUT_DIR / "phase54_reconstruction_report.csv"
    df_reconstruction.to_csv(output_csv, index=False)
    print(f"[SAVE] Reconstruction report saved to: {output_csv}")

    what_if_json = OUTPUT_DIR / "phase54_what_if_analysis.json"
    with what_if_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "what_if_scenarios": what_if_scenarios,
                "summary": {
                    "total_reconstructed": len(reconstructions),
                    "correct_predictions": sum(1 for r in reconstructions if r["was_correct"]),
                    "incorrect_predictions": sum(1 for r in reconstructions if not r["was_correct"]),
                    "avg_confidence_gap": np.mean([r["confidence_gap"] for r in reconstructions]),
                },
                "analysis_date": datetime.now().isoformat(),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] What-if analysis saved to: {what_if_json}")

    # Summary
    print(f"\n=== BACK-RECONSTRUCTION SUMMARY ===")
    print(f"Total reconstructions: {len(reconstructions)}")
    correct = sum(1 for r in reconstructions if r["was_correct"])
    incorrect = len(reconstructions) - correct
    print(f"Correct predictions: {correct} ({correct/len(reconstructions)*100:.1f}%)")
    print(f"Incorrect predictions: {incorrect} ({incorrect/len(reconstructions)*100:.1f}%)")
    avg_gap = np.mean([r["confidence_gap"] for r in reconstructions])
    print(f"Average confidence gap: {avg_gap:.3f}")
    print(f"What-if scenarios: {len(what_if_scenarios)}")

    print("\n[OK] Phase 54 Real Outcome Back-Reconstruction completed")


def main() -> None:
    """Main entry point."""
    run_phase54_back_reconstruction()


if __name__ == "__main__":
    main()
