"""
System3 Phase 292 - Weekly Summary Report

Generates weekly summary report aggregating daily performance.
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
REPORT_PATH = LOG_DIR / f"system3_weekly_summary_{datetime.now().strftime('%Y%W')}.md"


def run_phase292(**kwargs) -> Dict[str, Any]:
    """Run Phase 292: Weekly Summary Report."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 292,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 292,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 292,
                "status": "WARN",
                "details": "No data or missing timestamp",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Filter to last 7 days
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        week_ago = datetime.now() - timedelta(days=7)
        df_week = df[df["ts"] >= week_ago]

        if df_week.empty:
            return {
                "phase": 292,
                "status": "WARN",
                "details": "No data in last 7 days",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate weekly metrics
        pnl_cols = [c for c in df_week.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 292,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        weekly_pnl = df_week[pnl_col].sum()
        weekly_win_rate = (df_week[pnl_col] > 0).sum() / len(df_week) * 100 if len(df_week) > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Weekly Summary Report\n",
            f"**Week**: {datetime.now().strftime('%Y-W%W')}\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Weekly Summary\n",
            f"**Total Trades**: {len(df_week)}\n",
            f"**Weekly PnL**: {weekly_pnl:.2f}\n",
            f"**Win Rate**: {weekly_win_rate:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Weekly summary: {len(df_week)} trades, PnL: {weekly_pnl:.2f}"

        return {
            "phase": 292,
            "status": status,
            "details": details,
            "outputs": {
                "weekly_trades": len(df_week),
                "weekly_pnl": float(weekly_pnl),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 292,
            "status": "ERROR",
            "details": f"Phase 292 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase292()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
