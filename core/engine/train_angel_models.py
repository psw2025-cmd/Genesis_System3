import os
import sys
import json
from datetime import datetime

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

from core.engine.angel_multi_resolution_labels import generate_labels

# ---------------- Path & logger setup ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger  # existing logger


TRAIN_CSV = os.path.join(
    ROOT_DIR,
    "storage",
    "training",
    "angel_index_options_training.csv",
)
# NOTE: models live under core/models/angel_one
MODELS_DIR = os.path.join(ROOT_DIR, "core", "models", "angel_one")
FEATURE_IMPORTANCE_DIR = os.path.join(ROOT_DIR, "storage", "training")


def _load_top_features_map(root: str) -> dict[str, list[str]]:
    """
    Optional: read feature_importance_<UNDERLYING>.csv files (if present)
    and return a mapping {underlying: [top_feature1, top_feature2, ...]}.
    If files are missing, return {} and training will use all features.
    """
    top_features: dict[str, list[str]] = {}

    # Same underlyings as training loop
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

    for u in underlyings:
        path = os.path.join(root, f"feature_importance_{u}.csv")
        if not os.path.exists(path):
            continue

        try:
            df_mi = pd.read_csv(path)
        except Exception as e:
            print(f"[WARN] Failed to read MI file for {u}: {e}")
            continue

        if "feature" not in df_mi.columns or "mi_score" not in df_mi.columns:
            print(f"[WARN] MI file for {u} missing required columns; skipping.")
            continue

        if df_mi.empty:
            print(f"[WARN] MI file for {u} is empty; skipping.")
            continue

        # Take top N features by MI score
        df_mi_sorted = df_mi.sort_values("mi_score", ascending=False)
        top_n = df_mi_sorted.head(20)
        features_list = [str(f) for f in top_n["feature"].tolist() if isinstance(f, str) and f]

        if not features_list:
            continue

        top_features[u] = features_list

    if not top_features:
        print("[INFO] No MI feature selection files found; training will use all features.")

    return top_features


def _load_training_data() -> pd.DataFrame | None:
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

    # Enrich with multi-resolution forward labels (non-breaking; adds extra cols)
    df = generate_labels(df)

    # Prefer new 3-class label; fall back to older 'label' if needed
    label_col = None
    if "label_3class" in df.columns:
        label_col = "label_3class"
    elif "label" in df.columns:
        label_col = "label"
    else:
        print("[ERROR] No label column found (expected 'label_3class' or 'label').")
        return None

    required = [
        "underlying",
        "side",
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
        label_col,
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[WARN] Training CSV missing some feature columns: {missing}")
        # We still proceed, but will only use available subset
        required = [c for c in required if c in df.columns]

    # Filter to labels we know - accept both old format (BUY/SELL/HOLD) and new format (BUY_CE/BUY_PE/HOLD)
    valid_labels = ["BUY", "SELL", "HOLD", "BUY_CE", "BUY_PE", "SELL_CE", "SELL_PE"]
    df = df[df[label_col].isin(valid_labels)]

    if df.empty:
        print("[ERROR] No usable label rows (all labels might be NaN or unknown).")
        return None

    df["label_used"] = df[label_col]
    return df


def _prepare_features_labels(
    df: pd.DataFrame,
    selected_features: list[str] | None = None,
) -> tuple[pd.DataFrame | None, pd.Series | None, list[str] | None]:
    """
    Map categorical to numeric and return X, y, feature_names.
    """
    df = df.copy()

    # Encode side: CE=1, PE=0
    df["side_enc"] = df["side"].map({"CE": 1, "PE": 0}).fillna(0).astype(int)

    # Base feature set (subset of all engineered features; can be expanded later)
    base_feature_cols = [
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

    base_feature_cols = [c for c in base_feature_cols if c in df.columns]

    if selected_features:
        # Use only MI-selected features that also exist in df
        feature_cols = [c for c in selected_features if c in df.columns]
        if not feature_cols:
            # Fallback: if MI list doesn't intersect with df, revert to base
            feature_cols = base_feature_cols
    else:
        feature_cols = base_feature_cols

    if not feature_cols:
        print("[ERROR] No feature columns available for training.")
        return None, None, None

    # Drop rows with missing feature values
    df_feat = df.dropna(subset=feature_cols + ["label_used"])

    if df_feat.empty:
        print("[ERROR] After dropping NaNs, no rows left for training.")
        return None, None, None

    X = df_feat[feature_cols].values
    y = df_feat["label_used"].values

    return X, y, feature_cols


def _train_model_for_underlying(
    df: pd.DataFrame, underlying: str, top_features_map: dict[str, list[str]] | None = None
):
    """
    Train a model only for a single index (e.g. NIFTY, BANKNIFTY).
    """
    df_u = df[df["underlying"] == underlying].copy()
    if df_u.empty:
        print(f"[WARN] No data for underlying {underlying}, skipping.")
        return None

    selected = None
    if top_features_map:
        selected = top_features_map.get(underlying)

    X, y, feature_cols = _prepare_features_labels(df_u, selected_features=selected)
    if X is None:
        print(f"[WARN] Not enough data for {underlying} after preprocessing.")
        return None

    # Logging for feature selection
    total_numeric = len(feature_cols)
    if selected is not None and selected:
        used = len(feature_cols)
        print(f"[TRAIN] {underlying}: using {used} features (MI-selected) out of {total_numeric}.")
    else:
        print(f"[INFO] No MI feature selection for {underlying}, using all features ({total_numeric}).")

    # Check if we have at least 2 classes
    unique_labels = sorted(pd.unique(y))
    if len(unique_labels) < 2:
        print(f"[WARN] Underlying {underlying} has only one label class {unique_labels}; skipping.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"\n[TRAIN] {underlying}: samples={len(y_train)}, test={len(y_test)}, classes={sorted(pd.unique(y_train))}")

    # Simple, robust classifier
    clf = GradientBoostingClassifier(random_state=42)
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[RESULT] {underlying} accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    # Save model + metadata
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, f"{underlying}_model.pkl")
    meta_path = os.path.join(MODELS_DIR, f"{underlying}_model_meta.json")

    joblib.dump(clf, model_path)

    meta = {
        "underlying": underlying,
        "created_at": datetime.utcnow().isoformat(),
        "features": feature_cols,
        "classes": sorted([str(c) for c in pd.unique(y)]),
        "train_samples": int(len(y_train)),
        "test_samples": int(len(y_test)),
        "test_accuracy": float(acc),
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[SAVE] Model saved: {model_path}")
    print(f"[SAVE] Meta saved:  {meta_path}")
    logger.info(f"Trained {underlying} model saved to {model_path}")

    return acc


def main():
    logger.info("=== Train Angel One index options models (v2) ===")
    print(f"Reading training data from: {TRAIN_CSV}")

    df = _load_training_data()
    if df is None:
        logger.error("Training data load failed; aborting.")
        return

    print(f"Total training rows: {len(df)}")

    # Target underlyings
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

    # Optional MI-based feature selection
    top_features_map = _load_top_features_map(FEATURE_IMPORTANCE_DIR)

    results = {}
    for u in underlyings:
        acc = _train_model_for_underlying(df, u, top_features_map=top_features_map)
        if acc is not None:
            results[u] = acc

    if not results:
        print("[WARN] No models were trained (insufficient data or single-class issues).")
        return

    print("\n=== SUMMARY: MODEL ACCURACY ===")
    for u, acc in results.items():
        print(f"{u}: {acc:.4f}")

    logger.info(f"Training completed for underlyings: {list(results.keys())}")


if __name__ == "__main__":
    main()
