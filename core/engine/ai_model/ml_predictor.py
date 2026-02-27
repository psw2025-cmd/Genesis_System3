"""
ML Predictor - Train XGBoost/RandomForest for direction prediction

System3 AI upgrade - training data pipeline hardening:
- Robust CSV loader with fast+fallback parser
- Preference for curated training history over raw live CSV
- Diagnostics for data loading
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
import joblib
from datetime import datetime, timedelta
from collections import Counter
import logging

from core.utils.logger import logger

try:
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ---------------------------------------------------------------------------
# System3 training data configuration
# ---------------------------------------------------------------------------
CURATED_TRAINING_PATH = Path("storage") / "live" / "angel_index_ai_signals_curated.csv"
LIVE_TRAINING_PATH = Path("storage") / "live" / "angel_index_ai_signals.csv"

# Minimum number of rows required for a dataset to be considered usable
MIN_TRAINING_SAMPLES = 200


def _get_loader_logger() -> logging.Logger:
    """
    Small dedicated logger for training-data loading diagnostics.
    Writes into logs/model_diagnostics/system3_training_data_loader_YYYYMMDD.log
    """
    logs_dir = Path("logs") / "model_diagnostics"
    logs_dir.mkdir(parents=True, exist_ok=True)

    today_str = datetime.now().strftime("%Y%m%d")
    log_path = logs_dir / f"system3_training_data_loader_{today_str}.log"

    loader_logger = logging.getLogger("system3.training_data_loader")
    # Avoid adding multiple handlers if this is called more than once
    if not any(
        isinstance(h, logging.FileHandler) and getattr(h, "_system3_loader", False) for h in loader_logger.handlers
    ):
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh._system3_loader = True  # type: ignore[attr-defined]
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(fmt)
        loader_logger.addHandler(fh)
        loader_logger.setLevel(logging.INFO)

    return loader_logger


def load_training_data(path: Path, min_samples: int = MIN_TRAINING_SAMPLES) -> Optional[pd.DataFrame]:
    """
    Robust loader for training history CSV.

    Strategy:
      1) Try fast pandas C-engine.
      2) On tokenizing/parsing error, retry with engine='python', on_bad_lines='skip'.
      3) Enforce a minimum row count; otherwise return None.

    This must NEVER raise to callers; it should log and return None on failure.
    """
    loader_logger = _get_loader_logger()
    path = Path(path)

    if not path.exists():
        msg = f"Training data file not found: {path}"
        logger.warning(msg)
        loader_logger.warning(msg)
        return None

    # First attempt: fast parser
    try:
        df = pd.read_csv(path)
        rows = len(df)
        if rows < min_samples:
            msg = f"Training data from {path} has only {rows} rows " f"(min required {min_samples}); skipping training."
            logger.warning(msg)
            loader_logger.warning(msg)
            return None

        info = f"Loaded training data from {path} with {rows} rows using fast parser."
        logger.info(info)
        loader_logger.info(info)
        return df
    except Exception as e:
        msg = f"Fast CSV parser failed for {path}: {e}"
        logger.warning(msg)
        loader_logger.warning(msg)

    # Second attempt: robust parser, skipping bad lines
    try:
        df = pd.read_csv(path, engine="python", on_bad_lines="skip")
        rows = len(df)
        if rows < min_samples:
            msg = f"Robust parser loaded {rows} rows from {path} " f"(min required {min_samples}); skipping training."
            logger.warning(msg)
            loader_logger.warning(msg)
            return None

        info = (
            f"Loaded training data from {path} with {rows} rows using robust parser "
            f"(some malformed lines were skipped)."
        )
        logger.info(info)
        loader_logger.info(info)
        return df
    except Exception as e:
        msg = f"Robust CSV parser also failed for {path}: {e}. Training will be skipped."
        logger.warning(msg)
        loader_logger.warning(msg)
        return None


def get_training_dataframe(prefer_curated: bool = True) -> Optional[pd.DataFrame]:
    """
    Select an appropriate DataFrame for ML training.

    Priority:
      1) Curated training CSV, if present and valid.
      2) Raw live CSV, as a fallback.
    """
    # Prefer curated history if available
    if prefer_curated and CURATED_TRAINING_PATH.exists():
        df = load_training_data(CURATED_TRAINING_PATH)
        if df is not None:
            logger.info(
                "Training ML model from curated history: %s (rows=%d)",
                CURATED_TRAINING_PATH,
                len(df),
            )
            return df
        else:
            logger.warning("Curated training file unavailable or invalid, falling back to live CSV.")

    # Fallback to live training CSV
    if LIVE_TRAINING_PATH.exists():
        df = load_training_data(LIVE_TRAINING_PATH)
        if df is not None:
            logger.info(
                "Training ML model from live history: %s (rows=%d)",
                LIVE_TRAINING_PATH,
                len(df),
            )
            return df

    logger.warning(
        "No valid training data available (neither curated nor live). "
        "ML training will be skipped and delta-based ai_score will be used."
    )
    return None


def prepare_features_for_ml(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features for ML model training.

    Args:
        df: DataFrame with all signal features

    Returns:
        DataFrame with ML-ready features
    """
    if df.empty:
        return df

    df = df.copy()

    # Derived features that may not be present yet
    # Moneyness and time to expiry give strong structure to options behaviour
    if "spot" in df.columns and "strike" in df.columns:
        spot = pd.to_numeric(df["spot"], errors="coerce").fillna(0.0)
        strike = pd.to_numeric(df["strike"], errors="coerce").replace(0, np.nan)
        df["moneyness"] = ((spot - strike) / strike).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    else:
        df["moneyness"] = 0.0

    if "expiry" in df.columns:
        try:
            # Parse expiry as datetime
            try:
                expiry_dt = pd.to_datetime(df["expiry"], errors="coerce", format="%d%b%Y")
            except Exception:
                expiry_dt = pd.to_datetime(df["expiry"], errors="coerce")

            # Reference time: per-row ts where available, otherwise "now" per row
            if "ts" in df.columns:
                ref_time = pd.to_datetime(df["ts"], errors="coerce")
            else:
                ref_time = pd.Series(pd.Timestamp.utcnow(), index=df.index)

            # Ensure both are datetime-like Series before using .dt
            expiry_norm = expiry_dt.dt.normalize()
            ref_norm = ref_time.dt.normalize()

            days_to_expiry = (expiry_norm - ref_norm).dt.days
            df["time_to_expiry"] = (days_to_expiry.astype(float).divide(365.0)).clip(-0.01, 1.0).fillna(0.0)
        except Exception as e:
            logger.warning("Failed to compute time_to_expiry: %s", e)
            df["time_to_expiry"] = 0.0
    else:
        df["time_to_expiry"] = 0.0

    # Select feature columns (extended)
    feature_cols = [
        "delta",
        "gamma",
        "theta",
        "vega",
        "rsi",
        "macd",
        "macd_histogram",
        "iv_percentile",
        "iv_rank",
        "volatility_score",
        "breakout_score",
        "momentum_score",
        "trend_score",
        "multi_tf_trend_score",
        "moneyness",
        "time_to_expiry",
    ]

    # Fill missing features with 0
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0

    return df


