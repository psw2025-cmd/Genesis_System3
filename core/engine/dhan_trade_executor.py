"""
Dhan trade executor (DRY RUN).

Reads:
    storage/live/dhan_index_ai_trades_plan.csv

For each planned trade:
    - Constructs an Angel order payload (symbol, qty, side, product, etc.)
    - Logs what would be sent (no actual API call in DRY RUN mode)

Outputs:
    - storage/live/dhan_index_ai_trades_exec_log.csv
"""

import os
from datetime import datetime

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LIVE_DIR = os.path.join(PROJECT_ROOT, "storage", "live")
TRADE_PLAN_CSV = os.path.join(LIVE_DIR, "dhan_index_ai_trades_plan.csv")
EXEC_LOG_CSV = os.path.join(LIVE_DIR, "dhan_index_ai_trades_exec_log.csv")


def load_trade_plan() -> pd.DataFrame:
    """Load trade plan CSV."""
    if not os.path.exists(TRADE_PLAN_CSV):
        print(f"[EXEC] Trade plan not found: {TRADE_PLAN_CSV}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(TRADE_PLAN_CSV)
        if df.empty:
            print("[EXEC] Trade plan CSV is empty.")
        return df
    except Exception as e:
        print(f"[EXEC] Failed to read trade plan: {e}")
        return pd.DataFrame()


def build_order_payload(row: pd.Series) -> dict | None:
    """
    Map trade plan row to Angel order payload (dry-run only).

    Returns dict with order details, or None if not a valid BUY signal.
    """
    # Check for pred_label or signal column
    side = row.get("pred_label") or row.get("signal", "HOLD")
    if side not in ("BUY_CE", "BUY_PE"):
        return None

    # Basic info
    underlying = row["underlying"]
    strike = float(row["strike"])
    opt_type = "CE" if side == "BUY_CE" else "PE"
    qty = int(row.get("quantity", 1))  # default 1 lot placeholder

    # Get entry price from various possible column names
    entry_price = row.get("entry_price") or row.get("ltp_entry") or row.get("ltp", 0.0)

    payload = {
        "underlying": underlying,
        "strike": strike,
        "option_type": opt_type,
        "side": "BUY",  # all current signals are buy
        "quantity": qty,
        "entry_price": float(entry_price),
        "ts_plan": row.get("ts"),
        "mode": "DRY_RUN",
    }

    return payload


def execute_dry_run(only_new: bool = True) -> None:
    """
    Execute trades in DRY RUN mode (no real API calls).

    Args:
        only_new: If True, only execute trades that haven't been executed yet
                  (checks execution log to avoid duplicates)
    """
    df = load_trade_plan()
    if df.empty:
        print("[EXEC] No trades to execute (DRY RUN).")
        return

    # Filter out already-executed trades if only_new is True
    if only_new and os.path.exists(EXEC_LOG_CSV):
        try:
            exec_log = pd.read_csv(EXEC_LOG_CSV)
            if not exec_log.empty and "ts_plan" in exec_log.columns:
                executed_ts = set(exec_log["ts_plan"].astype(str))
                if "ts" in df.columns:
                    df = df[~df["ts"].astype(str).isin(executed_ts)]
        except Exception as e:
            print(f"[EXEC] Warning: Could not filter executed trades: {e}")

    if df.empty:
        print("[EXEC] No new trades to execute (all already executed).")
        return

    exec_rows = []
    from core.engine.dhan_trade_lifecycle_logger import (
        generate_trade_id,
        get_lifecycle_logger,
    )

    lifecycle_logger = get_lifecycle_logger()
    for _, row in df.iterrows():
        payload = build_order_payload(row)
        if payload is None:
            continue

        print(
            f"[EXEC DRY] Would send order: {payload['underlying']} {payload['strike']} {payload['option_type']} @ {payload['entry_price']:.2f}"
        )
        payload["ts_exec"] = datetime.utcnow().isoformat()
        exec_rows.append(payload)

        # Log execution event
        trade_id = generate_trade_id(
            payload["underlying"],
            payload["strike"],
            payload["option_type"],
            payload.get("ts_plan", payload["ts_exec"]),
        )
        lifecycle_logger.log_event(
            "TRADE_EXECUTED",
            trade_id=trade_id,
            underlying=payload["underlying"],
            strike=payload["strike"],
            side=payload["option_type"],
            details={"mode": "DRY_RUN", "entry_price": payload["entry_price"]},
        )

    if not exec_rows:
        print("[EXEC] No BUY_CE/BUY_PE trades found in plan.")
        return

    exec_df = pd.DataFrame(exec_rows)

    # Append to existing log if it exists
    if os.path.exists(EXEC_LOG_CSV):
        try:
            old = pd.read_csv(EXEC_LOG_CSV)
            exec_df = pd.concat([old, exec_df], ignore_index=True)
        except Exception as e:
            print(f"[EXEC] Warning: Could not read existing exec log: {e}")

    exec_df.to_csv(EXEC_LOG_CSV, index=False)
    print(f"[EXEC] DRY RUN execution log written to: {EXEC_LOG_CSV}")
    print(f"[EXEC] Total orders (DRY RUN): {len(exec_rows)}")


if __name__ == "__main__":
    print("=== ANGEL ONE TRADE EXECUTOR (DRY RUN) ===")
    execute_dry_run()
