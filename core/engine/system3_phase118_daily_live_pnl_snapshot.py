"""
System3 Phase 118 - Daily Live PnL Snapshot (Angel Only)

Summarize daily PnL from ledger.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
OUTPUT_MD = STORAGE_LIVE / "phase118_daily_pnl_snapshot.md"


def run_phase118(**kwargs) -> dict:
    """
    Generate daily PnL snapshot from ledger.

    Returns:
        dict: {
            "phase": 118,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Read ledger
        if LEDGER_CSV.exists():
            df = pd.read_csv(LEDGER_CSV)

            # Filter today's trades
            today_trades = df[df["timestamp"].astype(str).str.contains(today)]

            # Calculate PnL
            total_pnl_absolute = 0.0
            total_pnl_percent = 0.0

            if "pnl_absolute" in today_trades.columns:
                total_pnl_absolute = float(today_trades["pnl_absolute"].fillna(0).sum())

            if "pnl_percent" in today_trades.columns:
                total_pnl_percent = float(today_trades["pnl_percent"].fillna(0).sum())

            # Count trades
            total_trades = len(today_trades)
            filled_trades = len(today_trades[today_trades["status"] == "FILLED"])

            # Per-underlying breakdown
            per_underlying = {}
            if not today_trades.empty:
                for underlying, group in today_trades.groupby("underlying"):
                    underlying_pnl = (
                        float(group["pnl_absolute"].fillna(0).sum()) if "pnl_absolute" in group.columns else 0.0
                    )
                    per_underlying[underlying] = {
                        "trades": len(group),
                        "pnl_absolute": underlying_pnl,
                    }
        else:
            total_pnl_absolute = 0.0
            total_pnl_percent = 0.0
            total_trades = 0
            filled_trades = 0
            per_underlying = {}

        # Generate Markdown report
        with OUTPUT_MD.open("w", encoding="utf-8") as f:
            f.write("# System3 Daily Live PnL Snapshot\n\n")
            f.write(f"**Date**: {today}\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Total Trades**: {total_trades}\n")
            f.write(f"- **Filled Trades**: {filled_trades}\n")
            f.write(f"- **Total PnL (Absolute)**: ₹{total_pnl_absolute:.2f}\n")
            f.write(f"- **Total PnL (Percent)**: {total_pnl_percent:.2f}%\n\n")

            if per_underlying:
                f.write("## Per-Underlying Breakdown\n\n")
                f.write("| Underlying | Trades | PnL (₹) |\n")
                f.write("|------------|--------|--------|\n")
                for underlying, data in per_underlying.items():
                    f.write(f"| {underlying} | {data['trades']} | {data['pnl_absolute']:.2f} |\n")
                f.write("\n")

        status = "OK"
        details = f"Daily PnL snapshot generated: ₹{total_pnl_absolute:.2f} ({total_trades} trades)"

        return {
            "phase": 118,
            "status": status,
            "details": details,
            "outputs": {
                "snapshot_path": str(OUTPUT_MD),
                "total_trades": total_trades,
                "filled_trades": filled_trades,
                "total_pnl_absolute": round(total_pnl_absolute, 2),
                "total_pnl_percent": round(total_pnl_percent, 2),
                "per_underlying": per_underlying,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 118,
            "status": "ERROR",
            "details": f"Phase 118 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 118 - DAILY LIVE PnL SNAPSHOT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase118()

    print(f"Phase118: {result['details']}")
    if result["outputs"]:
        print(f"\nTotal trades: {result['outputs']['total_trades']}")
        print(f"Filled trades: {result['outputs']['filled_trades']}")
        print(f"Total PnL: ₹{result['outputs']['total_pnl_absolute']:.2f}")
        print(f"Snapshot: {result['outputs']['snapshot_path']}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
