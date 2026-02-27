"""
System3 Phase 213 - Training Window Selector

Evaluates candidate training windows and selects preferred window.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
WINDOW_JSON = STORAGE_META / "system3_training_window.json"

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_training_window_selection.log"

CURATED_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_curated.csv"
ARCHIVE_DIR = PROJECT_ROOT / "storage" / "live" / "archive"


def evaluate_window(df: pd.DataFrame, window_days: int) -> Dict[str, Any]:
    """Evaluate a training window."""
    if len(df) == 0:
        return {"rows": 0, "label_diversity": 0.0, "has_gaps": True, "score": 0.0}

    # Check label diversity
    if "pred_label" in df.columns:
        unique_labels = df["pred_label"].nunique()
        label_diversity = float(unique_labels / max(3, len(df)))  # Normalize
    else:
        label_diversity = 0.0

    # Check for gaps (simplified)
    has_gaps = False
    if "ts" in df.columns and len(df) > 1:
        df_sorted = df.sort_values("ts")
        gaps = df_sorted["ts"].diff().dt.total_seconds() / 3600  # hours
        has_gaps = bool((gaps > 24).any())  # More than 24 hour gap

    # Simple score
    score = float(len(df) * 0.5 + label_diversity * 100 - (100 if has_gaps else 0))

    return {
        "rows": int(len(df)),
        "label_diversity": float(label_diversity),
        "has_gaps": bool(has_gaps),
        "score": float(score),
    }


def run_phase213(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 213: Training Window Selector.

    Returns:
        dict: {
            "phase": 213,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "candidate_windows": int,
                "selected_window_days": int,
                "selected_window_path": str,
            },
            "errors": [],
        }
    """
    errors = []
    candidate_windows = [5, 10, 20]
    evaluations = []

    try:
        # Load curated data
        df = None
        if CURATED_CSV.exists():
            try:
                df = pd.read_csv(CURATED_CSV)
            except Exception:
                df = pd.read_csv(CURATED_CSV, engine="python", on_bad_lines="skip")

        # Also try archive files
        if df is None or len(df) < 100:
            archive_files = list(ARCHIVE_DIR.glob("*.csv")) if ARCHIVE_DIR.exists() else []
            if archive_files:
                dfs = []
                for arch_file in archive_files[-10:]:  # Last 10 files
                    try:
                        df_arch = pd.read_csv(arch_file, engine="python", on_bad_lines="skip")
                        dfs.append(df_arch)
                    except Exception:
                        pass
                if dfs:
                    try:
                        df = pd.concat(dfs, ignore_index=True)
                    except Exception as e:
                        # If concat fails (different schemas), use first non-empty DF
                        df = next((d for d in dfs if len(d) > 0), None)
                        if df is None:
                            errors.append(f"Failed to concatenate archive files: {e}")

        if df is None or len(df) == 0:
            return {
                "phase": 213,
                "status": "WARN",
                "details": "No training data available",
                "outputs": {
                    "candidate_windows": 0,
                    "selected_window_days": 0,
                    "selected_window_path": str(WINDOW_JSON),
                },
                "errors": [],
            }

        # Parse timestamps
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.dropna(subset=["ts"]).sort_values("ts")

        # Evaluate each candidate window
        for window_days in candidate_windows:
            cutoff_date = df["ts"].max() - timedelta(days=window_days) if "ts" in df.columns else None
            if cutoff_date:
                window_df = df[df["ts"] >= cutoff_date]
            else:
                window_df = df.tail(int(len(df) * window_days / 30))  # Approximate

            eval_result = evaluate_window(window_df, window_days)
            eval_result["window_days"] = window_days
            evaluations.append(eval_result)

        # Select best window
        if evaluations:
            best = max(evaluations, key=lambda x: x["score"])
            selected_window_days = best["window_days"]
        else:
            selected_window_days = 10  # Default

        # Convert evaluations to JSON-serializable format
        json_evaluations = []
        for eval_result in evaluations:
            json_evaluations.append(
                {
                    "window_days": int(eval_result["window_days"]),
                    "rows": int(eval_result["rows"]),
                    "label_diversity": float(eval_result["label_diversity"]),
                    "has_gaps": bool(eval_result["has_gaps"]),
                    "score": float(eval_result["score"]),
                }
            )

        # Save window selection
        window_data = {
            "selected_window_days": int(selected_window_days),
            "selection_date": datetime.now().isoformat(),
            "evaluations": json_evaluations,
        }
        with WINDOW_JSON.open("w", encoding="utf-8") as f:
            json.dump(window_data, f, indent=2)

        # Log evaluation metrics
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Training Window Selection Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            for eval_result in evaluations:
                f.write(f"Window: {eval_result['window_days']} days\n")
                f.write(f"  Rows: {eval_result['rows']}\n")
                f.write(f"  Label Diversity: {eval_result['label_diversity']:.3f}\n")
                f.write(f"  Has Gaps: {eval_result['has_gaps']}\n")
                f.write(f"  Score: {eval_result['score']:.2f}\n\n")
            f.write(f"Selected: {selected_window_days} days\n")

        status = "OK"
        details = f"Selected {selected_window_days}-day window from {len(candidate_windows)} candidates"

        return {
            "phase": 213,
            "status": status,
            "details": details,
            "outputs": {
                "candidate_windows": len(candidate_windows),
                "selected_window_days": selected_window_days,
                "selected_window_path": str(WINDOW_JSON),
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 213,
            "status": "ERROR",
            "details": f"Phase 213 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 213 - TRAINING WINDOW SELECTOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase213()

    print(f"Phase 213: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nWindow JSON: {result['outputs']['selected_window_path']}")
        print(f"Selected: {result['outputs']['selected_window_days']} days")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
