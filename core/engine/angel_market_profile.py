"""
Angel One Index Options - Multi-Timeframe Market Profile

Builds market profile maps for different timeframes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


def build_timeframe_profile(
    df_signals: pd.DataFrame,
    timeframe_min: int,
) -> pd.DataFrame:
    """
    Build market profile for a specific timeframe.

    Args:
        df_signals: DataFrame with price data
        timeframe_min: Timeframe in minutes (1, 3, 5, etc.)

    Returns:
        DataFrame with profile columns
    """
    if df_signals.empty or "spot" not in df_signals.columns:
        return df_signals

    if timeframe_min not in [1, 3, 5, 15, 30]:
        timeframe_min = 5

    df = df_signals.copy()

    # Group by timeframe (simplified: use row index)
    # In production, group by actual timestamps
    df[f"profile_{timeframe_min}min"] = (
        df["spot"]
        .rolling(
            window=timeframe_min,
            min_periods=1,
        )
        .mean()
    )

    return df


def compute_profile_levels(
    df: pd.DataFrame,
    num_levels: int = 5,
) -> Dict[str, List[float]]:
    """
    Compute support/resistance levels from profile.

    Args:
        df: DataFrame with price data
        num_levels: Number of levels to compute

    Returns:
        Dict with support_levels, resistance_levels, poc_level
    """
    if df.empty or "spot" not in df.columns:
        return {
            "support_levels": [],
            "resistance_levels": [],
            "poc_level": 0.0,
        }

    if num_levels < 2:
        num_levels = 5

    prices = df["spot"].dropna()
    if len(prices) == 0:
        return {
            "support_levels": [],
            "resistance_levels": [],
            "poc_level": 0.0,
        }

    min_price = prices.min()
    max_price = prices.max()
    price_range = max_price - min_price

    if price_range == 0:
        return {
            "support_levels": [min_price] * num_levels,
            "resistance_levels": [max_price] * num_levels,
            "poc_level": min_price,
        }

    # Compute levels
    level_size = price_range / num_levels
    support_levels = [min_price + i * level_size for i in range(num_levels)]
    resistance_levels = [min_price + (i + 1) * level_size for i in range(num_levels)]

    # POC (Point of Control) = most frequent price
    poc_level = prices.mode().iloc[0] if len(prices.mode()) > 0 else prices.median()

    return {
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "poc_level": float(poc_level),
    }


def classify_price_location(
    price: float,
    profile_levels: Dict[str, List[float]],
) -> str:
    """
    Classify price location relative to profile levels.

    Returns: "BELOW_SUPPORT", "SUPPORT_ZONE", "VALUE_AREA", "RESISTANCE_ZONE", "ABOVE_RESISTANCE"
    """
    if not profile_levels or "support_levels" not in profile_levels:
        return "VALUE_AREA"

    support = profile_levels.get("support_levels", [])
    resistance = profile_levels.get("resistance_levels", [])

    if not support or not resistance:
        return "VALUE_AREA"

    min_support = min(support)
    max_resistance = max(resistance)

    if price < min_support:
        return "BELOW_SUPPORT"
    elif price <= support[-1] if support else min_support:
        return "SUPPORT_ZONE"
    elif price >= resistance[0] if resistance else max_resistance:
        return "RESISTANCE_ZONE"
    elif price > max_resistance:
        return "ABOVE_RESISTANCE"
    else:
        return "VALUE_AREA"


def main() -> None:
    """Test market profile."""
    print("=== ANGEL ONE INDEX OPTIONS - MARKET PROFILE ===")
    df = pd.DataFrame(
        {
            "spot": [22000, 22100, 22050, 22200, 22150, 22300],
        }
    )
    result = build_timeframe_profile(df, timeframe_min=3)
    levels = compute_profile_levels(result)
    print(f"Profile levels: {levels}")


if __name__ == "__main__":
    main()
