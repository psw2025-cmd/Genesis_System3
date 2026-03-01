"""
Institutional Entry/Exit Rules - Professional Profit Harvesting
Upgraded for World-Class AI Trading performance.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

def compute_dynamic_sl_tp(
    entry_price: float, volatility: float, atr: float = None, risk_reward: float = 2.5
) -> Dict[str, float]:
    """
    Compute institutional-grade dynamic stop loss and multi-stage target prices.
    Uses Volatility-Aware Sizing.
    """
    if entry_price <= 0:
        return {"stop_loss": 0, "target_price": 0, "partial_target": 0}

    # Volatility multiplier (Standard institutional 1.5 - 2.5 range)
    vol = max(volatility, 0.15) # Floor at 15% IV
    
    # Calculate Risk Amount (Institutional 1.5 Sigma)
    risk_amount = entry_price * vol * 0.4 
    
    stop_loss = entry_price - risk_amount
    target_price = entry_price + (risk_amount * risk_reward)
    
    # NEW: Partial Profit Target (1.2R) - Standard for winning desks
    partial_target = entry_price + (risk_amount * 1.2)

    return {
        "stop_loss": float(max(stop_loss, entry_price * 0.85)),
        "target_price": float(target_price),
        "partial_target": float(partial_target),
        "risk_amount": float(risk_amount)
    }

def compute_entry_signals(df: pd.DataFrame, score_col: str = "final_score") -> pd.DataFrame:
    """
    Compute high-conviction entry signals.
    """
    if df.empty: return df
    df = df.copy()

    score = pd.to_numeric(df.get(score_col, 0), errors="coerce").fillna(0.0)

    # World-Class Thresholds (Raising the bar for quality)
    HIGH_CONVICTION = 0.65 
    
    df["entry_buy"] = (score >= HIGH_CONVICTION).astype(int)
    df["entry_sell"] = (score <= -HIGH_CONVICTION).astype(int)
    df["entry_hold"] = ((score > -HIGH_CONVICTION) & (score < HIGH_CONVICTION)).astype(int)

    # Metadata for dashboard
    df["conviction_level"] = np.where(score.abs() >= 0.8, "ULTRA", 
                             np.where(score.abs() >= 0.65, "HIGH", "LOW"))

    return df

def compute_exit_signals(
    df: pd.DataFrame,
    entry_price_col: str = "entry_price",
    current_price_col: str = "ltp",
    stop_loss_col: str = "stop_loss",
    target_col: str = "target_price",
    partial_target_col: str = "partial_target"
) -> pd.DataFrame:
    """
    Compute exit signals with Partial Profit Harvesting logic.
    """
    if df.empty: return df
    df = df.copy()

    # Ensure columns
    for col in [entry_price_col, current_price_col, stop_loss_col, target_col, partial_target_col]:
        if col not in df.columns: df[col] = 0.0

    cp = pd.to_numeric(df[current_price_col], errors="coerce").fillna(0.0)
    sl = pd.to_numeric(df[stop_loss_col], errors="coerce").fillna(0.0)
    tp = pd.to_numeric(df[target_col], errors="coerce").fillna(0.0)
    pt = pd.to_numeric(df[partial_target_col], errors="coerce").fillna(0.0)

    # 1. Stop Loss Hit
    df["exit_sl_hit"] = (cp <= sl).astype(int)

    # 2. Main Target Hit
    df["exit_target_hit"] = (cp >= tp).astype(int)
    
    # 3. Partial Target Hit (Signal to sell 50%)
    df["exit_partial_hit"] = ((cp >= pt) & (pt > 0)).astype(int)

    # Final Combined Exit Signal
    df["exit_signal"] = ((df["exit_sl_hit"] == 1) | (df["exit_target_hit"] == 1)).astype(int)
    
    return df
