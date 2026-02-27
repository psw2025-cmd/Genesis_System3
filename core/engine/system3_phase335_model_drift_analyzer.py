"""
System3 Phase 335 - Model Drift Analyzer (Light)

Reads model_drift_daily.csv and detects early signs of drift.
Compares recent performance against moving averages.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Drift detection thresholds
DRIFT_THRESHOLD_PCT = 15.0  # % drop from average
MIN_DAYS_FOR_ANALYSIS = 5


def run_phase335_model_drift_analyzer(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 335: Model Drift Analyzer (Light)

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 335: Model Drift Analyzer (Light)")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load drift daily CSV
    drift_csv = root / "storage" / "live" / "diagnostics" / "model_drift_daily.csv"

    if not drift_csv.exists():
        logger.warning(f"Drift CSV not found: {drift_csv}")
        return {"phase": 335, "status": "WARN", "outputs": {"error": "Drift CSV not found - run Phase 334 first"}}

    try:
        df = pd.read_csv(drift_csv)

        if len(df) < MIN_DAYS_FOR_ANALYSIS:
            logger.warning(f"Insufficient data for drift analysis: {len(df)} days, need {MIN_DAYS_FOR_ANALYSIS}")
            return {
                "phase": 335,
                "status": "WARN",
                "outputs": {
                    "warning": f"Insufficient data: {len(df)} days",
                    "drift_detected": False,
                },
            }

        # Sort by date
        df = df.sort_values("date")

        # Compute moving averages
        df["hit_rate_buy_ma5"] = df["hit_rate_buy"].rolling(window=5, min_periods=1).mean()
        df["hit_rate_sell_ma5"] = df["hit_rate_sell"].rolling(window=5, min_periods=1).mean()
        df["hit_rate_buy_ma20"] = df["hit_rate_buy"].rolling(window=20, min_periods=5).mean()
        df["hit_rate_sell_ma20"] = df["hit_rate_sell"].rolling(window=20, min_periods=5).mean()

        df["avg_fwd_ret_buy_ma5"] = df["avg_fwd_ret_buy"].rolling(window=5, min_periods=1).mean()
        df["avg_fwd_ret_sell_ma5"] = df["avg_fwd_ret_sell"].rolling(window=5, min_periods=1).mean()
        df["avg_fwd_ret_buy_ma20"] = df["avg_fwd_ret_buy"].rolling(window=20, min_periods=5).mean()
        df["avg_fwd_ret_sell_ma20"] = df["avg_fwd_ret_sell"].rolling(window=20, min_periods=5).mean()

        # Get latest row
        latest = df.iloc[-1]

        drift_signals = []
        drift_detected = False

        # Check buy hit rate
        if pd.notna(latest["hit_rate_buy"]) and pd.notna(latest["hit_rate_buy_ma5"]):
            buy_hit_latest = latest["hit_rate_buy"]
            buy_hit_ma5 = latest["hit_rate_buy_ma5"]
            buy_hit_ma20 = latest["hit_rate_buy_ma20"] if pd.notna(latest["hit_rate_buy_ma20"]) else buy_hit_ma5

            if buy_hit_ma5 > 0:
                drop_pct_5d = ((buy_hit_ma5 - buy_hit_latest) / buy_hit_ma5) * 100
                if drop_pct_5d > DRIFT_THRESHOLD_PCT:
                    drift_signals.append(
                        f"BUY hit rate dropped {drop_pct_5d:.1f}% below 5-day avg ({buy_hit_latest:.2%} vs {buy_hit_ma5:.2%})"
                    )
                    drift_detected = True

            if buy_hit_ma20 > 0:
                drop_pct_20d = ((buy_hit_ma20 - buy_hit_latest) / buy_hit_ma20) * 100
                if drop_pct_20d > DRIFT_THRESHOLD_PCT:
                    drift_signals.append(
                        f"BUY hit rate dropped {drop_pct_20d:.1f}% below 20-day avg ({buy_hit_latest:.2%} vs {buy_hit_ma20:.2%})"
                    )
                    drift_detected = True

        # Check sell hit rate
        if pd.notna(latest["hit_rate_sell"]) and pd.notna(latest["hit_rate_sell_ma5"]):
            sell_hit_latest = latest["hit_rate_sell"]
            sell_hit_ma5 = latest["hit_rate_sell_ma5"]
            sell_hit_ma20 = latest["hit_rate_sell_ma20"] if pd.notna(latest["hit_rate_sell_ma20"]) else sell_hit_ma5

            if sell_hit_ma5 > 0:
                drop_pct_5d = ((sell_hit_ma5 - sell_hit_latest) / sell_hit_ma5) * 100
                if drop_pct_5d > DRIFT_THRESHOLD_PCT:
                    drift_signals.append(
                        f"SELL hit rate dropped {drop_pct_5d:.1f}% below 5-day avg ({sell_hit_latest:.2%} vs {sell_hit_ma5:.2%})"
                    )
                    drift_detected = True

            if sell_hit_ma20 > 0:
                drop_pct_20d = ((sell_hit_ma20 - sell_hit_latest) / sell_hit_ma20) * 100
                if drop_pct_20d > DRIFT_THRESHOLD_PCT:
                    drift_signals.append(
                        f"SELL hit rate dropped {drop_pct_20d:.1f}% below 20-day avg ({sell_hit_latest:.2%} vs {sell_hit_ma20:.2%})"
                    )
                    drift_detected = True

        # Check forward returns
        if pd.notna(latest["avg_fwd_ret_buy"]) and pd.notna(latest["avg_fwd_ret_buy_ma5"]):
            buy_ret_latest = latest["avg_fwd_ret_buy"]
            buy_ret_ma5 = latest["avg_fwd_ret_buy_ma5"]

            if buy_ret_ma5 > 0:
                drop_pct = ((buy_ret_ma5 - buy_ret_latest) / buy_ret_ma5) * 100
                if drop_pct > DRIFT_THRESHOLD_PCT:
                    drift_signals.append(f"BUY avg forward return dropped {drop_pct:.1f}% below 5-day avg")
                    drift_detected = True

        # Log drift signals
        if drift_detected:
            logger.warning("⚠️  MODEL DRIFT DETECTED:")
            for signal in drift_signals:
                logger.warning(f"  - {signal}")
        else:
            logger.info("✓ No significant drift detected")

        # Write drift status
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        drift_status = {
            "timestamp": datetime.now().isoformat(),
            "phase": 335,
            "drift_detected": drift_detected,
            "drift_signals": drift_signals,
            "latest_metrics": {
                "date": latest["date"],
                "hit_rate_buy": float(latest["hit_rate_buy"]) if pd.notna(latest["hit_rate_buy"]) else None,
                "hit_rate_sell": float(latest["hit_rate_sell"]) if pd.notna(latest["hit_rate_sell"]) else None,
                "hit_rate_buy_ma5": float(latest["hit_rate_buy_ma5"]) if pd.notna(latest["hit_rate_buy_ma5"]) else None,
                "hit_rate_sell_ma5": (
                    float(latest["hit_rate_sell_ma5"]) if pd.notna(latest["hit_rate_sell_ma5"]) else None
                ),
                "hit_rate_buy_ma20": (
                    float(latest["hit_rate_buy_ma20"]) if pd.notna(latest["hit_rate_buy_ma20"]) else None
                ),
                "hit_rate_sell_ma20": (
                    float(latest["hit_rate_sell_ma20"]) if pd.notna(latest["hit_rate_sell_ma20"]) else None
                ),
            },
            "threshold_pct": DRIFT_THRESHOLD_PCT,
        }

        status_file = diagnostics_dir / "model_drift_status.json"
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(drift_status, f, indent=2)

        logger.info(f"Drift status written to: {status_file}")

        # Determine phase status
        status = "WARN" if drift_detected else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 335 Complete: {status}")
        logger.info(f"Drift detected: {drift_detected}")
        logger.info("=" * 70)

        return {
            "phase": 335,
            "status": status,
            "outputs": drift_status,
        }

    except Exception as e:
        logger.error(f"Error in Phase 335: {e}")
        return {"phase": 335, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_335(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase335_model_drift_analyzer(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase335_model_drift_analyzer()
    print(f"\nPhase 335 Status: {result['status']}")
