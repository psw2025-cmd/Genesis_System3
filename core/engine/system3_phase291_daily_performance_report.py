"""
System3 Phase 291 - Daily Performance Report

Generates comprehensive daily performance report.
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

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / f"system3_daily_performance_{datetime.now().strftime('%Y%m%d')}.md"


def run_phase291(**kwargs) -> Dict[str, Any]:
    """Run Phase 291: Daily Performance Report."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 291,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 291,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 291,
                "status": "WARN",
                "details": "No data for daily report",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate daily metrics
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 291,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        total_pnl = df[pnl_col].sum()
        win_rate = (df[pnl_col] > 0).sum() / len(df) * 100 if len(df) > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Daily Performance Report\n",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Summary\n",
            f"**Total Trades**: {len(df)}\n",
            f"**Total PnL**: {total_pnl:.2f}\n",
            f"**Win Rate**: {win_rate:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Daily report: {len(df)} trades, PnL: {total_pnl:.2f}"

        return {
            "phase": 291,
            "status": status,
            "details": details,
            "outputs": {
                "total_trades": len(df),
                "total_pnl": float(total_pnl),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 291,
            "status": "ERROR",
            "details": f"Phase 291 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase291()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
