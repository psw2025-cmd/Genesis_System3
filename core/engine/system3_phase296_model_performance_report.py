"""
System3 Phase 296 - Model Performance Report

Generates ML model performance report.
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
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_model_performance_report.md"


def run_phase296(**kwargs) -> Dict[str, Any]:
    """Run Phase 296: Model Performance Report."""
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 296,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip", nrows=1000)
        except Exception as e:
            return {
                "phase": 296,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 296,
                "status": "WARN",
                "details": "No data for model report",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate model metrics
        model_metrics = {}

        if "ai_score" in df.columns:
            ai_numeric = pd.to_numeric(df["ai_score"], errors="coerce")
            if ai_numeric.notna().any():
                model_metrics["ai_score_mean"] = float(ai_numeric.mean())
                model_metrics["ai_score_std"] = float(ai_numeric.std())

        if "pred_label" in df.columns:
            try:
                label_dist = df["pred_label"].value_counts().to_dict()
                model_metrics["label_distribution"] = {str(k): int(v) for k, v in label_dist.items()}
            except Exception:
                model_metrics["label_distribution"] = {}

        # Generate report
        report_lines = [
            "# System3 Model Performance Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Model Metrics\n",
        ]

        for metric, value in model_metrics.items():
            if isinstance(value, dict):
                report_lines.append(f"**{metric}**:\n")
                for k, v in value.items():
                    try:
                        report_lines.append(f"- {k}: {v}\n")
                    except Exception:
                        report_lines.append(f"- {k}: {repr(v)}\n")
            elif value is None or (isinstance(value, float) and pd.isna(value)):
                report_lines.append(f"**{metric}**: N/A\n")
            else:
                try:
                    report_lines.append(f"**{metric}**: {float(value):.3f}\n")
                except (TypeError, ValueError):
                    report_lines.append(f"**{metric}**: {value}\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Model performance report: {len(model_metrics)} metrics"

        return {
            "phase": 296,
            "status": status,
            "details": details,
            "outputs": {
                "metrics_count": len(model_metrics),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 296,
            "status": "ERROR",
            "details": f"Phase 296 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase296()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
