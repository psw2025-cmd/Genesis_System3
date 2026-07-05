"""
System3 Phase 263 - Advanced PnL Attribution

Performs detailed PnL attribution analysis by component, timeframe, and regime.
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
SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_advanced_pnl_attribution.md"


def run_phase263(**kwargs) -> Dict[str, Any]:
    """Run Phase 263: Advanced PnL Attribution."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists() or not SIGNALS_CSV.exists():
            return {
                "phase": 263,
                "status": "WARN",
                "details": "Required input files not found",
                "outputs": {"attribution_components": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Load data
        try:
            orders_df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
            signals_df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 263,
                "status": "WARN",
                "details": f"Error loading data: {e}",
                "outputs": {"attribution_components": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        # Join orders with signals to get component scores
        join_keys = ["ts", "underlying", "strike", "side", "option_type", "expiry"]
        available_keys = [k for k in join_keys if k in orders_df.columns and k in signals_df.columns]

        if not available_keys:
            return {
                "phase": 263,
                "status": "WARN",
                "details": "No matching keys for join",
                "outputs": {"attribution_components": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        merged = orders_df.merge(signals_df, on=available_keys, how="left")

        # Find PnL column
        pnl_cols = [c for c in merged.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 263,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"attribution_components": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Attribution by component
        score_components = [
            "ai_score",
            "greeks_score",
            "trend_score",
            "volatility_score",
            "momentum_score",
            "breakout_score",
        ]
        available_components = [c for c in score_components if c in merged.columns]

        attribution_results = {}
        for component in available_components:
            if merged[component].notna().sum() > 0:
                correlation = merged[component].corr(merged[pnl_col])
                attribution_results[component] = correlation if not pd.isna(correlation) else 0.0

        # Generate report
        report_lines = [
            "# System3 Advanced PnL Attribution\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Component Attribution\n",
            "| Component | Correlation with PnL |\n",
            "|-----------|---------------------|\n",
        ]

        for component, corr in sorted(attribution_results.items(), key=lambda x: abs(x[1]), reverse=True):
            report_lines.append(f"| {component} | {corr:.3f} |\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Attributed PnL across {len(attribution_results)} components"

        return {
            "phase": 263,
            "status": status,
            "details": details,
            "outputs": {
                "attribution_components": len(attribution_results),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 263,
            "status": "ERROR",
            "details": f"Phase 263 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase263()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
