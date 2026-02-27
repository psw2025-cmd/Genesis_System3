"""
Angel One Index Options - Confidence-Score Fusion Layer

Fuses confidence and score into unified signal strength metric.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def fuse_confidence_score(
    confidence: float,
    score: float,
    weights: Dict[str, float] | None = None,
) -> float:
    """
    Fuse confidence and score into single metric.

    Args:
        confidence: Model confidence (0.0 to 1.0)
        score: Expected move score
        weights: Optional weights dict (default: {"confidence": 0.6, "score": 0.4})

    Returns:
        Fused score
    """
    if weights is None:
        weights = {"confidence": 0.6, "score": 0.4}

    # Normalize weights
    total = sum(weights.values())
    if total == 0:
        weights = {"confidence": 0.6, "score": 0.4}
        total = 1.0

    weights = {k: v / total for k, v in weights.items()}

    # Normalize score to [0, 1] range
    score_normalized = min(1.0, max(0.0, abs(score) / 1.0))

    # Fuse
    fused = weights.get("confidence", 0.6) * confidence + weights.get("score", 0.4) * score_normalized

    return float(fused)


def compute_fusion_rank(df_signals: pd.DataFrame) -> pd.DataFrame:
    """
    Compute fusion rank for all signals.

    Args:
        df_signals: DataFrame with confidence and score columns

    Returns:
        DataFrame with fused_score and fusion_rank columns
    """
    if df_signals.empty:
        return df_signals

    df = df_signals.copy()

    # Compute fused scores
    fused_scores = []
    for _, row in df.iterrows():
        conf = float(row.get("pred_confidence", 0.0))
        score = float(row.get("expected_move_score", 0.0))
        fused = fuse_confidence_score(conf, score)
        fused_scores.append(fused)

    df["fused_score"] = fused_scores

    # Rank by fused score
    df["fusion_rank"] = df["fused_score"].rank(ascending=False, method="dense").astype(int)

    # Normalize
    if len(fused_scores) > 0:
        max_score = max(fused_scores)
        min_score = min(fused_scores)
        if max_score > min_score:
            df["normalized_fusion"] = (df["fused_score"] - min_score) / (max_score - min_score)
        else:
            df["normalized_fusion"] = 0.5
    else:
        df["normalized_fusion"] = 0.0

    return df


def normalize_fusion_scores(scores: pd.Series) -> pd.Series:
    """
    Normalize fusion scores to [0, 1] range.

    Args:
        scores: Series of fusion scores

    Returns:
        Normalized scores
    """
    if len(scores) == 0:
        return scores

    min_score = scores.min()
    max_score = scores.max()

    if max_score > min_score:
        normalized = (scores - min_score) / (max_score - min_score)
    else:
        normalized = pd.Series([0.5] * len(scores))

    return normalized


def main() -> None:
    """Test confidence-score fusion."""
    print("=== ANGEL ONE INDEX OPTIONS - CONFIDENCE-SCORE FUSION ===")
    df = pd.DataFrame(
        {
            "pred_confidence": [0.9, 0.8, 0.7, 0.85],
            "expected_move_score": [0.4, 0.3, 0.2, 0.35],
        }
    )
    result = compute_fusion_rank(df)
    print(result[["pred_confidence", "expected_move_score", "fused_score", "fusion_rank"]].to_string())


if __name__ == "__main__":
    main()
