"""
System3 Phase 109 - Intraday Risk Guard (Hard Caps)

Before sending orders, enforce capital and drawdown limits.
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
        MAX_LIVE_TRADES_PER_DAY,
        MAX_DAILY_DRAWDOWN_RUPEES,
    )
except ImportError as e:
    print(f"[PH109] ERROR: Failed to import live_trade_config: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"


def calculate_realized_pnl(df: pd.DataFrame) -> float:
    """
    Calculate approximate realized PnL from ledger.

    Only counts rows where exit_reason is not null (closed trades).
    """
    closed_trades = df[df["exit_reason"].notna() & (df["exit_reason"] != "")]

    if closed_trades.empty:
        return 0.0

    # Sum pnl_absolute if available
    if "pnl_absolute" in closed_trades.columns:
        pnl_sum = closed_trades["pnl_absolute"].fillna(0).sum()
        return float(pnl_sum)

    # Otherwise calculate from entry/exit prices
    if "entry_price" in closed_trades.columns and "exit_price" in closed_trades.columns:
        pnl_sum = 0.0
        for _, row in closed_trades.iterrows():
            entry = float(row.get("entry_price", 0))
            exit_price = float(row.get("exit_price", 0))
            qty = float(row.get("qty", 0))

            if entry > 0 and exit_price > 0:
                # Simplified PnL calculation
                pnl = (exit_price - entry) * qty
                pnl_sum += pnl

        return pnl_sum

    return 0.0


def run_phase109(**kwargs) -> dict:
    """
    Check intraday risk limits.

    Returns:
        dict: {
            "phase": 109,
            "status": "OK" or "BLOCK",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Read ledger
        if not LEDGER_CSV.exists():
            return {
                "phase": 109,
                "status": "OK",
                "details": "Ledger not found, assuming no trades today",
                "outputs": {
                    "reason": "Ledger not found",
                    "trades_today": 0,
                    "approx_realized_pnl": 0.0,
                },
                "errors": [],
            }

        df = pd.read_csv(LEDGER_CSV)

        # Calculate today's trades (non-PLANNED)
        today = datetime.now().strftime("%Y-%m-%d")
        today_trades = df[(df["timestamp"].astype(str).str.contains(today)) & (df["status"] != "PLANNED")]

        trades_today = len(today_trades)

        # Calculate realized PnL
        approx_realized_pnl = calculate_realized_pnl(df)

        # Check limits
        reason = None

        if trades_today >= MAX_LIVE_TRADES_PER_DAY:
            reason = f"Daily trade limit reached ({trades_today}/{MAX_LIVE_TRADES_PER_DAY})"
            status = "BLOCK"
        elif approx_realized_pnl <= -MAX_DAILY_DRAWDOWN_RUPEES:
            reason = f"Daily drawdown limit reached ({approx_realized_pnl:.2f} <= -{MAX_DAILY_DRAWDOWN_RUPEES})"
            status = "BLOCK"
        else:
            status = "OK"
            reason = "All limits within bounds"

        return {
            "phase": 109,
            "status": status,
            "details": reason,
            "outputs": {
                "reason": reason,
                "trades_today": trades_today,
                "approx_realized_pnl": round(approx_realized_pnl, 2),
                "max_trades_per_day": MAX_LIVE_TRADES_PER_DAY,
                "max_daily_drawdown": MAX_DAILY_DRAWDOWN_RUPEES,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 109,
            "status": "BLOCK",  # Block on error for safety
            "details": f"Risk guard check failed: {e}",
            "outputs": {
                "reason": f"Error: {e}",
                "trades_today": 0,
                "approx_realized_pnl": 0.0,
            },
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 109 - INTRADAY RISK GUARD")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase109()

    print(f"Phase109: {result['details']}")
    print(f"\nStatus: {result['status']}")
    print(f"Trades today: {result['outputs']['trades_today']}")
    print(f"Realized PnL: ₹{result['outputs']['approx_realized_pnl']:.2f}")

    if result["status"] == "BLOCK":
        print(f"\n[BLOCKED] {result['outputs']['reason']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
