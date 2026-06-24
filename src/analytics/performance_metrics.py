"""
Performance Metrics - Advanced analytics for trading performance
Based on multi-AI consultation for comprehensive performance tracking
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class PerformanceMetrics:
    """
    Calculate advanced performance metrics for trading.

    Metrics:
    1. Sharpe Ratio
    2. Profit Factor
    3. Calmar Ratio
    4. Sortino Ratio
    5. Win Rate
    6. Average Win/Loss
    7. Maximum Drawdown
    8. Recovery Factor
    """

    def __init__(self, risk_free_rate: float = 0.06):
        """
        Initialize performance metrics calculator.

        Args:
            risk_free_rate: Risk-free rate (default: 6% annual)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_sharpe_ratio(self, returns: List[float], periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe Ratio.

        Formula: (Avg Return - Risk Free Rate) / Std Dev

        Args:
            returns: List of returns
            periods_per_year: Number of periods per year (252 for daily)

        Returns:
            Sharpe Ratio
        """
        if not returns or len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)
        avg_return = np.mean(returns_array)
        std_return = np.std(returns_array)

        if std_return == 0:
            return 0.0

        # Annualize
        annual_return = avg_return * periods_per_year
        annual_std = std_return * np.sqrt(periods_per_year)
        annual_rf = self.risk_free_rate

        sharpe = (annual_return - annual_rf) / annual_std

        return float(sharpe)

    def calculate_profit_factor(self, wins: List[float], losses: List[float]) -> float:
        """
        Calculate Profit Factor.

        Formula: Total Wins / Total Losses

        Args:
            wins: List of winning trade PnLs
            losses: List of losing trade PnLs

        Returns:
            Profit Factor
        """
        total_wins = sum(wins) if wins else 0.0
        total_losses = abs(sum(losses)) if losses else 0.0

        if total_losses == 0:
            return float("inf") if total_wins > 0 else 0.0

        profit_factor = total_wins / total_losses

        return float(profit_factor)

    def calculate_calmar_ratio(self, annual_return: float, max_drawdown: float) -> float:
        """
        Calculate Calmar Ratio.

        Formula: Annual Return / Max Drawdown

        Args:
            annual_return: Annual return (e.g., 0.20 for 20%)
            max_drawdown: Maximum drawdown (e.g., 0.15 for 15%)

        Returns:
            Calmar Ratio
        """
        if max_drawdown == 0:
            return 0.0

        calmar = annual_return / abs(max_drawdown)

        return float(calmar)

    def calculate_sortino_ratio(self, returns: List[float], periods_per_year: int = 252) -> float:
        """
        Calculate Sortino Ratio (only penalizes downside volatility).

        Formula: (Avg Return - Risk Free Rate) / Downside Deviation

        Args:
            returns: List of returns
            periods_per_year: Number of periods per year

        Returns:
            Sortino Ratio
        """
        if not returns or len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)
        avg_return = np.mean(returns_array)

        # Calculate downside deviation (only negative returns)
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) == 0:
            downside_std = 0.0
        else:
            downside_std = np.std(downside_returns)

        if downside_std == 0:
            return 0.0

        # Annualize
        annual_return = avg_return * periods_per_year
        annual_downside_std = downside_std * np.sqrt(periods_per_year)
        annual_rf = self.risk_free_rate

        sortino = (annual_return - annual_rf) / annual_downside_std

        return float(sortino)

    def calculate_max_drawdown(self, equity_curve: List[float]) -> Dict:
        """
        Calculate Maximum Drawdown.

        Args:
            equity_curve: List of equity values over time

        Returns:
            Dict with max drawdown and details
        """
        if not equity_curve or len(equity_curve) < 2:
            return {"max_drawdown": 0.0, "max_drawdown_pct": 0.0, "peak": 0.0, "trough": 0.0}

        equity_array = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - peak) / peak
        max_dd = np.min(drawdown)
        max_dd_pct = abs(max_dd) * 100

        # Find peak and trough
        max_dd_idx = np.argmin(drawdown)
        peak_value = peak[max_dd_idx]
        trough_value = equity_array[max_dd_idx]

        return {
            "max_drawdown": float(max_dd),
            "max_drawdown_pct": float(max_dd_pct),
            "peak": float(peak_value),
            "trough": float(trough_value),
            "recovery_factor": float(peak_value / trough_value) if trough_value > 0 else 0.0,
        }

    def calculate_win_rate(self, trades: List[Dict]) -> Dict:
        """
        Calculate win rate and related metrics.

        Args:
            trades: List of trade dicts with 'realized_pnl' or 'pnl'

        Returns:
            Dict with win rate metrics
        """
        if not trades:
            return {
                "win_rate": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
            }

        wins = []
        losses = []

        for trade in trades:
            pnl = trade.get("realized_pnl", trade.get("pnl", 0))
            if pnl > 0:
                wins.append(pnl)
            elif pnl < 0:
                losses.append(pnl)

        total_trades = len(trades)
        winning_trades = len(wins)
        losing_trades = len(losses)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0
        largest_win = max(wins) if wins else 0.0
        largest_loss = min(losses) if losses else 0.0

        return {
            "win_rate": float(win_rate),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "largest_win": float(largest_win),
            "largest_loss": float(largest_loss),
        }

    def calculate_all_metrics(
        self, trades: List[Dict], equity_curve: Optional[List[float]] = None, returns: Optional[List[float]] = None
    ) -> Dict:
        """
        Calculate all performance metrics.

        Args:
            trades: List of trade dicts
            equity_curve: Equity curve over time (optional)
            returns: List of returns (optional)

        Returns:
            Dict with all metrics
        """
        # Win rate metrics
        win_rate_metrics = self.calculate_win_rate(trades)

        # Extract wins and losses
        wins = [t.get("realized_pnl", t.get("pnl", 0)) for t in trades if t.get("realized_pnl", t.get("pnl", 0)) > 0]
        losses = [t.get("realized_pnl", t.get("pnl", 0)) for t in trades if t.get("realized_pnl", t.get("pnl", 0)) < 0]

        # Profit Factor
        profit_factor = self.calculate_profit_factor(wins, losses)

        # Returns (if not provided, calculate from trades)
        if returns is None:
            returns = [t.get("realized_pnl", t.get("pnl", 0)) / 1000.0 for t in trades]  # Normalize

        # Sharpe Ratio
        sharpe = self.calculate_sharpe_ratio(returns)

        # Sortino Ratio
        sortino = self.calculate_sortino_ratio(returns)

        # Max Drawdown
        if equity_curve is None:
            # Calculate from trades
            equity = 0.0
            equity_curve = []
            for trade in trades:
                equity += trade.get("realized_pnl", trade.get("pnl", 0))
                equity_curve.append(equity)

        drawdown_metrics = self.calculate_max_drawdown(equity_curve)

        # Calmar Ratio (if annual return can be estimated)
        if len(returns) > 0:
            avg_return = np.mean(returns)
            annual_return = avg_return * 252  # Assume daily
            calmar = self.calculate_calmar_ratio(annual_return, drawdown_metrics["max_drawdown"])
        else:
            calmar = 0.0

        # Total PnL
        total_pnl = sum(t.get("realized_pnl", t.get("pnl", 0)) for t in trades)

        # Average trade
        avg_trade = total_pnl / len(trades) if trades else 0.0

        return {
            "total_pnl": float(total_pnl),
            "total_trades": win_rate_metrics["total_trades"],
            "win_rate": win_rate_metrics["win_rate"],
            "winning_trades": win_rate_metrics["winning_trades"],
            "losing_trades": win_rate_metrics["losing_trades"],
            "avg_win": win_rate_metrics["avg_win"],
            "avg_loss": win_rate_metrics["avg_loss"],
            "largest_win": win_rate_metrics["largest_win"],
            "largest_loss": win_rate_metrics["largest_loss"],
            "profit_factor": float(profit_factor),
            "sharpe_ratio": float(sharpe),
            "sortino_ratio": float(sortino),
            "calmar_ratio": float(calmar),
            "max_drawdown": drawdown_metrics["max_drawdown"],
            "max_drawdown_pct": drawdown_metrics["max_drawdown_pct"],
            "avg_trade": float(avg_trade),
            "recovery_factor": drawdown_metrics.get("recovery_factor", 0.0),
        }


def calculate_performance_metrics(trades: List[Dict], **kwargs) -> Dict:
    """
    Calculate all performance metrics.

    Args:
        trades: List of trade dicts
        **kwargs: Additional parameters

    Returns:
        Dict with all metrics
    """
    calculator = PerformanceMetrics()
    return calculator.calculate_all_metrics(trades, **kwargs)
