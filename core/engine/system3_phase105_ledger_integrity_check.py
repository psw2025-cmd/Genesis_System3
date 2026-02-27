"""
System3 Phase 105 - Ledger Integrity Checker

Check ledger sanity before any live execution.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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

LOG_FILE = LOGS_DIR / "phase105_ledger_integrity_issues.log"

# Valid status values
VALID_STATUSES = ["PLANNED", "SENT", "PARTIAL", "FILLED", "CANCELLED", "REJECTED", "EXPIRED", "ERROR"]


def ensure_ledger_header() -> bool:
    """Create empty ledger with header if missing."""
    try:
        from core.engine.system3_phase102_order_ledger_schema import LEDGER_COLUMNS

        df = pd.DataFrame(columns=LEDGER_COLUMNS)
        df.to_csv(LEDGER_CSV, index=False)
        return True
    except Exception as e:
        return False


def validate_ledger() -> tuple[bool, List[str]]:
    """
    Validate ledger integrity.

    Returns:
        tuple: (is_valid: bool, errors: List[str])
    """
    errors = []

    # Check if ledger exists
    if not LEDGER_CSV.exists():
        ensure_ledger_header()
        return False, ["Ledger missing; created empty header"]

    try:
        # Read ledger
        df = pd.read_csv(LEDGER_CSV)

        # Check required columns exist
        from core.engine.system3_phase102_order_ledger_schema import LEDGER_COLUMNS

        missing_columns = set(LEDGER_COLUMNS) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")

        if df.empty:
            return True, []  # Empty ledger is valid

        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 for header and 0-based index

            # Check negative qty
            if "qty" in df.columns and pd.notna(row.get("qty")):
                if float(row["qty"]) < 0:
                    errors.append(f"Row {row_num}: Negative qty ({row['qty']})")

            # Check missing required fields
            if pd.isna(row.get("underlying")) or str(row.get("underlying")).strip() == "":
                errors.append(f"Row {row_num}: Missing underlying")

            if pd.isna(row.get("symbol")) or str(row.get("symbol")).strip() == "":
                errors.append(f"Row {row_num}: Missing symbol")

            if pd.isna(row.get("side")) or str(row.get("side")).strip() == "":
                errors.append(f"Row {row_num}: Missing side")

            # Check status is valid
            status = str(row.get("status", "")).strip()
            if status and status not in VALID_STATUSES:
                errors.append(f"Row {row_num}: Invalid status '{status}' (must be one of {VALID_STATUSES})")

            # Check broker_status is non-null only when status != PLANNED
            broker_status = row.get("broker_status")
            if status == "PLANNED" and pd.notna(broker_status) and str(broker_status).strip() != "":
                if str(broker_status).strip() != "NOT_SENT":
                    errors.append(f"Row {row_num}: broker_status should be null/empty for PLANNED orders")
            elif status != "PLANNED" and (pd.isna(broker_status) or str(broker_status).strip() == ""):
                errors.append(f"Row {row_num}: broker_status should be set for non-PLANNED orders")

        return len(errors) == 0, errors

    except Exception as e:
        return False, [f"Error reading ledger: {e}"]


def run_phase105(**kwargs) -> dict:
    """
    Check ledger integrity.

    Returns:
        dict: {
            "phase": 105,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    is_valid, errors = validate_ledger()

    # Write errors to log if any
    if errors:
        try:
            with LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now().isoformat()}] Ledger integrity check failed:\n")
                for error in errors:
                    f.write(f"  - {error}\n")
        except Exception:
            pass

    if is_valid:
        # Count rows
        try:
            if LEDGER_CSV.exists():
                df = pd.read_csv(LEDGER_CSV)
                row_count = len(df)
            else:
                row_count = 0
        except Exception:
            row_count = 0

        return {
            "phase": 105,
            "status": "OK",
            "details": f"Ledger integrity OK ({row_count} rows)",
            "outputs": {
                "ledger_path": str(LEDGER_CSV),
                "row_count": row_count,
                "valid": True,
            },
            "errors": [],
        }
    else:
        return {
            "phase": 105,
            "status": "ERROR",
            "details": f"Ledger integrity check failed: {len(errors)} issue(s) found",
            "outputs": {
                "ledger_path": str(LEDGER_CSV),
                "valid": False,
                "issue_count": len(errors),
            },
            "errors": errors,
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 105 - LEDGER INTEGRITY CHECK")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase105()

    print(f"Phase105: {result['details']}")
    if result.get("errors"):
        print(f"\nFound {len(result['errors'])} issue(s):")
        for error in result["errors"]:
            print(f"  [ERROR] {error}")
        print(f"\nDetails logged to: {LOG_FILE}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
