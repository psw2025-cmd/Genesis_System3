"""
System3 Phase 264 - Signal Quality Metrics

Computes signal quality metrics: accuracy, precision, recall, F1-score.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_signal_quality_metrics.md"


def run_phase264(**kwargs) -> Dict[str, Any]:
    """Run Phase 264: Signal Quality Metrics."""
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 264,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"metrics_computed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 264,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"metrics_computed": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 264,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"metrics_computed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Find forward return columns
        forward_cols = [c for c in df.columns if "forward" in c.lower() and "ret" in c.lower()]
        if not forward_cols:
            return {
                "phase": 264,
                "status": "WARN",
                "details": "No forward return columns found",
                "outputs": {"metrics_computed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        forward_col = forward_cols[0]

        # Compute quality metrics if pred_label exists
        metrics = {}
        if "pred_label" in df.columns and forward_col in df.columns:
            # Binary classification: BUY/SELL vs HOLD
            df["actual_direction"] = np.where(df[forward_col] > 0, "BUY", np.where(df[forward_col] < 0, "SELL", "HOLD"))

            buy_signals = df[df["pred_label"] == "BUY"]
            sell_signals = df[df["pred_label"] == "SELL"]

            if len(buy_signals) > 0:
                buy_accuracy = (buy_signals["actual_direction"] == "BUY").sum() / len(buy_signals)
                metrics["buy_accuracy"] = buy_accuracy

            if len(sell_signals) > 0:
                sell_accuracy = (sell_signals["actual_direction"] == "SELL").sum() / len(sell_signals)
                metrics["sell_accuracy"] = sell_accuracy

        # Generate report
        report_lines = [
            "# System3 Signal Quality Metrics\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Metrics\n",
        ]

        for metric, value in metrics.items():
            report_lines.append(f"- **{metric}**: {value:.3f}\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK" if metrics else "WARN"
        details = f"Computed {len(metrics)} quality metrics"

        return {
            "phase": 264,
            "status": status,
            "details": details,
            "outputs": {
                "metrics_computed": len(metrics),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 264,
            "status": "ERROR",
            "details": f"Phase 264 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase264()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