def train_ml_model(
    df: pd.DataFrame, model_type: str = "xgboost", target_col: str = "direction", days_back: int = 30
) -> Optional[Any]:
    """
    Train ML model (XGBoost or RandomForest) on historical data.

    Args:
        df: DataFrame with features and target
        model_type: "xgboost" or "randomforest"
        target_col: Column name for target variable
        days_back: Number of days to use for training

    Returns:
        Trained model or None
    """
    if df.empty:
        return None

    # Limit to recent history (days_back) if timestamp available
    df = df.copy()
    if "ts" in df.columns:
        try:
            ts_parsed = pd.to_datetime(df["ts"], format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")
            cutoff = ts_parsed.max() - timedelta(days=days_back)
            df = df[ts_parsed >= cutoff]
        except Exception:
            pass

    if df.empty:
        return None

    # Prepare features
    df_features = prepare_features_for_ml(df)

    # Select feature columns (extended, aligned with prepare_features_for_ml)
    feature_cols = [
        "delta",
        "gamma",
        "theta",
        "vega",
        "rsi",
        "macd",
        "macd_histogram",
        "iv_percentile",
        "iv_rank",
        "volatility_score",
        "breakout_score",
        "momentum_score",
        "trend_score",
        "multi_tf_trend_score",
        "moneyness",
        "time_to_expiry",
    ]

    X = df_features[[col for col in feature_cols if col in df_features.columns]].fillna(0.0)

    # Prepare target
    if target_col not in df.columns:
        # Create target from price movement
        if "spot" in df.columns and len(df) > 2:
            price_change = pd.to_numeric(df["spot"], errors="coerce").fillna(0.0).pct_change().shift(-1)
            # Ignore tiny moves to reduce noise
            thresh = 0.0005
            y = pd.Series(0, index=df.index)
            y[price_change > thresh] = 1
            y[price_change < -thresh] = 0
            # Drop rows where move is tiny (no strong label)
            mask = price_change.abs() >= thresh
            X = X[mask]
            y = y[mask]
        else:
            return None
    else:
        y = df[target_col].fillna(0).astype(int)

    if len(X) < 50:
        # Not enough varied samples
        return None

    # Train model
    if model_type == "xgboost" and XGBOOST_AVAILABLE:
        model = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
    elif model_type == "randomforest" and SKLEARN_AVAILABLE:
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=6,
            class_weight="balanced",
            random_state=42,
        )
    else:
        # Fallback to simple model
        if SKLEARN_AVAILABLE:
            model = RandomForestClassifier(n_estimators=80, max_depth=4, class_weight="balanced", random_state=42)
        else:
            return None

    # System3 AI upgrade: diagnostics
    try:
        counts = Counter(y.tolist())
        logger.info("ML training class distribution: %s", counts)
    except Exception:
        pass

    # Train model
    try:
        model.fit(X, y)

        # Feature importances
        try:
            if hasattr(model, "feature_importances_"):
                fi = model.feature_importances_
                importance = sorted(
                    zip(X.columns.tolist(), fi),
                    key=lambda x: x[1],
                    reverse=True,
                )
                logger.info(
                    "Top feature importances: %s",
                    importance[:15],
                )
        except Exception:
            pass

        # Write diagnostics to file
        try:
            logs_dir = Path("logs") / "ml_diagnostics"
            logs_dir.mkdir(parents=True, exist_ok=True)
            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            diag_path = logs_dir / f"ml_train_{ts_str}.log"
            with diag_path.open("w", encoding="utf-8") as f:
                f.write(f"Timestamp: {ts_str}\n")
                f.write(f"samples: {len(X)}\n")
                f.write(f"class_counts: {counts}\n")
                if hasattr(model, "feature_importances_"):
                    f.write("top_feature_importances:\n")
                    for name, val in importance[:30]:
                        f.write(f"  {name}: {val:.6f}\n")
        except Exception:
            pass

        return model
    except Exception as e:
        logger.warning("ML model training failed: %s", e)
        return None


