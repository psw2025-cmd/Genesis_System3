"""
Gain Regressor Trainer — Self-Learning Expected-Gain Regression Head
=====================================================================
Trains a per-underlying Ridge/XGBRegressor to predict expected % gain
(target_forward_return) from option chain features.

Data source:
  state/options_history/dataset/ce_pe_dataset.csv
  (populated by scripts/options_ce_pe_history_pipeline.py --mode build)

Outputs (one per underlying):
  state/models/gain_regressor_{UNDERLYING}.pkl

Also re-runs Spearman ρ calibration after training:
  calls scripts/calibrate_factor_weights.py --dry-run and logs ρ improvement.

Designed to be called:
  1. Manually: python scripts/train_gain_regressor.py
  2. By auto_retrain.py on retrain_signal.json
  3. By the scheduler at 16:30 IST weekdays (after bhavcopy download at 18:30)

Safety:
  - LIVE_TRADING_ENABLED must be 0.
  - No broker API calls — reads only from local CSV files.
  - Writes only to state/models/ and reports/latest/gain_regressor_proof/.

Self-learning loop:
  Each day new bhavcopy data arrives → options_ce_pe_history_pipeline builds
  new target_forward_return rows → this script retrains → ensemble_predictor
  uses the updated regressor → GainRankEngine produces better expected_gain_pct
  → MarketResultValidator measures Spearman ρ → if ρ < 0.40 for 3 days,
  retrain_signal.json fires → auto_retrain.py calls this script again.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("train_gain_regressor")

# Safety gate
if os.environ.get("LIVE_TRADING_ENABLED", "0") not in ("0", "false", "False", ""):
    logger.error("LIVE_TRADING_ENABLED is truthy — aborting.")
    sys.exit(1)

DATASET_CSV = ROOT / "state" / "options_history" / "dataset" / "ce_pe_dataset.csv"
MODEL_DIR = ROOT / "state" / "models"
REPORT_DIR = ROOT / "reports" / "latest" / "gain_regressor_proof"
BHAVCOPY_DATASET_CSV = ROOT / "state" / "bhavcopy_gain_dataset.csv"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
MIN_ROWS_PER_UNDERLYING = 30  # minimum rows to train (lower threshold for early operation)
TEST_FRACTION = 0.25           # temporal hold-out (last 25% of rows by time)

# Feature columns used by the regressor
# Must match _predict_expected_gain() in ensemble_predictor.py
FEATURE_COLS = ["mean_signal", "confidence", "iv", "pcr", "oi_change_pct"]


def _load_ce_pe_dataset() -> Optional[pd.DataFrame]:
    """Load the supervised CE/PE dataset from options_ce_pe_history_pipeline."""
    if not DATASET_CSV.exists():
        logger.warning(f"CE/PE dataset not found: {DATASET_CSV}")
        return None
    try:
        df = pd.read_csv(DATASET_CSV)
        if df.empty:
            logger.warning("CE/PE dataset is empty.")
            return None
        logger.info(f"Loaded CE/PE dataset: {len(df)} rows")
        return df
    except Exception as exc:
        logger.error(f"Could not load CE/PE dataset: {exc}")
        return None


def _build_features_from_ce_pe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw CE/PE candle rows into regressor features + target.

    The regressor uses 5 features that mirror what _predict_expected_gain()
    passes at inference time: mean_signal, confidence, iv, pcr, oi_change_pct.

    For the training dataset we proxy these from bhavcopy columns:
      mean_signal     ← return_1 (previous-bar return as directional signal)
      confidence      ← range_pct (high-low / close; wider range = more conviction)
      iv              ← range_pct * sqrt(252) (rough daily IV proxy)
      pcr             ← PE/CE OI ratio within the same expiry group
      oi_change_pct   ← (oi - prev_oi) / prev_oi per contract
    """
    required = ["underlying", "close", "volume", "oi", "return_1", "range_pct", "target_forward_return"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.error(f"CE/PE dataset missing columns: {missing}")
        return pd.DataFrame()

    # Sort chronologically
    time_cols = [c for c in df.columns if c.lower() in ("timestamp", "ts", "date", "datetime", "time")]
    if time_cols:
        df = df.sort_values(time_cols[0], ascending=True).reset_index(drop=True)

    # Build feature frame per underlying
    frames: List[pd.DataFrame] = []
    for und in df["underlying"].unique():
        sub = df[df["underlying"] == und].copy()

        # mean_signal: prior-bar return sign (directional proxy)
        sub["mean_signal"] = sub["return_1"].clip(-1, 1)

        # confidence: inferred from range width (wider = more volatile = higher conviction)
        sub["confidence"] = sub["range_pct"].clip(0, 1)

        # iv: annualised daily range proxy
        sub["iv"] = sub["range_pct"] * np.sqrt(252)

        # oi_change_pct: OI momentum
        sub["oi_change_pct"] = sub["oi"].pct_change().fillna(0).clip(-1, 1)

        # pcr: approximate from option_type distribution within same expiry (if available)
        if "option_type" in sub.columns and "expiry" in sub.columns:
            ce_oi = sub[sub["option_type"] == "CE"].groupby("expiry")["oi"].transform("sum")
            pe_oi = sub[sub["option_type"] == "PE"].groupby("expiry")["oi"].transform("sum")
            sub["pcr"] = (pe_oi / ce_oi.replace(0, np.nan)).fillna(1.0).clip(0.1, 5.0)
        else:
            sub["pcr"] = 1.0

        sub["target"] = sub["target_forward_return"]
        frames.append(sub[["underlying"] + FEATURE_COLS + ["target"]])

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _train_regressor(
    features: pd.DataFrame, underlying: str
) -> Tuple[Optional[object], Dict]:
    """Train a Ridge regressor (sklearn) with XGBoost upgrade when available."""
    sub = features[features["underlying"] == underlying].copy()
    sub = sub.dropna(subset=FEATURE_COLS + ["target"])

    if len(sub) < MIN_ROWS_PER_UNDERLYING:
        return None, {"status": "SKIPPED", "reason": f"only {len(sub)} rows (min {MIN_ROWS_PER_UNDERLYING})"}

    X = sub[FEATURE_COLS].values
    y = sub["target"].values

    # Temporal split — last TEST_FRACTION rows are the test set
    split = max(1, int(len(sub) * (1 - TEST_FRACTION)))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Try XGBoost regressor first; fall back to Ridge
    model = None
    model_type = "ridge"
    try:
        import xgboost as xgb
        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
        model.fit(X_train, y_train)
        model_type = "xgboost"
        logger.info(f"  [{underlying}] Trained XGBRegressor")
    except ImportError:
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        model = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
        model.fit(X_train, y_train)
        logger.info(f"  [{underlying}] Trained Ridge (XGBoost unavailable)")

    # Evaluate on temporal hold-out
    metrics: Dict = {"underlying": underlying, "model_type": model_type, "train_rows": int(len(X_train)),
                     "test_rows": int(len(X_test))}
    if len(X_test) > 0:
        y_pred = model.predict(X_test)
        ss_res = float(np.sum((y_test - y_pred) ** 2))
        ss_tot = float(np.sum((y_test - y_test.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        mae = float(np.mean(np.abs(y_test - y_pred)))
        metrics["r2"] = round(r2, 4)
        metrics["mae_pct"] = round(mae * 100, 4)
        logger.info(f"  [{underlying}] R²={r2:.3f} MAE={mae*100:.3f}%")
    else:
        metrics["r2"] = None
        metrics["mae_pct"] = None
        logger.warning(f"  [{underlying}] No test rows — skipping evaluation")

    metrics["status"] = "TRAINED"
    return model, metrics


def _save_regressor(model: object, underlying: str) -> Path:
    path = MODEL_DIR / f"gain_regressor_{underlying}.pkl"
    with open(path, "wb") as fh:
        pickle.dump(model, fh)
    logger.info(f"  Saved: {path}")
    return path


def run(dry_run: bool = False) -> Dict:
    """Main entry point. Returns result dict."""
    started = datetime.now(timezone.utc).isoformat()
    logger.info("=" * 70)
    logger.info("GAIN REGRESSOR TRAINER — self-learning expected-gain head")
    logger.info("=" * 70)

    result: Dict = {
        "started": started,
        "dry_run": dry_run,
        "underlyings_trained": [],
        "underlyings_skipped": [],
        "metrics": {},
        "pass": False,
    }

    df_raw = _load_ce_pe_dataset()
    if df_raw is None:
        result["reason"] = (
            "CE/PE dataset not found. Run: "
            "python scripts/options_ce_pe_history_pipeline.py --mode build"
        )
        result["pass"] = False
        _write_proof(result)
        return result

    features = _build_features_from_ce_pe(df_raw)
    if features.empty:
        result["reason"] = "Could not build regressor features from CE/PE dataset."
        result["pass"] = False
        _write_proof(result)
        return result

    trained_count = 0
    for und in UNDERLYINGS:
        logger.info(f"\n[{und}]")
        model, metrics = _train_regressor(features, und)
        result["metrics"][und] = metrics

        if model is not None:
            if not dry_run:
                _save_regressor(model, und)
            result["underlyings_trained"].append(und)
            trained_count += 1
        else:
            result["underlyings_skipped"].append(und)

    result["pass"] = trained_count > 0
    result["completed"] = datetime.now(timezone.utc).isoformat()
    result["status"] = "PASS" if result["pass"] else "FAIL"

    if not dry_run:
        _write_proof(result)
        # Trigger factor weight calibration to propagate improvement to GainRankEngine
        _trigger_calibration()

    logger.info(f"\n{'='*70}")
    logger.info(f"RESULT: trained={trained_count} skipped={len(result['underlyings_skipped'])}")
    return result


def _write_proof(result: Dict) -> None:
    out = REPORT_DIR / "summary.json"
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    logger.info(f"Proof written: {out}")


def _trigger_calibration() -> None:
    """Run calibrate_factor_weights.py in dry-run mode to log ρ and recommended weights."""
    import subprocess
    script = ROOT / "scripts" / "calibrate_factor_weights.py"
    if not script.exists():
        return
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--dry-run"],
            capture_output=True, text=True, timeout=120
        )
        if proc.stdout:
            logger.info("[calibrate_factor_weights --dry-run]\n" + proc.stdout[-2000:])
        if proc.returncode != 0 and proc.stderr:
            logger.warning(f"calibrate_factor_weights stderr: {proc.stderr[-500:]}")
    except Exception as exc:
        logger.warning(f"Could not run calibrate_factor_weights: {exc}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Train per-underlying gain regressors")
    ap.add_argument("--dry-run", action="store_true", help="Train but do not save models")
    args = ap.parse_args()
    r = run(dry_run=args.dry_run)
    sys.exit(0 if r.get("pass") else 1)
