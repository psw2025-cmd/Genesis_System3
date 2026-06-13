"""
Daily Gain Scanner
==================
Orchestrates the full daily cycle:
  1. Load live options chain for all tracked underlyings (Dhan API)
  2. Run GainRankEngine → produce ranked top-N symbols by predicted gain
  3. Log predictions to state/gain_rank_history.json
  4. Post-market: run MarketResultValidator → compare vs actual NSE top movers
  5. Compute Spearman ρ + hit rate, save validation report
  6. Emit retraining signal if accuracy drops below threshold

Run during market hours for prediction, after close for validation.
  python -m src.ranking.daily_gain_scanner --mode predict
  python -m src.ranking.daily_gain_scanner --mode validate
  python -m src.ranking.daily_gain_scanner --mode full
"""

import argparse
import json
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ranking.gain_rank_engine import GainRankEngine
from src.validation.market_result_validator import MarketResultValidator

try:
    from core.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("daily_gain_scanner")

TRACKED_SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
REPORT_DIR = os.path.join(ROOT_DIR, "state", "daily_scan_reports")


def load_chain_from_storage(symbol: str):
    """Load latest stored option chain CSV for a symbol."""
    import pandas as pd
    storage_dir = os.path.join(ROOT_DIR, "storage")
    if not os.path.isdir(storage_dir):
        return None
    candidates = sorted(
        [f for f in os.listdir(storage_dir)
         if symbol.lower() in f.lower() and f.endswith(".csv")],
        reverse=True
    )
    if not candidates:
        return None
    path = os.path.join(storage_dir, candidates[0])
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def load_spot_from_chain(df, symbol: str) -> float:
    """Extract spot price from chain dataframe."""
    for col in ("spot_price", "underlying_value", "spot", "ltp"):
        if col in df.columns:
            v = df[col].dropna()
            if not v.empty:
                return float(v.iloc[0])
    return 0.0


def run_prediction() -> dict:
    """Run gain ranking prediction and save snapshot."""
    logger.info("=== DAILY GAIN SCANNER: PREDICTION MODE ===")

    all_data, spots = {}, {}
    for sym in TRACKED_SYMBOLS:
        df = load_chain_from_storage(sym)
        if df is not None and not df.empty:
            all_data[sym] = df
            spots[sym] = load_spot_from_chain(df, sym)

    if not all_data:
        logger.warning("No chain data available — skipping prediction")
        return {"status": "skipped", "reason": "no_chain_data"}

    engine = GainRankEngine(top_n=3)
    ranked = engine.rank_all(all_data, spots)

    if ranked.empty:
        return {"status": "skipped", "reason": "ranking_empty"}

    top3 = engine.get_top_n(all_data, spots)
    result = {
        "status": "ok",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "top_predictions": top3,
        "full_ranking": ranked[["rank", "underlying", "gain_score",
                                  "expected_move_pct", "recommendation"]].to_dict(orient="records"),
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    fname = f"prediction_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
    with open(os.path.join(REPORT_DIR, fname), "w") as f:
        json.dump(result, f, indent=2)

    logger.info("Top predictions today:")
    for p in top3:
        logger.info(f"  #{p['rank']} {p['underlying']:12s} | gain_score={p['gain_score']:.1f} | "
                    f"expected_move={p['expected_move_pct']*100:.2f}%")

    return result


def run_validation() -> dict:
    """Run post-market validation: predicted vs actual NSE results."""
    logger.info("=== DAILY GAIN SCANNER: VALIDATION MODE ===")
    validator = MarketResultValidator()
    report = validator.run_daily_validation()

    corr = report.get("spearman_correlation")
    hit = report.get("hit_rate")
    status = report.get("status", "UNKNOWN")

    if corr is not None:
        logger.info(f"Spearman ρ = {corr:.3f} | Hit Rate = {hit:.1%} | Status = {status}")

    if report.get("retrain_signal"):
        logger.warning(">>> RETRAIN SIGNAL: model accuracy below threshold — schedule retraining")
        _emit_retrain_signal()

    trend = validator.get_accuracy_trend(last_n_days=14)
    logger.info(f"14-day trend | avg_ρ={trend.get('avg_spearman_correlation', 0):.3f} | "
                f"avg_hit={trend.get('avg_hit_rate', 0):.1%} | "
                f"trend={'↑' if trend.get('correlation_trend', 0) > 0 else '↓'}")
    return report


def _emit_retrain_signal():
    """Write a retrain signal file that the ML pipeline monitors."""
    signal_file = os.path.join(ROOT_DIR, "state", "retrain_signal.json")
    signal = {
        "triggered_at": datetime.now().isoformat(),
        "reason": "market_result_validation_below_threshold",
        "action": "retrain_ensemble_models",
    }
    with open(signal_file, "w") as f:
        json.dump(signal, f, indent=2)
    logger.warning(f"Retrain signal written to {signal_file}")


def main():
    parser = argparse.ArgumentParser(description="Daily Gain Scanner")
    parser.add_argument("--mode", choices=["predict", "validate", "full"],
                        default="full", help="Mode to run")
    args = parser.parse_args()

    results = {}
    if args.mode in ("predict", "full"):
        results["prediction"] = run_prediction()

    if args.mode in ("validate", "full"):
        results["validation"] = run_validation()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
