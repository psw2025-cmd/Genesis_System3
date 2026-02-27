"""
Entry/Exit Rules - Compute entry signals, dynamic SL/Target, trailing SL
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def compute_dynamic_sl_tp(
    entry_price: float, volatility: float, atr: float = None, risk_reward: float = 2.0
) -> Dict[str, float]:
    """
    Compute dynamic stop loss and target price.

    Args:
        entry_price: Entry price
        volatility: Volatility (IV or historical)
        atr: Average True Range (optional)
        risk_reward: Risk-reward ratio (default 2.0)

    Returns:
        Dict with stop_loss and target_price
    """
    if entry_price <= 0 or volatility <= 0:
        return {
            "stop_loss": entry_price * 0.95,  # Default 5% SL
            "target_price": entry_price * 1.10,  # Default 10% target
        }

    # Use ATR if available, otherwise use volatility-based
    if atr and atr > 0:
        risk_amount = atr * 1.5
    else:
        risk_amount = entry_price * volatility * 0.5

    stop_loss = entry_price - risk_amount
    target_price = entry_price + (risk_amount * risk_reward)

    # Ensure stop loss is not negative
    stop_loss = max(stop_loss, entry_price * 0.90)

    return {"stop_loss": float(stop_loss), "target_price": float(target_price), "risk_amount": float(risk_amount)}


def compute_entry_signals(df: pd.DataFrame, score_col: str = "final_score") -> pd.DataFrame:
    """
    Compute entry signals based on score.

    Args:
        df: DataFrame with scores
        score_col: Column name for final score

    Returns:
        DataFrame with entry signals
    """
    if df.empty:
        return df

    df = df.copy()

    if score_col not in df.columns:
        df[score_col] = 0.0

    score = pd.to_numeric(df[score_col], errors="coerce").fillna(0.0)

    # Entry signals
    df["entry_buy"] = (score > 0.55).astype(int)
    df["entry_sell"] = (score < -0.55).astype(int)
    df["entry_hold"] = ((score >= -0.55) & (score <= 0.55)).astype(int)

    # Entry confidence (based on score magnitude)
    df["entry_confidence"] = np.abs(score).clip(0.0, 1.0).values

    return df


def compute_exit_signals(
    df: pd.DataFrame,
    entry_price_col: str = "entry_price",
    current_price_col: str = "ltp",
    stop_loss_col: str = "stop_loss",
    target_col: str = "target_price",
) -> pd.DataFrame:
    """
    Compute exit signals based on SL/Target.

    Args:
        df: DataFrame with trade data
        entry_price_col: Column name for entry price
        current_price_col: Column name for current price
        stop_loss_col: Column name for stop loss
        target_col: Column name for target price

    Returns:
        DataFrame with exit signals
    """
    if df.empty:
        return df

    df = df.copy()

    # Ensure columns exist
    for col in [entry_price_col, current_price_col, stop_loss_col, target_col]:
        if col not in df.columns:
            df[col] = 0.0

    entry_price = pd.to_numeric(df[entry_price_col], errors="coerce").fillna(0.0)
    current_price = pd.to_numeric(df[current_price_col], errors="coerce").fillna(0.0)
    stop_loss = pd.to_numeric(df[stop_loss_col], errors="coerce").fillna(0.0)
    target = pd.to_numeric(df[target_col], errors="coerce").fillna(0.0)

    # Exit signals
    df["exit_sl_hit"] = (
        ((df["entry_buy"] == 1) & (current_price <= stop_loss))
        | ((df["entry_sell"] == 1) & (current_price >= stop_loss))
    ).astype(int)

    df["exit_target_hit"] = (
        ((df["entry_buy"] == 1) & (current_price >= target)) | ((df["entry_sell"] == 1) & (current_price <= target))
    ).astype(int)

    # Trailing stop logic (simplified)
    df["trailing_sl"] = stop_loss  # Can be enhanced with trailing logic

    # Exit signal
    df["exit_signal"] = ((df["exit_sl_hit"] == 1) | (df["exit_target_hit"] == 1)).astype(int)

    return df


def compute_trailing_stop(
    entry_price: float, current_price: float, highest_price: float, stop_loss: float, trailing_pct: float = 0.02
) -> float:
    """
    Compute trailing stop loss.

    Args:
        entry_price: Entry price
        current_price: Current price
        highest_price: Highest price since entry
        stop_loss: Initial stop loss
        trailing_pct: Trailing percentage (default 2%)

    Returns:
        Updated stop loss
    """
    if entry_price <= 0:
        return stop_loss

    # For long positions
    if current_price > entry_price:
        trailing_sl = highest_price * (1 - trailing_pct)
        return max(trailing_sl, stop_loss)

    return stop_loss
