"""
Volatility Analyzer - Compute IV, IVP, IVR, volatility regimes
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def compute_iv_percentile(iv_current: float, iv_history: pd.Series) -> float:
    """
    Compute IV percentile (0-100).

    Args:
        iv_current: Current IV value
        iv_history: Historical IV values

    Returns:
        Percentile rank (0.0 to 100.0)
    """
    if len(iv_history) == 0:
        return 50.0

    iv_history = iv_history.dropna()
    if len(iv_history) == 0:
        return 50.0

    percentile = (iv_history < iv_current).sum() / len(iv_history) * 100.0
    return float(percentile)


def compute_iv_rank(iv_current: float, iv_min: float, iv_max: float) -> float:
    """
    Compute IV rank (0-100).

    Args:
        iv_current: Current IV value
        iv_min: Minimum IV in lookback period
        iv_max: Maximum IV in lookback period

    Returns:
        IV rank (0.0 to 100.0)
    """
    if iv_max <= iv_min:
        return 50.0

    rank = ((iv_current - iv_min) / (iv_max - iv_min)) * 100.0
    return float(np.clip(rank, 0.0, 100.0))


def compute_volatility_features(df: pd.DataFrame, iv_col: str = "iv", lookback_days: int = 30) -> pd.DataFrame:
    """
    Compute volatility features: IV, IV percentile, IV rank.

    Args:
        df: DataFrame with IV data
        iv_col: Column name for IV
        lookback_days: Days to look back for percentile/rank

    Returns:
        DataFrame with added volatility columns
    """
    if df.empty:
        return df

    df = df.copy()

    # Ensure IV column exists
    if iv_col not in df.columns:
        if "iv_estimate" in df.columns:
            df[iv_col] = df["iv_estimate"]
        elif "implied_volatility" in df.columns:
            df[iv_col] = df["implied_volatility"]
        else:
            df[iv_col] = 0.0

    df[iv_col] = pd.to_numeric(df[iv_col], errors="coerce").fillna(0.0)

    # Group by underlying if available
    group_col = "underlying" if "underlying" in df.columns else None

    if group_col:
        grouped = df.groupby(group_col)
    else:
        grouped = [(None, df)]

    all_results = []

    for group_key, group_df in grouped:
        iv_series = group_df[iv_col]

        # IV percentile (requires historical data)
        # For live data, we use rolling window
        if len(group_df) > 1:
            iv_percentiles = []
            for i in range(len(group_df)):
                if i < lookback_days:
                    iv_percentiles.append(50.0)  # Default
                else:
                    hist_iv = iv_series.iloc[max(0, i - lookback_days) : i]
                    iv_percentiles.append(compute_iv_percentile(iv_series.iloc[i], hist_iv))
            group_df["iv_percentile"] = iv_percentiles
        else:
            group_df["iv_percentile"] = 50.0

        # IV rank
        if len(group_df) > 1:
            rolling_min = iv_series.rolling(window=min(lookback_days, len(group_df)), min_periods=1).min()
            rolling_max = iv_series.rolling(window=min(lookback_days, len(group_df)), min_periods=1).max()
            iv_ranks = []
            for i in range(len(group_df)):
                iv_ranks.append(compute_iv_rank(iv_series.iloc[i], rolling_min.iloc[i], rolling_max.iloc[i]))
            group_df["iv_rank"] = iv_ranks
        else:
            group_df["iv_rank"] = 50.0

        # Volatility regime classification
        def classify_regime(iv_val, iv_pct, iv_rnk):
            if iv_pct >= 75 or iv_rnk >= 75:
                return "HIGH"
            elif iv_pct <= 25 or iv_rnk <= 25:
                return "LOW"
            else:
                return "MEDIUM"

        group_df["volatility_regime"] = group_df.apply(
            lambda row: classify_regime(row[iv_col], row.get("iv_percentile", 50.0), row.get("iv_rank", 50.0)), axis=1
        )

        # Volatility score (-1 to +1, where +1 = high vol, -1 = low vol)
        group_df["volatility_score"] = ((group_df["iv_percentile"] - 50.0) / 50.0).clip(-1.0, 1.0).values

        all_results.append(group_df)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return df


def detect_volatility_regime(df: pd.DataFrame, iv_col: str = "iv", window: int = 20) -> pd.DataFrame:
    """
    Detect volatility regime (high/low/medium).

    Args:
        df: DataFrame with IV data
        iv_col: Column name for IV
        window: Rolling window for regime detection

    Returns:
        DataFrame with volatility regime classification
    """
    if df.empty:
        return df

    df = compute_volatility_features(df, iv_col=iv_col)

    # Additional regime detection based on IV changes
    if "underlying" in df.columns:
        grouped = df.groupby("underlying")
    else:
        grouped = [(None, df)]

    all_results = []

    for group_key, group_df in grouped:
        iv_series = pd.to_numeric(group_df.get(iv_col, 0.0), errors="coerce").fillna(0.0)

        # IV change rate
        iv_change = iv_series.pct_change().fillna(0.0)
        group_df["iv_change_rate"] = iv_change.values

        # Volatility spike detection
        iv_std = iv_series.rolling(window=min(window, len(group_df))).std().fillna(0.0)
        iv_mean = iv_series.rolling(window=min(window, len(group_df))).mean().fillna(0.0)

        group_df["iv_spike"] = ((iv_series > (iv_mean + 2 * iv_std)).astype(int)).values

        # Regime transition
        group_df["regime_transition"] = (
            (group_df["volatility_regime"] != group_df["volatility_regime"].shift(1)).astype(int).fillna(0).values
        )

        all_results.append(group_df)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return df
