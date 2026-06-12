"""
System3 Phase 108 - Order Status Refresher

Pull order statuses from Angel (or simulated now) and update ledger.
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

# Import wrapper
try:
    from core.broker.dhan_live_order_wrapper import AngelLiveOrderWrapper
except ImportError as e:
    print(f"[PH108] ERROR: Failed to import AngelLiveOrderWrapper: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"


def map_broker_status_to_ledger_status(broker_status: str) -> str:
    """
    Map broker status to ledger status.

    Returns:
        str: Ledger status value
    """
    broker_status_upper = broker_status.upper()

    if "COMPLETE" in broker_status_upper or "FILLED" in broker_status_upper:
        return "FILLED"
    elif "REJECTED" in broker_status_upper:
        return "REJECTED"
    elif "CANCELLED" in broker_status_upper or "CANCEL" in broker_status_upper:
        return "CANCELLED"
    elif "PARTIAL" in broker_status_upper:
        return "PARTIAL"
    else:
        return "SENT"  # Keep as SENT for other statuses


def run_phase108(**kwargs) -> dict:
    """
    Refresh order statuses from broker and update ledger.

    Returns:
        dict: {
            "phase": 108,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    status_counts = {}

    try:
        # Read ledger
        if not LEDGER_CSV.exists():
            return {
                "phase": 108,
                "status": "ERROR",
                "details": f"Ledger not found: {LEDGER_CSV}",
                "outputs": {"status_counts": {}},
                "errors": [f"Ledger not found: {LEDGER_CSV}"],
            }

        df = pd.read_csv(LEDGER_CSV)
        if df.empty:
            return {
                "phase": 108,
                "status": "OK",
                "details": "Ledger is empty, no orders to refresh",
                "outputs": {"status_counts": {}},
                "errors": [],
            }

        # Find rows that need status refresh
        pending_orders = df[df["status"].isin(["SENT", "PARTIAL"])].copy()

        if pending_orders.empty:
            return {
                "phase": 108,
                "status": "OK",
                "details": "No pending orders to refresh",
                "outputs": {"status_counts": {}},
                "errors": [],
            }

        # Initialize wrapper
        wrapper = AngelLiveOrderWrapper()

        # Refresh each pending order
        updated_count = 0
        for idx, row in pending_orders.iterrows():
            broker_order_id = row.get("broker_order_id")

            if pd.isna(broker_order_id) or str(broker_order_id).strip() == "":
                continue  # Skip if no broker_order_id

            try:
                # Get order status from broker
                result = wrapper.get_order_status(str(broker_order_id))

                if result.get("status") == "OK":
                    broker_status = result.get("broker_status", "")

                    # Map to ledger status
                    new_ledger_status = map_broker_status_to_ledger_status(broker_status)

                    # Update ledger
                    df.at[idx, "status"] = new_ledger_status
                    df.at[idx, "broker_status"] = broker_status
                    df.at[idx, "last_update_ts"] = datetime.now().isoformat()

                    # Count by status
                    status_counts[new_ledger_status] = status_counts.get(new_ledger_status, 0) + 1
                    updated_count += 1
                else:
                    # Status check failed
                    if result.get("error") == "NOT_IMPLEMENTED":
                        # Wrapper is still DRY_RUN - log and return
                        return {
                            "phase": 108,
                            "status": "ERROR",
                            "details": "Order status refresh not implemented (wrapper is DRY_RUN)",
                            "outputs": {"status_counts": {}},
                            "errors": ["NOT_IMPLEMENTED - Real DhanHQ integration pending"],
                        }
                    else:
                        errors.append(f"Status check failed for {broker_order_id}: {result.get('error')}")

            except Exception as e:
                errors.append(f"Error refreshing order {broker_order_id}: {e}")

        # Save updated ledger
        if updated_count > 0:
            df.to_csv(LEDGER_CSV, index=False)

        status = "OK" if not errors else "ERROR"
        details = f"Refreshed {updated_count} order statuses"

        return {
            "phase": 108,
            "status": status,
            "details": details,
            "outputs": {
                "status_counts": status_counts,
                "orders_refreshed": updated_count,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 108,
            "status": "ERROR",
            "details": f"Phase 108 failed: {e}",
            "outputs": {"status_counts": {}},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 108 - ORDER STATUS REFRESHER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase108()

    print(f"Phase108: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"].get("status_counts"):
        print("\nStatus distribution:")
        for status, count in result["outputs"]["status_counts"].items():
            print(f"  {status}: {count}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
