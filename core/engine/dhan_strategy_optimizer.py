"""
Dhan Index Options - Strategy Optimizer

Optimizes overall trading strategy parameters:
- Entry/exit timing
- Position sizing
- Risk management
- Portfolio allocation
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
PNL_LOG_CSV = LIVE_DIR / "dhan_index_ai_pnl_log.csv"
OPTIMIZATION_JSON = PROJECT_ROOT / "storage" / "config" / "strategy_optimization.json"


class StrategyOptimizer:
    """Optimizes trading strategy parameters."""

    def __init__(self):
        self.optimization_path = OPTIMIZATION_JSON

    def optimize_strategy(self, days: int = 7) -> Dict[str, Any]:
        """
        Optimize strategy parameters based on recent performance.

        Returns optimization recommendations.
        """
        if not PNL_LOG_CSV.exists():
            return {
                "status": "NO_DATA",
                "message": "No PnL data available",
            }

        try:
            df_pnl = pd.read_csv(PNL_LOG_CSV)
            if df_pnl.empty:
                return {
                    "status": "EMPTY",
                    "message": "PnL log is empty",
                }

            # Filter by date
            if "exit_ts" in df_pnl.columns:
                df_pnl["exit_ts"] = pd.to_datetime(df_pnl["exit_ts"], errors="coerce")
                cutoff = datetime.utcnow() - pd.Timedelta(days=days)
                df_pnl = df_pnl[df_pnl["exit_ts"] >= cutoff]

            if df_pnl.empty:
                return {
                    "status": "NO_RECENT_DATA",
                    "message": f"No PnL data in last {days} days",
                }

            pnl_col = "pnl_pct" if "pnl_pct" in df_pnl.columns else "pct_pnl"
            if pnl_col not in df_pnl.columns:
                return {
                    "status": "NO_PNL_COLUMN",
                    "message": "PnL column not found",
                }

            # Analyze performance
            total_trades = len(df_pnl)
            win_rate = (df_pnl[pnl_col] > 0).sum() / total_trades * 100 if total_trades > 0 else 0
            avg_pnl = df_pnl[pnl_col].mean()
            max_drawdown = df_pnl[pnl_col].min()

            # Analyze by underlying
            by_underlying = {}
            if "underlying" in df_pnl.columns:
                for u in df_pnl["underlying"].unique():
                    df_u = df_pnl[df_pnl["underlying"] == u]
                    by_underlying[u] = {
                        "trades": len(df_u),
                        "win_rate": (df_u[pnl_col] > 0).sum() / len(df_u) * 100 if len(df_u) > 0 else 0,
                        "avg_pnl": df_u[pnl_col].mean(),
                    }

            # Generate optimization recommendations
            recommendations = {
                "position_sizing": self._optimize_position_sizing(win_rate, avg_pnl),
                "risk_management": self._optimize_risk_management(max_drawdown, win_rate),
                "portfolio_allocation": self._optimize_allocation(by_underlying),
                "entry_timing": self._optimize_entry_timing(df_pnl),
            }

            return {
                "status": "SUCCESS",
                "analysis": {
                    "total_trades": total_trades,
                    "win_rate": win_rate,
                    "avg_pnl": avg_pnl,
                    "max_drawdown": max_drawdown,
                    "by_underlying": by_underlying,
                },
                "recommendations": recommendations,
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e),
            }

    def _optimize_position_sizing(self, win_rate: float, avg_pnl: float) -> Dict[str, Any]:
        """Optimize position sizing based on performance."""
        # Kelly Criterion approximation
        if win_rate > 0 and avg_pnl > 0:
            # Simplified position sizing
            recommended_size = min(1.0, (win_rate / 100.0) * (avg_pnl / 100.0))
        else:
            recommended_size = 0.5  # Conservative default

        return {
            "recommended_size": recommended_size,
            "reasoning": f"Based on win_rate={win_rate:.1f}%, avg_pnl={avg_pnl:.2f}%",
        }

    def _optimize_risk_management(self, max_drawdown: float, win_rate: float) -> Dict[str, Any]:
        """Optimize risk management parameters."""
        recommendations = {
            "stoploss_pct": 5.0,  # Default
            "target_pct": 10.0,  # Default
            "max_drawdown_limit": abs(max_drawdown) * 1.5,
        }

        if max_drawdown < -10.0:
            recommendations["stoploss_pct"] = 3.0  # Tighter stop-loss
            recommendations["reasoning"] = "Large drawdowns detected - tighten stop-loss"

        return recommendations

    def _optimize_allocation(self, by_underlying: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize portfolio allocation across underlyings."""
        if not by_underlying:
            return {"allocation": {}, "reasoning": "Insufficient data"}

        # Allocate based on performance
        total_trades = sum(data["trades"] for data in by_underlying.values())
        allocation = {}

        for u, data in by_underlying.items():
            if total_trades > 0:
                weight = data["trades"] / total_trades
                # Adjust based on performance
                if data.get("win_rate", 0) > 50:
                    weight *= 1.2  # Favor better performers
                allocation[u] = min(1.0, weight)

        return {
            "allocation": allocation,
            "reasoning": "Allocation based on trade frequency and performance",
        }

    def _optimize_entry_timing(self, df_pnl: pd.DataFrame) -> Dict[str, Any]:
        """Optimize entry timing based on exit reasons."""
        if "exit_reason" not in df_pnl.columns:
            return {"reasoning": "No exit reason data available"}

        exit_reasons = df_pnl["exit_reason"].value_counts()
        return {
            "exit_reason_distribution": exit_reasons.to_dict(),
            "reasoning": "Monitor exit reasons to optimize entry timing",
        }

    def save_optimization(self, optimization: Dict[str, Any]) -> bool:
        """Save optimization results to JSON."""
        import json

        self.optimization_path.parent.mkdir(parents=True, exist_ok=True)

        output = {
            "optimized_at": datetime.utcnow().isoformat(),
            "optimization": optimization,
        }

        try:
            with self.optimization_path.open("w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            return True
        except Exception as e:
            print(f"[OPTIMIZER] Failed to save optimization: {e}")
            return False


def main() -> None:
    """Main entry point for strategy optimizer."""
    print("=== ANGEL ONE INDEX OPTIONS - STRATEGY OPTIMIZER ===")

    optimizer = StrategyOptimizer()
    result = optimizer.optimize_strategy(days=7)

    if result["status"] == "SUCCESS":
        print("\n=== STRATEGY ANALYSIS ===")
        analysis = result["analysis"]
        print(f"Total trades: {analysis['total_trades']}")
        print(f"Win rate: {analysis['win_rate']:.1f}%")
        print(f"Average PnL: {analysis['avg_pnl']:.2f}%")
        print(f"Max drawdown: {analysis['max_drawdown']:.2f}%")

        print("\n=== OPTIMIZATION RECOMMENDATIONS ===")
        rec = result["recommendations"]
        print("Position Sizing:", rec.get("position_sizing", {}))
        print("Risk Management:", rec.get("risk_management", {}))
        print("Portfolio Allocation:", rec.get("portfolio_allocation", {}))

        optimizer.save_optimization(result)
        print(f"\n[SAVE] Optimization saved to: {optimizer.optimization_path}")
    else:
        print(f"[INFO] {result.get('message', 'Optimization not available')}")


if __name__ == "__main__":
    main()
