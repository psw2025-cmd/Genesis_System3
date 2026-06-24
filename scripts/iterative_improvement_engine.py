"""
Iterative Improvement Engine - World-Class Optimization
Tests multiple improvements and finds the best configuration
"""

import itertools
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.optimize_10k_strategies import StrategyOptimizer


class IterativeImprovementEngine:
    """Iterative improvement with try-and-error approach."""

    def __init__(self):
        self.improvements = []
        self.results = []

    def test_improvement(self, config: Dict, data: pd.DataFrame) -> Dict:
        """Test a specific improvement configuration."""
        optimizer = StrategyOptimizer()

        # Override optimizer defaults with config
        if "position_sizing" in config:
            # Modify position sizing logic
            pass

        # Simulate strategy
        result = optimizer.simulate_strategy(config, data)

        return {"config": config, "result": result, "score": self._calculate_score(result)}

    def _calculate_score(self, result: Dict) -> float:
        """Calculate overall score for ranking."""
        # Weighted combination of metrics
        pnl_score = min(result.get("total_pnl", 0) / 100000, 1.0) * 0.3
        roi_score = min(result.get("roi_pct", 0) / 100, 1.0) * 0.25
        win_rate_score = result.get("win_rate", 0) * 0.2
        sharpe_score = min(result.get("sharpe_ratio", 0) / 50, 1.0) * 0.15
        profit_factor_score = min(result.get("profit_factor", 0) / 100, 1.0) * 0.1

        return (pnl_score + roi_score + win_rate_score + sharpe_score + profit_factor_score) * 100

    def generate_improvements(self) -> List[Dict]:
        """Generate improvement variations to test."""
        improvements = []

        # Improvement 1: Dynamic position sizing based on volatility regime
        improvements.append(
            {
                "name": "Dynamic Volatility-Based Sizing",
                "position_sizing": "volatility_regime_adaptive",
                "stop_loss": "atr_2x",
                "take_profit": "fixed_50pct",
                "entry_strategy": "predicted_profit_high",
                "volatility_adjustment": "high_vol_reduce_30pct",
            }
        )

        # Improvement 2: Multi-timeframe entry confirmation
        improvements.append(
            {
                "name": "Multi-Timeframe Confirmation",
                "position_sizing": "kelly_half",
                "stop_loss": "atr_2x",
                "take_profit": "fixed_50pct",
                "entry_strategy": "multi_tf_confirmed",
                "confirmation_timeframes": [5, 15, 60],  # minutes
            }
        )

        # Improvement 3: Adaptive stop loss based on IV rank
        improvements.append(
            {
                "name": "IV Rank Adaptive Stop",
                "position_sizing": "kelly_half",
                "stop_loss": "iv_rank_adaptive",
                "take_profit": "fixed_50pct",
                "entry_strategy": "predicted_profit_high",
                "iv_rank_threshold": 0.7,
            }
        )

        # Improvement 4: Partial profit taking with trailing stop
        improvements.append(
            {
                "name": "Partial Profit + Trailing Stop",
                "position_sizing": "kelly_half",
                "stop_loss": "atr_2x",
                "take_profit": "partial_25_50_25",
                "entry_strategy": "predicted_profit_high",
                "trailing_stop": "atr_1x_after_1r",
            }
        )

        # Improvement 5: Ensemble entry with multiple ML models
        improvements.append(
            {
                "name": "Ensemble ML Entry",
                "position_sizing": "kelly_half",
                "stop_loss": "atr_2x",
                "take_profit": "fixed_50pct",
                "entry_strategy": "ensemble_ml_voting",
                "ml_models": ["ultra", "xgboost", "randomforest"],
                "voting_threshold": 0.7,
            }
        )

        # Improvement 6: Time-of-day optimization
        improvements.append(
            {
                "name": "Time-of-Day Optimization",
                "position_sizing": "kelly_half",
                "stop_loss": "atr_2x",
                "take_profit": "fixed_50pct",
                "entry_strategy": "predicted_profit_high",
                "time_filters": {
                    "morning": {"size_multiplier": 1.2, "confidence_boost": 0.1},
                    "afternoon": {"size_multiplier": 0.8, "confidence_boost": 0.0},
                },
            }
        )

        # Improvement 7: Correlation-based position sizing
        improvements.append(
            {
                "name": "Correlation-Based Sizing",
                "position_sizing": "correlation_adjusted",
                "stop_loss": "atr_2x",
                "take_profit": "fixed_50pct",
                "entry_strategy": "predicted_profit_high",
                "max_correlation": 0.7,
            }
        )

        # Improvement 8: Momentum-based entry timing
        improvements.append(
            {
                "name": "Momentum Entry Timing",
                "position_sizing": "kelly_half",
                "stop_loss": "atr_2x",
                "take_profit": "fixed_50pct",
                "entry_strategy": "momentum_confirmed",
                "momentum_periods": [5, 10, 20],
            }
        )

        # Improvement 9: Volatility clustering detection
        improvements.append(
            {
                "name": "Volatility Clustering",
                "position_sizing": "kelly_half",
                "stop_loss": "volatility_cluster_adaptive",
                "take_profit": "fixed_50pct",
                "entry_strategy": "predicted_profit_high",
                "cluster_detection": "garch_model",
            }
        )

        # Improvement 10: Market regime detection
        improvements.append(
            {
                "name": "Market Regime Detection",
                "position_sizing": "regime_based",
                "stop_loss": "atr_2x",
                "take_profit": "regime_adaptive",
                "entry_strategy": "predicted_profit_high",
                "regimes": ["trending", "ranging", "volatile", "calm"],
            }
        )

        return improvements

    def run_iterative_improvement(self, data: pd.DataFrame, iterations: int = 20) -> List[Dict]:
        """Run iterative improvement process."""
        print("=" * 80)
        print("  ITERATIVE IMPROVEMENT ENGINE - WORLD-CLASS OPTIMIZATION")
        print("=" * 80)

        improvements = self.generate_improvements()
        all_results = []

        # Test base configuration
        print("\n[ITERATION 0] Testing Base Configuration")
        print("-" * 80)
        base_config = {
            "position_sizing": "kelly_half",
            "stop_loss": "atr_2x",
            "take_profit": "fixed_50pct",
            "entry_strategy": "predicted_profit_high",
        }
        base_result = self.test_improvement(base_config, data)
        all_results.append(base_result)
        print(f"  Base Score: {base_result['score']:.2f}")
        print(f"  Base PnL: Rs {base_result['result']['total_pnl']:,.2f}")
        print(f"  Base ROI: {base_result['result']['roi_pct']:.1f}%")

        # Test each improvement
        for i, improvement in enumerate(improvements, 1):
            print(f"\n[ITERATION {i}] Testing: {improvement['name']}")
            print("-" * 80)

            try:
                result = self.test_improvement(improvement, data)
                all_results.append(result)

                improvement_pct = ((result["score"] - base_result["score"]) / base_result["score"]) * 100
                print(f"  Score: {result['score']:.2f} ({improvement_pct:+.1f}%)")
                print(f"  PnL: Rs {result['result']['total_pnl']:,.2f}")
                print(f"  ROI: {result['result']['roi_pct']:.1f}%")
                print(f"  Win Rate: {result['result']['win_rate']*100:.1f}%")
                print(f"  Sharpe: {result['result']['sharpe_ratio']:.2f}")

            except Exception as e:
                print(f"  ERROR: {e}")
                continue

        # Sort by score
        all_results.sort(key=lambda x: x["score"], reverse=True)

        # Display top 5
        print("\n" + "=" * 80)
        print("  TOP 5 IMPROVEMENTS")
        print("=" * 80)

        for i, result in enumerate(all_results[:5], 1):
            config = result["config"]
            res = result["result"]
            print(f"\n[{i}] {config.get('name', 'Base Configuration')}")
            print(f"    Score: {result['score']:.2f}")
            print(f"    PnL: Rs {res['total_pnl']:,.2f}")
            print(f"    ROI: {res['roi_pct']:.1f}%")
            print(f"    Win Rate: {res['win_rate']*100:.1f}%")
            print(f"    Sharpe: {res['sharpe_ratio']:.2f}")
            print(f"    Profit Factor: {res['profit_factor']:.2f}")

        # Save results
        results_path = ROOT_DIR / "outputs" / "iterative_improvement_results.json"
        with open(results_path, "w") as f:
            json.dump(all_results, f, indent=2, default=str)

        print(f"\n\nResults saved to: {results_path}")

        return all_results


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

    # Run iterative improvement
    engine = IterativeImprovementEngine()
    results = engine.run_iterative_improvement(df, iterations=20)

    # Best configuration
    if results:
        best = results[0]
        print("\n" + "=" * 80)
        print("  BEST WORLD-CLASS CONFIGURATION")
        print("=" * 80)
        print(json.dumps(best["config"], indent=2))
        print(f"\nPerformance:")
        print(f"  Score: {best['score']:.2f}")
        print(f"  PnL: Rs {best['result']['total_pnl']:,.2f}")
        print(f"  ROI: {best['result']['roi_pct']:.1f}%")
        print(f"  Win Rate: {best['result']['win_rate']*100:.1f}%")
        print(f"  Sharpe: {best['result']['sharpe_ratio']:.2f}")


if __name__ == "__main__":
    main()
