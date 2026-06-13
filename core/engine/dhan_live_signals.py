import os
import sys
import json
from datetime import datetime

import numpy as np
import pandas as pd
import joblib

# ---------------- Path setup ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger

LIVE_CSV = os.path.join(ROOT_DIR, "storage", "live", "dhan_index_options_watch.csv")
MODELS_DIR = os.path.join(ROOT_DIR, "core", "models", "dhan")

TARGET_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

# Feature list must match what we trained on (see train_dhan_models.py)
FEATURE_COLS = [
    "side_enc",
    "spot",
    "strike",
    "ltp",
    "moneyness",
    "atm_dist_abs",
    "atm_dist_pct",
    "ltp_chg_1_pct",
    "spot_chg_1_pct",
    "ltp_roll_std_5",
    "spot_roll_std_5",
    "ce_pe_diff",
    "ce_pe_ratio",
]


def _load_models():
    """Load models and their metadata (including feature lists)."""
    models = {}
    model_features = {}  # Store feature list for each model
    if not os.path.exists(MODELS_DIR):
        print(f"[WARN] Models directory not found: {MODELS_DIR}")
        return models, model_features

    for u in TARGET_UNDERLYINGS:
        model_path = os.path.join(MODELS_DIR, f"{u}_model.pkl")
        meta_path = os.path.join(MODELS_DIR, f"{u}_model_meta.json")
        if os.path.exists(model_path):
            try:
                models[u] = joblib.load(model_path)
                # Load metadata to get the exact feature list used during training
                if os.path.exists(meta_path):
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                        model_features[u] = meta.get("features", FEATURE_COLS)
                else:
                    # Fallback to default if no metadata
                    model_features[u] = FEATURE_COLS
            except Exception as e:
                print(f"[WARN] Failed to load model for {u}: {e}")
        else:
            print(f"[INFO] No model file yet for {u}: {model_path}")

    return models, model_features


def _load_latest_snapshot():
    """
    Read LIVE CSV and extract the last timestamp snapshot for each (underlying, strike, side).
    Then compute the same basic features we used for training.
    """
    if not os.path.exists(LIVE_CSV):
        print(f"[ERROR] Live CSV not found: {LIVE_CSV}")
        return None

    df = pd.read_csv(LIVE_CSV)
    if df.empty:
        print("[ERROR] Live CSV is empty.")
        return None

    required = ["underlying", "symbol", "side", "expiry", "ts", "spot", "strike", "ltp"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] Live CSV missing columns: {missing}")
        return None

    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df["spot"] = pd.to_numeric(df["spot"], errors="coerce")
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce")

    df = df.dropna(subset=["ts", "spot", "strike", "ltp"])
    if df.empty:
        print("[ERROR] Live CSV has no usable rows after cleaning.")
        return None

    # Sort & keep last snapshot per (underlying, strike, side)
    df = df.sort_values(["underlying", "strike", "side", "ts"])
    df_last = df.groupby(["underlying", "strike", "side"]).tail(1).copy()

    # Compute minimal features needed for prediction
    df_last["moneyness"] = (df_last["spot"] - df_last["strike"]) / df_last["spot"].replace(0, np.nan)
    df_last["atm_dist_abs"] = (df_last["spot"] - df_last["strike"]).abs()
    df_last["atm_dist_pct"] = df_last["atm_dist_abs"] / df_last["spot"].replace(0, np.nan)

    # Encode side: CE=1, PE=0
    df_last["side_enc"] = df_last["side"].map({"CE": 1, "PE": 0}).fillna(0).astype(int)

    # To estimate ltp/spot momentum, re-join some prior rows (very simple)
    g = df.sort_values("ts").groupby(["underlying", "symbol", "side"])
    df["ltp_prev"] = g["ltp"].shift(1)
    df["ltp_chg_1_pct"] = (df["ltp"] - df["ltp_prev"]) / df["ltp_prev"].replace(0, np.nan)

    u = df.groupby("underlying").apply(
        lambda x: x.sort_values("ts").assign(
            spot_prev=x["spot"].shift(1),
            spot_chg_1_pct=(x["spot"] - x["spot"].shift(1)) / x["spot"].shift(1).replace(0, np.nan),
        )
    )
    u = u.reset_index(drop=True)

    # Merge the change columns into latest snapshot
    merge_cols = ["underlying", "symbol", "side", "ts"]
    cols_to_merge = ["ltp_chg_1_pct", "spot_chg_1_pct"]
    df_latest = df_last.merge(
        u[merge_cols + cols_to_merge],
        on=merge_cols,
        how="left",
        suffixes=("", "_y"),
    )
    for c in cols_to_merge:
        if f"{c}_y" in df_latest.columns:
            df_latest[c] = df_latest[c].fillna(df_latest[f"{c}_y"])
            df_latest.drop(columns=[f"{c}_y"], inplace=True, errors="ignore")

    # For now, approximate rolling std with zeros if not available
    df_latest["ltp_roll_std_5"] = 0.0
    df_latest["spot_roll_std_5"] = 0.0

    # CE/PE pair diff/ratio
    pivot_cols = ["underlying", "expiry", "strike", "ts", "spot"]
    wide = df.pivot_table(index=pivot_cols, columns="side", values="ltp", aggfunc="last").reset_index()
    for side in ["CE", "PE"]:
        if side not in wide.columns:
            wide[side] = np.nan

    wide["ce_pe_diff"] = wide["CE"] - wide["PE"]
    wide["ce_pe_ratio"] = wide["CE"] / wide["PE"].replace(0, np.nan)

    df_latest = df_latest.merge(
        wide[pivot_cols + ["ce_pe_diff", "ce_pe_ratio"]],
        on=pivot_cols,
        how="left",
    )

    return df_latest


