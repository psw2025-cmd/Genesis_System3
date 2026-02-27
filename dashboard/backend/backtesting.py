"""
Backtesting & Strategy Analysis System
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import pytz

IST = pytz.timezone("Asia/Kolkata")


class BacktestingEngine:
    """
    Backtesting engine for strategy analysis
    """

    def __init__(self):
        self.backtest_results = []

    def run_backtest(
        self, strategy_config: Dict[str, Any], historical_data: List[Dict[str, Any]], initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data

        Args:
            strategy_config: Strategy configuration
            historical_data: Historical price/chain data
            initial_capital: Starting capital

        Returns:
            Backtest results
        """
        if not historical_data:
            return {"status": "ERROR", "message": "No historical data provided"}

        # Convert to DataFrame
        df = pd.DataFrame(historical_data)

        # Initialize tracking
        capital = initial_capital
        positions = []
        trades = []
        equity_curve = [capital]

        # Strategy parameters
        entry_condition = strategy_config.get("entry_condition", {})
        exit_condition = strategy_config.get("exit_condition", {})
        position_size = strategy_config.get("position_size", 0.1)  # 10% of capital
        stop_loss = strategy_config.get("stop_loss", 0.02)  # 2%
        take_profit = strategy_config.get("take_profit", 0.05)  # 5%

        # Simulate trading
        for idx, row in df.iterrows():
            # Check entry conditions
            if self._check_condition(row, entry_condition) and len(positions) < strategy_config.get("max_positions", 5):
                # Enter position
                position_value = capital * position_size
                entry_price = row.get("price", row.get("ltp", 0))
                qty = int(position_value / entry_price) if entry_price > 0 else 0

                if qty > 0:
                    position = {
                        "entry_price": entry_price,
                        "qty": qty,
                        "entry_time": row.get("timestamp", ""),
                        "stop_loss": entry_price * (1 - stop_loss),
                        "take_profit": entry_price * (1 + take_profit),
                    }
                    positions.append(position)
                    capital -= position_value

            # Check exit conditions
            for pos in positions[:]:
                current_price = row.get("price", row.get("ltp", 0))

                # Stop loss
                if current_price <= pos["stop_loss"]:
                    pnl = (current_price - pos["entry_price"]) * pos["qty"]
                    capital += (pos["entry_price"] * pos["qty"]) + pnl
                    trades.append(
                        {
                            "entry_price": pos["entry_price"],
                            "exit_price": current_price,
                            "qty": pos["qty"],
                            "pnl": pnl,
                            "exit_reason": "stop_loss",
                        }
                    )
                    positions.remove(pos)

                # Take profit
                elif current_price >= pos["take_profit"]:
                    pnl = (current_price - pos["entry_price"]) * pos["qty"]
                    capital += (pos["entry_price"] * pos["qty"]) + pnl
                    trades.append(
                        {
                            "entry_price": pos["entry_price"],
                            "exit_price": current_price,
                            "qty": pos["qty"],
                            "pnl": pnl,
                            "exit_reason": "take_profit",
                        }
                    )
                    positions.remove(pos)

                # Exit condition
                elif self._check_condition(row, exit_condition):
                    pnl = (current_price - pos["entry_price"]) * pos["qty"]
                    capital += (pos["entry_price"] * pos["qty"]) + pnl
                    trades.append(
                        {
                            "entry_price": pos["entry_price"],
                            "exit_price": current_price,
                            "qty": pos["qty"],
                            "pnl": pnl,
                            "exit_reason": "exit_signal",
                        }
                    )
                    positions.remove(pos)

            # Update equity curve
            unrealized_pnl = sum((row.get("price", row.get("ltp", 0)) - p["entry_price"]) * p["qty"] for p in positions)
            equity_curve.append(capital + unrealized_pnl)

        # Calculate metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t["pnl"] > 0]
        losing_trades = [t for t in trades if t["pnl"] < 0]

        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_pnl = sum(t["pnl"] for t in trades)
        avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        profit_factor = (
            abs(sum(t["pnl"] for t in winning_trades) / sum(t["pnl"] for t in losing_trades))
            if losing_trades
            else float("inf")
        )

        # Sharpe ratio
        returns = [t["pnl"] / initial_capital for t in trades]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0

        # Max drawdown
        peak = equity_curve[0]
        max_dd = 0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        result = {
            "status": "ok",
            "initial_capital": initial_capital,
            "final_capital": capital,
            "total_return": (capital - initial_capital) / initial_capital * 100,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate * 100,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd * 100,
            "equity_curve": equity_curve,
            "trades": trades,
        }

        self.backtest_results.append(result)
        return result

    def _check_condition(self, row: pd.Series, condition: Dict[str, Any]) -> bool:
        """Check if condition is met"""
        if not condition:
            return False

        # Simple condition checking
        # Can be extended for complex conditions
        field = condition.get("field")
        operator = condition.get("operator", ">")
        value = condition.get("value", 0)

        if field not in row:
            return False

        row_value = row[field]

        if operator == ">":
            return row_value > value
        elif operator == "<":
            return row_value < value
        elif operator == ">=":
            return row_value >= value
        elif operator == "<=":
            return row_value <= value
        elif operator == "==":
            return row_value == value

        return False

    def compare_strategies(
        self, strategies: List[Dict[str, Any]], historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare multiple strategies"""
        results = {}

        for strategy in strategies:
            name = strategy.get("name", "Unknown")
            result = self.run_backtest(strategy, historical_data)
            results[name] = result

        # Find best strategy
        best_strategy = max(results.items(), key=lambda x: x[1].get("total_return", 0))

        return {
            "status": "ok",
            "strategies": results,
            "best_strategy": {"name": best_strategy[0], "metrics": best_strategy[1]},
        }


# Global instance
_backtesting_engine = BacktestingEngine()


def get_backtesting_engine() -> BacktestingEngine:
    """Get global backtesting engine instance"""
    return _backtesting_engine
