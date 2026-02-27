"""
Angel One Index Options - Multi-Model Agreement Filter

Filters signals based on agreement across multiple models or timeframes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


def check_model_agreement(
    predictions: List[str],
    confidences: List[float],
) -> Dict[str, Any]:
    """
    Check agreement across multiple model predictions.

    Args:
        predictions: List of prediction labels
        confidences: List of confidence values

    Returns:
        Dict with agreement details
    """
    if not predictions or len(predictions) == 0:
        return {
            "agreement_score": 0.0,
            "agreed_prediction": "NONE",
            "agreement_level": "NONE",
        }

    # Count predictions
    from collections import Counter

    pred_counts = Counter(predictions)
    most_common = pred_counts.most_common(1)[0]

    # Agreement score = proportion of models agreeing
    agreement_score = most_common[1] / len(predictions)

    # Weighted by confidence
    if confidences and len(confidences) == len(predictions):
        agreed_pred = most_common[0]
        avg_confidence = np.mean([c for p, c in zip(predictions, confidences) if p == agreed_pred])
        agreement_score = agreement_score * avg_confidence

    # Classify agreement level
    if agreement_score >= 0.8:
        level = "STRONG"
    elif agreement_score >= 0.6:
        level = "MODERATE"
    elif agreement_score >= 0.4:
        level = "WEAK"
    else:
        level = "NONE"

    return {
        "agreement_score": float(agreement_score),
        "agreed_prediction": most_common[0],
        "agreement_level": level,
    }


def compute_agreement_score(predictions: List[str]) -> float:
    """
    Compute simple agreement score.

    Args:
        predictions: List of predictions

    Returns:
        Agreement score (0.0 to 1.0)
    """
    if not predictions or len(predictions) == 0:
        return 0.0

    from collections import Counter

    pred_counts = Counter(predictions)
    most_common_count = pred_counts.most_common(1)[0][1]

    return float(most_common_count / len(predictions))


def filter_by_agreement(
    df_signals: pd.DataFrame,
    min_agreement: float = 0.7,
) -> pd.DataFrame:
    """
    Filter signals by agreement score.

    Args:
        df_signals: DataFrame with signals
        min_agreement: Minimum agreement score required

    Returns:
        Filtered DataFrame
    """
    if df_signals.empty:
        return df_signals

    if min_agreement < 0.0 or min_agreement > 1.0:
        min_agreement = 0.7

    df = df_signals.copy()

    # For each underlying, check agreement across strikes/sides
    # Simplified: use confidence as proxy for agreement
    if "pred_confidence" in df.columns:
        # High confidence = high agreement (simplified)
        df["agreement_score"] = df["pred_confidence"]
    else:
        df["agreement_score"] = 0.5

    # Filter
    df_filtered = df[df["agreement_score"] >= min_agreement].copy()

    return df_filtered


def main() -> None:
    """Test multi-model agreement."""
    print("=== ANGEL ONE INDEX OPTIONS - MULTI-MODEL AGREEMENT ===")
    predictions = ["BUY_CE", "BUY_CE", "BUY_CE", "HOLD"]
    confidences = [0.9, 0.85, 0.8, 0.6]
    result = check_model_agreement(predictions, confidences)
    print(f"Agreement result: {result}")


if __name__ == "__main__":
    main()
