"""
Angel One Index Options - Blended Model Trainer V2

Trains models on blended synthetic + real data.
MANUAL TRIGGER ONLY - Never runs automatically.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
BLENDED_CSV = TRAINING_DIR / "angel_blended_training_preview.csv"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"


def train_blended_models() -> Dict[str, Any]:
    """
    Train models on blended dataset.

    MANUAL TRIGGER ONLY - Requires explicit menu call.

    Returns:
        Dict with training results
    """
    if not BLENDED_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "Blended training CSV not found. Run blended dataset builder first.",
        }

    try:
        df = pd.read_csv(BLENDED_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Blended dataset is empty",
            }

        print(f"[TRAIN] Training on {len(df)} blended rows")

        # Use existing training pipeline
        from core.engine.train_angel_models import (
            _train_model_for_underlying,
            _load_top_features_map,
        )

        # Load feature importance
        top_features_map = _load_top_features_map(str(PROJECT_ROOT))

        results = {}
        underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

        for underlying in underlyings:
            df_u = df[df["underlying"] == underlying]
            if df_u.empty:
                continue

            print(f"\n[TRAIN] Training {underlying}...")
            selected_features = top_features_map.get(underlying)

            try:
                accuracy, model, meta = _train_model_for_underlying(
                    df_u,
                    underlying,
                    selected_features=selected_features,
                )

                # Save model
                model_path = MODELS_DIR / f"{underlying}_model.pkl"
                meta_path = MODELS_DIR / f"{underlying}_model_meta.json"

                import joblib
                import json

                joblib.dump(model, model_path)
                with meta_path.open("w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)

                results[underlying] = {
                    "status": "SUCCESS",
                    "accuracy": float(accuracy),
                    "model_path": str(model_path),
                }

                print(f"[SAVE] Model saved: {model_path}")
            except Exception as e:
                results[underlying] = {
                    "status": "ERROR",
                    "message": str(e),
                }
                print(f"[ERROR] Failed to train {underlying}: {e}")

        return {
            "status": "SUCCESS",
            "results": results,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def validate_training_prerequisites() -> tuple[bool, str]:
    """
    Validate prerequisites before training.

    Returns:
        (is_valid, message)
    """
    if not BLENDED_CSV.exists():
        return False, "Blended training CSV not found. Run menu 34 first."

    try:
        df = pd.read_csv(BLENDED_CSV)
        if df.empty:
            return False, "Blended dataset is empty."
        if len(df) < 100:
            return False, f"Blended dataset too small ({len(df)} rows). Need at least 100 rows."
    except Exception as e:
        return False, f"Failed to read blended CSV: {e}"

    # Check if models directory exists
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

    return True, "Prerequisites validated."


def backup_existing_models() -> bool:
    """
    Backup existing models before retraining.

    Returns:
        True if backup successful
    """
    from datetime import datetime
    import shutil

    backup_dir = MODELS_DIR.parent / "angel_one_backup"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"

    try:
        if MODELS_DIR.exists():
            backup_path.mkdir(parents=True, exist_ok=True)
            for model_file in MODELS_DIR.glob("*.pkl"):
                shutil.copy2(model_file, backup_path / model_file.name)
            for meta_file in MODELS_DIR.glob("*.json"):
                shutil.copy2(meta_file, backup_path / meta_file.name)
            print(f"[BACKUP] Models backed up to: {backup_path}")
            return True
    except Exception as e:
        print(f"[WARNING] Backup failed: {e}")
        return False

    return True


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - BLENDED MODEL TRAINER V2 ===")
    print("[INFO] MANUAL TRIGGER ONLY - Never runs automatically\n")
    print("[SAFETY] Baseline models will be backed up before training\n")

    # Validate prerequisites
    is_valid, message = validate_training_prerequisites()
    if not is_valid:
        print(f"[ERROR] {message}")
        return

    print(f"[VALIDATED] {message}\n")

    # Show training preview
    df = pd.read_csv(BLENDED_CSV)
    print(f"[PREVIEW] Blended dataset: {len(df)} rows")
    if "label" in df.columns:
        print("\nLabel distribution:")
        label_counts = df["label"].value_counts()
        for label, count in label_counts.items():
            print(f"  {label}: {count}")

    print("\n" + "=" * 60)
    print("⚠️  WARNING: This will retrain ALL models on blended data")
    print("⚠️  Existing models will be backed up first")
    print("=" * 60 + "\n")

    confirm = input("Type 'TRAIN' to proceed, or anything else to cancel: ")
    if confirm != "TRAIN":
        print("[CANCELLED] Training cancelled by user.")
        return

    # Backup existing models
    backup_existing_models()

    # Train
    print("\n[TRAINING] Starting model training...\n")
    results = train_blended_models()

    if results["status"] == "SUCCESS":
        print("\n=== TRAINING RESULTS ===")
        for underlying, result in results["results"].items():
            if result["status"] == "SUCCESS":
                print(f"{underlying}: Accuracy = {result['accuracy']:.4f}")
            else:
                print(f"{underlying}: {result.get('message', 'Failed')}")
        print("\n[SUCCESS] Model training completed.")
    else:
        print(f"[ERROR] {results.get('message', 'Training failed')}")


if __name__ == "__main__":
    main()
