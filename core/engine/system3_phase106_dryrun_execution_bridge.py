"""
System3 Phase 106 - Live Execution DRY-RUN Bridge

Wire ledger to existing DRY RUN executor without real Angel calls.
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
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "phase106_dryrun_execution.log"


def simulate_fill_price(entry_price: float) -> float:
    """
    Simulate fill price (slight variation from entry).

    In real scenario, this would come from market data or DRY RUN executor.
    """
    import random

    # Simulate small slippage (-0.1% to +0.1%)
    slippage = random.uniform(-0.001, 0.001)
    return entry_price * (1 + slippage)


def run_phase106(**kwargs) -> dict:
    """
    Execute PLANNED orders in DRY_RUN mode.

    Returns:
        dict: {
            "phase": 106,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    orders_processed = 0
    orders_filled_dryrun = 0

    try:
        # Read ledger
        if not LEDGER_CSV.exists():
            return {
                "phase": 106,
                "status": "ERROR",
                "details": f"Ledger not found: {LEDGER_CSV}",
                "outputs": {
                    "orders_processed": 0,
                    "orders_filled_dryrun": 0,
                },
                "errors": [f"Ledger not found: {LEDGER_CSV}"],
            }

        df = pd.read_csv(LEDGER_CSV)
        if df.empty:
            return {
                "phase": 106,
                "status": "OK",
                "details": "Ledger is empty, no orders to process",
                "outputs": {
                    "orders_processed": 0,
                    "orders_filled_dryrun": 0,
                },
                "errors": [],
            }

        # Filter PLANNED orders
        planned_orders = df[df["status"] == "PLANNED"].copy()

        if planned_orders.empty:
            return {
                "phase": 106,
                "status": "OK",
                "details": "No PLANNED orders to process",
                "outputs": {
                    "orders_processed": 0,
                    "orders_filled_dryrun": 0,
                },
                "errors": [],
            }

        orders_processed = len(planned_orders)

        # Process each PLANNED order
        for idx, row in planned_orders.iterrows():
            try:
                # Simulate fill using DRY_RUN logic
                entry_price = float(row.get("entry_price", 0))
                if entry_price <= 0:
                    # Use simulated price if entry_price not set
                    entry_price = 100.0  # Placeholder

                # Simulate fill price
                fill_price = simulate_fill_price(entry_price)

                # Update ledger row
                df.at[idx, "status"] = "FILLED"
                df.at[idx, "broker_status"] = "DRY_RUN_FILLED"
                df.at[idx, "entry_price"] = fill_price
                df.at[idx, "last_update_ts"] = datetime.now().isoformat()

                orders_filled_dryrun += 1

                # Log
                log_msg = (
                    f"[{datetime.now().isoformat()}] DRY_RUN FILLED: "
                    f"{row.get('underlying')} {row.get('strike')} {row.get('option_type')} "
                    f"@ {fill_price:.2f} (local_order_id: {row.get('local_order_id')})\n"
                )
                with LOG_FILE.open("a", encoding="utf-8") as f:
                    f.write(log_msg)

            except Exception as e:
                error_msg = f"Error processing order {row.get('local_order_id', 'unknown')}: {e}"
                errors.append(error_msg)
                with LOG_FILE.open("a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")

        # Save updated ledger
        if orders_filled_dryrun > 0:
            df.to_csv(LEDGER_CSV, index=False)

        status = "OK" if not errors else "ERROR"
        details = f"Processed {orders_processed} PLANNED orders, {orders_filled_dryrun} filled (DRY_RUN)"

        return {
            "phase": 106,
            "status": status,
            "details": details,
            "outputs": {
                "orders_processed": orders_processed,
                "orders_filled_dryrun": orders_filled_dryrun,
                "ledger_path": str(LEDGER_CSV),
            },
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Phase 106 failed: {e}"
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")

        return {
            "phase": 106,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {
                "orders_processed": orders_processed,
                "orders_filled_dryrun": orders_filled_dryrun,
            },
            "errors": [error_msg],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 106 - DRY-RUN EXECUTION BRIDGE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase106()

    print(f"Phase106: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nOrders processed: {result['outputs']['orders_processed']}")
    print(f"Orders filled (DRY_RUN): {result['outputs']['orders_filled_dryrun']}")
    print(f"Log: {LOG_FILE}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
