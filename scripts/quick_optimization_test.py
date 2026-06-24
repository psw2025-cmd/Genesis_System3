"""
Quick Optimization Test - Tests 1000 strategies to find best approach
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.optimize_10k_strategies import StrategyOptimizer


def main():
    """Quick test with 1000 strategies."""
    print("=" * 80)
    print("  QUICK OPTIMIZATION TEST (1000 Strategies)")
    print("=" * 80)

    # Load data
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

    if not excel_path.exists():
        print(f"ERROR: Excel file not found: {excel_path}")
        return

    print("\nLoading data...")
    xl = pd.ExcelFile(excel_path)
    df = pd.read_excel(xl, sheet_name="OptionChain_Data")
    print(f"Loaded {len(df)} contracts")

    # Run optimization
    optimizer = StrategyOptimizer()
    top_strategies = optimizer.optimize(df, max_combinations=1000, top_n=10)

    # Display top 10
    print("\n" + "=" * 80)
    print("  TOP 10 STRATEGIES")
    print("=" * 80)

    for i, result in enumerate(top_strategies, 1):
        print(f"\n[{i}] Total PnL: Rs {result['total_pnl']:,.2f}")
        print(
            f"    ROI: {result['roi_pct']:.1f}% | Win Rate: {result['win_rate']*100:.1f}% | Trades: {result['total_trades']}"
        )
        print(f"    Position: {result['strategy']['position_sizing']}")
        print(f"    Stop: {result['strategy']['stop_loss']} | Target: {result['strategy']['take_profit']}")
        print(f"    Entry: {result['strategy']['entry_strategy']}")
        print(f"    Sharpe: {result['sharpe_ratio']:.2f} | Profit Factor: {result['profit_factor']:.2f}")

    # Best strategy
    if top_strategies:
        best = top_strategies[0]
        print("\n" + "=" * 80)
        print("  BEST STRATEGY FOR HIGHEST PROFIT")
        print("=" * 80)
        print(f"\nConfiguration:")
        print(f"  Position Sizing: {best['strategy']['position_sizing']}")
        print(f"  Stop Loss: {best['strategy']['stop_loss']}")
        print(f"  Take Profit: {best['strategy']['take_profit']}")
        print(f"  Entry Strategy: {best['strategy']['entry_strategy']}")
        print(f"  Exit Strategy: {best['strategy']['exit_strategy']}")
        print(f"\nExpected Performance:")
        print(f"  Total PnL: Rs {best['total_pnl']:,.2f}")
        print(f"  ROI: {best['roi_pct']:.1f}%")
        print(f"  Win Rate: {best['win_rate']*100:.1f}%")
        print(f"  Sharpe Ratio: {best['sharpe_ratio']:.2f}")
        print(f"  Profit Factor: {best['profit_factor']:.2f}")
        print(f"  Max Drawdown: Rs {best['max_drawdown']:,.2f}")


if __name__ == "__main__":
    main()