def _build_feature_matrix(df_latest: pd.DataFrame, feature_cols: list):
    """
    Build X and return (X, df_used) where df_used keeps meta columns.
    Uses the exact feature list provided (from model metadata).
    """
    df = df_latest.copy()

    # Keep meta
    meta_cols = ["underlying", "symbol", "side", "expiry", "ts", "spot", "strike", "ltp"]
    for c in meta_cols:
        if c not in df.columns:
            df[c] = np.nan

    # Ensure all required features exist
    for c in feature_cols:
        if c not in df.columns:
            df[c] = 0.0

    # Drop rows with any NaN in feature columns
    df = df.dropna(subset=feature_cols)
    if df.empty:
        print("[ERROR] No rows left after feature NaN filtering.")
        return None, None

    X = df[feature_cols].values
    return X, df


def main():
    logger.info("=== Dhan index options LIVE AI signals ===")

    models, model_features = _load_models()
    if not models:
        print("[ERROR] No trained models found yet. Run menu options 7 ? 9 ? 10 during market hours first.")
        return

    df_latest = _load_latest_snapshot()
    if df_latest is None or df_latest.empty:
        logger.error("Failed to load latest snapshot.")
        return

    print("\n=== AI SIGNALS (per underlying, sorted by confidence) ===\n")
    signals = []

    for u in TARGET_UNDERLYINGS:
        if u not in models:
            continue

        m = models[u]
        # Get the exact feature list used during training for this model
        feature_cols = model_features.get(u, FEATURE_COLS)

        df_u = df_latest[df_latest["underlying"] == u].copy()
        if df_u.empty:
            continue

        # Build feature matrix using the exact features this model was trained with
        X_u, df_used_u = _build_feature_matrix(df_u, feature_cols)
        if X_u is None:
            print(f"[WARN] Failed to build features for {u}, skipping.")
            continue

        # Predict classes and probabilities
        preds = m.predict(X_u)
        if hasattr(m, "predict_proba"):
            proba = m.predict_proba(X_u)
            classes = list(m.classes_)
        else:
            # Fallback: no probabilities
            proba = None
            classes = None

        for i in range(len(df_used_u)):
            row = df_used_u.iloc[i]
            label = preds[i]

            conf = None
            if proba is not None and classes is not None:
                # confidence for predicted class
                pred_idx = classes.index(label)
                conf = float(proba[i, pred_idx])

            signals.append(
                {
                    "underlying": u,
                    "symbol": row["symbol"],
                    "side": row["side"],
                    "expiry": row["expiry"],
                    "strike": float(row["strike"]),
                    "ltp": float(row["ltp"]),
                    "spot": float(row["spot"]),
                    "label": label,
                    "confidence": conf,
                }
            )

    if not signals:
        print("[WARN] No signals generated (no matching models/data).")
        return

    sig_df = pd.DataFrame(signals)

    # Sort: BUY first, then SELL, then HOLD; within each by confidence desc
    label_priority = {"BUY": 0, "SELL": 1, "HOLD": 2}
    sig_df["prio"] = sig_df["label"].map(label_priority).fillna(3).astype(int)
    sig_df["conf_sort"] = sig_df["confidence"].fillna(0.0)

    sig_df = sig_df.sort_values(["prio", "underlying", "conf_sort"], ascending=[True, True, False])

    # Show top 2 signals per underlying
    rows_to_show = []
    for u in TARGET_UNDERLYINGS:
        sub = sig_df[sig_df["underlying"] == u].head(2)
        if not sub.empty:
            rows_to_show.append(sub)

    if not rows_to_show:
        print("[WARN] No top signals for target underlyings.")
        return

    out = pd.concat(rows_to_show)

    display_cols = ["underlying", "symbol", "side", "expiry", "strike", "ltp", "spot", "label", "confidence"]
    print(out[display_cols].to_string(index=False))

    logger.info("Live AI signals generated and displayed.")


if __name__ == "__main__":
    main()
