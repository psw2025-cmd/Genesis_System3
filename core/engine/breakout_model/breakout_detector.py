"""
Breakout Detector - Detect H-L breakouts, CPR, ORB, support/resistance breaks
"""

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


def compute_cpr_levels(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, float]:
    """
    Compute Central Pivot Range (CPR) levels.

    Args:
        high: High prices
        low: Low prices
        close: Close prices

    Returns:
        Dict with pivot, top, bottom levels
    """
    if len(high) == 0 or len(low) == 0 or len(close) == 0:
        return {"pivot": 0.0, "top": 0.0, "bottom": 0.0}

    # Use latest values
    h = float(high.iloc[-1]) if len(high) > 0 else 0.0
    l = float(low.iloc[-1]) if len(low) > 0 else 0.0
    c = float(close.iloc[-1]) if len(close) > 0 else 0.0

    if h == 0 or l == 0 or c == 0:
        return {"pivot": 0.0, "top": 0.0, "bottom": 0.0}

    pivot = (h + l + c) / 3.0
    top = (h + l) / 2.0
    bottom = (h + l) / 2.0

    # Adjust if needed
    if top < pivot:
        top = pivot + (pivot - bottom)
    if bottom > pivot:
        bottom = pivot - (top - pivot)

    return {"pivot": float(pivot), "top": float(top), "bottom": float(bottom)}


def compute_orb_signals(prices: pd.Series, lookback: int = 20) -> Dict[str, Any]:
    """
    Compute Opening Range Breakout (ORB) signals.

    Args:
        prices: Price series
        lookback: Lookback period for range calculation

    Returns:
        Dict with ORB levels and signals
    """
    if len(prices) < lookback:
        return {
            "orb_high": float(prices.max()) if len(prices) > 0 else 0.0,
            "orb_low": float(prices.min()) if len(prices) > 0 else 0.0,
            "orb_breakout_up": False,
            "orb_breakout_down": False,
        }

    # Opening range (first N minutes)
    opening_range = prices.iloc[: min(lookback, len(prices))]
    orb_high = float(opening_range.max())
    orb_low = float(opening_range.min())

    current_price = float(prices.iloc[-1]) if len(prices) > 0 else 0.0

    return {
        "orb_high": orb_high,
        "orb_low": orb_low,
        "orb_breakout_up": current_price > orb_high,
        "orb_breakout_down": current_price < orb_low,
    }


def detect_support_resistance(prices: pd.Series, window: int = 20) -> Dict[str, float]:
    """
    Detect support and resistance levels.

    Args:
        prices: Price series
        window: Window for local min/max detection

    Returns:
        Dict with support and resistance levels
    """
    if len(prices) < window:
        return {
            "support": float(prices.min()) if len(prices) > 0 else 0.0,
            "resistance": float(prices.max()) if len(prices) > 0 else 0.0,
        }

    # Local minima (support)
    support = float(prices.rolling(window=window).min().iloc[-1])

    # Local maxima (resistance)
    resistance = float(prices.rolling(window=window).max().iloc[-1])

    return {"support": support, "resistance": resistance}


def detect_breakouts(
    df: pd.DataFrame, price_col: str = "spot", high_col: str = None, low_col: str = None
) -> pd.DataFrame:
    """
    Detect breakouts: H-L breaks, CPR breaks, ORB signals, S/R breaks.

    Args:
        df: DataFrame with price data
        price_col: Column name for prices
        high_col: Column name for high prices (optional)
        low_col: Column name for low prices (optional)

    Returns:
        DataFrame with breakout signals
    """
    if df.empty or price_col not in df.columns:
        return df

    df = df.copy()

    # Group by underlying
    group_col = "underlying" if "underlying" in df.columns else None

    if group_col:
        grouped = df.groupby(group_col)
    else:
        grouped = [(None, df)]

    all_results = []

    for group_key, group_df in grouped:
        prices = pd.to_numeric(group_df[price_col], errors="coerce").fillna(0)

        # High-Low breakout
        if high_col and high_col in group_df.columns:
            highs = pd.to_numeric(group_df[high_col], errors="coerce").fillna(prices)
        else:
            highs = prices.rolling(window=5).max()

        if low_col and low_col in group_df.columns:
            lows = pd.to_numeric(group_df[low_col], errors="coerce").fillna(prices)
        else:
            lows = prices.rolling(window=5).min()

        current_price = prices.iloc[-1] if len(prices) > 0 else 0.0
        recent_high = float(highs.iloc[-1]) if len(highs) > 0 else 0.0
        recent_low = float(lows.iloc[-1]) if len(lows) > 0 else 0.0

        # H-L breakout signals
        group_df["hl_breakout_up"] = (current_price > recent_high).astype(int)
        group_df["hl_breakout_down"] = (current_price < recent_low).astype(int)

        # CPR levels
        cpr = compute_cpr_levels(highs, lows, prices)
        group_df["cpr_pivot"] = cpr["pivot"]
        group_df["cpr_top"] = cpr["top"]
        group_df["cpr_bottom"] = cpr["bottom"]

        # CPR breakout signals
        group_df["cpr_breakout_up"] = (current_price > cpr["top"]).astype(int)
        group_df["cpr_breakout_down"] = (current_price < cpr["bottom"]).astype(int)

        # ORB signals
        orb = compute_orb_signals(prices, lookback=20)
        group_df["orb_high"] = orb["orb_high"]
        group_df["orb_low"] = orb["orb_low"]
        group_df["orb_breakout_up"] = orb["orb_breakout_up"].astype(int)
        group_df["orb_breakout_down"] = orb["orb_breakout_down"].astype(int)

        # Support/Resistance
        sr = detect_support_resistance(prices, window=20)
        group_df["support_level"] = sr["support"]
        group_df["resistance_level"] = sr["resistance"]

        # S/R breakouts
        group_df["sr_breakout_up"] = (current_price > sr["resistance"]).astype(int)
        group_df["sr_breakout_down"] = (current_price < sr["support"]).astype(int)

        # Combined breakout score (-1 to +1)
        breakout_score = (
            group_df["hl_breakout_up"] * 0.2
            + group_df["cpr_breakout_up"] * 0.3
            + group_df["orb_breakout_up"] * 0.2
            + group_df["sr_breakout_up"] * 0.3
            - group_df["hl_breakout_down"] * 0.2
            - group_df["cpr_breakout_down"] * 0.3
            - group_df["orb_breakout_down"] * 0.2
            - group_df["sr_breakout_down"] * 0.3
        )
        group_df["breakout_score"] = breakout_score.clip(-1.0, 1.0).values

        all_results.append(group_df)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return df


def compute_cpr_levels(df: pd.DataFrame) -> pd.DataFrame:
    """Compute CPR levels for DataFrame."""
    return detect_breakouts(df)


def compute_orb_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Compute ORB signals for DataFrame."""
    return detect_breakouts(df)
