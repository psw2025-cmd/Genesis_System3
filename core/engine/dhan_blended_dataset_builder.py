"""
Dhan Index Options - Blended Dataset Builder

Combines synthetic and real training data.
AUTO-UPDATE: DISABLED - Only builds preview, never auto-trains.
"""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
SYNTHETIC_CSV = TRAINING_DIR / "dhan_index_options_training.csv"
REAL_CSV = TRAINING_DIR / "dhan_real_training_candidates.csv"
BLENDED_PREVIEW_CSV = TRAINING_DIR / "dhan_blended_training_preview.csv"


def build_blended_dataset(
    synthetic_weight: float = 0.5,
    real_weight: float = 0.5,
    downsample_real: bool = False,
) -> pd.DataFrame:
    """
    Build blended dataset from synthetic and real data.

    Args:
        synthetic_weight: Weight for synthetic data (0.0 to 1.0)
        real_weight: Weight for real data (0.0 to 1.0)
        downsample_real: If True, downsample real data to match synthetic size

    Returns:
        Blended DataFrame
    """
    # Load synthetic
    df_synthetic = pd.DataFrame()
    if SYNTHETIC_CSV.exists():
        try:
            df_synthetic = pd.read_csv(SYNTHETIC_CSV)
            print(f"[BLENDED] Loaded {len(df_synthetic)} synthetic rows")
        except Exception as e:
            print(f"[BLENDED] Failed to load synthetic: {e}")

    # Load real
    df_real = pd.DataFrame()
    if REAL_CSV.exists():
        try:
            df_real = pd.read_csv(REAL_CSV)
            print(f"[BLENDED] Loaded {len(df_real)} real rows")
        except Exception as e:
            print(f"[BLENDED] Failed to load real: {e}")

    if df_synthetic.empty and df_real.empty:
        print("[BLENDED] No data available")
        return pd.DataFrame()

    # Normalize weights
    total_weight = synthetic_weight + real_weight
    if total_weight == 0:
        synthetic_weight = 0.5
        real_weight = 0.5
        total_weight = 1.0

    synthetic_weight /= total_weight
    real_weight /= total_weight

    # Sample based on weights
    blended_rows = []

    if not df_synthetic.empty:
        n_synthetic = int(len(df_synthetic) * synthetic_weight)
        df_syn_sample = df_synthetic.sample(min(n_synthetic, len(df_synthetic)), random_state=42)
        blended_rows.append(df_syn_sample)
        print(f"[BLENDED] Selected {len(df_syn_sample)} synthetic rows")

    if not df_real.empty:
        n_real = int(len(df_real) * real_weight)
        if downsample_real and len(df_real) > n_real:
            df_real_sample = df_real.sample(n_real, random_state=42)
        else:
            df_real_sample = df_real.head(n_real)
        blended_rows.append(df_real_sample)
        print(f"[BLENDED] Selected {len(df_real_sample)} real rows")

    if not blended_rows:
        return pd.DataFrame()

    # Combine
    df_blended = pd.concat(blended_rows, ignore_index=True)

    # Align columns (fill missing with 0)
    if not df_synthetic.empty and not df_real.empty:
        all_cols = set(df_synthetic.columns) | set(df_real.columns)
        for col in all_cols:
            if col not in df_blended.columns:
                df_blended[col] = 0.0

    print(f"[BLENDED] Final blended dataset: {len(df_blended)} rows")

    return df_blended


def save_blended_preview(df: pd.DataFrame) -> Path:
    """
    Save blended preview to CSV.

    Returns:
        Path to saved CSV
    """
    if df.empty:
        return BLENDED_PREVIEW_CSV

    df.to_csv(BLENDED_PREVIEW_CSV, index=False)
    return BLENDED_PREVIEW_CSV


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - BLENDED DATASET BUILDER ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Preview only\n")

    df_blended = build_blended_dataset(synthetic_weight=0.4, real_weight=0.6)

    if df_blended.empty:
        print("[INFO] Blended dataset is empty.")
        return

    # Show summary
    print("\n=== BLENDED DATASET SUMMARY ===")
    print(f"Total rows: {len(df_blended)}")

    if "label" in df_blended.columns:
        print("\nLabel distribution:")
        label_counts = df_blended["label"].value_counts()
        for label, count in label_counts.items():
            print(f"  {label}: {count}")

    # Save
    save_path = save_blended_preview(df_blended)
    print(f"\n[SAVE] Blended preview saved to: {save_path}")
    print("\n[NOTE] This is a PREVIEW. Manual review required before training.")


if __name__ == "__main__":
    main()
