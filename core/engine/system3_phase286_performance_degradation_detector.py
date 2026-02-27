"""
System3 Phase 286 - Performance Degradation Detector

Detects performance degradation over time.
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
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "monitoring"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_performance_degradation.md"


def run_phase286(**kwargs) -> Dict[str, Any]:
    """Run Phase 286: Performance Degradation Detector."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 286,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"degradation_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 286,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"degradation_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 286,
                "status": "WARN",
                "details": "No data or missing timestamp",
                "outputs": {"degradation_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Parse timestamps
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts").reset_index(drop=True)

        # Find PnL column
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols or len(df) < 20:
            return {
                "phase": 286,
                "status": "WARN",
                "details": "Insufficient data for degradation detection",
                "outputs": {"degradation_detected": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Split into early and late periods
        split_idx = len(df) // 2
        early_period = df.iloc[:split_idx]
        late_period = df.iloc[split_idx:]

        # Compare performance
        early_win_rate = (early_period[pnl_col] > 0).sum() / len(early_period) * 100 if len(early_period) > 0 else 0.0
        late_win_rate = (late_period[pnl_col] > 0).sum() / len(late_period) * 100 if len(late_period) > 0 else 0.0

        degradation_detected = late_win_rate < early_win_rate - 10.0  # 10% drop threshold

        # Generate report
        report_lines = [
            "# System3 Performance Degradation Detection\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Degradation Detected**: {degradation_detected}\n",
            f"**Early Win Rate**: {early_win_rate:.2f}%\n",
            f"**Late Win Rate**: {late_win_rate:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "WARN" if degradation_detected else "OK"
        details = "Performance degradation detected" if degradation_detected else "No degradation detected"

        return {
            "phase": 286,
            "status": status,
            "details": details,
            "outputs": {
                "degradation_detected": degradation_detected,
                "early_win_rate": float(early_win_rate),
                "late_win_rate": float(late_win_rate),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 286,
            "status": "ERROR",
            "details": f"Phase 286 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase286()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
