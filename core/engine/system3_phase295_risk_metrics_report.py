"""
System3 Phase 295 - Risk Metrics Report

Generates comprehensive risk metrics report.
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

LOG_DIR = PROJECT_ROOT / "logs" / "risk"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_risk_metrics_report.md"


def run_phase295(**kwargs) -> Dict[str, Any]:
    """Run Phase 295: Risk Metrics Report."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 295,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"risk_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 295,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"risk_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 295,
                "status": "WARN",
                "details": "No data for risk report",
                "outputs": {"risk_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate risk metrics
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 295,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"risk_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        returns = df[pnl_col].dropna()

        if len(returns) < 2:
            return {
                "phase": 295,
                "status": "WARN",
                "details": "Insufficient data for risk metrics",
                "outputs": {"risk_metrics": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        volatility = returns.std()
        max_loss = returns.min()
        var_95 = np.percentile(returns, 5)  # 95% VaR

        # Generate report
        report_lines = [
            "# System3 Risk Metrics Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Risk Metrics\n",
            f"**Volatility**: {volatility:.3f}\n",
            f"**Max Loss**: {max_loss:.2f}\n",
            f"**VaR (95%)**: {var_95:.2f}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Risk metrics: Vol={volatility:.3f}, Max Loss={max_loss:.2f}"

        return {
            "phase": 295,
            "status": status,
            "details": details,
            "outputs": {
                "risk_metrics": 3,
                "volatility": float(volatility),
                "max_loss": float(max_loss),
                "var_95": float(var_95),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 295,
            "status": "ERROR",
            "details": f"Phase 295 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase295()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
