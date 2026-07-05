"""
System3 Phase 288 - Latency Monitor

Monitors system latency: signal generation time, model inference time.
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

LOG_DIR = PROJECT_ROOT / "logs" / "monitoring"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_latency_monitor.md"


def run_phase288(**kwargs) -> Dict[str, Any]:
    """Run Phase 288: Latency Monitor."""
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 288,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"avg_latency": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip", nrows=100)
        except Exception as e:
            return {
                "phase": 288,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"avg_latency": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 288,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"avg_latency": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Estimate latency from timestamp gaps (if available)
        avg_latency = 0.0
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.dropna(subset=["ts"]).sort_values("ts")
            if len(df) > 1:
                time_diffs = df["ts"].diff().dt.total_seconds()
                avg_latency = time_diffs.mean() if len(time_diffs) > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Latency Monitor\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Average Latency**: {avg_latency:.2f} seconds\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK" if avg_latency > 0 else "WARN"
        details = f"Average latency: {avg_latency:.2f}s"

        return {
            "phase": 288,
            "status": status,
            "details": details,
            "outputs": {
                "avg_latency": float(avg_latency),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 288,
            "status": "ERROR",
            "details": f"Phase 288 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase288()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
