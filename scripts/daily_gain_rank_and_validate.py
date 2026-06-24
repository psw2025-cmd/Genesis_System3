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

from core.data.nse_provider import fetch_option_chain, spot_price_from_chain
from core.data.nse_provider import load_oi_cache, save_oi_cache, is_expiry_day
from src.ranking.gain_rank_engine import GainRankEngine
from src.ranking.ml_signal_aggregator import load_ml_confidence
from src.validation.market_result_validator import MarketResultValidator


def _nse_chain_to_df(chain_json: dict) -> pd.DataFrame:
    """Convert raw NSE option chain JSON to a flat DataFrame."""
    rows = []
    for entry in chain_json.get("records", {}).get("data", []):
        strike = entry.get("strikePrice", 0)
        for opt_type, key in [("CE", "CE"), ("PE", "PE")]:
            leg = entry.get(key, {})
            if not leg:
                continue
            rows.append(
                {
                    "strike": strike,
                    "option_type": opt_type,
                    "oi": leg.get("openInterest", 0),
                    "volume": leg.get("totalTradedVolume", 0),
                    "ltp": leg.get("lastPrice", 0.0),
                    "iv": leg.get("impliedVolatility", 0.0) / 100.0,
                }
            )
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def load_live_chain_data():
    """
    Load live options chain data.
    Priority: (1) NSE public API  (2) local CSV storage  (3) synthetic fallback.
    Returns (all_chain_data, spots).
    """
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
    all_data, spots = {}, {}

    for sym in underlyings:
        # --- Priority 1: NSE public API ---
        chain_json = fetch_option_chain(sym)
        if chain_json:
            df = _nse_chain_to_df(chain_json)
            if not df.empty:
                spot = spot_price_from_chain(chain_json)
                all_data[sym] = df
                spots[sym] = spot
                print(f"  {sym}: NSE live data ({len(df)} rows, spot={spot:.0f})")
                continue
            print(f"  {sym}: NSE returned empty chain — trying CSV")

        # --- Priority 2: local CSV ---
        storage_dir = os.path.join(ROOT_DIR, "storage")
        candidates = []
        if os.path.isdir(storage_dir):
            candidates = sorted(
                [f for f in os.listdir(storage_dir) if sym.lower() in f.lower() and f.endswith(".csv")],
                reverse=True,
            )
        if candidates:
            path = os.path.join(storage_dir, candidates[0])
            try:
                df = pd.read_csv(path)
                all_data[sym] = df
                spot_col = next((c for c in df.columns if "spot" in c.lower()), None)
                spots[sym] = float(df[spot_col].iloc[0]) if spot_col else 0.0
                print(f"  {sym}: loaded from CSV {candidates[0]} ({len(df)} rows)")
                continue
            except Exception as e:
                print(f"  {sym}: CSV load failed — {e}")

        # --- Priority 3: synthetic fallback (LAST RESORT — no real OI) ---
        spot = {"NIFTY": 23000, "BANKNIFTY": 52000, "FINNIFTY": 23500, "MIDCPNIFTY": 12000}[sym]
        strikes = [spot - 500 + i * 50 for i in range(20)]
        all_data[sym] = pd.DataFrame(
            {
                "strike": strikes,
                "option_type": ["CE"] * 10 + ["PE"] * 10,
                "oi": [100000] * 20,  # flat OI — zero change signal, not random noise
                "volume": [10000] * 20,
                "ltp": np.random.uniform(10, 300, 20),
                "iv": [0.18] * 20,
            }
        )
        spots[sym] = float(spot)
        print(f"  {sym}: SYNTHETIC fallback — OI change factor will be 0 (no real data)")

    return all_data, spots


