"""
System3 Phase 102 - Local Order Ledger Schema

Define the canonical local order ledger CSV that all live trades will write to.
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
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "phase102_order_ledger_schema.log"

# Ledger schema - canonical columns
LEDGER_COLUMNS = [
    "local_order_id",
    "timestamp",
    "underlying",
    "symbol",
    "expiry",
    "strike",
    "option_type",
    "side",
    "lots",
    "qty",
    "entry_price",
    "target_price",
    "stop_loss_price",
    "status",
    "broker_order_id",
    "broker_status",
    "last_update_ts",
    "pnl_absolute",
    "pnl_percent",
    "exit_price",
    "exit_reason",
    "notes",
]


def ensure_ledger_exists():
    """
    Ensure ledger CSV exists with correct header.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if LEDGER_CSV.exists():
            # Verify header matches
            df = pd.read_csv(LEDGER_CSV, nrows=0)  # Read only header
            existing_columns = list(df.columns)

            if existing_columns != LEDGER_COLUMNS:
                # Header mismatch - log and return error
                error_msg = f"Header mismatch. Expected {len(LEDGER_COLUMNS)} columns, found {len(existing_columns)}"
                with LOG_FILE.open("a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().isoformat()}] {error_msg}\n")
                    f.write(f"Expected: {LEDGER_COLUMNS}\n")
                    f.write(f"Found: {existing_columns}\n")
                return False, error_msg

            return True, "Ledger exists with correct header"
        else:
            # Create new ledger with header only
            df = pd.DataFrame(columns=LEDGER_COLUMNS)
            df.to_csv(LEDGER_CSV, index=False)
            return True, "Ledger created with header"

    except Exception as e:
        error_msg = f"Error ensuring ledger: {e}"
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {error_msg}\n")
        return False, error_msg


def run_phase102(**kwargs) -> dict:
    """
    Ensure order ledger CSV exists with correct schema.

    Returns:
        dict: {
            "phase": 102,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    # Ensure ledger exists
    success, message = ensure_ledger_exists()

    if not success:
        errors.append(message)
        status = "ERROR"
        details = f"Ledger schema check failed: {message}"
    else:
        status = "OK"
        details = f"Order ledger verified/created: {LEDGER_CSV}"

    return {
        "phase": 102,
        "status": status,
        "details": details,
        "outputs": {
            "ledger_path": str(LEDGER_CSV),
            "columns": LEDGER_COLUMNS,
            "column_count": len(LEDGER_COLUMNS),
            "exists": LEDGER_CSV.exists(),
        },
        "errors": errors,
    }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 102 - ORDER LEDGER SCHEMA")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase102()

    print(f"Phase102: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nLedger path: {result['outputs']['ledger_path']}")
    print(f"Columns: {result['outputs']['column_count']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
