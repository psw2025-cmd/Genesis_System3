"""
System3 training data inspector.

DRY-RUN only: inspects curated/live training CSVs used by the ML predictor.
"""

from pathlib import Path

import pandas as pd

from core.engine.ai_model.ml_predictor import (
    CURATED_TRAINING_PATH,
    LIVE_TRAINING_PATH,
    load_training_data,
)


MIN_SAMPLES_WARNING = 200


def main() -> None:
    print("=== SYSTEM3 TRAINING DATA INSPECTOR ===")

    # Prefer curated training dataset
    df = None
    used_path: Path | None = None

    if CURATED_TRAINING_PATH.exists():
        print(f"[INFO] Trying curated training file: {CURATED_TRAINING_PATH}")
        df = load_training_data(CURATED_TRAINING_PATH)
        used_path = CURATED_TRAINING_PATH if df is not None else None

    if df is None:
        if LIVE_TRAINING_PATH.exists():
            print(f"[INFO] Falling back to live training file: {LIVE_TRAINING_PATH}")
            df = load_training_data(LIVE_TRAINING_PATH)
            used_path = LIVE_TRAINING_PATH if df is not None else None
        else:
            print("[WARN] Neither curated nor live training CSV file exists.")

    if df is None or used_path is None:
        print("[ERROR] No valid training data; both curated and live CSV failed.")
        return

    print()
    print(f"[OK] Loaded training data from: {used_path}")
    print(f"[OK] Total rows: {len(df)}")

    # Basic class distribution
    label_col = None
    for candidate in ("direction", "pred_label", "signal"):
        if candidate in df.columns:
            label_col = candidate
            break

    if label_col is not None:
        vc = df[label_col].value_counts(dropna=False)
        print()
        print(f"[INFO] Class distribution by '{label_col}':")
        for cls, cnt in vc.items():
            print(f"  {cls!r}: {cnt}")
    else:
        print("[WARN] No obvious label column found (direction/pred_label/signal).")

    # Distinct underlyings
    if "underlying" in df.columns:
        unique_underlyings = sorted(df["underlying"].dropna().unique().tolist())
        print()
        print(f"[INFO] Distinct underlyings ({len(unique_underlyings)}): {unique_underlyings}")

    # Sample size warning
    if len(df) < MIN_SAMPLES_WARNING:
        print()
        print(
            f"[WARN] Training sample size is small ({len(df)} < {MIN_SAMPLES_WARNING}); "
            "ML model may be unstable."
        )

    print()
    print("=== INSPECTION COMPLETE ===")


if __name__ == "__main__":
    main()


