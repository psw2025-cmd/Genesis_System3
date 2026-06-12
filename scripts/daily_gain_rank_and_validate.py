"""
Daily Gain Rank + Market Validation Runner
==========================================
Runs every trading day (can be scheduled via cron or system3 orchestrator).

Schedule:
  09:15 — Pre-market: rank all symbols, save predictions
  15:35 — Post-market: validate predictions vs actual NSE results
  15:40 — Print accuracy trend, fire retrain signal if needed

Usage:
  python scripts/daily_gain_rank_and_validate.py --mode rank
  python scripts/daily_gain_rank_and_validate.py --mode validate
  python scripts/daily_gain_rank_and_validate.py --mode trend
  python scripts/daily_gain_rank_and_validate.py --mode full
"""

import argparse
import json
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import numpy as np
import pandas as pd

from src.ranking.gain_rank_engine import GainRankEngine
from src.validation.market_result_validator import MarketResultValidator


def load_live_chain_data():
    """
    Load live options chain data from storage.
    Falls back to generating synthetic data if storage files are missing.
    Returns (all_chain_data, spots).
    """
    storage_dir = os.path.join(ROOT_DIR, "storage")
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
    all_data, spots = {}, {}

    for sym in underlyings:
        candidates = []
        if os.path.isdir(storage_dir):
            candidates = sorted(
                [f for f in os.listdir(storage_dir)
                 if sym.lower() in f.lower() and f.endswith(".csv")],
                reverse=True
            )
        if candidates:
            path = os.path.join(storage_dir, candidates[0])
            try:
                df = pd.read_csv(path)
                all_data[sym] = df
                spot_col = next((c for c in df.columns if "spot" in c.lower()), None)
                spots[sym] = float(df[spot_col].iloc[0]) if spot_col else 0.0
                print(f"  Loaded {sym} from {candidates[0]} ({len(df)} rows)")
                continue
            except Exception as e:
                print(f"  WARNING: could not load {sym} CSV: {e}")

        # Fallback: synthetic chain for testing
        spot = {"NIFTY": 23000, "BANKNIFTY": 52000,
                "FINNIFTY": 23500, "MIDCPNIFTY": 12000}[sym]
        strikes = [spot - 500 + i * 50 for i in range(20)]
        all_data[sym] = pd.DataFrame({
            "strike": strikes,
            "option_type": ["CE"] * 10 + ["PE"] * 10,
            "oi": np.random.randint(50000, 500000, 20),
            "volume": np.random.randint(5000, 100000, 20),
            "ltp": np.random.uniform(10, 300, 20),
            "iv": np.random.uniform(0.12, 0.35, 20),
        })
        spots[sym] = float(spot)
        print(f"  {sym}: using synthetic data (no CSV found)")

    return all_data, spots


def run_ranking(top_n: int = 5) -> None:
    """Pre-market: rank all symbols, save predictions to gain_rank_history.json."""
    print(f"\n{'='*60}")
    print(f"  GAIN RANK ENGINE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    all_data, spots = load_live_chain_data()
    engine = GainRankEngine(top_n=top_n)
    ranked_df = engine.rank_all(all_data, spots)

    print(f"\n  Ranked {len(ranked_df)} underlyings by predicted gain potential:\n")
    print(ranked_df[["rank", "underlying", "gain_score",
                      "expected_move_pct", "recommendation"]].to_string(index=False))

    top = engine.get_top_n(all_data, spots)
    if top:
        print(f"\n  TOP {len(top)} SYMBOLS FOR TODAY:")
        for t in top:
            print(f"    #{t['rank']}  {t['underlying']:12s}  score={t['gain_score']:.1f}"
                  f"  expected_move={t['expected_move_pct']*100:.2f}%")
    else:
        print("\n  WARNING: No symbols met minimum gain score threshold.")


def run_validation() -> None:
    """Post-market: compare predictions vs actual NSE results."""
    print(f"\n{'='*60}")
    print(f"  MARKET RESULT VALIDATION — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    validator = MarketResultValidator()
    report = validator.run_daily_validation()

    if report.get("status") == "SKIPPED":
        print(f"\n  Validation skipped: {report.get('reason')}")
        return

    print(f"\n  Date            : {report['date']}")
    print(f"  Predicted order : {report.get('predicted_ranking', [])}")
    print(f"  Actual order    : {report.get('actual_ranking', [])}")
    print(f"  Spearman ρ      : {report.get('spearman_correlation', 'N/A')}")
    print(f"  Hit rate (top-3): {report.get('hit_rate', 0):.0%}")
    print(f"  Status          : {report.get('status')}")

    if report.get("retrain_signal"):
        print("\n  *** RETRAIN SIGNAL FIRED — accuracy below threshold ***")
        print("  Action: trigger model retraining pipeline")


def run_trend() -> None:
    """Print rolling accuracy trend."""
    print(f"\n{'='*60}")
    print(f"  ACCURACY TREND (last 14 days)")
    print(f"{'='*60}")

    validator = MarketResultValidator()
    trend = validator.get_accuracy_trend(last_n_days=14)
    print(json.dumps(trend, indent=2))

    if trend.get("retrain_signal"):
        print("\n  *** MODEL DRIFT DETECTED — retraining recommended ***")


def main():
    parser = argparse.ArgumentParser(description="Daily gain rank + market validation runner")
    parser.add_argument("--mode", choices=["rank", "validate", "trend", "full"],
                        default="full", help="Which step to run")
    parser.add_argument("--top-n", type=int, default=5,
                        help="Number of top symbols to rank (default: 5)")
    args = parser.parse_args()

    if args.mode in ("rank", "full"):
        run_ranking(top_n=args.top_n)

    if args.mode in ("validate", "full"):
        run_validation()

    if args.mode in ("trend", "full"):
        run_trend()


if __name__ == "__main__":
    main()
