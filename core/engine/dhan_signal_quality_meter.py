"""
Dhan Index Options - Signal Quality Meter

Measures and classifies signal quality.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def measure_signal_quality(signal_row: pd.Series) -> Dict[str, Any]:
    """
    Measure signal quality for a single signal.

    Args:
        signal_row: Signal row with confidence, score, etc.

    Returns:
        Dict with quality metrics
    """
    confidence = float(signal_row.get("pred_confidence", 0.0))
    score = abs(float(signal_row.get("expected_move_score", 0.0)))
    moneyness = abs(float(signal_row.get("moneyness", 0.0)))
    volatility = float(signal_row.get("ltp_roll_std_5", 0.0)) if "ltp_roll_std_5" in signal_row else 0.0

    quality_score = compute_quality_score(confidence, score, moneyness, volatility)
    quality_level = classify_quality_level(quality_score)

    # Quality factors
    factors = {
        "confidence": confidence,
        "score": score,
        "moneyness": moneyness,
        "volatility": volatility,
    }

    # Recommendation
    if quality_level == "EXCELLENT":
        recommendation = "STRONG_BUY"
    elif quality_level == "GOOD":
        recommendation = "BUY"
    elif quality_level == "FAIR":
        recommendation = "CONSIDER"
    else:
        recommendation = "AVOID"

    return {
        "quality_score": float(quality_score),
        "quality_level": quality_level,
        "quality_factors": factors,
        "recommendation": recommendation,
    }


def compute_quality_score(
    confidence: float,
    score: float,
    moneyness: float,
    volatility: float,
) -> float:
    """
    Compute overall quality score (0.0 to 1.0).

    Args:
        confidence: Model confidence
        score: Expected move score
        moneyness: Moneyness (distance from ATM)
        volatility: Volatility measure

    Returns:
        Quality score
    """
    # Normalize inputs
    conf_norm = min(1.0, max(0.0, confidence))
    score_norm = min(1.0, max(0.0, abs(score) / 1.0))
    moneyness_norm = min(1.0, max(0.0, 1.0 - moneyness / 5.0))  # Prefer near ATM
    vol_norm = min(1.0, max(0.0, volatility / 100.0)) if volatility > 0 else 0.5

    # Weighted combination
    quality = 0.4 * conf_norm + 0.3 * score_norm + 0.2 * moneyness_norm + 0.1 * vol_norm

    return float(quality)


def classify_quality_level(quality_score: float) -> str:
    """
    Classify quality level.

    Returns: "POOR", "FAIR", "GOOD", "EXCELLENT"
    """
    if quality_score >= 0.8:
        return "EXCELLENT"
    elif quality_score >= 0.6:
        return "GOOD"
    elif quality_score >= 0.4:
        return "FAIR"
    else:
        return "POOR"


def main() -> None:
    """Test signal quality meter."""
    print("=== ANGEL ONE INDEX OPTIONS - SIGNAL QUALITY METER ===")
    signal_row = pd.Series(
        {
            "pred_confidence": 0.9,
            "expected_move_score": 0.4,
            "moneyness": 0.5,
            "ltp_roll_std_5": 50.0,
        }
    )
    result = measure_signal_quality(signal_row)
    print(f"Signal quality: {result}")


if __name__ == "__main__":
    main()
