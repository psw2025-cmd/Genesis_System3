"""
Momentum Analyzer - Compute rate of change, acceleration factor
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def compute_momentum_features(df: pd.DataFrame, price_col: str = "spot") -> pd.DataFrame:
    """
    Compute momentum features: rate of change, acceleration.

    Args:
        df: DataFrame with price data
        price_col: Column name for prices

    Returns:
        DataFrame with momentum features
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

        # Rate of change (ROC) - multiple periods
        roc_1 = prices.pct_change(1).fillna(0.0) * 100.0
        roc_3 = prices.pct_change(3).fillna(0.0) * 100.0
        roc_5 = prices.pct_change(5).fillna(0.0) * 100.0
        roc_10 = prices.pct_change(10).fillna(0.0) * 100.0

        group_df["roc_1"] = roc_1.values
        group_df["roc_3"] = roc_3.values
        group_df["roc_5"] = roc_5.values
        group_df["roc_10"] = roc_10.values

        # Acceleration factor (rate of change of rate of change)
        acceleration = roc_1.diff().fillna(0.0)
        group_df["acceleration"] = acceleration.values

        # Momentum score (weighted average of ROCs)
        momentum_score = (roc_1 * 0.4 + roc_3 * 0.3 + roc_5 * 0.2 + roc_10 * 0.1) / 100.0  # Normalize to -1 to +1 range

        group_df["momentum_score"] = momentum_score.clip(-1.0, 1.0).values

        # Momentum strength (absolute value)
        group_df["momentum_strength"] = np.abs(momentum_score).values

        # Momentum direction
        group_df["momentum_direction"] = np.sign(momentum_score).values

        all_results.append(group_df)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return df
