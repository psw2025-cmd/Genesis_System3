"""
System3 Phase 269 - Win Rate by Time of Day

Analyzes win rate and performance by hour of day.
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
ENRICHED_ORDERS_CSV = STORAGE_LIVE / "dhan_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_winrate_by_time.md"


def run_phase269(**kwargs) -> Dict[str, Any]:
    """Run Phase 269: Win Rate by Time of Day."""
    errors = []

    try:
        if not ENRICHED_ORDERS_CSV.exists():
            return {
                "phase": 269,
                "status": "WARN",
                "details": "Enriched orders CSV not found",
                "outputs": {"hours_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(ENRICHED_ORDERS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 269,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"hours_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty or "ts" not in df.columns:
            return {
                "phase": 269,
                "status": "WARN",
                "details": "No data or missing timestamp",
                "outputs": {"hours_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Parse timestamps and extract hour
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"])
        df["hour"] = df["ts"].dt.hour

        # Find PnL column
        pnl_cols = [c for c in df.columns if "pnl" in c.lower()]
        if not pnl_cols:
            return {
                "phase": 269,
                "status": "WARN",
                "details": "No PnL columns found",
                "outputs": {"hours_analyzed": 0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        pnl_col = pnl_cols[0]

        # Calculate win rate by hour
        hourly_stats = []
        for hour in range(24):
            hour_data = df[df["hour"] == hour]
            if len(hour_data) > 0:
                wins = (hour_data[pnl_col] > 0).sum()
                total = len(hour_data)
                win_rate = (wins / total * 100) if total > 0 else 0.0
                avg_pnl = hour_data[pnl_col].mean()
                hourly_stats.append(
                    {
                        "hour": hour,
                        "trades": total,
                        "wins": wins,
                        "win_rate": win_rate,
                        "avg_pnl": avg_pnl,
                    }
                )

        # Generate report
        report_lines = [
            "# System3 Win Rate by Time of Day\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Hourly Statistics\n",
            "| Hour | Trades | Wins | Win Rate | Avg PnL |\n",
            "|------|--------|------|----------|----------|\n",
        ]

        for stat in hourly_stats:
            report_lines.append(
                f"| {stat['hour']:02d}:00 | {stat['trades']} | {stat['wins']} | "
                f"{stat['win_rate']:.2f}% | {stat['avg_pnl']:.2f} |\n"
            )

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Analyzed {len(hourly_stats)} hours"

        return {
            "phase": 269,
            "status": status,
            "details": details,
            "outputs": {
                "hours_analyzed": len(hourly_stats),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 269,
            "status": "ERROR",
            "details": f"Phase 269 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase269()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
