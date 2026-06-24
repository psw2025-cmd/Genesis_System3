"""
System3 Phase 117 - Live → Learning Bridge

Connect ledger & PnL to Real Outcome files already used by phases 28–37.
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
STORAGE_LEARNING = PROJECT_ROOT / "storage" / "learning"
STORAGE_LEARNING.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
OUTCOMES_CSV = STORAGE_LEARNING / "live_trade_outcomes.csv"


def run_phase117(**kwargs) -> dict:
    """
    Bridge live trades to learning outcomes.

    Returns:
        dict: {
            "phase": 117,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    outcomes_added = 0

    try:
        # Read ledger
        if not LEDGER_CSV.exists():
            return {
                "phase": 117,
                "status": "OK",
                "details": "Ledger not found, no outcomes to bridge",
                "outputs": {"outcomes_added": 0},
                "errors": [],
            }

        df = pd.read_csv(LEDGER_CSV)
        if df.empty:
            return {
                "phase": 117,
                "status": "OK",
                "details": "Ledger is empty, no outcomes to bridge",
                "outputs": {"outcomes_added": 0},
                "errors": [],
            }

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Filter finished trades (FILLED with exit)
        finished_trades = df[(df["status"] == "FILLED") & (df["exit_reason"].notna()) & (df["exit_reason"] != "")]

        if finished_trades.empty:
            return {
                "phase": 117,
                "status": "OK",
                "details": "No finished trades to bridge",
                "outputs": {"outcomes_added": 0},
                "errors": [],
            }

        # Build outcomes rows
        outcome_rows = []
        for _, row in finished_trades.iterrows():
            outcome_row = {
                "timestamp": row.get("timestamp", datetime.now().isoformat()),
                "underlying": row.get("underlying", ""),
                "strike": row.get("strike", 0),
                "option_type": row.get("option_type", ""),
                "side": row.get("side", ""),
                "entry_price": row.get("entry_price", 0),
                "exit_price": row.get("exit_price", 0),
                "pnl_absolute": row.get("pnl_absolute", 0),
                "pnl_percent": row.get("pnl_percent", 0),
                "exit_reason": row.get("exit_reason", ""),
                "local_order_id": row.get("local_order_id", ""),
            }
            outcome_rows.append(outcome_row)

        # Load or create outcomes CSV
        if OUTCOMES_CSV.exists():
            outcomes_df = pd.read_csv(OUTCOMES_CSV)
        else:
            # Create with header
            outcomes_df = pd.DataFrame(columns=outcome_rows[0].keys())

        # Append new outcomes
        new_outcomes_df = pd.DataFrame(outcome_rows)

        # Check for duplicates (by local_order_id)
        if "local_order_id" in outcomes_df.columns:
            existing_ids = set(outcomes_df["local_order_id"].astype(str))
            new_outcomes_df = new_outcomes_df[~new_outcomes_df["local_order_id"].astype(str).isin(existing_ids)]

        if not new_outcomes_df.empty:
            combined_df = pd.concat([outcomes_df, new_outcomes_df], ignore_index=True)
            combined_df.to_csv(OUTCOMES_CSV, index=False)
            outcomes_added = len(new_outcomes_df)

        status = "OK"
        details = f"Bridged {outcomes_added} trade outcomes to learning system"

        return {
            "phase": 117,
            "status": status,
            "details": details,
            "outputs": {
                "outcomes_added": outcomes_added,
                "outcomes_path": str(OUTCOMES_CSV),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 117,
            "status": "ERROR",
            "details": f"Phase 117 failed: {e}",
            "outputs": {"outcomes_added": 0},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 117 - LIVE TO LEARNING BRIDGE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase117()

    print(f"Phase117: {result['details']}")
    if result["outputs"]:
        print(f"Outcomes added: {result['outputs'].get('outcomes_added', 0)}")
        if "outcomes_path" in result["outputs"]:
            print(f"Outcomes file: {result['outputs']['outcomes_path']}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
