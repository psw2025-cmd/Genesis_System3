"""
OI Buildup Classification
"""

from typing import Literal, Optional

import pandas as pd

OI_BUILDUP_TYPES = Literal["Long Buildup", "Short Buildup", "Short Covering", "Long Unwinding", "Neutral"]


def classify_oi_buildup(
    price_change: float,
    oi_change: float,
    price_change_pct: Optional[float] = None,
    oi_change_pct: Optional[float] = None,
) -> OI_BUILDUP_TYPES:
    """
    Classify OI buildup based on price and OI changes.

    Classification:
    - price↑ & OI↑ = Long Buildup (bullish)
    - price↓ & OI↑ = Short Buildup (bearish)
    - price↑ & OI↓ = Short Covering (bullish)
    - price↓ & OI↓ = Long Unwinding (bearish)
    - Otherwise = Neutral

    Args:
        price_change: Change in price (current - previous)
        oi_change: Change in OI (current - previous)
        price_change_pct: Optional percentage change in price
        oi_change_pct: Optional percentage change in OI

    Returns:
        Classification string
    """
    # Use percentage if available, otherwise use absolute
    price_up = (price_change_pct > 0) if price_change_pct is not None else (price_change > 0)
    price_down = (price_change_pct < 0) if price_change_pct is not None else (price_change < 0)
    oi_up = (oi_change_pct > 0) if oi_change_pct is not None else (oi_change > 0)
    oi_down = (oi_change_pct < 0) if oi_change_pct is not None else (oi_change < 0)

    # Small changes are considered neutral
    price_threshold = abs(price_change_pct) > 0.1 if price_change_pct is not None else abs(price_change) > 0.01
    oi_threshold = abs(oi_change_pct) > 1.0 if oi_change_pct is not None else abs(oi_change) > 100

    if not (price_threshold and oi_threshold):
        return "Neutral"

    if price_up and oi_up:
        return "Long Buildup"
    elif price_down and oi_up:
        return "Short Buildup"
    elif price_up and oi_down:
        return "Short Covering"
    elif price_down and oi_down:
        return "Long Unwinding"
    else:
        return "Neutral"


def compute_deltas(
    current_df: pd.DataFrame, previous_df: pd.DataFrame, key_cols: list = ["token", "strike", "option_type"]
) -> pd.DataFrame:
    """
    Compute delta changes (dOI, dVolume, dPrice, etc.) between snapshots.

    Args:
        current_df: Current snapshot DataFrame
        previous_df: Previous snapshot DataFrame
        key_cols: Columns to use for merging

    Returns:
        DataFrame with delta columns added
    """
    if previous_df is None or previous_df.empty:
        # First snapshot - no deltas
        result = current_df.copy()
        result["dOI"] = None
        result["dVolume"] = None
        result["dMid"] = None
        result["dSpread"] = None
        result["dLTP"] = None
        result["oi_buildup"] = "Neutral"
        return result

    # Merge on key columns
    merged = current_df.merge(
        previous_df[key_cols + ["oi", "volume", "mid_price", "bid_ask_spread", "ltp"]],
        on=key_cols,
        how="left",
        suffixes=("", "_prev"),
    )

    # Compute deltas
    result = current_df.copy()

    # dOI
    if "oi_prev" in merged.columns:
        result["dOI"] = merged["oi"] - merged["oi_prev"]
        result["dOI_pct"] = ((merged["oi"] - merged["oi_prev"]) / merged["oi_prev"] * 100).where(
            merged["oi_prev"] > 0, None
        )
    else:
        result["dOI"] = None
        result["dOI_pct"] = None

    # dVolume
    if "volume_prev" in merged.columns:
        result["dVolume"] = merged["volume"] - merged["volume_prev"]
        result["dVolume_pct"] = ((merged["volume"] - merged["volume_prev"]) / merged["volume_prev"] * 100).where(
            merged["volume_prev"] > 0, None
        )
    else:
        result["dVolume"] = None
        result["dVolume_pct"] = None

    # dMid (mid price change)
    if "mid_price_prev" in merged.columns:
        result["dMid"] = merged["mid_price"] - merged["mid_price_prev"]
        result["dMid_pct"] = ((merged["mid_price"] - merged["mid_price_prev"]) / merged["mid_price_prev"] * 100).where(
            merged["mid_price_prev"] > 0, None
        )
    else:
        result["dMid"] = None
        result["dMid_pct"] = None

    # dSpread
    if "bid_ask_spread_prev" in merged.columns:
        result["dSpread"] = merged["bid_ask_spread"] - merged["bid_ask_spread_prev"]
    else:
        result["dSpread"] = None

    # dLTP
    if "ltp_prev" in merged.columns:
        result["dLTP"] = merged["ltp"] - merged["ltp_prev"]
        result["dLTP_pct"] = ((merged["ltp"] - merged["ltp_prev"]) / merged["ltp_prev"] * 100).where(
            merged["ltp_prev"] > 0, None
        )
    else:
        result["dLTP"] = None
        result["dLTP_pct"] = None

    # OI Buildup classification
    result["oi_buildup"] = result.apply(
        lambda row: classify_oi_buildup(row.get("dLTP", 0), row.get("dOI", 0), row.get("dLTP_pct"), row.get("dOI_pct")),
        axis=1,
    )

    return result
