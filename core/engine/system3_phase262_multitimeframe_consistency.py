"""
System3 Phase 262 - Multi-Timeframe Signal Consistency Checker

Validates signal consistency across different timeframes.
Checks if signals align across 1min, 5min, 15min aggregations.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_multitimeframe_consistency.md"


def run_phase262(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 262: Multi-Timeframe Signal Consistency Checker.

    Returns:
        dict: PhaseResult with status, details, outputs, errors
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 262,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"consistency_score": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 262,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"consistency_score": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 262,
                "status": "WARN",
                "details": "No data or missing timestamp column",
                "outputs": {"consistency_score": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Parse timestamps
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"]).sort_values("ts")

        # Aggregate by different timeframes
        df["ts_1min"] = df["ts"].dt.floor("1min")
        df["ts_5min"] = df["ts"].dt.floor("5min")
        df["ts_15min"] = df["ts"].dt.floor("15min")

        # Calculate consistency (if final_score available)
        consistency_score = 0.0
        if "final_score" in df.columns:
            # Compare score distributions across timeframes
            score_1min = df.groupby("ts_1min")["final_score"].mean()
            score_5min = df.groupby("ts_5min")["final_score"].mean()

            # Simple consistency: correlation between 1min and 5min aggregations
            if len(score_1min) > 1 and len(score_5min) > 1:
                # Align by timestamp
                aligned = pd.merge(
                    score_1min.reset_index(),
                    score_5min.reset_index(),
                    left_on="ts_1min",
                    right_on="ts_5min",
                    how="inner",
                )
                if len(aligned) > 1:
                    consistency_score = aligned["final_score_x"].corr(aligned["final_score_y"])
                    if pd.isna(consistency_score):
                        consistency_score = 0.0

        # Generate report
        report_lines = [
            "# System3 Multi-Timeframe Signal Consistency\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Consistency Score**: {consistency_score:.3f}\n",
            f"**Total Signals**: {len(df)}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK" if consistency_score > 0.5 else "WARN"
        details = f"Consistency score: {consistency_score:.3f} ({len(df)} signals)"

        return {
            "phase": 262,
            "status": status,
            "details": details,
            "outputs": {
                "consistency_score": float(consistency_score),
                "total_signals": len(df),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 262,
            "status": "ERROR",
            "details": f"Phase 262 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase262()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