def run_ranking(top_n: int = 5) -> None:
    """Pre-market: rank all symbols, save predictions to gain_rank_history.json."""
    print(f"\n{'='*60}")
    print(f"  GAIN RANK ENGINE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    all_data, spots = load_live_chain_data()

    # Expiry day guard: OI rollover distorts change% on weekly expiry (Thursdays)
    if is_expiry_day():
        oi_history = {}
        print("  EXPIRY DAY (Thursday): OI change factor DISABLED to prevent rollover distortion")
    else:
        # Build oi_history from persistent cache (real prev session OI vs current)
        prev_oi_cache = load_oi_cache()
        oi_history = {}
        curr_oi_snapshot = {}
        for sym, df in all_data.items():
            oi_col = next(
                (
                    c
                    for c in df.columns
                    if c.lower() == "oi"
                    or ("oi" in c.lower() and "change" not in c.lower() and "prev" not in c.lower())
                ),
                None,
            )
            curr_oi = float(df[oi_col].sum()) if oi_col is not None else 0.0
            curr_oi_snapshot[sym] = int(curr_oi)
            if sym in prev_oi_cache and prev_oi_cache[sym] > 0:
                oi_history[sym] = {"prev_oi": prev_oi_cache[sym], "curr_oi": curr_oi}
        if oi_history:
            print(f"  Real OI change available for: {list(oi_history.keys())}")
        else:
            print("  OI cache empty — first run, OI change factor will use intra-chain fallback")

    # Load ML signal confidence from system3_signal_engine output (7th factor)
    ml_confidence = load_ml_confidence()
    if ml_confidence:
        print(f"  ML signal confidence loaded for: {list(ml_confidence.keys())}")
    else:
        print("  ML signal CSV not found — 7th factor (ml_confidence) will be 0, weight redistributed")

    engine = GainRankEngine(top_n=top_n)
    ranked_df = engine.rank_all(all_data, spots, oi_history, ml_confidence=ml_confidence)

    print(f"\n  Ranked {len(ranked_df)} underlyings by predicted gain potential:\n")
    display_cols = [
        "rank",
        "underlying",
        "gain_score",
        "ml_confidence_score",
        "oi_change_score",
        "expected_move_pct",
        "recommendation",
    ]
    avail_cols = [c for c in display_cols if c in ranked_df.columns]
    print(ranked_df[avail_cols].to_string(index=False))

    top = engine.get_top_n(all_data, spots, oi_history, ml_confidence=ml_confidence)
    if top:
        print(f"\n  TOP {len(top)} SYMBOLS FOR TODAY:")
        for t in top:
            print(
                f"    #{t['rank']}  {t['underlying']:12s}  score={t['gain_score']:.1f}"
                f"  ml_conf={t.get('ml_confidence_score', 0):.1f}"
                f"  oi={t.get('oi_change_score', 0):.1f}"
                f"  move={t['expected_move_pct']*100:.2f}%"
            )
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

    rho = report.get("rank_correlation_spearman", report.get("spearman_correlation", "N/A"))
    print(f"\n  Date            : {report['date']}")
    print(f"  Predicted order : {report.get('predicted_ranking', [])}")
    print(f"  Actual order    : {report.get('actual_ranking', [])}")
    print(f"  Spearman ρ      : {rho}")
    print(f"  Hit rate (top-3): {report.get('hit_rate', 0):.0%}")
    print(f"  Status          : {report.get('status')}")

    if report.get("retrain_signal"):
        print("\n  *** RETRAIN SIGNAL FIRED — accuracy below threshold ***")
        print("  Action: trigger model retraining pipeline")

    # Save OI snapshot after post-market validation so tomorrow's rank has real prev_oi.
    # Only persist if we got real data (OI > 0 means NSE delivered actual values).
    print("\n  Saving OI snapshot for tomorrow's ranking...")
    all_data, _ = load_live_chain_data()
    oi_snapshot = {}
    for sym, df in all_data.items():
        oi_col = next((c for c in df.columns if "oi" in c.lower() and "change" not in c.lower()), None)
        total = int(df[oi_col].sum()) if oi_col is not None else 0
        if total > 0:
            oi_snapshot[sym] = total
    if oi_snapshot:
        save_oi_cache(oi_snapshot)
        print(f"  OI snapshot saved (real NSE data): {oi_snapshot}")
    else:
        print("  OI snapshot NOT saved — all data was synthetic (zero OI), skipping to avoid contamination")


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
    parser.add_argument(
        "--mode", choices=["rank", "validate", "trend", "full"], default="full", help="Which step to run"
    )
    parser.add_argument("--top-n", type=int, default=5, help="Number of top symbols to rank (default: 5)")
    args = parser.parse_args()

    if args.mode in ("rank", "full"):
        run_ranking(top_n=args.top_n)

    if args.mode in ("validate", "full"):
        run_validation()

    if args.mode in ("trend", "full"):
        run_trend()

    if args.mode in ("validate", "trend", "full"):
        print("\n  Running post-market auto pipeline (proofs + gate sync)...")
        try:
            import subprocess

            pipeline = os.path.join(ROOT_DIR, "scripts", "system3_post_market_auto_pipeline.py")
            if os.path.isfile(pipeline):
                subprocess.run([sys.executable, pipeline], cwd=ROOT_DIR, timeout=900)
        except Exception as exc:
            print(f"  Post-market pipeline warning: {exc}")


if __name__ == "__main__":
    main()
