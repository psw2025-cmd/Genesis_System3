"""
System3 Phase 110 - Stop-Loss & Exit Rule Builder (Static)

Build conservative SL/TP rules per trade from existing AI signals.
"""

import json
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
EXIT_RULES_JSON = STORAGE_LIVE / "phase110_exit_rules_pending.json"

# Default exit rules (conservative)
DEFAULT_TARGET_PCT = 0.02  # 2% gain
DEFAULT_STOP_LOSS_PCT = 0.01  # 1% loss


def run_phase110(**kwargs) -> dict:
    """
    Build exit rules for PLANNED orders.

    Returns:
        dict: {
            "phase": 110,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    rules_added = 0

    try:
        # Read ledger
        if not LEDGER_CSV.exists():
            return {
                "phase": 110,
                "status": "OK",
                "details": "Ledger not found, no rules to add",
                "outputs": {"rules_added": 0},
                "errors": [],
            }

        df = pd.read_csv(LEDGER_CSV)
        if df.empty:
            return {
                "phase": 110,
                "status": "OK",
                "details": "Ledger is empty, no rules to add",
                "outputs": {"rules_added": 0},
                "errors": [],
            }

        # Find PLANNED orders with missing target_price or stop_loss_price
        planned_orders = df[df["status"] == "PLANNED"].copy()

        # Filter orders missing exit rules
        missing_rules = planned_orders[
            (planned_orders["target_price"].isna() | (planned_orders["target_price"] == 0))
            | (planned_orders["stop_loss_price"].isna() | (planned_orders["stop_loss_price"] == 0))
        ]

        if missing_rules.empty:
            return {
                "phase": 110,
                "status": "OK",
                "details": "All PLANNED orders already have exit rules",
                "outputs": {"rules_added": 0},
                "errors": [],
            }

        # Build exit rules
        pending_rules = []

        for idx, row in missing_rules.iterrows():
            entry_price = float(row.get("entry_price", 0))

            if entry_price <= 0:
                # Entry price not known yet - store relative rules
                pending_rules.append(
                    {
                        "local_order_id": row.get("local_order_id"),
                        "target_pct": DEFAULT_TARGET_PCT,
                        "stop_loss_pct": DEFAULT_STOP_LOSS_PCT,
                        "entry_price_required": True,
                    }
                )
            else:
                # Calculate target and stop loss
                target_price = entry_price * (1 + DEFAULT_TARGET_PCT)
                stop_loss_price = entry_price * (1 - DEFAULT_STOP_LOSS_PCT)

                # Update ledger
                df.at[idx, "target_price"] = target_price
                df.at[idx, "stop_loss_price"] = stop_loss_price

                rules_added += 1

        # Save updated ledger
        if rules_added > 0:
            df.to_csv(LEDGER_CSV, index=False)

        # Save pending rules (for orders without entry_price)
        if pending_rules:
            with EXIT_RULES_JSON.open("w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "pending_rules": pending_rules,
                    },
                    f,
                    indent=2,
                )

        status = "OK"
        details = f"Added exit rules for {rules_added} orders"
        if pending_rules:
            details += f", {len(pending_rules)} pending (awaiting entry_price)"

        return {
            "phase": 110,
            "status": status,
            "details": details,
            "outputs": {
                "rules_added": rules_added,
                "pending_rules_count": len(pending_rules),
                "pending_rules_path": str(EXIT_RULES_JSON) if pending_rules else None,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 110,
            "status": "ERROR",
            "details": f"Phase 110 failed: {e}",
            "outputs": {"rules_added": 0},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 110 - EXIT RULE BUILDER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase110()

    print(f"Phase110: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nRules added: {result['outputs']['rules_added']}")
    if result["outputs"].get("pending_rules_count", 0) > 0:
        print(f"Pending rules: {result['outputs']['pending_rules_count']}")
        print(f"Pending rules file: {result['outputs']['pending_rules_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
