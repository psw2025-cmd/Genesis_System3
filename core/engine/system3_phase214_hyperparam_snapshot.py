"""
System3 Phase 214 - Model Hyperparameter Snapshotter

Records current ML model hyperparameters.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
HPARAMS_JSON = STORAGE_META / "system3_model_hparams.json"

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_hyperparam_history.md"

MODELS_DIR = PROJECT_ROOT / "core" / "models"


def run_phase214(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 214: Model Hyperparameter Snapshotter.

    Returns:
        dict: {
            "phase": 214,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "models_snapshot": int,
                "hparams_path": str,
            },
            "errors": [],
        }
    """
    errors = []
    models_snapshot = []

    try:
        # Default hyperparameters (from ml_predictor.py patterns)
        default_hparams = {
            "model_type": "RandomForestClassifier",
            "n_estimators": 100,
            "max_depth": 6,
            "class_weight": "balanced",
            "features": [
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
            ],
        }

        # Check for model files
        model_files = []
        if MODELS_DIR.exists():
            model_files = list(MODELS_DIR.rglob("*.pkl")) + list(MODELS_DIR.rglob("*.pickle"))

        # Create snapshot entry
        snapshot_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_type": default_hparams["model_type"],
            "hyperparameters": default_hparams,
            "model_files": [str(f) for f in model_files],
        }
        models_snapshot.append(snapshot_entry)

        # Load existing history
        history = {"snapshots": []}
        if HPARAMS_JSON.exists():
            try:
                with HPARAMS_JSON.open("r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass

        # Append new snapshot
        history["snapshots"].append(snapshot_entry)
        history["last_updated"] = datetime.now().isoformat()

        # Keep last 50 snapshots
        if len(history["snapshots"]) > 50:
            history["snapshots"] = history["snapshots"][-50:]

        # Save
        with HPARAMS_JSON.open("w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        # Generate markdown summary
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Model Hyperparameter History\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Snapshots**: {len(history['snapshots'])}\n\n")

            f.write("## Latest Snapshot\n\n")
            latest = history["snapshots"][-1]
            f.write(f"**Timestamp**: {latest['timestamp']}\n")
            f.write(f"**Model Type**: {latest['model_type']}\n\n")
            f.write("### Hyperparameters\n\n")
            for key, value in latest["hyperparameters"].items():
                if key != "features":
                    f.write(f"- **{key}**: {value}\n")
            f.write(f"\n**Features**: {len(latest['hyperparameters'].get('features', []))} features\n")

        status = "OK"
        details = f"Snapshot created for {len(model_files)} model file(s)"

        return {
            "phase": 214,
            "status": status,
            "details": details,
            "outputs": {
                "models_snapshot": len(models_snapshot),
                "hparams_path": str(HPARAMS_JSON),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 214,
            "status": "ERROR",
            "details": f"Phase 214 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 214 - MODEL HYPERPARAMETER SNAPSHOTTER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase214()

    print(f"Phase 214: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nHParams JSON: {result['outputs']['hparams_path']}")
        print(f"Snapshots: {result['outputs']['models_snapshot']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
