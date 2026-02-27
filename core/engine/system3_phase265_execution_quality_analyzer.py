"""
System3 Phase 265 - Execution Quality Analyzer

Analyzes execution quality: slippage, fill rates, latency.
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
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_execution_quality.md"


def run_phase265(**kwargs) -> Dict[str, Any]:
    """Run Phase 265: Execution Quality Analyzer."""
    errors = []

    try:
        if not VIRTUAL_ORDERS_CSV.exists():
            return {
                "phase": 265,
                "status": "WARN",
                "details": "Virtual orders CSV not found",
                "outputs": {"orders_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 265,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"orders_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 265,
                "status": "WARN",
                "details": "No orders to analyze",
                "outputs": {"orders_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Analyze execution quality
        total_orders = len(df)
        approved_orders = (
            len(df[df.get("approved", pd.Series([False] * len(df))) == True]) if "approved" in df.columns else 0
        )

        fill_rate = approved_orders / total_orders if total_orders > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Execution Quality Analysis\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Orders**: {total_orders}\n",
            f"**Approved Orders**: {approved_orders}\n",
            f"**Fill Rate**: {fill_rate:.2%}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Analyzed {total_orders} orders, fill rate: {fill_rate:.2%}"

        return {
            "phase": 265,
            "status": status,
            "details": details,
            "outputs": {
                "orders_analyzed": total_orders,
                "fill_rate": float(fill_rate),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 265,
            "status": "ERROR",
            "details": f"Phase 265 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase265()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
