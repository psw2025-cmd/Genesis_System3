"""
Angel One Index Options - Premium-to-Spot Behavior Classifier

Classifies relationship between option premium and underlying spot.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def classify_premium_spot_behavior(
    ltp: float,
    spot: float,
    strike: float,
    moneyness: float,
) -> str:
    """
    Classify premium-to-spot behavior.

    Returns: "NORMAL", "PREMIUM_LEADING", "SPOT_LEADING", "DIVERGENT"
    """
    if ltp <= 0 or spot <= 0 or strike <= 0:
        return "NORMAL"

    # Compute intrinsic value
    intrinsic = max(0, spot - strike) if spot > strike else max(0, strike - spot)
    time_value = ltp - intrinsic

    # If time value is very high relative to intrinsic, premium might be leading
    if intrinsic > 0 and time_value / intrinsic > 2.0:
        return "PREMIUM_LEADING"

    # If time value is very low, spot might be leading
    if intrinsic > 0 and time_value / intrinsic < 0.1:
        return "SPOT_LEADING"

    # If moneyness is extreme but premium doesn't reflect it
    if abs(moneyness) > 2.0 and time_value < intrinsic * 0.5:
        return "DIVERGENT"

    return "NORMAL"


def compute_premium_spot_correlation(
    df_signals: pd.DataFrame,
    window: int = 5,
) -> float:
    """
    Compute correlation between premium and spot changes.

    Args:
        df_signals: DataFrame with ltp and spot data
        window: Rolling window for correlation

    Returns:
        Correlation coefficient (-1.0 to 1.0)
    """
    if df_signals.empty:
        return 0.0

    if window < 2:
        window = 5

    required = ["ltp", "spot"]
    if not all(col in df_signals.columns for col in required):
        return 0.0

    # Compute changes
    df = df_signals.copy()
    df["ltp_change"] = df["ltp"].pct_change()
    df["spot_change"] = df["spot"].pct_change()

    # Compute rolling correlation
    if len(df) >= window:
        recent = df.tail(window)
        corr = recent["ltp_change"].corr(recent["spot_change"])
        return float(corr) if not pd.isna(corr) else 0.0

    return 0.0


def detect_premium_spot_divergence(df_signals: pd.DataFrame) -> pd.DataFrame:
    """
    Detect divergence between premium and spot movements.

    Args:
        df_signals: DataFrame with ltp and spot data

    Returns:
        DataFrame with divergence_flag column
    """
    if df_signals.empty:
        return df_signals

    df = df_signals.copy()

    # Compute correlation
    corr = compute_premium_spot_correlation(df, window=5)

    # Classify behavior
    behaviors = []
    for _, row in df.iterrows():
        ltp = float(row.get("ltp", 0.0))
        spot = float(row.get("spot", 0.0))
        strike = float(row.get("strike", 0.0))
        moneyness = float(row.get("moneyness", 0.0))

        behavior = classify_premium_spot_behavior(ltp, spot, strike, moneyness)
        behaviors.append(behavior)

    df["premium_spot_behavior"] = behaviors
    df["correlation"] = corr
    df["divergence_flag"] = df["premium_spot_behavior"].isin(["DIVERGENT", "PREMIUM_LEADING"])

    return df


def main() -> None:
    """Test premium-spot classifier."""
    print("=== ANGEL ONE INDEX OPTIONS - PREMIUM-SPOT CLASSIFIER ===")
    df = pd.DataFrame(
        {
            "ltp": [100, 105, 110],
            "spot": [22000, 22100, 22200],
            "strike": [22000, 22100, 22200],
            "moneyness": [0.0, 0.0, 0.0],
        }
    )
    result = detect_premium_spot_divergence(df)
    print(result[["ltp", "spot", "premium_spot_behavior", "divergence_flag"]].to_string())


if __name__ == "__main__":
    main()
