"""
System3 Phase 268 - Sharpe Ratio Calculator

Calculates Sharpe ratio and other risk-adjusted return metrics.
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

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_sharpe_ratio.md"


def run_phase268(**kwargs) -> Dict[str, Any]:
    """Run Phase 268: Sharpe Ratio Calculator."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 268,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"sharpe_ratio": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 268,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"sharpe_ratio": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 268,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"sharpe_ratio": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate Sharpe ratio
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 268,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"sharpe_ratio": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]
        returns = df[pnl_col].dropna()

        if len(returns) < 2:
            return {
                "phase": 268,
                "status": "WARN",
                "details": "Insufficient data for Sharpe ratio",
                "outputs": {"sharpe_ratio": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        mean_return = returns.mean()
        std_return = returns.std()
        sharpe_ratio = (mean_return / std_return) if std_return > 0 else 0.0

        # Annualize (assuming daily returns, 252 trading days)
        sharpe_annualized = sharpe_ratio * np.sqrt(252) if sharpe_ratio != 0 else 0.0

        # Generate report
        report_lines = [
            "# System3 Sharpe Ratio Analysis\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Sharpe Ratio (Daily)**: {sharpe_ratio:.3f}\n",
            f"**Sharpe Ratio (Annualized)**: {sharpe_annualized:.3f}\n",
            f"**Mean Return**: {mean_return:.3f}\n",
            f"**Std Return**: {std_return:.3f}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Sharpe ratio (annualized): {sharpe_annualized:.3f}"

        return {
            "phase": 268,
            "status": status,
            "details": details,
            "outputs": {
                "sharpe_ratio": float(sharpe_ratio),
                "sharpe_annualized": float(sharpe_annualized),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 268,
            "status": "ERROR",
            "details": f"Phase 268 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase268()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
