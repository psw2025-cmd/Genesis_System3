"""
Dhan Index Options - Real Threshold Recommender V3

Suggest-only threshold recommendations based on real outcomes.
Must NOT apply them - suggestions only.
SAFE MODE ONLY - Read-only, no threshold application.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

from core.engine.dhan_unified_outcome_logger_v3 import get_outcome_stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
THRESHOLD_RECO_DIR = REPORTS_DIR / "threshold_reco"

THRESHOLD_RECO_DIR.mkdir(parents=True, exist_ok=True)


def recommend_thresholds_v3(
    min_trades: int = 5,
    max_drawdown_limit: float = -10.0,
) -> Dict[str, Any]:
    """
    Recommend thresholds based on real outcomes (SUGGESTIONS ONLY).

    Does NOT apply thresholds - only generates recommendations.

    Args:
        min_trades: Minimum trades required for recommendation
        max_drawdown_limit: Maximum allowed drawdown

    Returns:
        Dict with threshold recommendations (not applied)
    """
    print("=== ANGEL ONE INDEX OPTIONS - REAL THRESHOLD RECOMMENDER V3 ===")
    print("[INFO] SAFE MODE - Suggestions only, NO threshold application\n")

    if not REAL_OUTCOMES_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    try:
        df = pd.read_csv(REAL_OUTCOMES_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Outcomes CSV is empty",
            }

        recommendations = {}

        # Per underlying
        if "underlying" in df.columns:
            underlyings = df["underlying"].unique()
        else:
            underlyings = ["ALL"]

        for underlying in underlyings:
            if underlying == "ALL":
                df_u = df
            else:
                df_u = df[df["underlying"] == underlying]

            if len(df_u) < min_trades:
                recommendations[underlying] = {
                    "status": "INSUFFICIENT_DATA",
                    "message": f"Only {len(df_u)} trades, need {min_trades}",
                }
                continue

            # Search threshold combinations
            best_combo = _search_best_thresholds_v3(df_u, max_drawdown_limit)

            recommendations[underlying] = {
                "status": "SUCCESS",
                "recommended_confidence": best_combo["confidence"],
                "recommended_score": best_combo["score"],
                "expected_pnl": best_combo["expected_pnl"],
                "trade_count": best_combo["trade_count"],
                "win_rate": best_combo["win_rate"],
                "rationale": best_combo["rationale"],
                "note": "SUGGESTION ONLY - NOT APPLIED",
            }

        return {
            "status": "SUCCESS",
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
            "applied": False,  # Explicitly marked as not applied
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def _search_best_thresholds_v3(
    df: pd.DataFrame,
    max_drawdown_limit: float,
) -> Dict[str, Any]:
    """Search for best threshold combination."""
    confidence_range = np.arange(0.60, 0.96, 0.05)
    score_range = np.arange(0.10, 0.61, 0.05)

    best_combo = None
    best_score = -np.inf

    for conf in confidence_range:
        for score in score_range:
            # Filter trades that would have passed these thresholds
            filtered = df[(df["entry_confidence"] >= conf) & (df["entry_score"].abs() >= score)]

            if len(filtered) < 3:
                continue

            # Compute metrics
            avg_pnl = filtered["pnl_pct"].mean()
            win_rate = (filtered["pnl_pct"] > 0).sum() / len(filtered)
            max_dd = filtered["pnl_pct"].min()

            # Check drawdown constraint
            if max_dd < max_drawdown_limit:
                continue

            # Score: maximize expected PnL
            expected_pnl = avg_pnl * win_rate
            trade_count_penalty = min(1.0, len(filtered) / 20.0)
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

    # Fallback
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


def save_threshold_recommendations(recommendations: Dict[str, Any]) -> Path:
    """
    Save threshold recommendations to JSON (suggestions only).

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = THRESHOLD_RECO_DIR / f"threshold_recommendations_{today}.json"

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "applied": False,  # Explicitly marked as not applied
        "note": "These are SUGGESTIONS ONLY. Manual review required before applying.",
        "recommendations": recommendations,
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    recommendations = recommend_thresholds_v3()

    if recommendations["status"] == "SUCCESS":
        print("=== THRESHOLD RECOMMENDATIONS (SUGGESTIONS ONLY) ===\n")

        for underlying, rec in recommendations["recommendations"].items():
            if rec["status"] == "SUCCESS":
                print(f"{underlying}:")
                print(f"  Recommended Confidence: {rec['recommended_confidence']:.2f}")
                print(f"  Recommended Score: {rec['recommended_score']:.2f}")
                print(f"  Expected PnL: {rec['expected_pnl']:.2f}%")
                print(f"  Trade Count: {rec['trade_count']}")
                print(f"  Win Rate: {rec['win_rate']:.1f}%")
                print(f"  Rationale: {rec['rationale']}")
                print(f"  ⚠️  {rec['note']}")
                print()
            else:
                print(f"{underlying}: {rec['message']}")

        # Save recommendations
        save_path = save_threshold_recommendations(recommendations)
        print(f"[SAVE] Recommendations saved to: {save_path}")
        print("\n⚠️  IMPORTANT: These are SUGGESTIONS ONLY. They have NOT been applied.")
        print("⚠️  Manual review and approval required before any threshold changes.")
    else:
        print(f"[INFO] {recommendations.get('message', 'Recommendations not available')}")


if __name__ == "__main__":
    main()
