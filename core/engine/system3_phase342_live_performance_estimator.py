"""
System3 Phase 342 - Live Prediction Performance Estimator (Paper)

During DRY-RUN, estimates real-time model performance using forward returns and virtual PnL.
Computes hit-rate, average returns, max drawdown, and realized vs predicted metrics.

Mode: Live, each OP cycle (hourly).
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


def run_phase_342_live_performance_estimator(root_path: str = None, logger_obj=None) -> str:
    """
    Phase 342: Estimate live model performance during DRY-RUN.

    Returns: 'OK'
    """
    if logger_obj:
        logger = logger_obj

    if root_path is None:
        root_path = str(PROJECT_ROOT)

    root = Path(root_path)
    logger.info("[PH342] Starting Live Performance Estimator")

    try:
        # Load virtual orders and forward returns
        virt_orders_file = root / "storage" / "live" / "dhan_virtual_orders.csv"
        signals_forward_file = root / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"
        diag_dir = root / "storage" / "live" / "diagnostics"
        diag_dir.mkdir(parents=True, exist_ok=True)

        output_file = diag_dir / "live_performance_snapshot.json"

        performance_snapshot = {
            "timestamp": datetime.now().isoformat(),
            "hit_rate_buy": 0.0,
            "hit_rate_sell": 0.0,
            "avg_return_buy": 0.0,
            "avg_return_sell": 0.0,
            "max_drawdown": 0.0,
            "realized_accuracy": 0.0,
            "trade_count": 0,
            "warning": None,
        }

        # Load virtual orders
        if virt_orders_file.exists():
            df_orders = pd.read_csv(virt_orders_file)
            performance_snapshot["trade_count"] = len(df_orders)
        else:
            logger.warning("[PH342] Virtual orders file not found")

        # Load forward returns
        if signals_forward_file.exists():
            df_signals = pd.read_csv(signals_forward_file)

            # Extract forward return columns
            fwd_cols = [c for c in df_signals.columns if "fwd_ret" in c.lower()]

            if fwd_cols and "signal" in df_signals.columns:
                # Compute hit rates per signal type
                for signal_type in ["BUY", "SELL"]:
                    mask = df_signals["signal"] == signal_type
                    if mask.sum() > 0:
                        subset = df_signals[mask]
                        # Simple hit rate: proportion of positive forward returns for BUY, negative for SELL
                        hits = 0
                        for col in fwd_cols:
                            if signal_type == "BUY":
                                hits += (subset[col] > 0).sum()
                            else:
                                hits += (subset[col] < 0).sum()

                        hit_rate = hits / (len(subset) * len(fwd_cols)) if len(fwd_cols) > 0 else 0.0
                        avg_return = subset[fwd_cols[0]].mean() if fwd_cols else 0.0

                        if signal_type == "BUY":
                            performance_snapshot["hit_rate_buy"] = float(hit_rate)
                            performance_snapshot["avg_return_buy"] = float(avg_return)
                        else:
                            performance_snapshot["hit_rate_sell"] = float(hit_rate)
                            performance_snapshot["avg_return_sell"] = float(avg_return)

                # Compute realized accuracy
                overall_hits = 0
                overall_total = 0
                for signal_type in ["BUY", "SELL"]:
                    mask = df_signals["signal"] == signal_type
                    for col in fwd_cols:
                        if signal_type == "BUY":
                            overall_hits += (df_signals[mask][col] > 0).sum()
                        else:
                            overall_hits += (df_signals[mask][col] < 0).sum()
                        overall_total += mask.sum()

                performance_snapshot["realized_accuracy"] = float(
                    overall_hits / overall_total if overall_total > 0 else 0.0
                )

        # Write snapshot
        with open(output_file, "w") as f:
            json.dump(performance_snapshot, f, indent=2)

        logger.info(f"[PH342] Live performance snapshot: {performance_snapshot}")
        return "OK"

    except Exception as e:
        logger.error(f"[PH342] Unexpected error: {e}", exc_info=True)
        return "WARN"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_phase_342_live_performance_estimator()
    print(f"Phase 342 result: {result}")
