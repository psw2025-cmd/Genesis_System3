"""
System3 Phase 334 - Model Drift Snapshot Builder

Creates daily snapshot of key model performance stats for drift detection.
No retraining here, just logging performance metrics.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def compute_hit_rate(df: pd.DataFrame, signal_type: str) -> float:
    """
    Compute hit rate for a signal type.
    Hit rate = proportion where forward return matches signal direction.
    """
    if signal_type not in df["signal"].values:
        return 0.0

    subset = df[df["signal"] == signal_type].copy()

    # Use fwd_ret_1 as primary forward return
    if "fwd_ret_1" not in subset.columns:
        return 0.0

    subset = subset.dropna(subset=["fwd_ret_1"])

    if len(subset) == 0:
        return 0.0

    # For BUY signals, hit = positive forward return
    # For SELL signals, hit = negative forward return
    if "BUY" in signal_type:
        hits = (subset["fwd_ret_1"] > 0).sum()
    elif "SELL" in signal_type:
        hits = (subset["fwd_ret_1"] < 0).sum()
    else:
        # HOLD or other: no clear direction
        return 0.0

    hit_rate = hits / len(subset)
    return hit_rate


def run_phase334_model_drift_snapshot(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 334: Model Drift Snapshot Builder

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 334: Model Drift Snapshot Builder")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load forward signals
    forward_file = root / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"

    if not forward_file.exists():
        logger.warning(f"Forward signals file not found: {forward_file}")
        return {"phase": 334, "status": "WARN", "outputs": {"error": "Forward signals file not found"}}

    try:
        df = pd.read_csv(forward_file, low_memory=False)

        # Filter to rows with valid forward returns
        valid_df = df.dropna(subset=["fwd_ret_1"]) if "fwd_ret_1" in df.columns else df

        n_signals = len(valid_df)
        logger.info(f"Signals with valid forward returns: {n_signals}")

        warnings = []
        if n_signals < 10:
            warnings.append(f"Low sample size: only {n_signals} signals with forward returns")

        # Compute metrics by signal type
        metrics = {}
        signal_types = ["BUY", "SELL", "BUY_CE", "BUY_PE", "SELL_CE", "SELL_PE"]

        for sig_type in signal_types:
            if sig_type in df["signal"].values if "signal" in df.columns else []:
                subset = valid_df[valid_df["signal"] == sig_type] if "signal" in valid_df.columns else pd.DataFrame()

                if len(subset) > 0:
                    avg_fwd_ret = subset["fwd_ret_1"].mean() if "fwd_ret_1" in subset.columns else 0.0
                    hit_rate = compute_hit_rate(valid_df, sig_type)

                    metrics[sig_type] = {
                        "count": len(subset),
                        "avg_forward_return": float(avg_fwd_ret),
                        "hit_rate": float(hit_rate),
                    }

                    logger.info(
                        f"{sig_type}: count={len(subset)}, avg_fwd_ret={avg_fwd_ret:.4f}, hit_rate={hit_rate:.2%}"
                    )

        # Overall averages
        overall_avg_fwd_ret = (
            valid_df["fwd_ret_1"].mean() if "fwd_ret_1" in valid_df.columns and len(valid_df) > 0 else 0.0
        )

        # Prepare daily snapshot
        snapshot = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "n_signals": n_signals,
            "overall_avg_forward_return": float(overall_avg_fwd_ret),
            "by_signal_type": metrics,
            "warnings": warnings,
        }

        # Append to daily CSV
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        drift_csv = diagnostics_dir / "model_drift_daily.csv"

        # Create CSV header if not exists
        if not drift_csv.exists():
            with open(drift_csv, "w", encoding="utf-8") as f:
                f.write(
                    "date,n_signals,overall_avg_forward_return,avg_fwd_ret_buy,avg_fwd_ret_sell,hit_rate_buy,hit_rate_sell,n_warn_cases\n"
                )

        # Append data
        avg_fwd_ret_buy = metrics.get("BUY", {}).get("avg_forward_return", 0.0)
        avg_fwd_ret_sell = metrics.get("SELL", {}).get("avg_forward_return", 0.0)
        hit_rate_buy = metrics.get("BUY", {}).get("hit_rate", 0.0)
        hit_rate_sell = metrics.get("SELL", {}).get("hit_rate", 0.0)
        n_warn = len(warnings)

        with open(drift_csv, "a", encoding="utf-8") as f:
            f.write(
                f"{snapshot['date']},{n_signals},{overall_avg_fwd_ret:.6f},{avg_fwd_ret_buy:.6f},{avg_fwd_ret_sell:.6f},{hit_rate_buy:.6f},{hit_rate_sell:.6f},{n_warn}\n"
            )

        logger.info(f"Daily snapshot appended to: {drift_csv}")

        # Determine status
        status = "WARN" if warnings else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 334 Complete: {status}")
        logger.info(f"Signals processed: {n_signals}")
        logger.info("=" * 70)

        return {
            "phase": 334,
            "status": status,
            "outputs": snapshot,
        }

    except Exception as e:
        logger.error(f"Error in Phase 334: {e}")
        return {"phase": 334, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_334(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase334_model_drift_snapshot(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase334_model_drift_snapshot()
    print(f"\nPhase 334 Status: {result['status']}")
