"""
Angel One Index Options - Real Threshold Recommender

Recommends thresholds based on real PnL outcomes.
AUTO-UPDATE: DISABLED - Only generates suggestions, never auto-applies.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

from core.engine.angel_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
THRESHOLDS_REAL_JSON = CONFIG_DIR / "thresholds_real_suggestions.json"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def recommend_thresholds(
    min_trades: int = 5,
    max_drawdown_limit: float = -10.0,
) -> Dict[str, Any]:
    """
    Recommend thresholds based on real outcomes.

    Args:
        min_trades: Minimum trades required for recommendation
        max_drawdown_limit: Maximum allowed drawdown

    Returns:
        Dict with recommendations per underlying
    """
    df = load_outcomes()
    if df.empty:
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    recommendations = {}

    # Per underlying
    underlyings = df["underlying"].unique() if "underlying" in df.columns else []

    for underlying in underlyings:
        df_u = df[df["underlying"] == underlying]

        if len(df_u) < min_trades:
            recommendations[underlying] = {
                "status": "INSUFFICIENT_DATA",
                "message": f"Only {len(df_u)} trades, need {min_trades}",
            }
            continue

        # Search threshold combinations
        best_combo = _search_best_thresholds(df_u, max_drawdown_limit)

        recommendations[underlying] = {
            "status": "SUCCESS",
            "recommended_confidence": best_combo["confidence"],
            "recommended_score": best_combo["score"],
            "expected_pnl": best_combo["expected_pnl"],
            "trade_count": best_combo["trade_count"],
            "win_rate": best_combo["win_rate"],
            "rationale": best_combo["rationale"],
        }

    return {
        "status": "SUCCESS",
        "recommendations": recommendations,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _search_best_thresholds(
    df: pd.DataFrame,
    max_drawdown_limit: float,
) -> Dict[str, Any]:
    """
    Search for best threshold combination.

    Args:
        df: Outcome DataFrame for one underlying
        max_drawdown_limit: Maximum allowed drawdown

    Returns:
        Best threshold combination
    """
    confidence_range = np.arange(0.60, 0.96, 0.05)
    score_range = np.arange(0.10, 0.61, 0.05)

    best_combo = None
    best_score = -np.inf

    for conf in confidence_range:
        for score in score_range:
            # Filter trades that would have passed these thresholds
            filtered = df[(df["signal_confidence"] >= conf) & (df["score"].abs() >= score)]

            if len(filtered) < 3:  # Need at least 3 trades
                continue

            # Compute metrics
            avg_pnl = filtered["pnl_pct"].mean()
            win_rate = (filtered["pnl_pct"] > 0).sum() / len(filtered)
            max_dd = filtered["pnl_pct"].min()

            # Check drawdown constraint
            if max_dd < max_drawdown_limit:
                continue

            # Score: maximize expected PnL with trade count penalty
            expected_pnl = avg_pnl * win_rate
            trade_count_penalty = min(1.0, len(filtered) / 20.0)  # Prefer more trades
            combo_score = expected_pnl * trade_count_penalty

            if combo_score > best_score:
                best_score = combo_score
                best_combo = {
                    "confidence": float(conf),
                    "score": float(score),
                    "expected_pnl": float(expected_pnl),
                    "trade_count": len(filtered),
                    "win_rate": float(win_rate * 100),
                    "avg_pnl": float(avg_pnl),
                    "max_drawdown": float(max_dd),
                    "rationale": f"Expected PnL: {expected_pnl:.2f}%, Win Rate: {win_rate*100:.1f}%, Trades: {len(filtered)}",
                }

    # Fallback to current if no good combo found
    if best_combo is None:
        best_combo = {
            "confidence": 0.80,
            "score": 0.30,
            "expected_pnl": 0.0,
            "trade_count": 0,
            "win_rate": 0.0,
            "rationale": "No suitable combination found, using conservative defaults",
        }

    return best_combo


def save_recommendations(recommendations: Dict[str, Any]) -> Path:
    """
    Save recommendations to JSON.

    Returns:
        Path to saved JSON
    """
    with THRESHOLDS_REAL_JSON.open("w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2)

    return THRESHOLDS_REAL_JSON


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - REAL THRESHOLD RECOMMENDER ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Suggestions only\n")

    recommendations = recommend_thresholds()

    if recommendations["status"] == "SUCCESS":
        print("=== THRESHOLD RECOMMENDATIONS ===\n")

        for underlying, rec in recommendations["recommendations"].items():
            if rec["status"] == "SUCCESS":
                print(f"{underlying}:")
                print(f"  Recommended Confidence: {rec['recommended_confidence']:.2f}")
                print(f"  Recommended Score: {rec['recommended_score']:.2f}")
                print(f"  Expected PnL: {rec['expected_pnl']:.2f}%")
                print(f"  Trade Count: {rec['trade_count']}")
                print(f"  Win Rate: {rec['win_rate']:.1f}%")
                print(f"  Rationale: {rec['rationale']}")
                print()
            else:
                print(f"{underlying}: {rec['message']}")

        # Save
        save_path = save_recommendations(recommendations)
        print(f"[SAVE] Recommendations saved to: {save_path}")
        print("\n[NOTE] These are SUGGESTIONS ONLY. Manual review required before applying.")
    else:
        print(f"[INFO] {recommendations.get('message', 'Recommendations not available')}")


if __name__ == "__main__":
    main()
