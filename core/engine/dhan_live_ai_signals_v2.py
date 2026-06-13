"""
Angel Live AI Signals V2 - Enhanced with System3 Signal Engine

This version integrates the new System3 signal engine while maintaining
compatibility with existing code.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger
from core.engine.system3_signal_engine import run_signal_engine

# Import original function for fallback
from core.engine.dhan_live_ai_signals import (
    load_models_and_meta,
    predict_for_snapshot_df as original_predict,
    append_signals_to_csv as original_append,
)

SIGNALS_CSV = ROOT_DIR / "storage" / "live" / "dhan_index_ai_signals.csv"


def run_once_with_snapshot(df_snap: pd.DataFrame, use_new_engine: bool = True) -> pd.DataFrame:
    """
    Entry point for one snapshot DataFrame.

    Uses new System3 signal engine by default, falls back to original if needed.

    Args:
        df_snap: Snapshot DataFrame
        use_new_engine: Whether to use new signal engine (default True)

    Returns:
        DataFrame with signals
    """
    if df_snap is None or df_snap.empty:
        logger.warning("Empty snapshot provided")
        return pd.DataFrame()

    if use_new_engine:
        try:
            logger.info("Using System3 Signal Engine (v2)")
            df_signals = run_signal_engine(df_snap)

            if not df_signals.empty:
                # Verify we have non-zero scores
                zero_scores = (df_signals["final_score"] == 0.0).sum()
                if zero_scores > 0:
                    logger.warning(f"Found {zero_scores} signals with zero scores")

                # Verify BUY/SELL signals exist
                buy_count = len(df_signals[df_signals["signal"] == "BUY"])
                sell_count = len(df_signals[df_signals["signal"] == "SELL"])
                logger.info(
                    f"Signals generated: BUY={buy_count}, SELL={sell_count}, HOLD={len(df_signals) - buy_count - sell_count}"
                )

            return df_signals

        except Exception as e:
            logger.error(f"New signal engine failed: {e}, falling back to original")
            use_new_engine = False

    # Fallback to original
    if not use_new_engine:
        logger.info("Using original signal engine")
        root = ROOT_DIR
        models = load_models_and_meta(root)

        if not models:
            logger.error("No models available")
            return pd.DataFrame()

        df_signals = original_predict(df_snap, models)
        if not df_signals.empty:
            original_append(df_signals, SIGNALS_CSV)

        return df_signals

    return pd.DataFrame()


# Maintain compatibility with existing code
def predict_for_snapshot_df(df_snap: pd.DataFrame, models: Dict[str, Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Compatibility wrapper - uses new engine by default.
    """
    return run_once_with_snapshot(df_snap, use_new_engine=True)


# Update the original module's function if imported
if __name__ != "__main__":
    # Monkey-patch the original module if needed
    import core.engine.dhan_live_ai_signals as original_module

    original_module.run_once_with_snapshot = run_once_with_snapshot
