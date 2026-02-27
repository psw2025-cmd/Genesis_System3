"""
System3 Phase 261 - Portfolio Risk Analyzer

Analyzes portfolio-level risk metrics from virtual trades.
Computes position concentration, correlation risk, and overall portfolio exposure.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_portfolio_risk_analysis.md"


def run_phase261(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 261: Portfolio Risk Analyzer.

    Returns:
        dict: {
            "phase": 261,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "total_positions": int,
                "concentration_risk": float,
                "report_file": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not VIRTUAL_ORDERS_CSV.exists():
            return {
                "phase": 261,
                "status": "WARN",
                "details": "Virtual orders CSV not found",
                "outputs": {"total_positions": 0, "concentration_risk": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Load virtual orders
        try:
            df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 261,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"total_positions": 0, "concentration_risk": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 261,
                "status": "WARN",
                "details": "No virtual orders to analyze",
                "outputs": {"total_positions": 0, "concentration_risk": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Calculate portfolio metrics
        total_positions = len(df)

        # Position concentration by underlying
        if "underlying" in df.columns:
            underlying_counts = df["underlying"].value_counts()
            max_concentration = underlying_counts.max() / total_positions if total_positions > 0 else 0.0
        else:
            max_concentration = 0.0

        # Total exposure (if lots and ltp available)
        total_exposure = 0.0
        if "lots" in df.columns and "ltp" in df.columns:
            df["exposure"] = df["lots"] * df["ltp"]
            total_exposure = df["exposure"].sum()

        # Generate report
        report_lines = [
            "# System3 Portfolio Risk Analysis\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Portfolio Metrics\n",
            f"**Total Positions**: {total_positions}\n",
            f"**Max Concentration**: {max_concentration:.2%}\n",
            f"**Total Exposure**: {total_exposure:.2f}\n",
        ]

        if "underlying" in df.columns and len(underlying_counts) > 0:
            report_lines.append("\n## Position Distribution by Underlying\n")
            report_lines.append("| Underlying | Count | Percentage |\n")
            report_lines.append("|------------|-------|------------|\n")
            for underlying, count in underlying_counts.items():
                pct = (count / total_positions * 100) if total_positions > 0 else 0.0
                report_lines.append(f"| {underlying} | {count} | {pct:.2f}% |\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Analyzed {total_positions} positions, max concentration: {max_concentration:.2%}"

        return {
            "phase": 261,
            "status": status,
            "details": details,
            "outputs": {
                "total_positions": total_positions,
                "concentration_risk": max_concentration,
                "total_exposure": total_exposure,
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 261,
            "status": "ERROR",
            "details": f"Phase 261 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase261()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
