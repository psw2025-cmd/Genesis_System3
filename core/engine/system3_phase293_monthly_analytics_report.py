"""
System3 Phase 293 - Monthly Analytics Report

Generates comprehensive monthly analytics report.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / f"system3_monthly_analytics_{datetime.now().strftime('%Y%m')}.md"


def run_phase293(**kwargs) -> Dict[str, Any]:
    """Run Phase 293: Monthly Analytics Report."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 293,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 293,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 293,
                "status": "WARN",
                "details": "No data or missing timestamp",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Filter to current month
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        current_month = datetime.now().replace(day=1)
        df_month = df[df["ts"] >= current_month]

        if df_month.empty:
            return {
                "phase": 293,
                "status": "WARN",
                "details": "No data in current month",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate monthly metrics
        pnl_cols = [c for c in df_month.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 293,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        monthly_pnl = df_month[pnl_col].sum()
        monthly_win_rate = (df_month[pnl_col] > 0).sum() / len(df_month) * 100 if len(df_month) > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Monthly Analytics Report\n",
            f"**Month**: {datetime.now().strftime('%Y-%m')}\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Monthly Summary\n",
            f"**Total Trades**: {len(df_month)}\n",
            f"**Monthly PnL**: {monthly_pnl:.2f}\n",
            f"**Win Rate**: {monthly_win_rate:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Monthly analytics: {len(df_month)} trades, PnL: {monthly_pnl:.2f}"

        return {
            "phase": 293,
            "status": status,
            "details": details,
            "outputs": {
                "monthly_trades": len(df_month),
                "monthly_pnl": float(monthly_pnl),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 293,
            "status": "ERROR",
            "details": f"Phase 293 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase293()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
