import os
import pandas as pd
import logging
from datetime import datetime

def run_phase_331_signal_integrity(root_path: str, logger) -> str:
    """
    Checks integrity of live signal CSVs before trade planning phases.
    Returns 'OK' if all checks pass, 'WARN' if any non-fatal issue, logs errors.
    """
    files = [
        "storage/live/angel_index_ai_signals.csv",
        "storage/live/angel_index_ai_signals_curated.csv",
        "storage/live/angel_index_ai_signals_with_forward.csv"
    ]
    required_columns = [
        "symbol", "index", "expiry", "strike", "option_type", "signal", "score"
    ]
    # Forward columns are dynamic, infer from with_forward.csv if present
    forward_cols = []
    result = "OK"
    for f in files:
        fpath = os.path.join(root_path, f)
        if not os.path.exists(fpath):
            logger.warning(f"Phase 331: Missing file: {f}")
            result = "WARN"
            continue
        try:
            df = pd.read_csv(fpath)
            if df.shape[0] == 0:
                logger.warning(f"Phase 331: File {f} has zero rows.")
                result = "WARN"
            # Infer forward columns from with_forward.csv
            if "with_forward" in f:
                forward_cols = [c for c in df.columns if c.startswith("forward_return")]
            # Check required columns
            missing = [c for c in required_columns if c not in df.columns]
            if missing:
                logger.warning(f"Phase 331: File {f} missing columns: {missing}")
                result = "WARN"
            # Check NaNs in key columns
            key_cols = required_columns + forward_cols
            for col in key_cols:
                if col in df.columns and df[col].isnull().any():
                    logger.warning(f"Phase 331: NaN detected in column '{col}' of {f}")
                    result = "WARN"
            # Check numeric types
            for col in ["score"] + forward_cols:
                if col in df.columns:
                    try:
                        pd.to_numeric(df[col])
                    except Exception:
                        logger.warning(f"Phase 331: Non-numeric values in column '{col}' of {f}")
                        result = "WARN"
        except Exception as e:
            logger.error(f"Phase 331: Fatal error reading {f}: {e}")
            result = "WARN"
    logger.info(f"Phase 331 completed with result: {result}")
    return result
