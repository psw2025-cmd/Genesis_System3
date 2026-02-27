"""
Angel One Index Options - Dynamic SL/TP Engine

Computes dynamic stop-loss and take-profit based on volatility and ATR.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def compute_dynamic_sl_tp(
    entry_price: float,
    volatility: float,
    atr: float,
    risk_reward: float = 2.0,
) -> Dict[str, float]:
    """
    Compute dynamic SL and TP based on volatility.

    Args:
        entry_price: Entry price
        volatility: Price volatility
        atr: Average True Range
        risk_reward: Risk-reward ratio

    Returns:
        Dict with dynamic_sl, dynamic_tp, atr_value
    """
    if entry_price <= 0 or risk_reward < 1.0:
        return {
            "dynamic_sl": entry_price * 0.95,
            "dynamic_tp": entry_price * 1.10,
            "atr_value": atr,
            "adjustment_reason": "INVALID_INPUTS",
        }

    # Use ATR if available, else use volatility
    if atr > 0:
        risk_amount = atr
    elif volatility > 0:
        risk_amount = entry_price * volatility / 100.0
    else:
        # Fallback to fixed percentage
        risk_amount = entry_price * 0.05

    # Dynamic SL: entry - risk_amount
    dynamic_sl = entry_price - risk_amount
    if dynamic_sl <= 0:
        dynamic_sl = entry_price * 0.95

    # Dynamic TP: entry + risk_amount * risk_reward
    dynamic_tp = entry_price + risk_amount * risk_reward

    return {
        "dynamic_sl": float(dynamic_sl),
        "dynamic_tp": float(dynamic_tp),
        "atr_value": float(atr),
        "adjustment_reason": "ATR_BASED" if atr > 0 else "VOLATILITY_BASED",
    }


def adjust_sl_tp_dynamically(
    trade_row: pd.Series,
    market_data: pd.DataFrame,
) -> Dict[str, float]:
    """
    Adjust SL/TP dynamically based on current market conditions.

    Args:
        trade_row: Trade row with entry details
        market_data: Recent market data

    Returns:
        Dict with adjusted SL/TP
    """
    entry_price = float(trade_row.get("entry_price", 0.0))
    if entry_price <= 0:
        return {
            "dynamic_sl": 0.0,
            "dynamic_tp": 0.0,
            "atr_value": 0.0,
            "adjustment_reason": "INVALID_ENTRY",
        }

    # Compute ATR from market data
    if market_data.empty or "high" not in market_data.columns:
        # Fallback to default
        return compute_dynamic_sl_tp(entry_price, 0.0, 0.0)

    atr = compute_atr(
        market_data["high"],
        market_data["low"],
        market_data.get("close", market_data.get("spot", pd.Series())),
        period=14,
    )

    atr_value = atr.iloc[-1] if len(atr) > 0 else 0.0
    volatility = market_data.get("spot", pd.Series()).std() if "spot" in market_data.columns else 0.0

    return compute_dynamic_sl_tp(entry_price, volatility, atr_value)


def compute_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """
    Compute Average True Range (ATR).

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period

    Returns:
        Series with ATR values
    """
    if len(high) < 2 or len(low) < 2 or len(close) < 2:
        return pd.Series([0.0] * len(high))

    if period < 1:
        period = 14

    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR = moving average of TR
    atr = tr.rolling(window=period, min_periods=1).mean()

    return atr


def main() -> None:
    """Test dynamic SL/TP engine."""
    print("=== ANGEL ONE INDEX OPTIONS - DYNAMIC SL/TP ENGINE ===")
    result = compute_dynamic_sl_tp(entry_price=100.0, volatility=2.0, atr=5.0, risk_reward=2.0)
    print(f"Dynamic SL/TP: {result}")


if __name__ == "__main__":
    main()
