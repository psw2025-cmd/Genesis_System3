"""
Angel One Index Options - Blended Training Orchestrator (Dry-Run)

Creates training plan for blended dataset.
Skip training, dry-run only.
SAFE MODE ONLY - No training, no model changes.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
MERGED_CSV = TRAINING_DIR / "merged_real_synth_dataset.csv"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"
TRAINING_PLAN_JSON = TRAINING_DIR / "blended_training_plan.json"

TRAINING_DIR.mkdir(parents=True, exist_ok=True)


def create_training_plan() -> Dict[str, Any]:
    """
    Create training plan for blended dataset (dry-run only).

    Does NOT train - creates plan only.

    Returns:
        Dict with training plan
    """
    print("=== ANGEL ONE INDEX OPTIONS - BLENDED TRAINING ORCHESTRATOR (DRY-RUN) ===")
    print("[INFO] SAFE MODE - Plan creation only, NO training\n")

    if not MERGED_CSV.exists():
        return {
            "status": "NO_DATASET",
            "message": "Merged dataset not found. Run dataset merger first.",
        }

    try:
        df = pd.read_csv(MERGED_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Merged dataset is empty",
            }

        print(f"[PLAN] Analyzing merged dataset: {len(df)} rows")

        # Analyze dataset
        underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
        plan_per_underlying = {}

        for underlying in underlyings:
            df_u = df[df["underlying"] == underlying] if "underlying" in df.columns else pd.DataFrame()

            if df_u.empty:
                plan_per_underlying[underlying] = {
                    "status": "NO_DATA",
                    "message": f"No data for {underlying}",
                }
                continue

            # Check feature availability
            exclude_cols = ["ts", "timestamp", "underlying", "expiry", "side", "strike", "label", "pred_label"]
            feature_cols = [c for c in df_u.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_u[c])]

            # Check label availability
            label_col = "label" if "label" in df_u.columns else None
            if label_col:
                label_distribution = df_u[label_col].value_counts().to_dict()
            else:
                label_distribution = {}

            plan_per_underlying[underlying] = {
                "status": "READY",
                "sample_count": len(df_u),
                "feature_count": len(feature_cols),
                "label_available": label_col is not None,
                "label_distribution": label_distribution,
                "training_ready": len(feature_cols) > 0 and label_col is not None and len(df_u) >= 100,
            }

        # Overall plan
        training_plan = {
            "status": "SUCCESS",
            "created_at": datetime.utcnow().isoformat(),
            "mode": "DRY_RUN",
            "training_performed": False,  # Explicitly marked as not trained
            "dataset_path": str(MERGED_CSV),
            "dataset_rows": len(df),
            "plan_per_underlying": plan_per_underlying,
            "note": "This is a TRAINING PLAN ONLY. No training has been performed.",
        }

        return training_plan

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def save_training_plan(plan: Dict[str, Any]) -> Path:
    """
    Save training plan to JSON.

    Returns:
        Path to saved JSON
    """
    with TRAINING_PLAN_JSON.open("w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    return TRAINING_PLAN_JSON


def main() -> None:
    """Main entry point."""
    plan = create_training_plan()

    if plan["status"] == "SUCCESS":
        print(f"\n=== TRAINING PLAN (DRY-RUN) ===\n")
        print(f"Dataset: {plan['dataset_path']}")
        print(f"Total Rows: {plan['dataset_rows']}")
        print(f"Mode: {plan['mode']}")
        print(f"Training Performed: {plan['training_performed']}")

        print("\n=== PLAN PER UNDERLYING ===")
        for underlying, underlying_plan in plan["plan_per_underlying"].items():
            if underlying_plan["status"] == "READY":
                print(f"\n{underlying}:")
                print(f"  Status: {underlying_plan['status']}")
                print(f"  Sample Count: {underlying_plan['sample_count']}")
                print(f"  Feature Count: {underlying_plan['feature_count']}")
                print(f"  Label Available: {underlying_plan['label_available']}")
                print(f"  Training Ready: {underlying_plan['training_ready']}")
                if underlying_plan["label_distribution"]:
                    print(f"  Label Distribution: {underlying_plan['label_distribution']}")
            else:
                print(f"\n{underlying}: {underlying_plan.get('message', 'Not ready')}")

        # Save plan
        save_path = save_training_plan(plan)
        print(f"\n[SAVE] Training plan saved to: {save_path}")
        print(f"\n⚠️  {plan['note']}")
        print("⚠️  IMPORTANT: This is a DRY-RUN plan. No training has been performed.")
    else:
        print(f"[INFO] {plan.get('message', 'Training plan not available')}")


if __name__ == "__main__":
    main()
