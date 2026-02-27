"""
Angel One Index Options - Multi-Timeframe Confirmation Logic - UPGRADED

Confirms signals across multiple timeframes.

UPGRADED FEATURES:
- Support for 5+ timeframes (1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d)
- Weighted confirmation based on timeframe importance
- Enhanced signal aggregation and agreement detection
- Timeframe-specific signal strength analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter


# Default timeframes (in minutes): 1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d
DEFAULT_TIMEFRAMES = [1, 3, 5, 15, 30, 60, 240, 1440]

# Timeframe weights (higher timeframes get more weight)
TIMEFRAME_WEIGHTS = {
    1: 0.10,  # 1 minute - lowest weight
    3: 0.15,  # 3 minutes
    5: 0.20,  # 5 minutes
    15: 0.25,  # 15 minutes
    30: 0.30,  # 30 minutes
    60: 0.35,  # 1 hour
    240: 0.40,  # 4 hours
    1440: 0.50,  # 1 day - highest weight
}


def get_timeframe_weight(timeframe: int) -> float:
    """Get weight for a timeframe."""
    return TIMEFRAME_WEIGHTS.get(timeframe, 0.20)  # Default 0.20


def aggregate_signals_across_timeframes(signals_by_timeframe: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate signals across multiple timeframes with weighted scoring.

    Args:
        signals_by_timeframe: Dict mapping timeframe (minutes) to signal dict
                             Each signal dict should have: 'signal', 'confidence', 'strength'

    Returns:
        Aggregated signal information
    """
    if not signals_by_timeframe:
        return {
            "confirmation_score": 0.0,
            "agreement_count": 0,
            "total_timeframes": 0,
            "dominant_signal": "NONE",
            "weighted_confidence": 0.0,
        }

    # Collect signals and confidences
    signal_list = []
    confidence_list = []
    weights_list = []

    for tf, signal_data in signals_by_timeframe.items():
        signal = signal_data.get("signal", "HOLD")
        confidence = float(signal_data.get("confidence", 0.5))
        weight = get_timeframe_weight(tf)

        signal_list.append(signal)
        confidence_list.append(confidence)
        weights_list.append(weight)

    # Count signal agreement
    signal_counts = Counter(signal_list)
    most_common_signal, most_common_count = signal_counts.most_common(1)[0]

    # Calculate weighted confidence
    total_weight = sum(weights_list)
    weighted_confidence = (
        sum(c * w for c, w in zip(confidence_list, weights_list)) / total_weight if total_weight > 0 else 0.0
    )

    # Agreement score (proportion of timeframes agreeing)
    agreement_ratio = most_common_count / len(signal_list)

    # Combined confirmation score (weighted confidence * agreement)
    confirmation_score = weighted_confidence * (0.5 + 0.5 * agreement_ratio)

    return {
        "confirmation_score": float(confirmation_score),
        "agreement_count": most_common_count,
        "total_timeframes": len(signal_list),
        "dominant_signal": most_common_signal,
        "weighted_confidence": float(weighted_confidence),
        "agreement_ratio": float(agreement_ratio),
    }


