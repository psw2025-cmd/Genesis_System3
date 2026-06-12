"""
System3 Phase 297 - Trade Execution Report

Generates trade execution quality report.
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
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "execution"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_trade_execution_report.md"


def run_phase297(**kwargs) -> Dict[str, Any]:
    """Run Phase 297: Trade Execution Report."""
    errors = []

    try:
        if not VIRTUAL_ORDERS_CSV.exists():
            return {
                "phase": 297,
                "status": "WARN",
                "details": "Virtual orders CSV not found",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 297,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 297,
                "status": "WARN",
                "details": "No orders for execution report",
                "outputs": {"report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate execution metrics
        total_orders = len(df)
        approved_orders = (
            len(df[df.get("approved", pd.Series([False] * len(df))) == True]) if "approved" in df.columns else 0
        )
        fill_rate = approved_orders / total_orders * 100 if total_orders > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Trade Execution Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Orders**: {total_orders}\n",
            f"**Approved Orders**: {approved_orders}\n",
            f"**Fill Rate**: {fill_rate:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Execution report: {total_orders} orders, {fill_rate:.1f}% fill rate"

        return {
            "phase": 297,
            "status": status,
            "details": details,
            "outputs": {
                "total_orders": total_orders,
                "fill_rate": float(fill_rate),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 297,
            "status": "ERROR",
            "details": f"Phase 297 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase297()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
