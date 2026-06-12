"""
System3 Phase 270 - Regime Performance Comparison

Compares performance across different volatility regimes.
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
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"
REGIMES_CSV = STORAGE_META / "system3_vol_regimes.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_regime_performance_comparison.md"


def run_phase270(**kwargs) -> Dict[str, Any]:
    """Run Phase 270: Regime Performance Comparison."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 270,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"regimes_compared": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            orders_df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 270,
                "status": "WARN",
                "details": f"Error loading orders: {e}",
                "outputs": {"regimes_compared": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if orders_df.empty:
            return {
                "phase": 270,
                "status": "WARN",
                "details": "No orders to analyze",
                "outputs": {"regimes_compared": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Load regimes if available
        regimes_df = None
        if REGIMES_CSV.exists():
            try:
                regimes_df = pd.read_csv(REGIMES_CSV, engine="python", on_bad_lines="skip")
            except Exception:
                pass

        # Extract date from timestamp
        if "ts" in orders_df.columns:
            orders_df["ts"] = pd.to_datetime(orders_df["ts"], errors="coerce")
            orders_df["date"] = orders_df["ts"].dt.date

        # Join with regimes if available
        if regimes_df is not None and "date" in orders_df.columns and "date" in regimes_df.columns:
            regimes_df["date"] = pd.to_datetime(regimes_df["date"], errors="coerce").dt.date
            merged = orders_df.merge(regimes_df, on=["date", "underlying"], how="left")
        else:
            merged = orders_df
            merged["regime"] = "UNKNOWN"

        # Find PnL column
        pnl_cols = [c for c in merged.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 270,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"regimes_compared": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Compare performance by regime
        regime_stats = []
        if "regime" in merged.columns:
            for regime in merged["regime"].unique():
                regime_data = merged[merged["regime"] == regime]
                if len(regime_data) > 0:
                    total_pnl = regime_data[pnl_col].sum()
                    avg_pnl = regime_data[pnl_col].mean()
                    wins = (regime_data[pnl_col] > 0).sum()
                    win_rate = (wins / len(regime_data) * 100) if len(regime_data) > 0 else 0.0
                    regime_stats.append(
                        {
                            "regime": regime,
                            "trades": len(regime_data),
                            "total_pnl": total_pnl,
                            "avg_pnl": avg_pnl,
                            "win_rate": win_rate,
                        }
                    )

        # Generate report
        report_lines = [
            "# System3 Regime Performance Comparison\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Performance by Regime\n",
            "| Regime | Trades | Total PnL | Avg PnL | Win Rate |\n",
            "|--------|--------|-----------|----------|----------|\n",
        ]

        for stat in regime_stats:
            report_lines.append(
                f"| {stat['regime']} | {stat['trades']} | {stat['total_pnl']:.2f} | "
                f"{stat['avg_pnl']:.2f} | {stat['win_rate']:.2f}% |\n"
            )

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK" if regime_stats else "WARN"
        details = f"Compared {len(regime_stats)} regimes"

        return {
            "phase": 270,
            "status": status,
            "details": details,
            "outputs": {
                "regimes_compared": len(regime_stats),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 270,
            "status": "ERROR",
            "details": f"Phase 270 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase270()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
