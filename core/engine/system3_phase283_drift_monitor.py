"""
System3 Phase 283 - Drift Monitor

Monitors feature drift and model performance drift over time.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "monitoring"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_drift_monitor.md"


def run_phase283(**kwargs) -> Dict[str, Any]:
    """Run Phase 283: Drift Monitor."""
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 283,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"drift_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 283,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"drift_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 283,
                "status": "WARN",
                "details": "No data or missing timestamp",
                "outputs": {"drift_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Parse timestamps
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts").reset_index(drop=True)

        # Split into early and late periods
        if len(df) < 20:
            return {
                "phase": 283,
                "status": "WARN",
                "details": "Insufficient data for drift detection",
                "outputs": {"drift_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        split_idx = len(df) // 2
        early_period = df.iloc[:split_idx]
        late_period = df.iloc[split_idx:]

        # Check for drift in final_score
        drift_detected = False
        if "final_score" in df.columns:
            early_mean = early_period["final_score"].mean()
            late_mean = late_period["final_score"].mean()
            drift_magnitude = abs(late_mean - early_mean)

            # Drift threshold: >20% change in mean
            if early_mean != 0:
                drift_pct = (drift_magnitude / abs(early_mean)) * 100
                drift_detected = drift_pct > 20.0

        # Generate report
        report_lines = [
            "# System3 Drift Monitor\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Drift Detected**: {drift_detected}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "WARN" if drift_detected else "OK"
        details = "Drift detected" if drift_detected else "No significant drift"

        return {
            "phase": 283,
            "status": status,
            "details": details,
            "outputs": {
                "drift_detected": drift_detected,
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 283,
            "status": "ERROR",
            "details": f"Phase 283 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase283()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
