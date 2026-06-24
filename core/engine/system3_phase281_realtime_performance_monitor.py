"""
System3 Phase 281 - Real-Time Performance Monitor

Monitors real-time performance metrics during trading sessions.
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
PERFORMANCE_JSON = STORAGE_META / "system3_realtime_performance.json"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_realtime_performance.md"


def run_phase281(**kwargs) -> Dict[str, Any]:
    """Run Phase 281: Real-Time Performance Monitor."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 281,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"metrics_monitored": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 281,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"metrics_monitored": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 281,
                "status": "WARN",
                "details": "No data to monitor",
                "outputs": {"metrics_monitored": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate real-time metrics
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 281,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"metrics_monitored": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        total_pnl = df[pnl_col].sum()
        win_rate = (df[pnl_col] > 0).sum() / len(df) * 100 if len(df) > 0 else 0.0

        # Save performance snapshot
        performance_snapshot = {
            "timestamp": datetime.now().isoformat(),
            "total_pnl": float(total_pnl),
            "win_rate": float(win_rate),
            "total_trades": len(df),
        }

        with PERFORMANCE_JSON.open("w", encoding="utf-8") as f:
            json.dump(performance_snapshot, f, indent=2)

        # Generate report
        report_lines = [
            "# System3 Real-Time Performance Monitor\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total PnL**: {total_pnl:.2f}\n",
            f"**Win Rate**: {win_rate:.2f}%\n",
            f"**Total Trades**: {len(df)}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Monitoring: PnL={total_pnl:.2f}, Win Rate={win_rate:.1f}%"

        return {
            "phase": 281,
            "status": status,
            "details": details,
            "outputs": {
                "metrics_monitored": 3,
                "total_pnl": float(total_pnl),
                "win_rate": float(win_rate),
                "performance_file": str(PERFORMANCE_JSON),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 281,
            "status": "ERROR",
            "details": f"Phase 281 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase281()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
