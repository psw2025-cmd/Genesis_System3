"""
System3 Phase 277 - Entry Timing Optimizer

Optimizes entry timing based on historical performance patterns.
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
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_entry_timing_optimizer.md"


def run_phase277(**kwargs) -> Dict[str, Any]:
    """Run Phase 277: Entry Timing Optimizer."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 277,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"optimal_hours": [], "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 277,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"optimal_hours": [], "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 277,
                "status": "WARN",
                "details": "No data or missing timestamp",
                "outputs": {"optimal_hours": [], "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Parse timestamps and extract hour
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"])
        df["hour"] = df["ts"].dt.hour

        # Find PnL column
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 277,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"optimal_hours": [], "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Find optimal hours (hours with positive average PnL)
        hourly_pnl = df.groupby("hour")[pnl_col].mean()
        optimal_hours = hourly_pnl[hourly_pnl > 0].index.tolist()

        # Generate report
        report_lines = [
            "# System3 Entry Timing Optimizer\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Optimal Hours**: {', '.join(map(str, optimal_hours))}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK" if optimal_hours else "WARN"
        details = f"Found {len(optimal_hours)} optimal hours"

        return {
            "phase": 277,
            "status": status,
            "details": details,
            "outputs": {
                "optimal_hours": optimal_hours,
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 277,
            "status": "ERROR",
            "details": f"Phase 277 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase277()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
