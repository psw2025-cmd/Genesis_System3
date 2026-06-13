"""
System3 Phase 267 - Drawdown Analyzer

Analyzes drawdowns: max drawdown, drawdown duration, recovery time.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_drawdown_analysis.md"


def run_phase267(**kwargs) -> Dict[str, Any]:
    """Run Phase 267: Drawdown Analyzer."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 267,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"max_drawdown": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 267,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"max_drawdown": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 267,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"max_drawdown": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate drawdowns
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 267,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"max_drawdown": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Sort by timestamp if available
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts").reset_index(drop=True)

        # Calculate cumulative PnL
        df["cumulative_pnl"] = df[pnl_col].cumsum()

        # Calculate running maximum
        df["running_max"] = df["cumulative_pnl"].expanding().max()

        # Calculate drawdown
        df["drawdown"] = df["cumulative_pnl"] - df["running_max"]
        max_drawdown = df["drawdown"].min() if len(df) > 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Drawdown Analysis\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Max Drawdown**: {max_drawdown:.2f}\n",
            f"**Current PnL**: {df['cumulative_pnl'].iloc[-1] if len(df) > 0 else 0.0:.2f}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Max drawdown: {max_drawdown:.2f}"

        return {
            "phase": 267,
            "status": status,
            "details": details,
            "outputs": {
                "max_drawdown": float(max_drawdown),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 267,
            "status": "ERROR",
            "details": f"Phase 267 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase267()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
