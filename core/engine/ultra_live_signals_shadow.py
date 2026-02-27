"""
System3 Ultra - Ultra Prediction Engine (Shadow Live)

Runs Ultra models in parallel (shadow) with baseline signals for comparison.
Shadow mode only - no trade plans generated.

Inputs:
- Live snapshots (same _build_full_snapshot used by baseline)
- Baseline models: core/models/angel_one/
- Ultra models: core/models/angel_one_ultra/

Outputs:
- storage/ultra/angel_ultra_live_shadow_signals.csv

Menu Option: 80
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Import snapshot builder
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.brokers.angel_one.broker import AngelOneBroker
from core.engine.angel_options_watch_loop import _build_full_snapshot
from core.engine.angel_features import add_advanced_features

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"
ULTRA_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one_ultra"

SHADOW_SIGNALS_CSV = ULTRA_DIR / "angel_ultra_live_shadow_signals.csv"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_model_with_meta(model_dir: Path, underlying: str, prefix: str = "") -> Optional[Dict[str, Any]]:
    """Load model and metadata."""
    model_file = model_dir / f"{underlying}{prefix}_model.pkl"
    meta_file = model_dir / f"{underlying}{prefix}_model_meta.json"

    if not model_file.exists():
        return None

    try:
        model = joblib.load(model_file)
        meta = {}
        if meta_file.exists():
            with meta_file.open("r", encoding="utf-8") as f:
                meta = json.load(f)
        return {
            "model": model,
            "meta": meta,
            "feature_cols": meta.get("features", meta.get("feature_cols", [])),
        }
    except Exception:
        return None


def run_ultra_live_shadow_once() -> Dict[str, Any]:
    """
    Run Ultra live shadow signals for a single snapshot.

    Returns:
        Dict with results
    """
    print("=== SYSTEM3 ULTRA - LIVE SIGNALS (SHADOW) ===")
    print("[INFO] Running Ultra models in shadow mode\n")
    print("[SAFETY] Shadow only - no trades, no executor calls\n")

    # Initialize broker
    try:
        broker = AngelOneBroker(allow_data_only=True)  # Data fetching doesn't require live trading permission
        print("[BROKER] Connected")
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to initialize broker: {e}",
        }

    # Build snapshot
    print("[SNAPSHOT] Building live snapshot...")
    try:
        df_snapshot = _build_full_snapshot(broker)
        if df_snapshot is None or df_snapshot.empty:
            return {
                "status": "NO_DATA",
                "message": "No snapshot data collected",
            }
        print(f"[SNAPSHOT] Collected {len(df_snapshot)} rows")
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to build snapshot: {e}",
        }

    # Add features
    try:
        df_snapshot = add_advanced_features(df_snapshot)
        print("[FEATURES] Advanced features added")
    except Exception as e:
        print(f"[WARN] Feature engineering failed: {e}")

    # Load models
    baseline_models = {}
    ultra_models = {}

    for underlying in UNDERLYINGS:
        baseline = load_model_with_meta(MODELS_DIR, underlying)
        if baseline:
            baseline_models[underlying] = baseline

        ultra = load_model_with_meta(ULTRA_MODELS_DIR, underlying, "_ultra")
        if ultra:
            ultra_models[underlying] = ultra

    print(f"[MODELS] Baseline: {len(baseline_models)}, Ultra: {len(ultra_models)}")

    # Run predictions
    shadow_rows = []
    ts = datetime.utcnow().isoformat()

    for _, row in df_snapshot.iterrows():
        underlying = row.get("underlying")
        if not underlying or underlying not in UNDERLYINGS:
            continue

        shadow_row = {
            "timestamp": ts,
            "underlying": underlying,
            "strike": row.get("strike", np.nan),
            "side": row.get("side", np.nan),
            "ltp": row.get("ltp", np.nan),
            "spot": row.get("spot", np.nan),
        }

        # Baseline prediction
        baseline_pred = None
        baseline_conf = None
        if underlying in baseline_models:
            try:
                baseline_info = baseline_models[underlying]
                feature_cols = baseline_info["feature_cols"]
                if feature_cols:
                    X = pd.DataFrame([row])[feature_cols].fillna(0.0)
                    if not X.empty:
                        proba = baseline_info["model"].predict_proba(X)[0]
                        classes = baseline_info["model"].classes_
                        baseline_pred = classes[np.argmax(proba)]
                        baseline_conf = float(np.max(proba))
            except Exception:
                pass

        shadow_row["baseline_pred"] = baseline_pred
        shadow_row["baseline_conf"] = baseline_conf

        # Ultra prediction
        ultra_pred = None
        ultra_conf = None
        if underlying in ultra_models:
            try:
                ultra_info = ultra_models[underlying]
                feature_cols = ultra_info["feature_cols"]
                if feature_cols:
                    X = pd.DataFrame([row])[feature_cols].fillna(0.0)
                    if not X.empty:
                        proba = ultra_info["model"].predict_proba(X)[0]
                        classes = ultra_info["model"].classes_
                        ultra_pred = classes[np.argmax(proba)]
                        ultra_conf = float(np.max(proba))
            except Exception:
                pass

        shadow_row["ultra_pred"] = ultra_pred
        shadow_row["ultra_conf"] = ultra_conf

        # Agreement
        shadow_row["agree_flag"] = (baseline_pred == ultra_pred) if (baseline_pred and ultra_pred) else False

        shadow_rows.append(shadow_row)

    if not shadow_rows:
        return {
            "status": "EMPTY",
            "message": "No shadow rows generated",
        }

    # Save
    df_shadow = pd.DataFrame(shadow_rows)
    write_header = not SHADOW_SIGNALS_CSV.exists()
    df_shadow.to_csv(SHADOW_SIGNALS_CSV, mode="a", header=write_header, index=False)
    print(f"[SAVE] Shadow signals: {SHADOW_SIGNALS_CSV} ({len(shadow_rows)} rows)")

    # Print summary
    print("\n=== SHADOW SIGNALS SUMMARY ===")
    agreement_count = df_shadow["agree_flag"].sum() if "agree_flag" in df_shadow.columns else 0
    agreement_rate = agreement_count / len(df_shadow) * 100 if len(df_shadow) > 0 else 0.0
    print(f"Total Signals: {len(df_shadow)}")
    print(f"Agreement Rate: {agreement_rate:.1f}%")
    print(f"\n[SAVE] All shadow signals saved")
    print("[NOTE] No trade plans generated - shadow only")

    return {
        "status": "SUCCESS",
        "total_signals": len(shadow_rows),
        "agreement_rate": float(agreement_rate),
    }


def main() -> None:
    """Main entry point."""
    result = run_ultra_live_shadow_once()

    if result["status"] != "SUCCESS":
        print(f"\n[INFO] {result.get('message', 'Shadow signals not generated')}")


if __name__ == "__main__":
    main()
