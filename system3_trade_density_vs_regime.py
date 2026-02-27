"""
System3 Phase 246 - Trade Density vs Volatility Regime
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
META_DIR = PROJECT_ROOT / "storage" / "meta"
ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"
REGIMES_CSV = META_DIR / "system3_vol_regimes.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_trade_density_vs_regime.md"


def run_phase246() -> dict:
    """Run Phase 246: Trade Density vs Volatility Regime."""
    if not ORDERS_CSV.exists():
        return {
            "phase": 246,
            "status": "WARN",
            "details": "Orders CSV not found",
            "outputs": {},
            "errors": []
        }
    
    try:
        orders_df = pd.read_csv(ORDERS_CSV, engine="python", on_bad_lines="skip")
        
        if REGIMES_CSV.exists():
            regimes_df = pd.read_csv(REGIMES_CSV, engine="python", on_bad_lines="skip")
            # Join on date + underlying
            if "ts" in orders_df.columns:
                orders_df["date"] = pd.to_datetime(orders_df["ts"], errors="coerce").dt.date
            if "date" in orders_df.columns and "date" in regimes_df.columns:
                merged = orders_df.merge(regimes_df, on=["date", "underlying"], how="left")
            else:
                merged = orders_df
        else:
            merged = orders_df
        
        # Group by regime
        report_lines = [
            "# System3 Trade Density vs Volatility Regime\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Trades by Regime\n",
            "| Regime | Trade Count |\n",
            "|--------|------------|\n"
        ]
        
        if "regime" in merged.columns:
            for regime, group in merged.groupby("regime"):
                report_lines.append(f"| {regime} | {len(group)} |\n")
        else:
            report_lines.append("| N/A | Regime data not available |\n")
        
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)
        
        return {
            "phase": 246,
            "status": "OK",
            "details": "Trade density report generated",
            "outputs": {
                "report_file": str(REPORT_PATH)
            },
            "errors": []
        }
        
    except Exception as e:
        return {
            "phase": 246,
            "status": "ERROR",
            "details": f"Error: {e}",
            "outputs": {},
            "errors": [str(e)]
        }


if __name__ == "__main__":
    result = run_phase246()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

