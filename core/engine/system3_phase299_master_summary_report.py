"""
System3 Phase 299 - Master Summary Report

Generates master summary report aggregating all system metrics.
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
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_master_summary_report.md"


def run_phase299(**kwargs) -> Dict[str, Any]:
    """Run Phase 299: Master Summary Report."""
    errors = []

    try:
        # Collect data from various sources
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
        }

        # Load enriched orders if available
        if ENRICHED_ORDERS_CSV.exists():
            try:
                df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
                if not df.empty:
                    pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
                    if pnl_cols:
                        pnl_col = pnl_cols[0]
                        summary_data["trades"] = len(df)
                        summary_data["total_pnl"] = float(df[pnl_col].sum())
                        summary_data["win_rate"] = (
                            float((df[pnl_col] > 0).sum() / len(df) * 100) if len(df) > 0 else 0.0
                        )
            except Exception:
                pass

        # Generate report
        report_lines = [
            "# System3 Master Summary Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Overall Summary\n",
            f"**Total Trades**: {summary_data['trades']}\n",
            f"**Total PnL**: {summary_data['total_pnl']:.2f}\n",
            f"**Win Rate**: {summary_data['win_rate']:.2f}%\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Master summary: {summary_data['trades']} trades, PnL: {summary_data['total_pnl']:.2f}"

        return {
            "phase": 299,
            "status": status,
            "details": details,
            "outputs": {
                "trades": summary_data["trades"],
                "total_pnl": summary_data["total_pnl"],
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 299,
            "status": "ERROR",
            "details": f"Phase 299 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase299()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