def predict_direction(model: Any, df: pd.DataFrame) -> pd.DataFrame:
    """
    Predict direction using trained ML model.

    Args:
        model: Trained ML model
        df: DataFrame with features

    Returns:
        DataFrame with prediction columns
    """
    if model is None or df.empty:
        if not df.empty:
            df = df.copy()
            df["ml_prediction"] = 0.0
            df["ml_probability"] = 0.5
        return df

    df = df.copy()

    # Prepare features
    df_features = prepare_features_for_ml(df)

    feature_cols = [
        "delta",
        "gamma",
        "theta",
        "vega",
        "rsi",
        "macd",
        "macd_histogram",
        "iv_percentile",
        "iv_rank",
        "volatility_score",
        "breakout_score",
        "momentum_score",
        "trend_score",
        "multi_tf_trend_score",
        "moneyness",
        "time_to_expiry",
    ]

    X = df_features[[col for col in feature_cols if col in df_features.columns]].fillna(0.0)

    try:
        # Predict
        predictions = model.predict(X)
        probabilities = model.predict_proba(X) if hasattr(model, "predict_proba") else None

        df["ml_prediction"] = predictions

        if probabilities is not None:
            # Use probability of positive class
            if probabilities.shape[1] > 1:
                df["ml_probability"] = probabilities[:, 1]
            else:
                df["ml_probability"] = probabilities[:, 0]
        else:
            df["ml_probability"] = 0.5

        # Convert to score (-1 to +1)
        if len(df) > 1 and df["ml_probability"].nunique() == 1:
            # Model is predicting same for all - use feature-based score instead
            # Use delta and Greeks as proxy for direction
            if "delta" in df.columns:
                delta_proxy = df["delta"].copy()
                if "side" in df.columns:
                    delta_proxy = delta_proxy.where(df["side"] == "CE", -delta_proxy)
                df["ai_score"] = (delta_proxy * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0) * 0.3
            else:
                df["ai_score"] = 0.0
        else:
            df["ai_score"] = (df["ml_probability"] - 0.5) * 1.5  # Slightly softer range
            df["ai_score"] = df["ai_score"].clip(-1.0, 1.0)

    except Exception as e:
        print(f"[WARN] ML prediction failed: {e}")
        df["ml_prediction"] = 0
        df["ml_probability"] = 0.5
        df["ai_score"] = 0.0

    return df
