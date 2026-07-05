"""
System3 Phase 104 - Trade Plan → Local Order Construction

Take rows from existing trade plan CSV and construct local ledger orders.
"""

import random
import string
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

TRADE_PLAN_CSV = STORAGE_LIVE / "dhan_index_ai_trades_plan.csv"
LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"


def generate_local_order_id(underlying: str, strike: float, option_type: str) -> str:
    """
    Generate deterministic local_order_id.

    Format: <underlying>_<strike>_<option_type>_<yyyymmddHHMMSS>_<random_suffix>
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{underlying}_{int(strike)}_{option_type}_{timestamp}_{random_suffix}"


def map_trade_plan_to_ledger(row: pd.Series) -> dict:
    """
    Map trade plan row to ledger row format.

    Args:
        row: Trade plan row from CSV

    Returns:
        dict: Ledger row data
    """
    underlying = str(row.get("underlying", ""))
    strike = float(row.get("strike", 0))
    side = str(row.get("side", ""))

    # Determine option_type from side
    if "CE" in side.upper():
        option_type = "CE"
    elif "PE" in side.upper():
        option_type = "PE"
    else:
        option_type = "CE"  # Default

    # Generate local_order_id
    local_order_id = generate_local_order_id(underlying, strike, option_type)

    # Get entry price
    entry_price = float(row.get("entry_price", 0))

    # Get target and stop loss
    target_price = float(row.get("target_price", 0))
    stop_loss_price = float(row.get("sl_price", 0)) or float(row.get("stop_loss_price", 0))

    # Build symbol (simplified - would need proper symbol construction in real scenario)
    # For now, use a placeholder
    symbol = f"{underlying}{int(strike)}{option_type}"

    # Extract expiry if available (default to current month)
    expiry = row.get("expiry", datetime.now().strftime("%Y-%m"))

    # Quantity (lots * lot_size, assume lot_size=1 for now)
    lots = 1  # DEFAULT_LOTS_PER_TRADE
    qty = lots  # Would multiply by lot_size in real scenario

    return {
        "local_order_id": local_order_id,
        "timestamp": row.get("ts", datetime.now().isoformat()),
        "underlying": underlying,
        "symbol": symbol,
        "expiry": expiry,
        "strike": strike,
        "option_type": option_type,
        "side": "BUY",  # All current signals are buy
        "lots": lots,
        "qty": qty,
        "entry_price": entry_price,
        "target_price": target_price,
        "stop_loss_price": stop_loss_price,
        "status": "PLANNED",
        "broker_order_id": None,
        "broker_status": "NOT_SENT",
        "last_update_ts": datetime.now().isoformat(),
        "pnl_absolute": None,
        "pnl_percent": None,
        "exit_price": None,
        "exit_reason": None,
        "notes": f"From trade plan: {row.get('pred_label', '')} conf={row.get('pred_confidence', 0):.2f}",
    }


def is_duplicate(ledger_df: pd.DataFrame, new_row: dict) -> bool:
    """
    Check if a trade plan row is already represented in ledger.

    Checks via combination of underlying+strike+side+timestamp.
    """
    if ledger_df.empty:
        return False

    # Check for matching combination
    mask = (
        (ledger_df["underlying"] == new_row["underlying"])
        & (ledger_df["strike"] == new_row["strike"])
        & (ledger_df["option_type"] == new_row["option_type"])
        & (ledger_df["timestamp"].astype(str).str.contains(new_row["timestamp"][:10]))  # Date match
    )

    return mask.any()


def run_phase104(**kwargs) -> dict:
    """
    Convert trade plan rows to ledger orders.

    Returns:
        dict: {
            "phase": 104,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    orders_created = 0

    try:
        # Read trade plan
        if not TRADE_PLAN_CSV.exists():
            return {
                "phase": 104,
                "status": "ERROR",
                "details": f"Trade plan not found: {TRADE_PLAN_CSV}",
                "outputs": {"orders_created": 0},
                "errors": [f"Trade plan CSV not found: {TRADE_PLAN_CSV}"],
            }

        trade_plan_df = pd.read_csv(TRADE_PLAN_CSV)
        if trade_plan_df.empty:
            return {
                "phase": 104,
                "status": "OK",
                "details": "Trade plan is empty, no orders to create",
                "outputs": {"orders_created": 0},
                "errors": [],
            }

        # Read last N rows (e.g., 50)
        last_n = min(50, len(trade_plan_df))
        recent_trades = trade_plan_df.tail(last_n)

        # Filter rows with status NEW or PENDING (if status column exists)
        # For now, process all rows that are BUY_CE or BUY_PE
        if "status" in recent_trades.columns:
            candidate_rows = recent_trades[recent_trades["status"].isin(["NEW", "PENDING"])]
        else:
            # Check pred_label or side column
            if "pred_label" in recent_trades.columns:
                candidate_rows = recent_trades[recent_trades["pred_label"].isin(["BUY_CE", "BUY_PE"])]
            elif "side" in recent_trades.columns:
                candidate_rows = recent_trades[recent_trades["side"].isin(["BUY_CE", "BUY_PE"])]
            else:
                candidate_rows = recent_trades

        if candidate_rows.empty:
            return {
                "phase": 104,
                "status": "OK",
                "details": "No new candidate trades to convert",
                "outputs": {"orders_created": 0},
                "errors": [],
            }

        # Load existing ledger
        if LEDGER_CSV.exists():
            ledger_df = pd.read_csv(LEDGER_CSV)
        else:
            # Create empty ledger with correct schema
            from core.engine.system3_phase102_order_ledger_schema import LEDGER_COLUMNS

            ledger_df = pd.DataFrame(columns=LEDGER_COLUMNS)

        # Convert each candidate row
        new_orders = []
        for _, row in candidate_rows.iterrows():
            try:
                ledger_row = map_trade_plan_to_ledger(row)

                # Check for duplicates
                if not is_duplicate(ledger_df, ledger_row):
                    new_orders.append(ledger_row)
                    orders_created += 1
            except Exception as e:
                errors.append(f"Error converting row: {e}")

        # Append new orders to ledger
        if new_orders:
            new_df = pd.DataFrame(new_orders)
            if ledger_df.empty:
                combined_df = new_df
            else:
                combined_df = pd.concat([ledger_df, new_df], ignore_index=True)

            combined_df.to_csv(LEDGER_CSV, index=False)

        status = "OK" if not errors else "ERROR"
        details = f"{orders_created} new planned orders appended to live ledger"

        return {
            "phase": 104,
            "status": status,
            "details": details,
            "outputs": {
                "orders_created": orders_created,
                "ledger_path": str(LEDGER_CSV),
                "candidates_processed": len(candidate_rows),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 104,
            "status": "ERROR",
            "details": f"Phase 104 failed: {e}",
            "outputs": {"orders_created": 0},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 104 - TRADE PLAN TO ORDERS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase104()

    print(f"Phase104: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nOrders created: {result['outputs']['orders_created']}")
    print(f"Ledger path: {result['outputs']['ledger_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
