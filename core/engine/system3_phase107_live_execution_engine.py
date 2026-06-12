"""
System3 Phase 107 - Dhan LIVE Execution (ONE-LOT, GUARDED, OFF BY DEFAULT)

Actual real-order placement, but tightly guarded and controlled by config.
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

# Import config
try:
    from config.live_trade_config import (
        LIVE_TRADING_ENABLED,
        MAX_LIVE_TRADES_PER_DAY,
        MAX_LIVE_TRADES_PER_UNDERLYING,
        DEFAULT_LOTS_PER_TRADE,
        LIVE_ALLOWED_UNDERLYINGS,
        ANGEL_PRODUCT_TYPE,
        ANGEL_ORDER_VARIETY,
    )
except ImportError as e:
    print(f"[PH107] ERROR: Failed to import live_trade_config: {e}")
    sys.exit(1)

# Import wrapper
try:
    from core.broker.dhan_live_order_wrapper import AngelLiveOrderWrapper
except ImportError as e:
    print(f"[PH107] ERROR: Failed to import AngelLiveOrderWrapper: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "phase107_live_execution_engine.log"


def count_trades_today(df: pd.DataFrame) -> dict:
    """Count trades for today by underlying."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Filter today's trades (non-PLANNED)
    today_trades = df[(df["timestamp"].astype(str).str.contains(today)) & (df["status"] != "PLANNED")]

    total_today = len(today_trades)
    per_underlying = today_trades.groupby("underlying").size().to_dict()

    return {
        "total": total_today,
        "per_underlying": per_underlying,
    }


