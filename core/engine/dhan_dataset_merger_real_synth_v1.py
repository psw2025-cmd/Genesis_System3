"""
Dhan Index Options - Dataset Merger Real + Synthetic V1

Merges real + synthetic data for blended training.
Does NOT train - merging only.
SAFE MODE ONLY - Read-only merge, no training.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
SYNTHETIC_CSV = TRAINING_DIR / "dhan_index_options_training.csv"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_SIGNALS_RAW_CSV = LEARNING_DIR / "real_signals_raw.csv"
MERGED_CSV = TRAINING_DIR / "merged_real_synth_dataset.csv"

TRAINING_DIR.mkdir(parents=True, exist_ok=True)
LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def merge_datasets(
    synthetic_weight: float = 0.5,
    real_weight: float = 0.5,
    downsample_real: bool = False,
) -> Dict[str, Any]:
    """
    Merge real + synthetic datasets.

    Does NOT train - merging only.

    Args:
        synthetic_weight: Weight for synthetic data (0.0 to 1.0)
        real_weight: Weight for real data (0.0 to 1.0)
        downsample_real: If True, downsample real data

    Returns:
        Dict with merge results
    """
    print("=== ANGEL ONE INDEX OPTIONS - DATASET MERGER REAL + SYNTHETIC V1 ===")
    print("[INFO] SAFE MODE - Merging only, NO training\n")

    # Load synthetic
    df_synthetic = pd.DataFrame()
    if SYNTHETIC_CSV.exists():
        try:
            df_synthetic = pd.read_csv(SYNTHETIC_CSV)
            print(f"[MERGE] Loaded {len(df_synthetic)} synthetic rows")
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to load synthetic: {e}",
            }
    else:
        return {
            "status": "NO_SYNTHETIC",
            "message": "Synthetic training CSV not found",
        }

    # Load real
    df_real = pd.DataFrame()
    if REAL_SIGNALS_RAW_CSV.exists():
        try:
            df_real = pd.read_csv(REAL_SIGNALS_RAW_CSV)
            print(f"[MERGE] Loaded {len(df_real)} real rows")
        except Exception as e:
            print(f"[WARN] Failed to load real data: {e}")
            df_real = pd.DataFrame()

    if df_synthetic.empty and df_real.empty:
        return {
            "status": "NO_DATA",
            "message": "No data available for merging",
        }

    # Normalize weights
    total_weight = synthetic_weight + real_weight
    if total_weight == 0:
        synthetic_weight = 0.5
        real_weight = 0.5
        total_weight = 1.0

    synthetic_weight /= total_weight
    real_weight /= total_weight

    # Sample based on weights
    merged_rows = []

    if not df_synthetic.empty:
        n_synthetic = int(len(df_synthetic) * synthetic_weight)
        df_syn_sample = df_synthetic.sample(min(n_synthetic, len(df_synthetic)), random_state=42)
        merged_rows.append(df_syn_sample)
        print(f"[MERGE] Selected {len(df_syn_sample)} synthetic rows")

    if not df_real.empty:
        n_real = int(len(df_real) * real_weight)
        if downsample_real and len(df_real) > n_real:
            df_real_sample = df_real.sample(n_real, random_state=42)
        else:
            df_real_sample = df_real.head(n_real)
        merged_rows.append(df_real_sample)
        print(f"[MERGE] Selected {len(df_real_sample)} real rows")

    if not merged_rows:
        return {
            "status": "EMPTY",
            "message": "No rows to merge",
        }

    # Combine
    df_merged = pd.concat(merged_rows, ignore_index=True)

    # Align columns (fill missing with 0)
    if not df_synthetic.empty and not df_real.empty:
        all_cols = set(df_synthetic.columns) | set(df_real.columns)
        for col in all_cols:
            if col not in df_merged.columns:
                df_merged[col] = 0.0

    print(f"[MERGE] Final merged dataset: {len(df_merged)} rows")

    # Save merged dataset
    try:
        df_merged.to_csv(MERGED_CSV, index=False)
        print(f"[SAVE] Merged dataset saved to: {MERGED_CSV}")
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to save merged dataset: {e}",
        }

    return {
        "status": "SUCCESS",
        "synthetic_rows": len(df_syn_sample) if not df_synthetic.empty else 0,
        "real_rows": len(df_real_sample) if not df_real.empty else 0,
        "total_rows": len(df_merged),
        "file_path": str(MERGED_CSV),
        "note": "MERGED ONLY - NO TRAINING PERFORMED",
    }


def get_merged_dataset_info() -> Dict[str, Any]:
    """
    Get merged dataset information (read-only).

    Returns:
        Dict with dataset info
    """
    if not MERGED_CSV.exists():
        return {
            "status": "NOT_FOUND",
            "message": "Merged dataset not found",
        }

    try:
        df = pd.read_csv(MERGED_CSV)
        info = {
            "status": "SUCCESS",
            "total_rows": len(df),
        }

        if "underlying" in df.columns:
            info["by_underlying"] = df["underlying"].value_counts().to_dict()

        if "label" in df.columns:
            info["by_label"] = df["label"].value_counts().to_dict()

        return info

    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    result = merge_datasets(synthetic_weight=0.4, real_weight=0.6)

    if result["status"] == "SUCCESS":
        print(f"\n=== MERGE SUMMARY ===")
        print(f"Synthetic Rows: {result['synthetic_rows']}")
        print(f"Real Rows: {result['real_rows']}")
        print(f"Total Rows: {result['total_rows']}")
        print(f"File: {result['file_path']}")
        print(f"\n⚠️  {result['note']}")

        # Show info
        info = get_merged_dataset_info()
        if info["status"] == "SUCCESS":
            print(f"\n=== DATASET INFO ===")
            if "by_underlying" in info:
                print("By Underlying:")
                for u, count in info["by_underlying"].items():
                    print(f"  {u}: {count}")
            if "by_label" in info:
                print("\nBy Label:")
                for label, count in info["by_label"].items():
                    print(f"  {label}: {count}")
    else:
        print(f"[INFO] {result.get('message', 'Merge not available')}")


if __name__ == "__main__":
    main()
