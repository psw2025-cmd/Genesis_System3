# ================================================
# GENESIS SYSTEM 3
# Offline test of Dhan index options models
#
# Uses:
#   - storage/training/dhan_index_options_training.csv
#   - core/models/dhan/*_rf.pkl
#
# Prints sample predictions per index (NIFTY, BANKNIFTY, etc.)
# ================================================

import os
import numpy as np
import pandas as pd
import joblib

# Label mapping used during training
LABEL_MAP = {
    "HOLD": 0,
    "BUY_CE": 1,
    "BUY_PE": 2,
}


def _project_root() -> str:
    """
    Infer project root from this file location.
    Expected layout: <root>/core/engine/offline_dhan_ai_test.py
    """
    here = os.path.abspath(__file__)
    core_dir = os.path.dirname(os.path.dirname(here))  # .../core
    root = os.path.dirname(core_dir)  # project root
    return root


def _training_csv_path(root: str) -> str:
    return os.path.join(root, "storage", "training", "dhan_index_options_training.csv")


def _models_dir(root: str) -> str:
    return os.path.join(root, "core", "models", "dhan")


def _int_to_label(y_int: int) -> str:
    for k, v in LABEL_MAP.items():
        if v == y_int:
            return k
    return f"UNKNOWN({y_int})"


def _ensure_basic_features(df: pd.DataFrame, feature_cols_from_model):
    """
    Make sure all feature columns that the model expects exist in df.
    If some are missing, create them with zeros.
    Also ensure side_enc exists if 'side' is present.
    """
    df = df.copy()

    # side_enc from 'side' if possible
    if "side" in df.columns and "side_enc" not in df.columns:
        df["side_enc"] = df["side"].map({"CE": 1, "PE": 0}).fillna(0).astype(int)

    # Ensure all model feature columns exist
    for col in feature_cols_from_model:
        if col not in df.columns:
            df[col] = 0.0

    # Return df and the final list of feature columns (keep exactly what model expects)
    feature_cols_final = [c for c in feature_cols_from_model if c in df.columns]
    return df, feature_cols_final


def main():
    root = _project_root()
    train_csv = _training_csv_path(root)
    models_dir = _models_dir(root)

    print("=== ANGEL ONE INDEX OPTIONS - OFFLINE AI TEST ===")
    print("Project root :", root)
    print("Training CSV :", train_csv)
    print("Models dir   :", models_dir)
    print()

    if not os.path.exists(train_csv):
        print("[ERROR] Training CSV not found. Run synthetic generator or real training-builder first.")
        return

    df = pd.read_csv(train_csv)
    if df.empty:
        print("[ERROR] Training CSV is empty.")
        return

    if "underlying" not in df.columns:
        print("[ERROR] 'underlying' column not found in training CSV.")
        return

    underlyings = sorted(df["underlying"].dropna().unique().tolist())
    print("Underlyings found in training CSV:", underlyings)
    print()

    for u in underlyings:
        model_path = os.path.join(models_dir, f"{u}_rf.pkl")
        if not os.path.exists(model_path):
            print(f"[WARN] Model file missing for {u}: {model_path}")
            continue

        print(f"--- {u}: loading model and sampling rows ---")
        bundle = joblib.load(model_path)
        model = bundle["model"]
        feature_cols_from_model = bundle["features"]

        df_u = df[df["underlying"] == u].copy()
        if df_u.empty:
            print(f"[WARN] No rows for {u} in training CSV; skipping.")
            continue

        # Ensure feature columns and side_enc exist
        df_u, feature_cols_final = _ensure_basic_features(df_u, feature_cols_from_model)

        if not feature_cols_final:
            print(f"[WARN] No usable feature columns found for {u}; skipping.")
            continue

        # Sample up to 10 rows from this underlying
        n_rows = min(10, len(df_u))
        df_sample = df_u.sample(n=n_rows, random_state=42).copy()

        X = df_sample[feature_cols_final].astype(float)
        y_true = df_sample.get("label", pd.Series([""] * len(df_sample))).astype(str)

        y_pred_int = model.predict(X)
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X)
        else:
            y_proba = None

        print(f"Sample predictions for {u} (n={n_rows}):")
        print("ts\t\tstrike\tside\tltp\tspot\ttrue\tpred\tconfidence")

        for idx, (i, row) in enumerate(df_sample.iterrows()):
            ts = row.get("timestamp", "")
            strike = row.get("strike", "")
            side = row.get("side", "")
            ltp = row.get("ltp", 0.0)
            spot = row.get("spot", 0.0)
            true_label = str(row.get("label", ""))

            pred_int = int(y_pred_int[idx])
            pred_label = _int_to_label(pred_int)

            if y_proba is not None:
                conf = float(np.max(y_proba[idx]))
            else:
                conf = 1.0

            try:
                ltp_f = float(ltp)
            except Exception:
                ltp_f = 0.0

            try:
                spot_f = float(spot)
            except Exception:
                spot_f = 0.0

            print(f"{ts}\t{strike}\t{side}\t{ltp_f:.2f}\t{spot_f:.2f}\t" f"{true_label}\t{pred_label}\t{conf:.3f}")
        print()

    print("[DONE] Offline AI test completed.")


if __name__ == "__main__":
    main()
