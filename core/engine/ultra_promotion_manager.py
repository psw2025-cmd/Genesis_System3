"""
System3 Ultra - Ultra Promotion System (Compare & Promote)

Side-by-side comparison of Baseline vs Ultra models, and manual promotion only.
Respects safety switches - no auto-promotion.

Inputs:
- Baseline models: core/models/angel_one/
- Ultra models: core/models/angel_one_ultra/
- Reports and metadata

Outputs:
- Comparison table (console)
- Promotion log (if promoted)

Menu Option: 83
"""

import pandas as pd
import numpy as np
import joblib
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"
ULTRA_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one_ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"
CONFIG_DIR = PROJECT_ROOT / "core" / "config"

PROMOTION_LOG = REPORTS_ULTRA_DIR / "ultra_promotion_log.txt"
SAFETY_JSON = CONFIG_DIR / "system3_ultra_safety.json"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_model_meta(model_dir: Path, underlying: str, prefix: str = "") -> Optional[Dict[str, Any]]:
    """Load model metadata."""
    meta_file = model_dir / f"{underlying}{prefix}_model_meta.json"
    if not meta_file.exists():
        return None

    try:
        with meta_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_safety_config() -> Dict[str, bool]:
    """Load safety configuration."""
    if not SAFETY_JSON.exists():
        return {"AUTO_PROMOTE_MODELS": False}

    try:
        with SAFETY_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"AUTO_PROMOTE_MODELS": False}


def show_comparison() -> Dict[str, Any]:
    """
    Show side-by-side comparison of Baseline vs Ultra models.

    Returns:
        Dict with comparison data
    """
    print("=== SYSTEM3 ULTRA - PROMOTION MANAGER ===")
    print("[INFO] Comparing Baseline vs Ultra models\n")
    print("[SAFETY] Manual promotion only - requires explicit keyword\n")

    comparison_rows = []

    for underlying in UNDERLYINGS:
        baseline_meta = load_model_meta(MODELS_DIR, underlying)
        ultra_meta = load_model_meta(ULTRA_MODELS_DIR, underlying, "_ultra")

        if not baseline_meta and not ultra_meta:
            continue

        row = {
            "underlying": underlying,
            "baseline_exists": baseline_meta is not None,
            "ultra_exists": ultra_meta is not None,
            "baseline_accuracy": baseline_meta.get("accuracy", 0.0) if baseline_meta else None,
            "ultra_accuracy": ultra_meta.get("accuracy", 0.0) if ultra_meta else None,
            "baseline_train_rows": baseline_meta.get("train_rows", 0) if baseline_meta else None,
            "ultra_train_rows": ultra_meta.get("train_rows", 0) if ultra_meta else None,
            "baseline_features": baseline_meta.get("feature_count", 0) if baseline_meta else None,
            "ultra_features": ultra_meta.get("feature_count", 0) if ultra_meta else None,
        }

        comparison_rows.append(row)

    if not comparison_rows:
        return {
            "status": "NO_MODELS",
            "message": "No models found for comparison",
        }

    # Print comparison table
    print("\n=== BASELINE vs ULTRA COMPARISON ===\n")
    print(f"{'Underlying':<12} {'Baseline':<20} {'Ultra':<20} {'Diff':<10}")
    print("-" * 70)

    for row in comparison_rows:
        baseline_acc = f"{row['baseline_accuracy']:.4f}" if row["baseline_accuracy"] is not None else "N/A"
        ultra_acc = f"{row['ultra_accuracy']:.4f}" if row["ultra_accuracy"] is not None else "N/A"

        if row["baseline_accuracy"] is not None and row["ultra_accuracy"] is not None:
            diff = row["ultra_accuracy"] - row["baseline_accuracy"]
            diff_str = f"{diff:+.4f}"
        else:
            diff_str = "N/A"

        print(f"{row['underlying']:<12} {baseline_acc:<20} {ultra_acc:<20} {diff_str:<10}")

    return {
        "status": "SUCCESS",
        "comparison": comparison_rows,
    }


def interactive_promote() -> None:
    """Interactive promotion with explicit keyword requirement."""
    comparison = show_comparison()

    if comparison["status"] != "SUCCESS":
        print(f"\n[INFO] {comparison.get('message', 'Cannot show comparison')}")
        return

    # Check safety
    safety = load_safety_config()
    auto_promote = safety.get("AUTO_PROMOTE_MODELS", False)

    if auto_promote:
        print("\n[WARN] AUTO_PROMOTE_MODELS is enabled, but manual promotion still requires explicit keyword")

    print("\n=== PROMOTION ===")
    print("To promote a model, type: PROMOTE_<UNDERLYING>")
    print("Example: PROMOTE_NIFTY")
    print("Press ENTER to cancel\n")

    user_input = input("Enter promotion command (or ENTER to cancel): ").strip().upper()

    if not user_input:
        print("[CANCEL] No promotion performed")
        return

    # Parse command
    if not user_input.startswith("PROMOTE_"):
        print(f"[ERROR] Invalid command. Must start with 'PROMOTE_'")
        return

    underlying = user_input.replace("PROMOTE_", "").upper()
    if underlying not in UNDERLYINGS:
        print(f"[ERROR] Invalid underlying: {underlying}")
        return

    # Check if Ultra model exists
    ultra_model_file = ULTRA_MODELS_DIR / f"{underlying}_ultra_model.pkl"
    ultra_meta_file = ULTRA_MODELS_DIR / f"{underlying}_ultra_model_meta.json"

    if not ultra_model_file.exists():
        print(f"[ERROR] Ultra model not found for {underlying}")
        return

    # Check baseline model
    baseline_model_file = MODELS_DIR / f"{underlying}_model.pkl"
    baseline_meta_file = MODELS_DIR / f"{underlying}_model_meta.json"

    if not baseline_model_file.exists():
        print(f"[WARN] Baseline model not found - will create new")

    # Confirm
    print(f"\n[CONFIRM] Promote Ultra {underlying} model to baseline?")
    print(f"  Ultra: {ultra_model_file}")
    print(f"  Baseline: {baseline_model_file}")
    confirm = input("Type 'YES' to confirm: ").strip().upper()

    if confirm != "YES":
        print("[CANCEL] Promotion cancelled")
        return

    # Perform promotion
    try:
        # Backup baseline (if exists)
        if baseline_model_file.exists():
            backup_file = MODELS_DIR / f"{underlying}_model_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pkl"
            shutil.copy2(baseline_model_file, backup_file)
            print(f"[BACKUP] Baseline backed up: {backup_file}")

        # Copy Ultra to baseline
        shutil.copy2(ultra_model_file, baseline_model_file)
        print(f"[PROMOTE] Model copied: {baseline_model_file}")

        # Copy metadata
        if ultra_meta_file.exists():
            if baseline_meta_file.exists():
                backup_meta = (
                    MODELS_DIR / f"{underlying}_model_meta_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                )
                shutil.copy2(baseline_meta_file, backup_meta)
            shutil.copy2(ultra_meta_file, baseline_meta_file)
            print(f"[PROMOTE] Metadata copied: {baseline_meta_file}")

        # Log promotion
        log_entry = f"{datetime.utcnow().isoformat()} | PROMOTED {underlying} | Ultra -> Baseline\n"
        with PROMOTION_LOG.open("a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"\n✅ Promotion successful: {underlying}")
        print(f"[LOG] Promotion logged: {PROMOTION_LOG}")

    except Exception as e:
        print(f"[ERROR] Promotion failed: {e}")


def main() -> None:
    """Main entry point."""
    interactive_promote()


if __name__ == "__main__":
    main()
