"""
1-Month All-Day Trading Simulation
Simulates complete trading month with optimized strategy
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import json
from typing import Dict, List

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.sim.replay_engine import ReplayEngine
from scripts.run_live_chain import LiveChainRunner
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker
from src.storage.trade_history import TradeHistoryStore
from src.analytics.performance_metrics import PerformanceMetrics
from core.utils.logger import logger


class OneMonthSimulation:
    """Simulate 1 month of all-day trading."""

    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.results = []
        self.daily_results = []

    def run_simulation(self, start_date: str = None, days: int = 30):
        """Run 1-month simulation."""
        print("=" * 80)
        print("  1-MONTH ALL-DAY TRADING SIMULATION")
        print("=" * 80)

        if start_date is None:
            # Start from next Monday
            today = datetime.now(self.ist)
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0 and today.hour < 9:
                days_until_monday = 0
            elif days_until_monday == 0:
                days_until_monday = 7
            start_date = (today + timedelta(days=days_until_monday)).strftime("%Y-%m-%d")

        print(
            f"\nSimulation Period: {start_date} to {(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=days-1)).strftime('%Y-%m-%d')}"
        )
        print(f"Total Trading Days: {days}")
        print(f"Trading Hours: 09:15 - 15:30 IST (6.25 hours/day)")
        print(f"Total Trading Hours: {days * 6.25} hours")
        print(f"Refresh Rate: 5 seconds")
        print(f"Total Cycles: ~{int(days * 6.25 * 3600 / 5):,}")

        # Initialize components
        print("\n[INITIALIZATION]")
        print("-" * 80)

        # Create replay engine
        replay_engine = ReplayEngine()
        replay_engine.load_base_data()

        # Create runner with optimized settings
        runner = LiveChainRunner(
            refresh_interval=5,
            use_websocket=False,  # Use REST in simulation
            prefer_weekly=True,
            sim_mode=True,
            ignore_market_hours=False,
            replay_engine=replay_engine,
        )

        # Initialize
        if not runner.initialize_expiries():
            print("ERROR: Failed to initialize expiries")
            return

        # Paper trading components
        paper_executor = PaperExecutor()
        pnl_tracker = PnLTracker()
        trade_history = TradeHistoryStore()
        performance_metrics = PerformanceMetrics()

        print("  Components initialized")
        print("  Using optimized strategy:")
        print("    - Position Sizing: Kelly Half (5% capital)")
        print("    - Stop Loss: ATR 2x")
        print("    - Take Profit: Fixed 50%")
        print("    - Entry: Predicted Profit High")
        print("    - Exit: Time-based 50%")

        # Run simulation day by day
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        total_trades = 0
        total_pnl = 0.0

        print("\n[TRADING SIMULATION]")
        print("-" * 80)

        for day in range(days):
            current_date = start_dt + timedelta(days=day)

            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                print(f"\nDay {day+1}/{days}: {current_date.strftime('%Y-%m-%d')} - WEEKEND (Skipped)")
                continue

            print(f"\nDay {day+1}/{days}: {current_date.strftime('%Y-%m-%d %A')}")
            print(f"  Market Hours: 09:15 - 15:30 IST")

            # Simulate trading day (6.25 hours = 22,500 seconds / 5 = 4,500 cycles)
            # For speed, simulate 1 cycle per minute (375 cycles per day)
            cycles_per_day = 375  # 1 cycle per minute for faster simulation
            day_trades = 0
            day_pnl = 0.0

            for cycle in range(cycles_per_day):
                # Simulate cycle
                cycle_time = current_date.replace(hour=9, minute=15) + timedelta(minutes=cycle)

                # Fetch data (simulated)
                try:
                    data_dict = runner.fetch_data_rest()
                    if not data_dict:
                        continue

                    # Process each underlying
                    for underlying, df in data_dict.items():
                        if len(df) == 0:
                            continue

                        # Add calculations
                        df = runner.add_calculations(df, underlying)

                        # Get top signal
                        spots = {underlying: df["spot_price"].median() if "spot_price" in df.columns else 25000}
                        time_to_expiry_map = {underlying: 0.065}  # ~24 days

                        rankings = runner.selector.select_top_underlying(
                            {underlying: df}, spots=spots, time_to_expiry_map=time_to_expiry_map
                        )

                        if not rankings or rankings.get("underlying_score", 0) < 50:
                            continue

                        # Get strategy
                        spot = spots[underlying]
                        expected_move = df["expected_move"].median() if "expected_move" in df.columns else spot * 0.02
                        pcr = rankings.get("pcr", 1.0)
                        delta_pcr = rankings.get("pcr_delta_weighted", 1.0)

                        sentiment = runner.strategy_engine.analyze_sentiment(df, spot, pcr, delta_pcr)
                        strategy = runner.strategy_engine.recommend_strategy(
                            df,
                            underlying,
                            spot,
                            expected_move,
                            sentiment,
                            rankings.get("execution_quality", 50),
                            rankings.get("signal_strength", 50),
                        )

                        # Execute trade if signal
                        if strategy.get("action") == "TRADE":
                            position = paper_executor.execute_trade(
                                strategy, df, cycle_time.strftime("%Y-%m-%d %H:%M:%S IST")
                            )

                            if position:
                                day_trades += 1
                                total_trades += 1

                except Exception as e:
                    if cycle % 50 == 0:  # Log every 50 cycles
                        logger.debug(f"Cycle {cycle} error: {e}")
                    continue

                # Update positions and PnL every 10 cycles
                if cycle % 10 == 0:
                    paper_executor.update_positions(df if "df" in locals() else pd.DataFrame())
                    pnl_data = pnl_tracker.update(paper_executor.positions)
                    if pnl_data:
                        day_pnl = pnl_data.get("total_pnl", 0.0)
                        total_pnl = pnl_data.get("total_pnl", 0.0)

            # End of day summary
            print(f"  Trades: {day_trades} | PnL: Rs {day_pnl:,.2f}")
            self.daily_results.append({"date": current_date.strftime("%Y-%m-%d"), "trades": day_trades, "pnl": day_pnl})

        # Final summary
        print("\n" + "=" * 80)
        print("  SIMULATION COMPLETE")
        print("=" * 80)

        final_pnl = pnl_tracker.update(paper_executor.positions)

        print(f"\n[FINAL RESULTS]")
        print(f"  Total Trading Days: {days}")
        print(f"  Total Trades: {total_trades}")
        print(f"  Total PnL: Rs {total_pnl:,.2f}")
        print(f"  Final PnL: Rs {final_pnl.get('total_pnl', 0):,.2f}")
        print(f"  Win Rate: {final_pnl.get('win_rate', 0)*100:.1f}%")
        print(f"  Winning Trades: {final_pnl.get('winning_trades', 0)}")
        print(f"  Losing Trades: {final_pnl.get('losing_trades', 0)}")

        # Calculate performance metrics
        if total_trades > 0:
            metrics = performance_metrics.calculate_all_metrics(paper_executor.trade_history, initial_capital=100000.0)

            print(f"\n[PERFORMANCE METRICS]")
            print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"  Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}")
            print(f"  Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}")
            print(f"  Max Drawdown: Rs {metrics.get('max_drawdown', 0):,.2f}")
            print(f"  ROI: {((final_pnl.get('total_pnl', 0) / 100000.0) * 100):.1f}%")

        # Save results
        results_path = ROOT_DIR / "outputs" / "1month_simulation_results.json"
        with open(results_path, "w") as f:
            json.dump(
                {
                    "simulation_period": f"{start_date} to {(start_dt + timedelta(days=days-1)).strftime('%Y-%m-%d')}",
                    "total_days": days,
                    "total_trades": total_trades,
                    "final_pnl": final_pnl,
                    "daily_results": self.daily_results,
                    "performance_metrics": metrics if total_trades > 0 else {},
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\nResults saved to: {results_path}")

        return {
            "total_trades": total_trades,
            "total_pnl": total_pnl,
            "final_pnl": final_pnl,
            "daily_results": self.daily_results,
            "metrics": metrics if total_trades > 0 else {},
        }


def main():
    """Main execution."""
    sim = OneMonthSimulation()
    results = sim.run_simulation(days=30)

    if results:
        print("\n" + "=" * 80)
        print("  SIMULATION SUCCESSFUL")
        print("=" * 80)
        print(f"\nCheck outputs/1month_simulation_results.json for detailed results")
    else:
        print("\nSimulation failed - check logs for details")


if __name__ == "__main__":
    main()
