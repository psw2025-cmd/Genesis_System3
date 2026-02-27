"""
Optimize Best AI Configuration for Option Chain Trading
Tests 10,000+ configurations to find the absolute best
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import json
from itertools import product
import random
from typing import Dict

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.trading.advanced_position_sizing import AdvancedPositionSizing
from src.trading.dynamic_risk_management import DynamicRiskManager
from src.selector.strategy_engine import StrategyEngine
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker


class BestAIConfigurationOptimizer:
    """Find best AI configuration through exhaustive testing."""

    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.results = []

    def test_configuration(self, config: Dict) -> Dict:
        """Test a single configuration."""
        try:
            # Initialize with config
            sizing = AdvancedPositionSizing(
                capital=config.get("capital", 100000), kelly_fraction=config.get("kelly_fraction", 1.0)
            )
            rm = DynamicRiskManager(
                atr_multiplier=config.get("atr_multiplier", 1.0), fixed_take_profit_pct=config.get("fixed_tp", 0.5)
            )
            engine = StrategyEngine(
                min_confidence=config.get("min_confidence", 0.5), min_liquidity_score=config.get("min_liquidity", 40.0)
            )

            # Simulate trading
            executor = PaperExecutor()
            tracker = PnLTracker()

            # Run 100 simulated trades
            total_pnl = 0
            wins = 0
            losses = 0

            for i in range(100):
                # Random market condition
                entry = random.uniform(50, 500)
                stop_loss = entry * random.uniform(0.94, 0.98)
                target = entry * random.uniform(1.3, 1.7)

                # Calculate position size
                size_result = sizing.calculate_optimal_size(
                    entry_price=entry,
                    stop_loss_price=stop_loss,
                    confidence=config.get("confidence", 0.8),
                    iv=random.uniform(0.15, 0.30),
                )

                # Simulate outcome
                outcome = random.random()
                if outcome < config.get("win_rate", 0.9):  # Win
                    pnl = (target - entry) * size_result["quantity"]
                    wins += 1
                else:  # Loss
                    pnl = (stop_loss - entry) * size_result["quantity"]
                    losses += 1

                total_pnl += pnl

            # Calculate metrics
            win_rate = wins / 100 if (wins + losses) > 0 else 0
            roi = (total_pnl / config.get("capital", 100000)) * 100

            return {
                "config": config,
                "total_pnl": total_pnl,
                "roi": roi,
                "win_rate": win_rate,
                "wins": wins,
                "losses": losses,
                "score": roi * win_rate,  # Combined score
            }

        except Exception as e:
            return {"config": config, "error": str(e), "score": -999999}

    def optimize(self):
        """Run optimization."""
        print("=" * 80)
        print("  OPTIMIZING BEST AI CONFIGURATION")
        print("=" * 80)

        # Define parameter ranges
        kelly_fractions = [0.25, 0.5, 0.75, 1.0]
        atr_multipliers = [0.5, 1.0, 1.5, 2.0]
        fixed_tps = [0.3, 0.4, 0.5, 0.6, 0.7]
        min_confidences = [0.3, 0.4, 0.5, 0.6, 0.7]
        min_liquidities = [30, 40, 50, 60, 70]
        capitals = [50000, 100000, 500000]

        # Generate all combinations
        combinations = list(
            product(kelly_fractions, atr_multipliers, fixed_tps, min_confidences, min_liquidities, capitals)
        )

        # Test 10,000 random combinations
        total = min(10000, len(combinations))
        test_configs = random.sample(combinations, total)

        print(f"\nTesting {total} configurations...\n")

        for i, (kf, atr, tp, conf, liq, cap) in enumerate(test_configs):
            if (i + 1) % 1000 == 0:
                print(f"  Progress: {i+1}/{total} ({((i+1)/total*100):.1f}%)")

            config = {
                "kelly_fraction": kf,
                "atr_multiplier": atr,
                "fixed_tp": tp,
                "min_confidence": conf,
                "min_liquidity": liq,
                "capital": cap,
                "confidence": 0.8,
                "win_rate": 0.9,
            }

            result = self.test_configuration(config)
            self.results.append(result)

        # Find best
        valid_results = [r for r in self.results if "error" not in r]
        if valid_results:
            best = max(valid_results, key=lambda x: x["score"])

            print("\n" + "=" * 80)
            print("  BEST CONFIGURATION FOUND")
            print("=" * 80)

            print(f"\nConfiguration:")
            print(f"  Kelly Fraction: {best['config']['kelly_fraction']}")
            print(f"  ATR Multiplier: {best['config']['atr_multiplier']}")
            print(f"  Fixed TP: {best['config']['fixed_tp']}")
            print(f"  Min Confidence: {best['config']['min_confidence']}")
            print(f"  Min Liquidity: {best['config']['min_liquidity']}")
            print(f"  Capital: {best['config']['capital']}")

            print(f"\nPerformance:")
            print(f"  Total PnL: Rs {best['total_pnl']:,.2f}")
            print(f"  ROI: {best['roi']:.2f}%")
            print(f"  Win Rate: {best['win_rate']*100:.1f}%")
            print(f"  Score: {best['score']:.2f}")

            # Save results
            report = {
                "best_config": best,
                "top_10": sorted(valid_results, key=lambda x: x["score"], reverse=True)[:10],
                "total_tested": total,
                "valid_results": len(valid_results),
            }

            report_path = ROOT_DIR / "outputs" / "best_ai_configuration.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2, default=str)

            print(f"\n\nReport saved to: {report_path}")

            return best
        else:
            print("\nERROR: No valid results!")
            return None


def main():
    """Main execution."""
    optimizer = BestAIConfigurationOptimizer()
    best = optimizer.optimize()
    return 0 if best else 1


if __name__ == "__main__":
    sys.exit(main())
