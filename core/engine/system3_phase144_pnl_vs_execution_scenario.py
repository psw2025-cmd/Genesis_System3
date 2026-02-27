"""
System3 Phase 144 - DRY-RUN PnL vs Execution Scenario

Recomputes PnL under different execution scenarios.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
SLIPPAGE_CSV = STORAGE_ULTRA / "phase142_slippage_results.csv"
QUALITY_CSV = STORAGE_ULTRA / "phase143_execution_quality.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase144_pnl_execution_scenarios.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase144_pnl_execution_scenarios.md"


def run_phase144_pnl_vs_execution_scenario() -> Dict[str, Any]:
    """
    Recompute PnL under different execution scenarios.

    Returns:
        dict: {
            "phase": 144,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    summary_by_underlying = {}  # Initialize to avoid reference error

    try:
        # Load ledger
        df_ledger = pd.DataFrame()
        if LEDGER_CSV.exists():
            try:
                df_ledger = pd.read_csv(LEDGER_CSV, engine="python", on_bad_lines="skip")
                # Filter FILLED orders with exit
                df_ledger = df_ledger[
                    (df_ledger["status"] == "FILLED")
                    & (df_ledger["exit_price"].notna())
                    & (df_ledger["exit_price"] != "")
                ]
            except Exception as e:
                errors.append(f"Error reading ledger: {e}")

        # Load slippage (optional)
        df_slippage = pd.DataFrame()
        if SLIPPAGE_CSV.exists():
            try:
                df_slippage = pd.read_csv(SLIPPAGE_CSV, engine="python", on_bad_lines="skip")
            except Exception:
                pass

        if df_ledger.empty:
            # Create empty result
            df_result = pd.DataFrame(
                columns=[
                    "local_order_id",
                    "underlying",
                    "entry_price",
                    "exit_price",
                    "pnl_ideal",
                    "pnl_realistic",
                    "pnl_worst",
                ]
            )
            status = "OK"
            details = "No completed trades available, created empty scenarios file"
        else:
            # Compute PnL scenarios
            scenario_rows = []

            for _, row in df_ledger.iterrows():
                local_order_id = row.get("local_order_id", "")
                underlying = row.get("underlying", "")
                entry_price = float(row.get("entry_price", 0))
                exit_price = float(row.get("exit_price", 0))
                qty = float(row.get("qty", 1))

                if entry_price <= 0 or exit_price <= 0:
                    continue

                # Get slippage for this trade (if available)
                slippage_pct = 0.0
                if not df_slippage.empty:
                    trade_slippage = df_slippage[df_slippage["local_order_id"] == local_order_id]
                    if not trade_slippage.empty:
                        slippage_pct = float(trade_slippage.iloc[0]["slippage_percent"])

                # Ideal fill: no slippage
                ideal_entry = entry_price * (1 - slippage_pct / 100) if slippage_pct > 0 else entry_price
                pnl_ideal = (exit_price - ideal_entry) * qty

                # Realistic fill: with slippage
                pnl_realistic = (exit_price - entry_price) * qty

                # Worst case: maximum slippage (assume 1% worse entry)
                worst_entry = entry_price * 1.01
                pnl_worst = (exit_price - worst_entry) * qty

                scenario_rows.append(
                    {
                        "local_order_id": local_order_id,
                        "underlying": underlying,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl_ideal": round(pnl_ideal, 2),
                        "pnl_realistic": round(pnl_realistic, 2),
                        "pnl_worst": round(pnl_worst, 2),
                    }
                )

            df_result = pd.DataFrame(scenario_rows)

            # Summarize by underlying
            summary_by_underlying = {}
            if not df_result.empty:
                for underlying in df_result["underlying"].unique():
                    underlying_data = df_result[df_result["underlying"] == underlying]
                    summary_by_underlying[underlying] = {
                        "pnl_ideal_total": float(underlying_data["pnl_ideal"].sum()),
                        "pnl_realistic_total": float(underlying_data["pnl_realistic"].sum()),
                        "pnl_worst_total": float(underlying_data["pnl_worst"].sum()),
                        "slippage_impact_pct": 0.0,
                    }
                    # Calculate impact
                    if summary_by_underlying[underlying]["pnl_ideal_total"] != 0:
                        impact = (
                            (
                                summary_by_underlying[underlying]["pnl_realistic_total"]
                                - summary_by_underlying[underlying]["pnl_ideal_total"]
                            )
                            / abs(summary_by_underlying[underlying]["pnl_ideal_total"])
                        ) * 100
                        summary_by_underlying[underlying]["slippage_impact_pct"] = round(impact, 2)

            status = "OK"
            details = f"PnL scenarios computed: {len(df_result)} trades"

        # Save CSV
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)

        # Generate MD summary
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 PnL vs Execution Scenario Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if summary_by_underlying:
                f.write("## Per-Underlying PnL Impact Summary\n\n")
                f.write("| Underlying | Ideal PnL | Realistic PnL | Worst PnL | Slippage Impact % |\n")
                f.write("|------------|-----------|--------------|-----------|-------------------|\n")
                for underlying, summary in summary_by_underlying.items():
                    f.write(
                        f"| {underlying} | ₹{summary['pnl_ideal_total']:.2f} | ₹{summary['pnl_realistic_total']:.2f} | ₹{summary['pnl_worst_total']:.2f} | {summary['slippage_impact_pct']:.2f}% |\n"
                    )
            else:
                f.write("## Summary\n\n")
                f.write("No completed trades available for PnL scenario analysis.\n")

        return {
            "phase": 144,
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
            "phase": 144,
            "status": "ERROR",
            "details": f"Phase 144 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 144 - DRY-RUN PnL vs EXECUTION SCENARIO")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase144_pnl_vs_execution_scenario()

    print(f"Phase144: {result['details']}")
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
