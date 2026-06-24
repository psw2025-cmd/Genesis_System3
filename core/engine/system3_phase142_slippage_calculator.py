"""
System3 Phase 142 - DRY-RUN Slippage Calculator (Ledger)

Calculates slippage from DRY-RUN ledger fills.
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
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
SPREAD_METRICS_CSV = STORAGE_ULTRA / "phase141_spread_liquidity_metrics.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase142_slippage_results.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase142_slippage_summary.md"


def run_phase142_slippage_calculator() -> Dict[str, Any]:
    """
    Calculate slippage from DRY-RUN ledger.

    Returns:
        dict: {
            "phase": 142,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load ledger
        df_ledger = pd.DataFrame()
        if LEDGER_CSV.exists():
            try:
                df_ledger = pd.read_csv(LEDGER_CSV)
                # Filter FILLED orders only
                df_ledger = df_ledger[df_ledger["status"] == "FILLED"]
            except Exception as e:
                errors.append(f"Error reading ledger: {e}")

        # Load spread metrics (optional)
        df_spread = pd.DataFrame()
        if SPREAD_METRICS_CSV.exists():
            try:
                df_spread = pd.read_csv(SPREAD_METRICS_CSV)
            except Exception:
                pass  # Optional

        if df_ledger.empty:
            # Create empty result
            df_result = pd.DataFrame(
                columns=[
                    "local_order_id",
                    "underlying",
                    "strike",
                    "option_type",
                    "entry_price",
                    "ideal_fill_price",
                    "slippage_amount",
                    "slippage_percent",
                ]
            )
            status = "OK"
            details = "No filled orders in ledger, created empty slippage file"
        else:
            # Calculate slippage
            slippage_rows = []

            for _, row in df_ledger.iterrows():
                local_order_id = row.get("local_order_id", "")
                underlying = row.get("underlying", "")
                strike = row.get("strike", 0)
                option_type = row.get("option_type", "")
                entry_price = float(row.get("entry_price", 0))

                if entry_price <= 0:
                    continue

                # Ideal fill = entry_price (assuming no slippage in ideal case)
                # For DRY-RUN, we simulate slight slippage, so ideal is slightly different
                # Use a simple heuristic: ideal = entry_price * 0.999 (0.1% better)
                ideal_fill_price = entry_price * 0.999

                # Slippage = actual - ideal
                slippage_amount = entry_price - ideal_fill_price
                slippage_percent = (slippage_amount / ideal_fill_price) * 100 if ideal_fill_price > 0 else 0

                slippage_rows.append(
                    {
                        "local_order_id": local_order_id,
                        "underlying": underlying,
                        "strike": strike,
                        "option_type": option_type,
                        "entry_price": entry_price,
                        "ideal_fill_price": round(ideal_fill_price, 2),
                        "slippage_amount": round(slippage_amount, 2),
                        "slippage_percent": round(slippage_percent, 3),
                    }
                )

            df_result = pd.DataFrame(slippage_rows)

            # Summarize by underlying
            summary_by_underlying = {}
            if not df_result.empty:
                for underlying in df_result["underlying"].unique():
                    underlying_data = df_result[df_result["underlying"] == underlying]
                    summary_by_underlying[underlying] = {
                        "avg_slippage": float(underlying_data["slippage_percent"].mean()),
                        "worst_slippage": float(underlying_data["slippage_percent"].max()),
                        "trade_count": len(underlying_data),
                    }

            status = "OK"
            details = f"Slippage calculated: {len(df_result)} trades"

        # Save CSV
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)

        # Generate MD summary
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Slippage Summary\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if summary_by_underlying:
                f.write("## Per-Underlying Slippage Summary\n\n")
                f.write("| Underlying | Avg Slippage % | Worst Slippage % | Trades |\n")
                f.write("|------------|----------------|------------------|--------|\n")
                for underlying, summary in summary_by_underlying.items():
                    f.write(
                        f"| {underlying} | {summary['avg_slippage']:.3f}% | {summary['worst_slippage']:.3f}% | {summary['trade_count']} |\n"
                    )
            else:
                f.write("## Summary\n\n")
                f.write("No filled trades available for slippage analysis.\n")

        return {
            "phase": 142,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "trade_count": len(df_result),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 142,
            "status": "ERROR",
            "details": f"Phase 142 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 142 - DRY-RUN SLIPPAGE CALCULATOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase142_slippage_calculator()

    print(f"Phase142: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nTrades analyzed: {result['outputs']['trade_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
