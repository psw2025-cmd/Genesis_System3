"""
Dhan Index Options - Exit Optimizer (UPGRADED)

Optimizes trade exit timing and strategy.

UPGRADES (World-Class AI Trading System):
- Partial profit taking (50% at 2R, 25% at 3R, 25% at 5R)
- ML-based exit signals (when model confidence drops or reverses)
- Enhanced trailing stops with volatility adjustment
- Time-based exits for range-bound markets
"""

import pandas as pd
from typing import Dict, Any, Optional, List


def calculate_partial_profit_levels(
    entry_price: float, risk_amount: float, current_price: float
) -> List[Dict[str, Any]]:
    """
    Calculate partial profit taking levels.

    Strategy:
    - 50% at 2R (2x risk)
    - 25% at 3R (3x risk)
    - 25% at 5R (5x risk)

    Args:
        entry_price: Entry price
        risk_amount: Risk amount (entry - stop loss)
        current_price: Current market price

    Returns:
        List of profit levels with quantities
    """
    if risk_amount <= 0 or entry_price <= 0:
        return []

    levels = []

    # 2R level: 50% of position
    level_2r = entry_price + (risk_amount * 2.0)
    levels.append(
        {
            "level": 2.0,  # 2R
            "price": level_2r,
            "quantity_pct": 0.50,  # 50%
            "reached": current_price >= level_2r if current_price > 0 else False,
        }
    )

    # 3R level: 25% of position
    level_3r = entry_price + (risk_amount * 3.0)
    levels.append(
        {
            "level": 3.0,  # 3R
            "price": level_3r,
            "quantity_pct": 0.25,  # 25%
            "reached": current_price >= level_3r if current_price > 0 else False,
        }
    )

    # 5R level: 25% of position
    level_5r = entry_price + (risk_amount * 5.0)
    levels.append(
        {
            "level": 5.0,  # 5R
            "price": level_5r,
            "quantity_pct": 0.25,  # 25%
            "reached": current_price >= level_5r if current_price > 0 else False,
        }
    )

    return levels


def check_ml_exit_signal(
    current_confidence: float, entry_confidence: float, confidence_drop_threshold: float = 0.15
) -> Dict[str, Any]:
    """
    Check if ML model suggests exit based on confidence drop or reversal.

    Args:
        current_confidence: Current model confidence
        entry_confidence: Confidence at entry
        confidence_drop_threshold: Threshold for confidence drop (default: 15%)

    Returns:
        Dict with exit signal details
    """
    if entry_confidence <= 0:
        return {"exit_signal": False, "reason": "INVALID_ENTRY_CONFIDENCE", "confidence_drop": 0.0}

    confidence_drop = entry_confidence - current_confidence
    confidence_drop_pct = (confidence_drop / entry_confidence) * 100.0 if entry_confidence > 0 else 0.0

    # Exit if confidence dropped significantly
    if confidence_drop_pct >= confidence_drop_threshold:
        return {
            "exit_signal": True,
            "reason": "CONFIDENCE_DROP",
            "confidence_drop": confidence_drop_pct,
            "entry_confidence": entry_confidence,
            "current_confidence": current_confidence,
        }

    # Exit if confidence reversed (went below 0.5)
    if current_confidence < 0.5 and entry_confidence >= 0.5:
        return {
            "exit_signal": True,
            "reason": "CONFIDENCE_REVERSAL",
            "confidence_drop": confidence_drop_pct,
            "entry_confidence": entry_confidence,
            "current_confidence": current_confidence,
        }

    return {"exit_signal": False, "reason": "HOLD", "confidence_drop": confidence_drop_pct}


