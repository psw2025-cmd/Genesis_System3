"""
System3 Phase 282 - Anomaly Detector

Detects anomalies in signals, PnL, and system behavior.
"""

import sys
import pandas as pd
import numpy as np
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
REPORT_PATH = LOG_DIR / "system3_anomaly_detection.md"


def run_phase282(**kwargs) -> Dict[str, Any]:
    """Run Phase 282: Anomaly Detector."""
    errors = []
    anomalies = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 282,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"anomalies_detected": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 282,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"anomalies_detected": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 282,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"anomalies_detected": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Detect anomalies in final_score
        if "final_score" in df.columns:
            scores = df["final_score"].dropna()
            if len(scores) > 0:
                mean_score = scores.mean()
                std_score = scores.std()

                # Detect outliers (>3 standard deviations)
                outliers = scores[abs(scores - mean_score) > 3 * std_score]
                if len(outliers) > 0:
                    anomalies.append(f"{len(outliers)} score outliers detected")

        # Detect anomalies in signal distribution
        if "pred_label" in df.columns:
            label_counts = df["pred_label"].value_counts()
            if len(label_counts) > 0:
                # Check if all signals are HOLD (anomaly)
                if "HOLD" in label_counts and label_counts["HOLD"] == len(df):
                    anomalies.append("All signals are HOLD (potential issue)")

        # Generate report
        report_lines = [
            "# System3 Anomaly Detection\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Anomalies Detected**: {len(anomalies)}\n",
        ]

        if anomalies:
            report_lines.append("\n## Detected Anomalies\n")
            for anomaly in anomalies:
                report_lines.append(f"- ⚠️ {anomaly}\n")
        else:
            report_lines.append("\n✅ No anomalies detected\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "WARN" if anomalies else "OK"
        details = f"Detected {len(anomalies)} anomalies" if anomalies else "No anomalies detected"

        return {
            "phase": 282,
            "status": status,
            "details": details,
            "outputs": {
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 282,
            "status": "ERROR",
            "details": f"Phase 282 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase282()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
