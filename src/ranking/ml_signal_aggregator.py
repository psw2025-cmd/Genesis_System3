"""
ML Signal Aggregator — bridges system3_signal_engine to GainRankEngine.

Reads the per-option ML signal CSV (storage/live/dhan_index_ai_signals.csv)
and aggregates to per-underlying ML confidence scores used as a 7th factor
in GainRankEngine's gain ranking.

Signal CSV schema:
  ts, underlying, expiry, strike, side, ltp, spot,
  prob_BUY_CE, prob_BUY_PE, expected_move_score, signal_label

Aggregation logic:
  ml_confidence = avg(prob_BUY_CE) across all rows for that underlying
  → High prob_BUY_CE = ML expects calls to gain = underlying likely goes UP
  → Scaled 0-100 for consistent scoring with other GainRankEngine factors
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SIGNAL_CSV = os.path.join(ROOT_DIR, "storage", "live", "dhan_index_ai_signals.csv")

MAX_SIGNAL_AGE_HOURS = 24.0  # bhavcopy signals written at 18:45 IST are valid until next-day 09:15 (14.5h gap)


def load_ml_confidence() -> Dict[str, float]:
    """
    Reads the signal CSV and returns per-underlying ML confidence score (0-100).
    Returns empty dict if CSV missing, stale, or unreadable — GainRankEngine
    treats missing ml_confidence as 0 and weights other factors normally.
    """
    if not os.path.exists(SIGNAL_CSV):
        logger.info("ML signal CSV not found — signal engine has not run today")
        return {}

    try:
        df = pd.read_csv(SIGNAL_CSV)
    except Exception as e:
        logger.warning(f"Failed to read signal CSV: {e}")
        return {}

    if df.empty:
        return {}

    # Staleness check
    if "ts" in df.columns:
        try:
            latest_ts = pd.to_datetime(df["ts"]).max()
            age_hours = (datetime.now() - latest_ts.replace(tzinfo=None)).total_seconds() / 3600
            if age_hours > MAX_SIGNAL_AGE_HOURS:
                logger.warning(f"ML signals stale ({age_hours:.1f}h old) — skipping for today's ranking")
                return {}
        except Exception:
            pass

    required = {"underlying", "prob_BUY_CE", "expected_move_score"}
    if not required.issubset(df.columns):
        logger.warning(f"Signal CSV missing columns: {required - set(df.columns)}")
        return {}

    result: Dict[str, float] = {}

    for underlying, group in df.groupby("underlying"):
        prob_ce = group["prob_BUY_CE"].dropna()
        move_score = group["expected_move_score"].dropna()

        if prob_ce.empty:
            continue

        # avg prob_BUY_CE → directional conviction (0.5 = neutral, 1.0 = strong bull)
        avg_ce = float(prob_ce.mean())
        # avg expected_move_score → magnitude conviction (positive = CE-biased)
        avg_move = float(move_score.mean()) if not move_score.empty else 0.0

        # Convert to 0-100 scale:
        # prob_BUY_CE: 0.5 = 0 signal, 1.0 = 100 signal (scale linearly above 0.5)
        directional_score = max(0.0, (avg_ce - 0.5) * 200)  # 0 to 100
        # move_score is already 0-centred; scale by 50 to normalize
        magnitude_score = min(100.0, max(0.0, avg_move * 50 + 50))

        # Blend: 60% directional + 40% magnitude
        ml_conf = directional_score * 0.6 + magnitude_score * 0.4
        result[str(underlying)] = round(min(100.0, max(0.0, ml_conf)), 2)

        logger.info(
            f"  {underlying}: ml_conf={result[str(underlying)]:.1f} "
            f"(prob_CE={avg_ce:.3f}, move={avg_move:.3f}, n={len(group)})"
        )

    if result:
        logger.info(f"ML confidence loaded for: {list(result.keys())}")
    return result


def ml_confidence_score(underlying: str, ml_confidence: Dict[str, float]) -> float:
    """Returns the 0-100 ML confidence score for a specific underlying, or 0 if missing."""
    return ml_confidence.get(underlying, 0.0)