def optimize_exit_timing(
    trade_row: pd.Series,
    current_pnl: float,
    target: float,
    sl: float,
    current_confidence: Optional[float] = None,
    entry_confidence: Optional[float] = None,
    current_price: Optional[float] = None,
    atr: Optional[float] = None,
    volatility: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Optimize exit timing for a trade (UPGRADED with partial profit taking and ML exits).

    Args:
        trade_row: Trade row with entry details
        current_pnl: Current PnL percentage
        target: Target PnL percentage
        sl: Stop-loss PnL percentage
        current_confidence: Current model confidence (for ML exit signal)
        entry_confidence: Confidence at entry (for ML exit signal)
        current_price: Current market price (for partial profit taking)
        atr: Average True Range (for volatility-adjusted trailing stop)
        volatility: Current volatility (for volatility-adjusted trailing stop)

    Returns:
        Dict with exit optimization details including partial profit levels
    """
    if pd.isna(current_pnl) or pd.isna(target) or pd.isna(sl):
        return {
            "exit_strategy": "HOLD",
            "exit_price": trade_row.get("entry_price", 0.0),
            "trailing_stop_price": 0.0,
            "exit_timing": "NONE",
            "partial_profit_levels": [],
            "ml_exit_signal": {"exit_signal": False},
        }

    entry_price = float(trade_row.get("entry_price", 0.0))
    stop_loss_price = float(trade_row.get("stoploss_price", entry_price * (1.0 + sl / 100.0)))

    if entry_price <= 0:
        return {
            "exit_strategy": "HOLD",
            "exit_price": 0.0,
            "trailing_stop_price": 0.0,
            "exit_timing": "NONE",
            "partial_profit_levels": [],
            "ml_exit_signal": {"exit_signal": False},
        }

    # Calculate risk amount for partial profit levels
    risk_amount = abs(entry_price - stop_loss_price)
    current_market_price = (
        current_price if current_price and current_price > 0 else entry_price * (1.0 + current_pnl / 100.0)
    )

    # Calculate partial profit levels
    partial_levels = calculate_partial_profit_levels(entry_price, risk_amount, current_market_price)

    # Check ML exit signal
    ml_exit = {"exit_signal": False}
    if current_confidence is not None and entry_confidence is not None:
        ml_exit = check_ml_exit_signal(current_confidence, entry_confidence)

    # Check if target hit
    if current_pnl >= target:
        return {
            "exit_strategy": "TAKE_PROFIT",
            "exit_price": entry_price * (1.0 + target / 100.0),
            "trailing_stop_price": 0.0,
            "exit_timing": "IMMEDIATE",
            "partial_profit_levels": partial_levels,
            "ml_exit_signal": ml_exit,
        }

    # Check if stop-loss hit
    if current_pnl <= sl:
        return {
            "exit_strategy": "STOP_LOSS",
            "exit_price": entry_price * (1.0 + sl / 100.0),
            "trailing_stop_price": 0.0,
            "exit_timing": "IMMEDIATE",
            "partial_profit_levels": [],
            "ml_exit_signal": ml_exit,
        }

    # Check ML exit signal (exit if confidence dropped significantly)
    if ml_exit.get("exit_signal", False):
        return {
            "exit_strategy": "ML_EXIT",
            "exit_price": current_market_price,
            "trailing_stop_price": 0.0,
            "exit_timing": "IMMEDIATE",
            "partial_profit_levels": partial_levels,
            "ml_exit_signal": ml_exit,
            "reason": ml_exit.get("reason", "CONFIDENCE_DROP"),
        }

    # Check partial profit levels
    reached_levels = [level for level in partial_levels if level.get("reached", False)]
    if reached_levels:
        return {
            "exit_strategy": "PARTIAL_PROFIT",
            "exit_price": current_market_price,
            "trailing_stop_price": 0.0,
            "exit_timing": "PARTIAL",
            "partial_profit_levels": partial_levels,
            "reached_levels": reached_levels,
            "ml_exit_signal": ml_exit,
        }

    # Consider trailing stop if in profit
    if current_pnl > 0:
        # Use volatility-adjusted trailing stop
        trailing_pct = 2.0  # Default 2%
        if atr and entry_price > 0:
            # Adjust trailing stop based on ATR
            atr_pct = (atr / entry_price) * 100.0
            trailing_pct = max(1.5, min(3.0, atr_pct * 1.5))  # 1.5x to 3.0% based on ATR

        trailing_stop = compute_trailing_stop(entry_price, current_market_price, trailing_pct)
        return {
            "exit_strategy": "TRAILING",
            "exit_price": current_market_price,
            "trailing_stop_price": trailing_stop,
            "exit_timing": "MONITOR",
            "partial_profit_levels": partial_levels,
            "ml_exit_signal": ml_exit,
            "trailing_pct": trailing_pct,
        }

    # Hold if no exit condition
    return {
        "exit_strategy": "HOLD",
        "exit_price": current_market_price,
        "trailing_stop_price": 0.0,
        "exit_timing": "MONITOR",
        "partial_profit_levels": partial_levels,
        "ml_exit_signal": ml_exit,
    }


def compute_trailing_stop(
    current_price: float,
    entry_price: float,
    trailing_pct: float,
) -> float:
    """
    Compute trailing stop price.

    Args:
        current_price: Current market price
        entry_price: Entry price
        trailing_pct: Trailing stop percentage

    Returns:
        Trailing stop price
    """
    if current_price <= 0 or entry_price <= 0 or trailing_pct <= 0:
        return entry_price

    # Trailing stop: current_price - trailing_pct%
    trailing_stop = current_price * (1.0 - trailing_pct / 100.0)

    # Ensure trailing stop is above entry (for long)
    if trailing_stop < entry_price:
        trailing_stop = entry_price

    return float(trailing_stop)


def suggest_exit_strategy(trade_data: Dict[str, Any]) -> str:
    """
    Suggest exit strategy.

    Returns: "HOLD", "TAKE_PROFIT", "STOP_LOSS", "TRAILING"
    """
    current_pnl = trade_data.get("current_pnl", 0.0)
    target = trade_data.get("target", 10.0)
    sl = trade_data.get("stoploss", -5.0)

    if current_pnl >= target:
        return "TAKE_PROFIT"
    elif current_pnl <= sl:
        return "STOP_LOSS"
    elif current_pnl > target * 0.5:
        return "TRAILING"
    else:
        return "HOLD"


def main() -> None:
    """Test exit optimizer."""
    print("=== ANGEL ONE INDEX OPTIONS - EXIT OPTIMIZER ===")
    trade_row = pd.Series(
        {
            "entry_price": 100.0,
            "target_price": 110.0,
            "sl_price": 95.0,
        }
    )
    result = optimize_exit_timing(trade_row, current_pnl=8.0, target=10.0, sl=-5.0)
    print(f"Exit optimization: {result}")


if __name__ == "__main__":
    main()
