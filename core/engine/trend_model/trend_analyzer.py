"""
Trend Analyzer - Compute RSI, MACD, VWAP, SuperTrend, multi-timeframe trends
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List


def compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Compute Relative Strength Index."""
    if len(prices) < period + 1:
        return pd.Series([50.0] * len(prices), index=prices.index)

    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def compute_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """Compute MACD (Moving Average Convergence Divergence)."""
    if len(prices) < slow:
        return {
            "macd": pd.Series([0.0] * len(prices), index=prices.index),
            "signal": pd.Series([0.0] * len(prices), index=prices.index),
            "histogram": pd.Series([0.0] * len(prices), index=prices.index),
        }

    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


def compute_vwap(prices: pd.Series, volumes: pd.Series = None) -> pd.Series:
    """Compute Volume Weighted Average Price."""
    if volumes is None or volumes.sum() == 0:
        return prices.rolling(window=20).mean()

    vwap = (prices * volumes).cumsum() / volumes.cumsum()
    return vwap.fillna(prices.mean())


def compute_supertrend(prices: pd.Series, period: int = 10, multiplier: float = 3.0) -> Dict[str, pd.Series]:
    """Compute SuperTrend indicator."""
    if len(prices) < period:
        return {"supertrend": prices, "direction": pd.Series([1] * len(prices), index=prices.index)}

    hl_avg = (prices.rolling(period).max() + prices.rolling(period).min()) / 2
    atr = prices.rolling(period).apply(lambda x: x.max() - x.min(), raw=True)

    upper_band = hl_avg + (multiplier * atr)
    lower_band = hl_avg - (multiplier * atr)

    supertrend = pd.Series(index=prices.index, dtype=float)
    direction = pd.Series(index=prices.index, dtype=int)

    for i in range(len(prices)):
        if i == 0:
            supertrend.iloc[i] = upper_band.iloc[i]
            direction.iloc[i] = -1
        else:
            if prices.iloc[i] > supertrend.iloc[i - 1]:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
            else:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = -1

    return {"supertrend": supertrend.fillna(prices), "direction": direction.fillna(1)}


def compute_trend_features(df: pd.DataFrame, price_col: str = "spot", volume_col: str = None) -> pd.DataFrame:
    """
    Compute trend features for DataFrame.

    Args:
        df: DataFrame with price data
        price_col: Column name for prices (default "spot")
        volume_col: Column name for volumes (optional)

    Returns:
        DataFrame with added trend columns
    """
    if df.empty or price_col not in df.columns:
        return df

    df = df.copy()

    # Group by underlying if available
    group_col = "underlying" if "underlying" in df.columns else None

    if group_col:
        grouped = df.groupby(group_col)
    else:
        grouped = [(None, df)]

    all_results = []

    for group_key, group_df in grouped:
        prices = pd.to_numeric(group_df[price_col], errors="coerce").fillna(0)
        volumes = (
            pd.to_numeric(group_df.get(volume_col, pd.Series([1.0] * len(group_df))), errors="coerce").fillna(1.0)
            if volume_col
            else None
        )

        # RSI
        rsi = compute_rsi(prices, period=14)
        group_df["rsi"] = rsi.values

        # MACD
        macd_data = compute_macd(prices, fast=12, slow=26, signal=9)
        group_df["macd"] = macd_data["macd"].values
        group_df["macd_signal"] = macd_data["signal"].values
        group_df["macd_histogram"] = macd_data["histogram"].values

        # VWAP
        vwap = compute_vwap(prices, volumes)
        group_df["vwap"] = vwap.values
        group_df["price_vs_vwap"] = (prices - vwap) / vwap.replace(0, np.nan) * 100.0
        group_df["price_vs_vwap"] = group_df["price_vs_vwap"].fillna(0.0)

        # SuperTrend
        st_data = compute_supertrend(prices, period=10, multiplier=3.0)
        group_df["supertrend"] = st_data["supertrend"].values
        group_df["supertrend_direction"] = st_data["direction"].values

        # Moving averages
        group_df["sma_5"] = prices.rolling(5).mean().fillna(prices).values
        group_df["sma_10"] = prices.rolling(10).mean().fillna(prices).values
        group_df["sma_20"] = prices.rolling(20).mean().fillna(prices).values

        # Trend strength
        group_df["trend_strength"] = (
            (prices > group_df["sma_5"]) * 1.0
            + (prices > group_df["sma_10"]) * 1.0
            + (prices > group_df["sma_20"]) * 1.0
        ) / 3.0

        all_results.append(group_df)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return df


def compute_multi_timeframe_trend(df: pd.DataFrame, price_col: str = "spot") -> pd.DataFrame:
    """
    Compute multi-timeframe trend scores (1m, 3m, 5m, 15m).

    Note: This assumes df has time-series data. For live snapshots,
    we compute based on rolling windows.

    Args:
        df: DataFrame with price data
        price_col: Column name for prices

    Returns:
        DataFrame with multi-timeframe trend scores
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

        # Simulate different timeframes using different rolling windows
        # 1m trend (very short)
        trend_1m = (prices - prices.shift(1)).fillna(0)
        group_df["trend_1m"] = np.sign(trend_1m).values

        # 3m trend (short)
        trend_3m = (prices - prices.shift(3)).fillna(0)
        group_df["trend_3m"] = np.sign(trend_3m).values

        # 5m trend (medium)
        trend_5m = (prices - prices.shift(5)).fillna(0)
        group_df["trend_5m"] = np.sign(trend_5m).values

        # 15m trend (longer)
        trend_15m = (prices - prices.shift(15)).fillna(0)
        group_df["trend_15m"] = np.sign(trend_15m).values

        # Combined trend score (-1 to +1)
        group_df["multi_tf_trend_score"] = (
            group_df["trend_1m"] * 0.1
            + group_df["trend_3m"] * 0.2
            + group_df["trend_5m"] * 0.3
            + group_df["trend_15m"] * 0.4
        ).values

        all_results.append(group_df)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return df
