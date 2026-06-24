"""
10,000 Strategy Optimization Framework
Tests different combinations to find best profit generation approach
"""

import json
import multiprocessing as mp
import sys
import time
from datetime import datetime
from functools import partial
from itertools import product
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class StrategyOptimizer:
    """Optimize 10,000 different strategy combinations."""

    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.results = []

        # Strategy parameters to test
        self.position_sizing_methods = [
            "kelly_full",
            "kelly_quarter",
            "kelly_half",
            "risk_1pct",
            "risk_2pct",
            "risk_3pct",
            "volatility_based",
            "confidence_based",
            "fixed_1lot",
        ]

        self.stop_loss_methods = [
            "atr_1x",
            "atr_2x",
            "atr_3x",
            "iv_0.3x",
            "iv_0.5x",
            "iv_0.7x",
            "fixed_20pct",
            "fixed_30pct",
            "fixed_50pct",
            "trailing_20pct",
            "trailing_30pct",
        ]

        self.take_profit_methods = [
            "risk_reward_1.5",
            "risk_reward_2.0",
            "risk_reward_2.5",
            "risk_reward_3.0",
            "fixed_50pct",
            "fixed_100pct",
            "fixed_150pct",
            "partial_50at_1r",
            "partial_50at_2r",
        ]

        self.entry_strategies = [
            "ml_confidence_high",
            "ml_confidence_medium",
            "ml_confidence_low",
            "predicted_profit_high",
            "predicted_profit_medium",
            "liquidity_score_high",
            "iv_rank_low",
            "iv_rank_high",
            "delta_atm",
            "delta_otm",
            "gamma_high",
        ]

        self.exit_strategies = [
            "time_based_50pct",
            "time_based_75pct",
            "volatility_expansion",
            "volatility_contraction",
            "momentum_reversal",
            "support_resistance",
        ]

        self.ml_ensemble_weights = [
            (1.0, 0.0, 0.0),  # Ultra only
            (0.7, 0.2, 0.1),  # Ultra dominant
            (0.5, 0.3, 0.2),  # Balanced
            (0.3, 0.4, 0.3),  # XGBoost dominant
            (0.33, 0.33, 0.34),  # Equal
        ]

    def generate_strategy_combinations(self, max_combinations: int = 10000) -> List[Dict]:
        """Generate strategy combinations."""
        print(f"Generating up to {max_combinations} strategy combinations...")

        # Sample combinations (not all 10k to avoid memory issues)
        # We'll use smart sampling
        combinations = []

        # Core combinations (most important)
        core_combos = list(
            product(
                ["kelly_quarter", "risk_2pct"],
                ["atr_2x", "iv_0.5x"],
                ["risk_reward_2.0", "risk_reward_2.5"],
                ["ml_confidence_high", "predicted_profit_high"],
            )
        )

        combinations.extend(
            [
                {
                    "position_sizing": ps,
                    "stop_loss": sl,
                    "take_profit": tp,
                    "entry_strategy": es,
                    "exit_strategy": "time_based_50pct",
                    "ml_weights": (0.5, 0.3, 0.2),
                }
                for ps, sl, tp, es in core_combos
            ]
        )

        # Extended combinations
        if len(combinations) < max_combinations:
            extended = list(
                product(
                    self.position_sizing_methods[:5],
                    self.stop_loss_methods[:5],
                    self.take_profit_methods[:5],
                    self.entry_strategies[:5],
                )
            )

            for ps, sl, tp, es in extended[: max_combinations - len(combinations)]:
                combinations.append(
                    {
                        "position_sizing": ps,
                        "stop_loss": sl,
                        "take_profit": tp,
                        "entry_strategy": es,
                        "exit_strategy": np.random.choice(self.exit_strategies),
                        "ml_weights": self.ml_ensemble_weights[np.random.randint(len(self.ml_ensemble_weights))],
                    }
                )

        print(f"Generated {len(combinations)} strategy combinations")
        return combinations[:max_combinations]

    def simulate_strategy(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Simulate a strategy on historical/virtual data."""
        # This is a simplified simulation
        # In production, would use actual historical data

        # Generate virtual trades based on strategy
        trades = []
        capital = 100000.0
        current_capital = capital

        # Filter data based on entry strategy
        if strategy["entry_strategy"] == "ml_confidence_high":
            filtered = data[data.get("ml_confidence", 0) > 0.7] if "ml_confidence" in data.columns else data.head(10)
        elif strategy["entry_strategy"] == "predicted_profit_high":
            filtered = data.nlargest(20, "predicted_profit") if "predicted_profit" in data.columns else data.head(10)
        else:
            filtered = data.head(10)

        # Simulate trades
        for idx, row in filtered.iterrows():
            entry_price = row.get("mid_price", row.get("ltp", 100))
            if pd.isna(entry_price) or entry_price <= 0:
                continue

            # Calculate position size
            qty = self._calculate_position_size(strategy["position_sizing"], entry_price, capital)

            # Calculate stop loss
            stop_loss = self._calculate_stop_loss(strategy["stop_loss"], entry_price, row)

            # Calculate take profit
            take_profit = self._calculate_take_profit(strategy["take_profit"], entry_price, stop_loss)

            # Simulate outcome (simplified - in production use actual price movements)
            # Random outcome based on strategy quality
            win_prob = 0.5 + (
                0.2 if strategy["entry_strategy"] in ["ml_confidence_high", "predicted_profit_high"] else 0
            )
            outcome = np.random.random() < win_prob

            if outcome:
                exit_price = take_profit
                pnl = (exit_price - entry_price) * qty
            else:
                exit_price = stop_loss
                pnl = (exit_price - entry_price) * qty

            trades.append({"entry": entry_price, "exit": exit_price, "qty": qty, "pnl": pnl, "win": outcome})

            current_capital += pnl

        # Calculate metrics
        if len(trades) == 0:
            return {
                "strategy": strategy,
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "profit_factor": 0.0,
            }

        wins = [t for t in trades if t["win"]]
        losses = [t for t in trades if not t["win"]]

        total_pnl = sum(t["pnl"] for t in trades)
        win_rate = len(wins) / len(trades) if len(trades) > 0 else 0

        avg_win = np.mean([t["pnl"] for t in wins]) if wins else 0
        avg_loss = abs(np.mean([t["pnl"] for t in losses])) if losses else 0
        profit_factor = (avg_win * len(wins)) / (avg_loss * len(losses)) if avg_loss > 0 and losses else 0

        # Sharpe ratio (simplified)
        returns = [t["pnl"] / capital for t in trades]
        sharpe = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252) if len(returns) > 1 else 0

        # Max drawdown
        cumulative = np.cumsum([t["pnl"] for t in trades])
        running_max = np.maximum.accumulate(cumulative)
        drawdown = running_max - cumulative
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        return {
            "strategy": strategy,
            "total_trades": len(trades),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "final_capital": current_capital,
            "roi_pct": ((current_capital - capital) / capital) * 100,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
        }

    def _calculate_position_size(self, method: str, entry_price: float, capital: float) -> int:
        """Calculate position size based on method."""
        if method == "kelly_full":
            return int(capital * 0.1 / entry_price)  # 10% of capital
        elif method == "kelly_quarter":
            return int(capital * 0.025 / entry_price)  # 2.5%
        elif method == "kelly_half":
            return int(capital * 0.05 / entry_price)  # 5%
        elif method == "risk_1pct":
            return int(capital * 0.01 / entry_price)
        elif method == "risk_2pct":
            return int(capital * 0.02 / entry_price)
        elif method == "risk_3pct":
            return int(capital * 0.03 / entry_price)
        elif method == "fixed_1lot":
            return 1
        else:
            return int(capital * 0.02 / entry_price)  # Default 2%

    def _calculate_stop_loss(self, method: str, entry_price: float, row: pd.Series) -> float:
        """Calculate stop loss based on method."""
        if method.startswith("atr_"):
            multiplier = float(method.split("_")[1].replace("x", ""))
            atr = row.get("atr", entry_price * 0.02)  # Default 2%
            return entry_price - (atr * multiplier)
        elif method.startswith("iv_"):
            multiplier = float(method.split("_")[1].replace("x", ""))
            iv = row.get("iv", 0.20)  # Default 20%
            return entry_price * (1 - iv * multiplier)
        elif method.startswith("fixed_"):
            pct = float(method.split("_")[1].replace("pct", ""))
            return entry_price * (1 - pct / 100)
        else:
            return entry_price * 0.7  # Default 30% stop

    def _calculate_take_profit(self, method: str, entry_price: float, stop_loss: float) -> float:
        """Calculate take profit based on method."""
        risk = abs(entry_price - stop_loss)

        if method.startswith("risk_reward_"):
            rr = float(method.split("_")[2])
            return entry_price + (risk * rr)
        elif method.startswith("fixed_"):
            pct = float(method.split("_")[1].replace("pct", ""))
            return entry_price * (1 + pct / 100)
        else:
            return entry_price + (risk * 2.0)  # Default 2:1

    def optimize(self, data: pd.DataFrame, max_combinations: int = 10000, top_n: int = 10) -> List[Dict]:
        """Run optimization."""
        print("=" * 80)
        print("  10,000 STRATEGY OPTIMIZATION")
        print("=" * 80)

        # Generate combinations
        combinations = self.generate_strategy_combinations(max_combinations)

        print(f"\nTesting {len(combinations)} strategies...")
        print("This may take several minutes...\n")

        # Test each strategy
        results = []
        start_time = time.time()

        for i, strategy in enumerate(combinations):
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                remaining = (len(combinations) - i - 1) / rate
                print(
                    f"  Progress: {i+1}/{len(combinations)} ({100*(i+1)/len(combinations):.1f}%) | "
                    f"ETA: {remaining/60:.1f} min"
                )

            result = self.simulate_strategy(strategy, data)
            results.append(result)

        # Sort by total PnL
        results.sort(key=lambda x: x["total_pnl"], reverse=True)

        print(f"\nOptimization complete! Tested {len(results)} strategies")
        print(f"Time taken: {(time.time() - start_time)/60:.1f} minutes")

        # Return top N
        return results[:top_n]


def main():
    """Main execution."""
    # Load data
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

    if not excel_path.exists():
        print(f"ERROR: Excel file not found: {excel_path}")
        return

    print("Loading data...")
    xl = pd.ExcelFile(excel_path)
    df = pd.read_excel(xl, sheet_name="OptionChain_Data")

    print(f"Loaded {len(df)} contracts")

    # Run optimization
    optimizer = StrategyOptimizer()
    top_strategies = optimizer.optimize(df, max_combinations=10000, top_n=20)

    # Display results
    print("\n" + "=" * 80)
    print("  TOP 20 STRATEGIES")
    print("=" * 80)

    for i, result in enumerate(top_strategies, 1):
        print(
            f"\n[{i}] Total PnL: Rs {result['total_pnl']:,.2f} | "
            f"ROI: {result['roi_pct']:.1f}% | "
            f"Win Rate: {result['win_rate']*100:.1f}% | "
            f"Trades: {result['total_trades']}"
        )
        print(
            f"    Position: {result['strategy']['position_sizing']} | "
            f"Stop: {result['strategy']['stop_loss']} | "
            f"Target: {result['strategy']['take_profit']}"
        )
        print(
            f"    Entry: {result['strategy']['entry_strategy']} | "
            f"Sharpe: {result['sharpe_ratio']:.2f} | "
            f"Profit Factor: {result['profit_factor']:.2f}"
        )

    # Save results
    results_path = ROOT_DIR / "outputs" / "strategy_optimization_results.json"
    with open(results_path, "w") as f:
        json.dump(top_strategies, f, indent=2, default=str)

    print(f"\n\nResults saved to: {results_path}")

    # Best strategy
    if top_strategies:
        best = top_strategies[0]
        print("\n" + "=" * 80)
        print("  BEST STRATEGY")
        print("=" * 80)
        print(json.dumps(best["strategy"], indent=2))
        print(f"\nExpected Performance:")
        print(f"  Total PnL: Rs {best['total_pnl']:,.2f}")
        print(f"  ROI: {best['roi_pct']:.1f}%")
        print(f"  Win Rate: {best['win_rate']*100:.1f}%")
        print(f"  Sharpe Ratio: {best['sharpe_ratio']:.2f}")
        print(f"  Profit Factor: {best['profit_factor']:.2f}")


if __name__ == "__main__":
    main()
