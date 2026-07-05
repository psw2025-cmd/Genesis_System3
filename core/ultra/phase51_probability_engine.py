"""
System3 Ultra - Phase 51: Real-Time Probability Engine

Compute real-time probability distributions for outcomes.
Generate probability forecasts and track changes over time.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 113
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


def load_recent_predictions() -> Optional[pd.DataFrame]:
    """Load recent predictions for probability computation."""
    fused_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if fused_csv.exists():
        try:
            return pd.read_csv(fused_csv)
        except Exception:
            pass
    return None


def compute_probability_distribution(confidence: float, score: float, action: str) -> Dict[str, float]:
    """
    Compute probability distribution for BUY_CE, BUY_PE, HOLD.

    Args:
        confidence: Prediction confidence
        score: Prediction score
        action: Predicted action

    Returns:
        Dict with probabilities for each outcome
    """
    # Base probabilities from confidence and score
    base_prob_hold = 1.0 - confidence

    if action == "BUY_CE":
        prob_buy_ce = confidence * (0.5 + score) if score > 0 else confidence * 0.5
        prob_buy_pe = confidence * (0.5 - score) if score < 0 else confidence * 0.3
    elif action == "BUY_PE":
        prob_buy_pe = confidence * (0.5 - score) if score < 0 else confidence * 0.5
        prob_buy_ce = confidence * (0.5 + score) if score > 0 else confidence * 0.3
    else:  # HOLD
        prob_buy_ce = confidence * 0.3
        prob_buy_pe = confidence * 0.3

    # Normalize to sum to 1.0
    total = base_prob_hold + prob_buy_ce + prob_buy_pe
    if total > 0:
        prob_hold = base_prob_hold / total
        prob_buy_ce = prob_buy_ce / total
        prob_buy_pe = prob_buy_pe / total
    else:
        prob_hold = 0.33
        prob_buy_ce = 0.33
        prob_buy_pe = 0.34

    return {
        "prob_buy_ce": float(prob_buy_ce),
        "prob_buy_pe": float(prob_buy_pe),
        "prob_hold": float(prob_hold),
        "most_likely": max(("BUY_CE", prob_buy_ce), ("BUY_PE", prob_buy_pe), ("HOLD", prob_hold), key=lambda x: x[1])[
            0
        ],
    }


def generate_probability_forecasts(df: pd.DataFrame, horizon: int = 5) -> List[Dict[str, Any]]:
    """
    Generate probability forecasts for next N steps.

    Args:
        df: Historical predictions
        horizon: Forecast horizon (steps)

    Returns:
        List of forecast dicts
    """
    forecasts = []

    if len(df) < 2:
        return forecasts

    # Handle different column name possibilities
    conf_col = (
        "final_confidence"
        if "final_confidence" in df.columns
        else ("pred_confidence" if "pred_confidence" in df.columns else "confidence")
    )
    score_col = "final_score" if "final_score" in df.columns else ("score" if "score" in df.columns else "pred_score")
    action_col = (
        "final_action" if "final_action" in df.columns else ("pred_label" if "pred_label" in df.columns else "action")
    )

    # Use recent trend to forecast
    if conf_col in df.columns:
        recent_conf = df[conf_col].tail(5).mean() if len(df) >= 5 else df[conf_col].mean()
    else:
        recent_conf = 0.7

    if score_col in df.columns:
        recent_score = df[score_col].tail(5).mean() if len(df) >= 5 else df[score_col].mean()
    else:
        recent_score = 0.0

    if action_col in df.columns and len(df[action_col].mode()) > 0:
        recent_action = df[action_col].mode().iloc[0]
    else:
        recent_action = "HOLD"

    for step in range(1, horizon + 1):
        # Simple extrapolation (would use more sophisticated model in production)
        forecast_conf = min(0.95, recent_conf + np.random.normal(0, 0.02))
        forecast_score = np.clip(recent_score + np.random.normal(0, 0.05), -1, 1)

        prob_dist = compute_probability_distribution(forecast_conf, forecast_score, recent_action)

        forecasts.append(
            {
                "forecast_step": step,
                "timestamp": (pd.Timestamp.now() + pd.Timedelta(hours=step)).isoformat(),
                **prob_dist,
            }
        )

    return forecasts


def run_phase51_probability_engine() -> None:
    """Run Phase 51: Real-Time Probability Engine."""
    print("=== SYSTEM3 ULTRA - PHASE 51: REAL-TIME PROBABILITY ENGINE ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load recent predictions
    df_pred = load_recent_predictions()

    if df_pred is None or df_pred.empty:
        print("[WARN] No predictions found. Using synthetic data for demo.")
        # Create synthetic data
        np.random.seed(42)
        df_pred = pd.DataFrame(
            {
                "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=20, freq="1H"),
                "underlying": np.random.choice(["NIFTY", "BANKNIFTY"], 20),
                "final_action": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], 20),
                "final_confidence": np.random.uniform(0.6, 0.9, 20),
                "final_score": np.random.uniform(-0.5, 0.5, 20),
            }
        )

    print(f"[LOAD] Loaded {len(df_pred)} predictions")

    # Compute probability distributions
    distributions = []
    for _, row in df_pred.iterrows():
        # Handle different column name possibilities
        confidence = row.get("final_confidence", row.get("pred_confidence", row.get("confidence", 0.0)))
        score = row.get("final_score", row.get("score", row.get("pred_score", 0.0)))
        action = row.get("final_action", row.get("pred_label", row.get("action", "HOLD")))

        prob_dist = compute_probability_distribution(confidence, score, action)
        distributions.append(
            {
                "timestamp": row.get("timestamp", datetime.now().isoformat()),
                "underlying": row.get("underlying", "UNKNOWN"),
                "prediction": action,
                "confidence": confidence,
                "score": score,
                **prob_dist,
            }
        )

    df_distributions = pd.DataFrame(distributions)

    # Generate forecasts (need to handle column names)
    if len(df_pred) > 0:
        # Ensure we have the right columns for forecasting
        forecast_df = df_pred.copy()
        if "final_confidence" not in forecast_df.columns:
            forecast_df["final_confidence"] = forecast_df.get("pred_confidence", forecast_df.get("confidence", 0.0))
        if "final_score" not in forecast_df.columns:
            forecast_df["final_score"] = forecast_df.get("score", forecast_df.get("pred_score", 0.0))
        if "final_action" not in forecast_df.columns:
            forecast_df["final_action"] = forecast_df.get("pred_label", forecast_df.get("action", "HOLD"))
        forecasts = generate_probability_forecasts(forecast_df, horizon=5)
    else:
        forecasts = []
    df_forecasts = pd.DataFrame(forecasts)

    # Save results
    output_csv = OUTPUT_DIR / "phase51_probability_distributions.csv"
    df_distributions.to_csv(output_csv, index=False)
    print(f"[SAVE] Probability distributions saved to: {output_csv}")

    forecasts_json = OUTPUT_DIR / "phase51_probability_forecasts.json"
    with forecasts_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "forecasts": forecasts,
                "generated_at": datetime.now().isoformat(),
                "horizon": 5,
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] Probability forecasts saved to: {forecasts_json}")

    # Summary
    print(f"\n=== PROBABILITY ENGINE SUMMARY ===")
    print(f"Total distributions computed: {len(df_distributions)}")
    print(f"\nAverage probabilities:")
    print(f"  BUY_CE: {df_distributions['prob_buy_ce'].mean():.2%}")
    print(f"  BUY_PE: {df_distributions['prob_buy_pe'].mean():.2%}")
    print(f"  HOLD: {df_distributions['prob_hold'].mean():.2%}")
    print(f"\nForecasts generated: {len(forecasts)}")
    if forecasts:
        print(f"Next step forecast:")
        next_forecast = forecasts[0]
        print(f"  Most likely: {next_forecast['most_likely']}")
        print(
            f"  Probabilities: BUY_CE={next_forecast['prob_buy_ce']:.2%}, "
            f"BUY_PE={next_forecast['prob_buy_pe']:.2%}, HOLD={next_forecast['prob_hold']:.2%}"
        )

    print("\n[OK] Phase 51 Real-Time Probability Engine completed")


def main() -> None:
    """Main entry point."""
    run_phase51_probability_engine()


if __name__ == "__main__":
    main()
