"""
System3 Phase 266 - Capital Efficiency Tracker

Tracks capital efficiency: ROI, capital utilization, returns per unit risk.
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
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_capital_efficiency.md"


def run_phase266(**kwargs) -> Dict[str, Any]:
    """Run Phase 266: Capital Efficiency Tracker."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 266,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"efficiency_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 266,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"efficiency_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 266,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"efficiency_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate capital efficiency metrics
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 266,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"efficiency_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        total_pnl = df[pnl_col].sum()
        avg_pnl = df[pnl_col].mean()

        # Calculate capital deployed (if lots and ltp available)
        if "lots" in df.columns and "ltp" in df.columns:
            capital_deployed = (df["lots"] * df["ltp"]).sum()
            roi = (total_pnl / capital_deployed * 100) if capital_deployed > 0 else 0.0
        else:
            capital_deployed = 0.0
            roi = 0.0

        # Generate report
        report_lines = [
            "# System3 Capital Efficiency Analysis\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total PnL**: {total_pnl:.2f}\n",
            f"**Average PnL**: {avg_pnl:.2f}\n",
            f"**Capital Deployed**: {capital_deployed:.2f}\n",
            f"**ROI**: {roi:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"ROI: {roi:.2f}%, Total PnL: {total_pnl:.2f}"

        return {
            "phase": 266,
            "status": status,
            "details": details,
            "outputs": {
                "efficiency_metrics": 4,
                "roi": float(roi),
                "total_pnl": float(total_pnl),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 266,
            "status": "ERROR",
            "details": f"Phase 266 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase266()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