def check_multi_timeframe_confirmation(
    df_signals: pd.DataFrame,
    timeframes: Optional[List[int]] = None,
    timeframe_data: Optional[Dict[int, pd.DataFrame]] = None,
) -> pd.DataFrame:
    """
    Check signal confirmation across 5+ timeframes with enhanced analysis.

    Args:
        df_signals: DataFrame with signals (current timeframe)
        timeframes: List of timeframe minutes (default: [1, 3, 5, 15, 30, 60, 240, 1440])
        timeframe_data: Optional dict mapping timeframe to DataFrame with signals for that timeframe

    Returns:
        DataFrame with confirmation columns
    """
    if df_signals.empty:
        return df_signals

    if timeframes is None or len(timeframes) == 0:
        timeframes = DEFAULT_TIMEFRAMES

    df = df_signals.copy()

    # If timeframe_data provided, use actual multi-timeframe analysis
    if timeframe_data and len(timeframe_data) > 0:
        confirmation_scores = []
        agreement_counts = []
        dominant_signals = []

        for idx in df.index:
            signals_by_tf = {}

            # Collect signals from each timeframe
            for tf in timeframes:
                if tf in timeframe_data:
                    tf_df = timeframe_data[tf]
                    if idx < len(tf_df):
                        row = tf_df.iloc[idx]
                        signals_by_tf[tf] = {
                            "signal": str(row.get("signal", row.get("pred_label", "HOLD"))),
                            "confidence": float(row.get("pred_confidence", row.get("confidence", 0.5))),
                            "strength": float(row.get("strength", 0.5)),
                        }

            # Aggregate signals
            if signals_by_tf:
                aggregated = aggregate_signals_across_timeframes(signals_by_tf)
                confirmation_scores.append(aggregated["confirmation_score"])
                agreement_counts.append(aggregated["agreement_count"])
                dominant_signals.append(aggregated["dominant_signal"])
            else:
                # Fallback to single timeframe
                if "pred_confidence" in df.columns:
                    confirmation_scores.append(float(df.loc[idx, "pred_confidence"]))
                else:
                    confirmation_scores.append(0.5)
                agreement_counts.append(1)
                dominant_signals.append("HOLD")

        df["confirmation_score"] = confirmation_scores
        df["timeframe_agreement_count"] = agreement_counts
        df["dominant_signal"] = dominant_signals
        df["confirmed_signal"] = df["confirmation_score"] >= 0.7
        df["timeframe_agreement"] = df["confirmation_score"].apply(
            lambda x: "STRONG" if x >= 0.8 else "MODERATE" if x >= 0.6 else "WEAK"
        )
    else:
        # Fallback: use confidence-based confirmation (original logic)
        if "pred_confidence" not in df.columns:
            df["confirmation_score"] = 0.5
            df["confirmed_signal"] = False
            df["timeframe_agreement"] = "NONE"
            df["timeframe_agreement_count"] = 1
            df["dominant_signal"] = "HOLD"
            return df

        # Compute confirmation score based on confidence consistency
        df["confirmation_score"] = df["pred_confidence"]
        df["confirmed_signal"] = df["confirmation_score"] >= 0.7
        df["timeframe_agreement"] = df["confirmation_score"].apply(
            lambda x: "STRONG" if x >= 0.8 else "MODERATE" if x >= 0.6 else "WEAK"
        )
        df["timeframe_agreement_count"] = 1  # Single timeframe
        df["dominant_signal"] = df.get("pred_label", "HOLD")

    return df


def compute_confirmation_score(
    signals_by_timeframe: Dict[int, Any],
    use_weights: bool = True,
) -> float:
    """
    Compute confirmation score from signals across timeframes with weighted scoring.

    Args:
        signals_by_timeframe: Dict mapping timeframe (minutes) to signal (str) or signal dict
        use_weights: Whether to use timeframe weights

    Returns:
        Confirmation score (0.0 to 1.0)
    """
    if not signals_by_timeframe or len(signals_by_timeframe) == 0:
        return 0.0

    # Extract signals
    signals = []
    weights = []

    for tf, signal_data in signals_by_timeframe.items():
        if isinstance(signal_data, dict):
            signal = signal_data.get("signal", "HOLD")
            confidence = signal_data.get("confidence", 0.5)
        else:
            signal = str(signal_data)
            confidence = 0.5

        signals.append(signal)
        if use_weights:
            weights.append(get_timeframe_weight(tf))
        else:
            weights.append(1.0)

    # Count agreement
    signal_counts = Counter(signals)
    most_common_signal, most_common_count = signal_counts.most_common(1)[0]

    # Base score = proportion of timeframes agreeing
    base_score = most_common_count / len(signals)

    # Weighted score (if using weights)
    if use_weights and len(weights) > 0:
        # Weight by timeframe importance
        total_weight = sum(weights)
        weighted_agreement = sum(w for s, w in zip(signals, weights) if s == most_common_signal) / total_weight
        score = 0.5 * base_score + 0.5 * weighted_agreement
    else:
        score = base_score

    return float(score)


def filter_confirmed_signals(
    df: pd.DataFrame,
    min_confirmation: float = 0.6,
) -> pd.DataFrame:
    """
    Filter signals by confirmation score.

    Args:
        df: DataFrame with signals
        min_confirmation: Minimum confirmation score

    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df

    if min_confirmation < 0.0 or min_confirmation > 1.0:
        min_confirmation = 0.6

    if "confirmation_score" not in df.columns:
        return df

    df_filtered = df[df["confirmation_score"] >= min_confirmation].copy()

    return df_filtered


def main() -> None:
    """Test multi-timeframe confirmation."""
    print("=== ANGEL ONE INDEX OPTIONS - MULTI-TIMEFRAME CONFIRMATION ===")
    df = pd.DataFrame(
        {
            "pred_confidence": [0.9, 0.8, 0.7, 0.85],
            "pred_label": ["BUY_CE", "BUY_CE", "HOLD", "BUY_CE"],
        }
    )
    result = check_multi_timeframe_confirmation(df, timeframes=[1, 3, 5])
    print(result[["pred_confidence", "confirmation_score", "confirmed_signal"]].to_string())


if __name__ == "__main__":
    main()
