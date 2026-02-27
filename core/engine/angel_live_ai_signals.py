import os
import json
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import joblib

from core.utils.logger import logger
from core.engine import angel_trade_decision


# ---------------------------------------------------------------------------
# Project root / paths (same pattern as other engine scripts)
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]


def _project_root() -> Path:
    return ROOT_DIR


MODELS_DIR = _project_root() / "core" / "models" / "angel_one"
LIVE_DIR = _project_root() / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"


TARGET_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_models_and_meta(root: Path, profile: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Load one model + meta per underlying.

    Args:
        root: Project root path
        profile: Optional profile name ("BASELINE" or "LIVE_BETA").
                 If None, auto-detect from config. Default behavior unchanged.

    Return dict:
      {
        'NIFTY': {
            'model': fitted_model,
            'feature_cols': [...],
            'classes': [...],  # model.classes_
        },
        ...
      }
    """
    # Check if profile-based loading is requested
    use_profile = profile is not None or os.getenv("SYSTEM3_PROFILE") is not None
    if use_profile:
        try:
            from core.engine.angel_model_selector import load_models_for_profile, get_active_profile

            if profile is None:
                profile = get_active_profile()
            model_data = load_models_for_profile(profile)
            if model_data["models"]:
                # Convert to expected format
                models: Dict[str, Dict[str, Any]] = {}
                for underlying, model in model_data["models"].items():
                    meta_path = model_data["meta_paths"].get(underlying)
                    if meta_path and Path(meta_path).exists():
                        try:
                            with open(meta_path, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                            feature_cols = meta.get("features") or meta.get("feature_cols")
                            if not feature_cols:
                                feature_cols = getattr(model, "feature_names_in_", None)
                            if feature_cols:
                                models[underlying] = {
                                    "model": model,
                                    "feature_cols": list(feature_cols),
                                    "classes": list(getattr(model, "classes_", [])),
                                }
                        except Exception as e:
                            logger.warning(f"Failed to load meta for {underlying} from profile: {e}")
                if models:
                    logger.info(f"Loaded models using profile: {profile}")
                    return models
        except Exception as e:
            logger.warning(f"Profile-based model loading failed, falling back to baseline: {e}")

    # Default baseline behavior (unchanged)
    models: Dict[str, Dict[str, Any]] = {}

    models_dir = root / "core" / "models" / "angel_one"
    if not models_dir.exists():
        msg = f"Models directory not found: {models_dir}"
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return models

    for underlying in TARGET_UNDERLYINGS:
        model_path = models_dir / f"{underlying}_model.pkl"
        meta_path = models_dir / f"{underlying}_model_meta.json"

        if not model_path.exists() or not meta_path.exists():
            msg = (
                f"Missing model or meta for {underlying} "
                f"(model={model_path.exists()}, meta={meta_path.exists()}); skipping."
            )
            print(f"[WARN] {msg}")
            logger.warning(msg)
            continue

        try:
            model = joblib.load(model_path)
        except Exception as e:
            msg = f"Failed to load model for {underlying}: {e}"
            print(f"[WARN] {msg}")
            logger.warning(msg)
            continue

        try:
            with meta_path.open("r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            msg = f"Failed to read meta for {underlying}: {e}"
            print(f"[WARN] {msg}")
            logger.warning(msg)
            continue

        # Feature columns: training code stores this under "features"
        feature_cols = meta.get("features") or meta.get("feature_cols")
        if not feature_cols:
            # Fallback to model's own feature names if available
            feature_cols = getattr(model, "feature_names_in_", None)
            if feature_cols is None:
                msg = f"No feature list in meta/model for {underlying}; skipping."
                print(f"[WARN] {msg}")
                logger.warning(msg)
                continue

        feature_cols = list(feature_cols)

        # Use model.classes_ for label ordering
        classes = getattr(model, "classes_", None)
        if classes is None:
            msg = f"Model for {underlying} has no classes_; skipping."
            print(f"[WARN] {msg}")
            logger.warning(msg)
            continue

        models[underlying] = {
            "model": model,
            "feature_cols": feature_cols,
            "classes": list(classes),
        }

    if not models:
        msg = "No models loaded; check that training has been run."
        print(f"[ERROR] {msg}")
        logger.error(msg)

    return models


def _ensure_features_for_df(
    df: pd.DataFrame,
    feature_cols: list[str],
) -> pd.DataFrame:
    """
    Ensure df has all required feature columns used in training.

    - Compute side_enc from side if needed.
    - For any missing numeric feature, create column filled with 0.0.
    - Extra columns are kept but ignored when building X.
    """
    df = df.copy()

    # Encode side: CE=1, PE=0 (same as training)
    if "side" in df.columns and "side_enc" in feature_cols:
        df["side_enc"] = df["side"].map({"CE": 1, "PE": 0}).fillna(0).astype(int)

    for col in feature_cols:
        if col not in df.columns:
            # Default missing engineered features (e.g. moneyness, atm_dist_*) to 0.0
            df[col] = 0.0

    return df


def predict_for_snapshot_df(
    df_snap: pd.DataFrame,
    models: Dict[str, Dict[str, Any]],
) -> pd.DataFrame:
    """
    Input: df_snap with columns [ts, underlying, expiry, strike, side, ltp, spot, ...]
    Output: df_signals with added columns:
       - pred_label
       - pred_confidence
       - prob_BUY_CE
       - prob_BUY_PE
       - prob_HOLD
       - expected_move_score
    """
    if df_snap is None or df_snap.empty:
        return pd.DataFrame()

    all_rows: list[pd.DataFrame] = []

    for underlying, info in models.items():
        model = info["model"]
        feature_cols: list[str] = info["feature_cols"]

        df_u = df_snap[df_snap["underlying"] == underlying].copy()
        if df_u.empty:
            continue

        # Ensure all required features exist
        df_u = _ensure_features_for_df(df_u, feature_cols)

        # Build feature matrix in training order
        X = df_u[feature_cols].to_numpy(dtype=float)

        # Predict probabilities
        try:
            proba = model.predict_proba(X)
        except Exception as e:
            msg = f"predict_proba failed for {underlying}: {e}"
            print(f"[WARN] {msg}")
            logger.warning(msg)
            continue

        class_labels = list(getattr(model, "classes_", []))
        if not class_labels:
            msg = f"Model for {underlying} has no classes_; skipping."
            print(f"[WARN] {msg}")
            logger.warning(msg)
            continue

        # Map probabilities to labels
        max_idx = np.argmax(proba, axis=1)
        pred_labels = [class_labels[i] for i in max_idx]
        pred_conf = proba.max(axis=1)

        # Initialize per-class probability columns
        prob_buy_ce = np.zeros(len(df_u), dtype=float)
        prob_buy_pe = np.zeros(len(df_u), dtype=float)
        prob_hold = np.zeros(len(df_u), dtype=float)

        for class_index, label in enumerate(class_labels):
            if label == "BUY_CE":
                prob_buy_ce = proba[:, class_index]
            elif label == "BUY_PE":
                prob_buy_pe = proba[:, class_index]
            elif label == "HOLD":
                prob_hold = proba[:, class_index]

        expected_move_score = prob_buy_ce * 1.0 + prob_buy_pe * -1.0 + prob_hold * 0.0

        df_u["pred_label"] = pred_labels
        df_u["pred_confidence"] = pred_conf
        df_u["prob_BUY_CE"] = prob_buy_ce
        df_u["prob_BUY_PE"] = prob_buy_pe
        df_u["prob_HOLD"] = prob_hold
        df_u["expected_move_score"] = expected_move_score

        all_rows.append(df_u)

    if not all_rows:
        return pd.DataFrame()

    out = pd.concat(all_rows, ignore_index=True)
    # Sort by underlying then strike for readability
    sort_cols = [c for c in ["underlying", "strike"] if c in out.columns]
    if sort_cols:
        out = out.sort_values(sort_cols).reset_index(drop=True)

    return out


def append_signals_to_csv(df_signals: pd.DataFrame, csv_path: Path) -> None:
    """
    Append df_signals to csv_path, creating it with header if it does not exist.
    """
    if df_signals is None or df_signals.empty:
        msg = "No signals to append (empty DataFrame)."
        print(f"[INFO] {msg}")
        logger.info(msg)
        return

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not csv_path.exists()

    df_signals.to_csv(
        csv_path,
        mode="a",
        header=write_header,
        index=False,
        encoding="utf-8",
    )


def run_once_with_snapshot(df_snap: pd.DataFrame, use_new_engine: bool = True) -> pd.DataFrame:
    """
    Entry point for one snapshot DataFrame.
    Uses new System3 signal engine by default, falls back to original if needed.

    Args:
        df_snap: Snapshot DataFrame
        use_new_engine: Whether to use new System3 signal engine (default True)
    """
    # Try new signal engine first
    if use_new_engine:
        try:
            from core.engine.system3_signal_engine import run_signal_engine

            logger.info("Using System3 Signal Engine (enhanced)")
            df_signals = run_signal_engine(df_snap)

            if not df_signals.empty:
                # Verify non-zero scores
                zero_scores = (df_signals.get("final_score", pd.Series([0.0])).abs() < 0.001).sum()
                if zero_scores > 0:
                    logger.warning(f"Found {zero_scores} signals with near-zero scores")

                buy_count = len(df_signals[df_signals.get("signal", "") == "BUY"])
                sell_count = len(df_signals[df_signals.get("signal", "") == "SELL"])
                logger.info(f"Signals: BUY={buy_count}, SELL={sell_count}")

            return df_signals
        except Exception as e:
            logger.warning(f"New signal engine failed: {e}, falling back to original")
            use_new_engine = False

    # Fallback to original
    root = _project_root()
    models = load_models_and_meta(root)

    if not models:
        logger.error("No models available; aborting AI signals generation.")
        print("[ERROR] No models available; aborting AI signals generation.")
        return pd.DataFrame()

    df_signals = predict_for_snapshot_df(df_snap, models)
    if df_signals.empty:
        logger.warning("No signals generated for given snapshot.")
        print("[WARN] No signals generated for given snapshot.")
        return df_signals

    append_signals_to_csv(df_signals, SIGNALS_CSV)
    logger.info(
        "AI signals snapshot generated: rows=%d, saved_to=%s",
        len(df_signals),
        str(SIGNALS_CSV),
    )

    # Compact console summary
    print("\n=== AI SIGNALS SNAPSHOT ===")
    summary_cols = [
        "underlying",
        "strike",
        "side",
        "ltp",
        "spot",
        "pred_label",
        "pred_confidence",
        "expected_move_score",
    ]
    cols = [c for c in summary_cols if c in df_signals.columns]
    for _, row in df_signals[cols].iterrows():
        print(
            f"{row.get('underlying')} {row.get('strike')} {row.get('side')} "
            f"ltp={row.get('ltp')} spot={row.get('spot')} "
            f"signal={row.get('pred_label')} "
            f"conf={row.get('pred_confidence'):.3f} "
            f"score={row.get('expected_move_score'):.3f}"
        )

    # Build trade plan from this snapshot
    cfg = angel_trade_decision.TradeConfig()
    plan_df = angel_trade_decision.build_trade_plan(df_signals, cfg)
    angel_trade_decision.print_trade_summary(plan_df)
    angel_trade_decision.append_trade_plan(plan_df)
    logger.info(
        "AI trade plan built: rows=%d, saved_to=%s",
        0 if plan_df is None else len(plan_df),
        str(angel_trade_decision._trades_csv()),
    )

    # Auto-execute trades if enabled (DRY RUN only)
    if not plan_df.empty:
        from core.engine.angel_automation_config import AUTOMATION_CONFIG
        from core.engine.angel_trade_executor import execute_dry_run
        from core.engine.angel_trade_lifecycle_logger import get_lifecycle_logger, generate_trade_id

        # Log trade plan creation
        lifecycle_logger = get_lifecycle_logger()
        for _, trade in plan_df.iterrows():
            trade_id = generate_trade_id(
                trade.get("underlying", ""),
                trade.get("strike", 0),
                trade.get("side", ""),
                str(trade.get("ts", "")),
            )
            lifecycle_logger.log_event(
                "TRADE_PLANNED",
                trade_id=trade_id,
                underlying=trade.get("underlying"),
                strike=trade.get("strike"),
                side=trade.get("side"),
                details={"entry_price": trade.get("entry_price"), "confidence": trade.get("pred_confidence")},
            )

        if AUTOMATION_CONFIG.auto_execute_trades:
            try:
                logger.info("Auto-executing trades (DRY RUN mode)...")
                execute_dry_run()
            except Exception as e:
                logger.error(f"Auto-execution failed: {e}", exc_info=True)
                print(f"[WARN] Auto-execution failed: {e}")

    return df_signals


def main() -> None:
    root = _project_root()
    watch_csv = root / "storage" / "live" / "angel_index_options_watch.csv"
    if not watch_csv.exists():
        msg = f"No watch CSV found at {watch_csv}"
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return

    try:
        df = pd.read_csv(watch_csv, engine="python", on_bad_lines="skip")
    except Exception as e:
        msg = f"Failed to read watch CSV: {e}"
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return

    if df.empty:
        msg = "Watch CSV is empty."
        print(f"[ERROR] {msg}")
        logger.error(msg)
        return

    # Take last 30 rows as a simple "last snapshot" approximation
    df_last = df.tail(30).copy()
    logger.info("Running offline AI signals on last 30 rows from %s", str(watch_csv))
    run_once_with_snapshot(df_last)


if __name__ == "__main__":
    main()
