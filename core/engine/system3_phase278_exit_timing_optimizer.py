"""
System3 Phase 278 - Exit Timing Optimizer

Optimizes exit timing based on historical performance.
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
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_exit_timing_optimizer.md"


def run_phase278(**kwargs) -> Dict[str, Any]:
    """Run Phase 278: Exit Timing Optimizer."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 278,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"optimal_hold_time": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 278,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"optimal_hold_time": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 278,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"optimal_hold_time": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Find PnL columns (different timeframes)
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 278,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"optimal_hold_time": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Find optimal hold time (timeframe with best average PnL)
        best_timeframe = None
        best_avg_pnl = -float("inf")

        for pnl_col in pnl_cols:
            avg_pnl = df[pnl_col].mean()
            if avg_pnl > best_avg_pnl:
                best_avg_pnl = avg_pnl
                best_timeframe = pnl_col

        # Extract timeframe number (e.g., "pnl_1" -> 1)
        optimal_hold_time = 0
        if best_timeframe:
            try:
                optimal_hold_time = int(best_timeframe.split("_")[-1])
            except:
                pass

        # Generate report
        report_lines = [
            "# System3 Exit Timing Optimizer\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Optimal Hold Time**: {optimal_hold_time} minutes\n",
            f"**Best Average PnL**: {best_avg_pnl:.2f}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Optimal hold time: {optimal_hold_time} minutes"

        return {
            "phase": 278,
            "status": status,
            "details": details,
            "outputs": {
                "optimal_hold_time": optimal_hold_time,
                "best_avg_pnl": float(best_avg_pnl),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 278,
            "status": "ERROR",
            "details": f"Phase 278 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase278()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