def run_phase107(**kwargs) -> dict:
    """
    Execute PLANNED orders in LIVE mode (if enabled).

    Returns:
        dict: {
            "phase": 107,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    orders_attempted = 0
    orders_sent = 0
    orders_failed = 0

    # CRITICAL SAFETY CHECK
    if not LIVE_TRADING_ENABLED:
        return {
            "phase": 107,
            "status": "ERROR",
            "details": "LIVE_TRADING_ENABLED=False; aborting",
            "outputs": {
                "orders_attempted": 0,
                "orders_sent": 0,
                "orders_failed": 0,
            },
            "errors": ["LIVE_TRADING_ENABLED=False"],
        }

    try:
        # Read ledger
        if not LEDGER_CSV.exists():
            return {
                "phase": 107,
                "status": "ERROR",
                "details": f"Ledger not found: {LEDGER_CSV}",
                "outputs": {
                    "orders_attempted": 0,
                    "orders_sent": 0,
                    "orders_failed": 0,
                },
                "errors": [f"Ledger not found: {LEDGER_CSV}"],
            }

        df = pd.read_csv(LEDGER_CSV)
        if df.empty:
            return {
                "phase": 107,
                "status": "OK",
                "details": "Ledger is empty, no orders to process",
                "outputs": {
                    "orders_attempted": 0,
                    "orders_sent": 0,
                    "orders_failed": 0,
                },
                "errors": [],
            }

        # Count existing trades today
        trade_counts = count_trades_today(df)

        # Filter candidate orders
        planned_orders = df[df["status"] == "PLANNED"].copy()

        # Filter by allowed underlyings
        planned_orders = planned_orders[planned_orders["underlying"].isin(LIVE_ALLOWED_UNDERLYINGS)]

        if planned_orders.empty:
            return {
                "phase": 107,
                "status": "OK",
                "details": "No PLANNED orders eligible for live execution",
                "outputs": {
                    "orders_attempted": 0,
                    "orders_sent": 0,
                    "orders_failed": 0,
                },
                "errors": [],
            }

        # Enforce caps
        # Check daily limit
        if trade_counts["total"] >= MAX_LIVE_TRADES_PER_DAY:
            return {
                "phase": 107,
                "status": "ERROR",
                "details": f"Daily trade limit reached ({trade_counts['total']}/{MAX_LIVE_TRADES_PER_DAY})",
                "outputs": {
                    "orders_attempted": 0,
                    "orders_sent": 0,
                    "orders_failed": 0,
                },
                "errors": [f"Daily limit reached: {trade_counts['total']}/{MAX_LIVE_TRADES_PER_DAY}"],
            }

        # Initialize wrapper (DRY_RUN mode by default)
        wrapper = AngelLiveOrderWrapper()

        # Process each candidate
        for idx, row in planned_orders.iterrows():
            # Check per-underlying limit
            underlying = row.get("underlying")
            underlying_count = trade_counts["per_underlying"].get(underlying, 0)

            if underlying_count >= MAX_LIVE_TRADES_PER_UNDERLYING:
                continue  # Skip this underlying

            # Check daily limit again (may have changed)
            if trade_counts["total"] >= MAX_LIVE_TRADES_PER_DAY:
                break  # Stop processing

            orders_attempted += 1

            try:
                # Build order parameters
                symbol = str(row.get("symbol", ""))
                qty = int(row.get("qty", DEFAULT_LOTS_PER_TRADE))
                side = str(row.get("side", "BUY"))

                # Place order via wrapper
                result = wrapper.place_market_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    product_type=ANGEL_PRODUCT_TYPE,
                    variety=ANGEL_ORDER_VARIETY,
                )

                if result.get("status") == "OK":
                    # Update ledger
                    df.at[idx, "status"] = "SENT"
                    df.at[idx, "broker_order_id"] = result.get("broker_order_id")
                    df.at[idx, "broker_status"] = "SENT"
                    df.at[idx, "last_update_ts"] = datetime.now().isoformat()

                    orders_sent += 1
                    trade_counts["total"] += 1
                    trade_counts["per_underlying"][underlying] = trade_counts["per_underlying"].get(underlying, 0) + 1

                    log_msg = (
                        f"[{datetime.now().isoformat()}] LIVE ORDER SENT: "
                        f"{underlying} {row.get('strike')} {row.get('option_type')} "
                        f"broker_order_id={result.get('broker_order_id')}\n"
                    )
                else:
                    # Order failed
                    df.at[idx, "status"] = "ERROR"
                    df.at[idx, "broker_status"] = "FAILED"
                    df.at[idx, "last_update_ts"] = datetime.now().isoformat()
                    df.at[idx, "notes"] = f"Order failed: {result.get('error', 'Unknown error')}"

                    orders_failed += 1
                    errors.append(f"Order {row.get('local_order_id')} failed: {result.get('error')}")

                    log_msg = (
                        f"[{datetime.now().isoformat()}] LIVE ORDER FAILED: "
                        f"{underlying} {row.get('strike')} {row.get('option_type')} "
                        f"error={result.get('error')}\n"
                    )

                # Log
                with LOG_FILE.open("a", encoding="utf-8") as f:
                    f.write(log_msg)

            except Exception as e:
                orders_failed += 1
                error_msg = f"Error processing order {row.get('local_order_id', 'unknown')}: {e}"
                errors.append(error_msg)

                df.at[idx, "status"] = "ERROR"
                df.at[idx, "broker_status"] = "FAILED"
                df.at[idx, "last_update_ts"] = datetime.now().isoformat()
                df.at[idx, "notes"] = f"Exception: {str(e)}"

                with LOG_FILE.open("a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")

        # Save updated ledger
        if orders_attempted > 0:
            df.to_csv(LEDGER_CSV, index=False)

        status = "OK" if not errors else "ERROR"
        details = f"Attempted {orders_attempted} orders, " f"sent {orders_sent}, failed {orders_failed}"

        return {
            "phase": 107,
            "status": status,
            "details": details,
            "outputs": {
                "orders_attempted": orders_attempted,
                "orders_sent": orders_sent,
                "orders_failed": orders_failed,
                "ledger_path": str(LEDGER_CSV),
            },
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Phase 107 failed: {e}"
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] ERROR: {error_msg}\n")

        return {
            "phase": 107,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {
                "orders_attempted": orders_attempted,
                "orders_sent": orders_sent,
                "orders_failed": orders_failed,
            },
            "errors": [error_msg],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 107 - LIVE EXECUTION ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase107()

    print(f"Phase107: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nOrders attempted: {result['outputs']['orders_attempted']}")
    print(f"Orders sent: {result['outputs']['orders_sent']}")
    print(f"Orders failed: {result['outputs']['orders_failed']}")
    print(f"Log: {LOG_FILE}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
