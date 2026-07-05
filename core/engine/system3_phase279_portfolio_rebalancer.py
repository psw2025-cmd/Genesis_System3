"""
System3 Phase 279 - Portfolio Rebalancer

Rebalances portfolio positions based on risk and performance.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders.csv"
REBALANCE_JSON = STORAGE_META / "system3_portfolio_rebalance.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_portfolio_rebalance.md"


def run_phase279(**kwargs) -> Dict[str, Any]:
    """Run Phase 279: Portfolio Rebalancer."""
    errors = []

    try:
        if not VIRTUAL_ORDERS_CSV.exists():
            return {
                "phase": 279,
                "status": "WARN",
                "details": "Virtual orders CSV not found",
                "outputs": {"rebalanced": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 279,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"rebalanced": False, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 279,
                "status": "WARN",
                "details": "No positions to rebalance",
                "outputs": {"rebalanced": False, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate current allocation by underlying
        if "underlying" in df.columns:
            allocation = df["underlying"].value_counts(normalize=True).to_dict()
        else:
            allocation = {}

        # Generate rebalance recommendations (equalize allocation)
        rebalance_plan = {
            "current_allocation": allocation,
            "target_allocation": {k: 1.0 / len(allocation) if allocation else 0.0 for k in allocation.keys()},
            "rebalance_needed": len(allocation) > 1,
            "generated": datetime.now().isoformat(),
        }

        # Save rebalance plan
        with REBALANCE_JSON.open("w", encoding="utf-8") as f:
            json.dump(rebalance_plan, f, indent=2)

        # Generate report
        report_lines = [
            "# System3 Portfolio Rebalancer\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Rebalance Needed**: {rebalance_plan['rebalance_needed']}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Rebalance plan generated for {len(allocation)} underlyings"

        return {
            "phase": 279,
            "status": status,
            "details": details,
            "outputs": {
                "rebalanced": rebalance_plan["rebalance_needed"],
                "underlyings": len(allocation),
                "rebalance_file": str(REBALANCE_JSON),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 279,
            "status": "ERROR",
            "details": f"Phase 279 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase279()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
