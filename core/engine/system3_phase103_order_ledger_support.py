"""
System3 Phase 103 - Order Ledger Support & Integrity Validator

Provides ledger initialization, schema validation, and basic integrity checks.
Bridges Phase 102 (schema definition) and Phase 104 (order construction).
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

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

LOG_FILE = LOGS_DIR / "phase103_order_ledger_support.log"

# Expected ledger schema from Phase 102
EXPECTED_LEDGER_COLUMNS = [
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


def log_message(message: str) -> None:
    """Write message to log file with timestamp."""
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")


def validate_ledger_schema() -> Tuple[bool, str]:
    """
    Validate that ledger CSV exists and has correct schema.

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    try:
        if not LEDGER_CSV.exists():
            return False, "Ledger CSV does not exist"

        # Read header only
        df = pd.read_csv(LEDGER_CSV, nrows=0)
        existing_columns = list(df.columns)

        # Check column match
        if existing_columns != EXPECTED_LEDGER_COLUMNS:
            missing = set(EXPECTED_LEDGER_COLUMNS) - set(existing_columns)
            extra = set(existing_columns) - set(EXPECTED_LEDGER_COLUMNS)

            msg = "Schema mismatch: "
            if missing:
                msg += f"Missing columns: {missing}. "
            if extra:
                msg += f"Extra columns: {extra}."

            log_message(f"Schema validation failed: {msg}")
            return False, msg

        return True, "Schema validation passed"

    except Exception as e:
        error_msg = f"Schema validation error: {str(e)}"
        log_message(error_msg)
        return False, error_msg


def initialize_ledger() -> Tuple[bool, str]:
    """
    Initialize ledger CSV if it doesn't exist.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if LEDGER_CSV.exists():
            return True, "Ledger already exists"

        # Create empty ledger with correct schema
        df = pd.DataFrame(columns=EXPECTED_LEDGER_COLUMNS)
        df.to_csv(LEDGER_CSV, index=False)

        msg = f"Ledger initialized at {LEDGER_CSV}"
        log_message(msg)
        return True, msg

    except Exception as e:
        error_msg = f"Ledger initialization failed: {str(e)}"
        log_message(error_msg)
        return False, error_msg


def check_ledger_integrity() -> Tuple[bool, List[str]]:
    """
    Perform basic integrity checks on ledger data.

    Returns:
        tuple: (is_valid: bool, issues: List[str])
    """
    issues = []

    try:
        if not LEDGER_CSV.exists():
            issues.append("Ledger file does not exist")
            return False, issues

        df = pd.read_csv(LEDGER_CSV)

        # Check for duplicate local_order_ids
        if not df.empty:
            duplicates = df[df.duplicated(subset=["local_order_id"], keep=False)]
            if not duplicates.empty:
                issues.append(f"Found {len(duplicates)} duplicate order IDs")

        # Check for required fields in active orders
        if not df.empty:
            active_orders = df[df["status"].isin(["PENDING", "ACTIVE", "OPEN"])]
            if not active_orders.empty:
                # Check for missing critical fields
                for col in ["underlying", "symbol", "entry_price", "strike"]:
                    if active_orders[col].isna().any():
                        count = active_orders[col].isna().sum()
                        issues.append(f"{count} active orders missing {col}")

        # Check for invalid numeric values
        numeric_cols = ["strike", "entry_price", "target_price", "stop_loss_price", "qty", "lots"]
        for col in numeric_cols:
            if col in df.columns and not df.empty:
                if (df[col] < 0).any():
                    count = (df[col] < 0).sum()
                    issues.append(f"{count} rows have negative {col}")

        if issues:
            log_message(f"Integrity check found {len(issues)} issue(s): {', '.join(issues)}")
            return False, issues
        else:
            log_message("Integrity check passed")
            return True, []

    except Exception as e:
        error_msg = f"Integrity check error: {str(e)}"
        issues.append(error_msg)
        log_message(error_msg)
        return False, issues


def run_phase103() -> Dict[str, Any]:
    """
    Execute Phase 103: Order Ledger Support.

    Returns:
        dict: {
            "phase": 103,
            "status": "OK" or "WARN" or "ERROR",
            "details": "summary message",
            "outputs": {
                "ledger_path": str,
                "ledger_exists": bool,
                "schema_valid": bool,
                "integrity_valid": bool,
                "row_count": int
            },
            "errors": List[str]
        }
    """
    errors = []
    outputs = {
        "ledger_path": str(LEDGER_CSV),
        "ledger_exists": False,
        "schema_valid": False,
        "integrity_valid": False,
        "row_count": 0,
    }

    try:
        # Step 1: Initialize ledger if needed
        init_success, init_msg = initialize_ledger()
        if not init_success:
            errors.append(init_msg)
            return {
                "phase": 103,
                "status": "ERROR",
                "details": f"Ledger initialization failed: {init_msg}",
                "outputs": outputs,
                "errors": errors,
            }

        outputs["ledger_exists"] = LEDGER_CSV.exists()

        # Step 2: Validate schema
        schema_valid, schema_msg = validate_ledger_schema()
        outputs["schema_valid"] = schema_valid

        if not schema_valid:
            errors.append(schema_msg)
            return {
                "phase": 103,
                "status": "ERROR",
                "details": f"Schema validation failed: {schema_msg}",
                "outputs": outputs,
                "errors": errors,
            }

        # Step 3: Check integrity
        integrity_valid, integrity_issues = check_ledger_integrity()
        outputs["integrity_valid"] = integrity_valid

        # Count rows
        try:
            df = pd.read_csv(LEDGER_CSV)
            outputs["row_count"] = len(df)
        except:
            outputs["row_count"] = 0

        # Determine status
        if integrity_issues:
            errors.extend(integrity_issues)
            status = "WARN"
            details = f"Ledger initialized with {len(integrity_issues)} integrity warning(s)"
        else:
            status = "OK"
            details = f"Ledger support ready ({outputs['row_count']} orders)"

        log_message(f"Phase 103 completed: {status} - {details}")

        return {"phase": 103, "status": status, "details": details, "outputs": outputs, "errors": errors}

    except Exception as e:
        error_msg = f"Phase 103 unexpected error: {str(e)}"
        errors.append(error_msg)
        log_message(error_msg)

        return {"phase": 103, "status": "ERROR", "details": error_msg, "outputs": outputs, "errors": errors}


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 103 - ORDER LEDGER SUPPORT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    result = run_phase103()

    print(f"Status: {result['status']}")
    print(f"Details: {result['details']}")
    print()

    if result["outputs"]:
        print("Outputs:")
        for key, value in result["outputs"].items():
            print(f"  {key}: {value}")
        print()

    if result["errors"]:
        print(f"Errors/Warnings ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  - {error}")
        print()

    print("=" * 70)

    return 0 if result["status"] in ["OK", "WARN"] else 1


if __name__ == "__main__":
    sys.exit(main())
