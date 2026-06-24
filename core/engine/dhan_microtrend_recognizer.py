"""
Dhan Index Options - Microtrend Recognition

Detects short-term trends in price movements.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd


def detect_microtrend(df_signals: pd.DataFrame, lookback: int = 3) -> pd.DataFrame:
    """
    Detect microtrends in signals DataFrame.

    Args:
        df_signals: DataFrame with price data
        lookback: Number of periods to look back

    Returns:
        DataFrame with added microtrend columns
    """
    if df_signals.empty:
        return df_signals

    if lookback < 2:
        lookback = 2

    df = df_signals.copy()

    # Detect trend for spot
    if "spot" in df.columns:
        df["trend_strength"] = df["spot"].apply(
            lambda x: compute_trend_strength(df["spot"].tail(lookback + 1)) if len(df) > lookback else 0.0
        )
        df["trend_direction"] = df["spot"].apply(
            lambda x: classify_trend_direction(df["spot"].tail(lookback + 1)) if len(df) > lookback else "SIDEWAYS"
        )

    return df


def compute_trend_strength(price_series: pd.Series) -> float:
    """
    Compute trend strength (0.0 to 1.0).

    Args:
        price_series: Series of prices

    Returns:
        Trend strength between 0.0 and 1.0
    """
    if len(price_series) < 2:
        return 0.0

    # Simple linear regression slope
    x = np.arange(len(price_series))
    y = price_series.values

    if len(y) < 2:
        return 0.0

    # Compute slope
    slope = np.polyfit(x, y, 1)[0]

    # Normalize to [0, 1]
    max_slope = abs(price_series.max() - price_series.min()) / len(price_series)
    if max_slope == 0:
        return 0.0

    strength = min(1.0, abs(slope) / max_slope)
    return float(strength)


def classify_trend_direction(df: pd.DataFrame) -> str:
    """
    Classify trend direction.

    Returns: "UP", "DOWN", "SIDEWAYS"
    """
    if df.empty or "spot" not in df.columns:
        return "SIDEWAYS"

    spot = df["spot"].dropna()
    if len(spot) < 2:
        return "SIDEWAYS"

    # Simple: compare first and last
    first = spot.iloc[0]
    last = spot.iloc[-1]
    change_pct = (last - first) / first * 100.0

    if change_pct > 0.1:
        return "UP"
    elif change_pct < -0.1:
        return "DOWN"
    else:
        return "SIDEWAYS"


def main() -> None:
    """Test microtrend recognizer."""
    print("=== ANGEL ONE INDEX OPTIONS - MICROTREND RECOGNIZER ===")
    df = pd.DataFrame(
        {
            "spot": [22000, 22100, 22200, 22300, 22400],
        }
    )
    result = detect_microtrend(df, lookback=3)
    print(result[["spot", "trend_direction", "trend_strength"]].to_string())


if __name__ == "__main__":
    main()
