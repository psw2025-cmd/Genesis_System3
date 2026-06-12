"""
System3 Ultra - Multi-Consensus Engine (Shadow)

Combines predictions from multiple Ultra models & baseline model for analysis.
Shadow mode only - no trade plans generated.

Inputs:
- Baseline models: core/models/dhan/
- Ultra models: core/models/dhan_ultra/
- Sample signals or shadow dataset snapshots

Outputs:
- storage/reports_ultra/ultra_consensus_sample.csv

Menu Option: 78
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
ULTRA_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan_ultra"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

SHADOW_PARQUET = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.parquet"
SHADOW_CSV = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"
CONSENSUS_CSV = REPORTS_ULTRA_DIR / "ultra_consensus_sample.csv"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

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


def run_consensus_sample() -> Dict[str, Any]:
    """
    Run consensus analysis on sample data.

    Returns:
        Dict with consensus results
    """
    print("=== SYSTEM3 ULTRA - MULTI-CONSENSUS ENGINE (SHADOW) ===")
    print("[INFO] Comparing Baseline vs Ultra predictions\n")
    print("[SAFETY] Shadow mode only - analysis only, no trades\n")

    # Load sample from shadow dataset
    df_sample = None
    if SHADOW_PARQUET.exists():
        try:
            df_sample = pd.read_parquet(SHADOW_PARQUET)
            # Take small sample
            if len(df_sample) > 100:
                df_sample = df_sample.sample(100, random_state=42)
        except Exception:
            if SHADOW_CSV.exists():
                df_sample = pd.read_csv(SHADOW_CSV)
                if len(df_sample) > 100:
                    df_sample = df_sample.sample(100, random_state=42)

    if df_sample is None or df_sample.empty:
        return {
            "status": "NO_DATA",
            "message": "Shadow dataset not found. Run Phase 10 first.",
        }

    print(f"[LOAD] Sample: {len(df_sample)} rows")

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

    if not baseline_models and not ultra_models:
        return {
            "status": "NO_MODELS",
            "message": "No models found (baseline or ultra)",
        }

    print(f"[LOAD] Baseline models: {len(baseline_models)}")
    print(f"[LOAD] Ultra models: {len(ultra_models)}")

    # Run consensus analysis
    consensus_rows = []

    for _, row in df_sample.iterrows():
        underlying = row.get("underlying")
        if not underlying or underlying not in UNDERLYINGS:
            continue

        consensus_row = {
            "underlying": underlying,
            "strike": row.get("strike", np.nan),
            "side": row.get("side", np.nan),
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

        consensus_row["baseline_pred"] = baseline_pred
        consensus_row["baseline_conf"] = baseline_conf

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

        consensus_row["ultra_pred"] = ultra_pred
        consensus_row["ultra_conf"] = ultra_conf

        # Agreement
        agree_flag = (baseline_pred == ultra_pred) if (baseline_pred and ultra_pred) else False
        consensus_row["agree_flag"] = agree_flag

        # Final recommendation (use Ultra if available, else baseline)
        consensus_row["final_shadow_recommendation"] = ultra_pred if ultra_pred else baseline_pred

        consensus_rows.append(consensus_row)

    if not consensus_rows:
        return {
            "status": "EMPTY",
            "message": "No consensus rows generated",
        }

    # Save consensus report
    df_consensus = pd.DataFrame(consensus_rows)
    df_consensus.to_csv(CONSENSUS_CSV, index=False)
    print(f"[SAVE] Consensus report: {CONSENSUS_CSV}")

    # Statistics
    agreement_rate = df_consensus["agree_flag"].mean() * 100 if "agree_flag" in df_consensus.columns else 0.0

    return {
        "status": "SUCCESS",
        "total_samples": len(consensus_rows),
        "agreement_rate": float(agreement_rate),
        "baseline_models": len(baseline_models),
        "ultra_models": len(ultra_models),
    }


def main() -> None:
    """Main entry point."""
    result = run_consensus_sample()

    if result["status"] == "SUCCESS":
        print("\n=== CONSENSUS ANALYSIS SUMMARY ===")
        print(f"Total Samples: {result['total_samples']}")
        print(f"Baseline Models: {result['baseline_models']}")
        print(f"Ultra Models: {result['ultra_models']}")
        print(f"Agreement Rate: {result['agreement_rate']:.1f}%")
        print(f"\n[SAVE] Consensus report saved")
        print("[NOTE] Analysis only - no trade plans generated")
    else:
        print(f"\n[INFO] {result.get('message', 'Consensus analysis not completed')}")


if __name__ == "__main__":
    main()
