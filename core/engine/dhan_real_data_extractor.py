"""
Dhan Index Options - Real Data Extractor for Training

Converts real outcomes into training rows.
AUTO-UPDATE: DISABLED - Only extracts, never auto-trains.
"""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from core.engine.dhan_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
REAL_TRAINING_CSV = TRAINING_DIR / "dhan_real_training_candidates.csv"

TRAINING_DIR.mkdir(parents=True, exist_ok=True)


def extract_real_training_data() -> pd.DataFrame:
    """
    Extract real outcomes as training candidates.

    Returns:
        DataFrame with training candidate rows
    """
    df_outcomes = load_outcomes()
    if df_outcomes.empty:
        return pd.DataFrame()

    # Load original signals to get features
    from pathlib import Path

    LIVE_DIR = PROJECT_ROOT / "storage" / "live"
    SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"

    if not SIGNALS_CSV.exists():
        print("[EXTRACTOR] Signals CSV not found. Cannot extract features.")
        return pd.DataFrame()

    try:
        df_signals = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
    except Exception as e:
        print(f"[EXTRACTOR] Failed to load signals: {e}")
        return pd.DataFrame()

    # Match outcomes with signals by snapshot_index
    training_rows = []

    for _, outcome in df_outcomes.iterrows():
        snapshot_idx = outcome.get("snapshot_index", -1)
        if snapshot_idx < 0:
            continue

        # Find matching signal row
        if "snapshot_index" in df_signals.columns:
            signal_row = df_signals[df_signals["snapshot_index"] == snapshot_idx]
        else:
            # Fallback: match by underlying, strike, side, timestamp
            signal_row = df_signals[
                (df_signals.get("underlying", "") == outcome.get("underlying", ""))
                & (df_signals.get("strike", 0) == outcome.get("strike", 0))
                & (df_signals.get("side", "") == outcome.get("side", ""))
            ]

        if signal_row.empty:
            continue

        signal_row = signal_row.iloc[0]

        # Create training row
        training_row = {}

        # Copy all features from signal
        feature_cols = [
            c
            for c in df_signals.columns
            if c
            not in [
                "ts",
                "underlying",
                "expiry",
                "side",
                "strike",
                "pred_label",
                "pred_confidence",
                "expected_move_score",
            ]
        ]
        for col in feature_cols:
            training_row[col] = signal_row.get(col, 0.0)

        # Add outcome label
        pnl = outcome.get("pnl_pct", 0.0)
        if pnl > 5.0:
            training_row["label"] = "STRONG_BUY"
        elif pnl > 2.0:
            training_row["label"] = "BUY"
        elif pnl < -5.0:
            training_row["label"] = "STRONG_SELL"
        elif pnl < -2.0:
            training_row["label"] = "SELL"
        else:
            training_row["label"] = "HOLD"

        # Add PnL bucket
        if pnl > 10.0:
            training_row["pnl_bucket"] = "HIGH_WIN"
        elif pnl > 2.0:
            training_row["pnl_bucket"] = "WIN"
        elif pnl < -10.0:
            training_row["pnl_bucket"] = "HIGH_LOSS"
        elif pnl < -2.0:
            training_row["pnl_bucket"] = "LOSS"
        else:
            training_row["pnl_bucket"] = "FLAT"

        # Add metadata
        training_row["underlying"] = outcome.get("underlying", "")
        training_row["strike"] = outcome.get("strike", 0.0)
        training_row["side"] = outcome.get("side", "")
        training_row["actual_pnl_pct"] = pnl
        training_row["outcome_timestamp"] = outcome.get("timestamp", "")

        training_rows.append(training_row)

    if not training_rows:
        return pd.DataFrame()

    df_training = pd.DataFrame(training_rows)
    return df_training


def save_training_candidates(df: pd.DataFrame) -> Path:
    """
    Save training candidates to CSV.

    Returns:
        Path to saved CSV
    """
    if df.empty:
        return REAL_TRAINING_CSV

    df.to_csv(REAL_TRAINING_CSV, index=False)
    return REAL_TRAINING_CSV


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - REAL DATA EXTRACTOR ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Extraction only\n")

    df_training = extract_real_training_data()

    if df_training.empty:
        print("[INFO] No training candidates extracted.")
        return

    print(f"[EXTRACTED] {len(df_training)} training candidates")

    # Show label distribution
    if "label" in df_training.columns:
        print("\n=== LABEL DISTRIBUTION ===")
        label_counts = df_training["label"].value_counts()
        for label, count in label_counts.items():
            print(f"{label}: {count}")

    # Save
    save_path = save_training_candidates(df_training)
    print(f"\n[SAVE] Training candidates saved to: {save_path}")


if __name__ == "__main__":
    main()
