"""
dhan_feature_importance.py

Compute mutual-information based feature importance for Dhan index options
training data, per underlying.
"""

import os
import sys
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif


# ---------------------------------------------------------------------------
# Path setup (same pattern as other engine scripts)
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


TRAIN_CSV = os.path.join(ROOT_DIR, "storage", "training", "dhan_index_options_training.csv")
OUTPUT_DIR = os.path.join(ROOT_DIR, "storage", "training")

TARGET_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def _load_training_data() -> pd.DataFrame | None:
    """Load the training CSV and perform basic validation."""
    if not os.path.exists(TRAIN_CSV):
        print(f"[ERROR] Training CSV not found: {TRAIN_CSV}")
        return None

    try:
        df = pd.read_csv(TRAIN_CSV)
    except Exception as e:
        print(f"[ERROR] Failed to read training CSV: {e}")
        return None

    if df.empty:
        print("[ERROR] Training CSV is empty.")
        return None

    if "underlying" not in df.columns:
        print("[ERROR] 'underlying' column not found in training CSV.")
        return None

    # Prefer new 3-class label if present, fall back to older 'label'
    label_col = None
    if "label_3class" in df.columns:
        label_col = "label_3class"
    elif "label" in df.columns:
        label_col = "label"
    else:
        print("[ERROR] No label column found (expected 'label_3class' or 'label').")
        return None

    # Drop rows with missing label
    df = df.dropna(subset=[label_col])

    if df.empty:
        print("[ERROR] No rows with non-null labels after filtering.")
        return None

    df["__label_used__"] = df[label_col]
    return df


def _compute_mi_for_underlying(df: pd.DataFrame, underlying: str) -> Dict[str, Any] | None:
    """
    Compute mutual information between numeric features and label for a given underlying.

    Returns a dict containing:
        - 'underlying'
        - 'mi_df': full MI DataFrame (feature, mi_score)
        - 'top_feature'
        - 'top_mi_score'
    """
    df_u = df[df["underlying"] == underlying].copy()

    if df_u.empty:
        print(f"[WARN] No rows found for underlying {underlying}; skipping.")
        return None

    # Work with a label Series aligned to df_u's index
    label_series = df_u["__label_used__"].astype(str)

    # Select numeric feature columns; drop non-feature columns explicitly
    numeric_df = df_u.select_dtypes(include=[np.number])

    # Explicitly drop known non-features if they survived numeric filter
    non_feature_cols = {"underlying", "label", "label_3class"}
    numeric_df = numeric_df[[c for c in numeric_df.columns if c not in non_feature_cols]]

    if numeric_df.empty:
        print(f"[WARN] No numeric feature columns available for {underlying}; skipping.")
        return None

    # Drop rows with NaNs in features
    numeric_df = numeric_df.dropna(axis=0, how="any")
    if numeric_df.empty:
        print(f"[WARN] After dropping NaNs, no rows left for {underlying}; skipping.")
        return None

    # Align labels with filtered feature rows, then encode
    label_aligned = label_series.loc[numeric_df.index]
    y_encoded, _ = pd.factorize(label_aligned)

    X = numeric_df.to_numpy()

    # Compute MI per feature
    mi_scores = mutual_info_classif(
        X,
        y_encoded,
        discrete_features=False,
        random_state=42,
    )

    mi_df = pd.DataFrame(
        {
            "feature": numeric_df.columns,
            "mi_score": mi_scores,
        }
    ).sort_values("mi_score", ascending=False)

    mi_df.reset_index(drop=True, inplace=True)

    if mi_df.empty:
        print(f"[WARN] MI computation yielded no results for {underlying}; skipping.")
        return None

    # Print top-15 to console
    print(f"\n--- {underlying}: TOP FEATURES BY MI ---")
    top_k = mi_df.head(15)
    print(top_k.to_string(index=False))

    # Save full table
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"feature_importance_{underlying}.csv")
    mi_df.to_csv(out_path, index=False)
    print(f"[SAVE] Full MI table saved to: {out_path}")

    # Top feature summary
    top_feature = str(mi_df.iloc[0]["feature"])
    top_mi_score = float(mi_df.iloc[0]["mi_score"])

    return {
        "underlying": underlying,
        "mi_df": mi_df,
        "top_feature": top_feature,
        "top_mi_score": top_mi_score,
    }


def main():
    print("=== Dhan Index Options Feature Importance (MI) ===")
    print(f"Reading training data from: {TRAIN_CSV}")

    df = _load_training_data()
    if df is None:
        print("[ERROR] Could not load training data; aborting.")
        return

    summaries: List[Dict[str, Any]] = []

    for underlying in TARGET_UNDERLYINGS:
        result = _compute_mi_for_underlying(df, underlying)
        if result is not None:
            summaries.append(
                {
                    "underlying": result["underlying"],
                    "top_feature": result["top_feature"],
                    "top_mi_score": result["top_mi_score"],
                }
            )

    if not summaries:
        print("[WARN] No feature importance results generated for any underlying.")
        return

    summary_df = pd.DataFrame(summaries)

    summary_path = os.path.join(OUTPUT_DIR, "feature_importance_summary.csv")
    summary_df.to_csv(summary_path, index=False)

    print("\n=== FEATURE IMPORTANCE SUMMARY (top feature per underlying) ===")
    print(summary_df.to_string(index=False))
    print(f"\n[SAVE] Summary table saved to: {summary_path}")


if __name__ == "__main__":
    main()
