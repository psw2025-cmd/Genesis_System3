"""
System3 Phase 225 - Label Reconciliation Engine

Rebuilds labels using consistent rules and forward returns.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RECONCILED_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_reconciled.csv"
SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"


def run_phase225(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 225: Label Reconciliation Engine.

    Returns:
        dict: {
            "phase": 225,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "rows_reconciled": int,
                "discrepancies": int,
                "reconciled_file": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        # Try with forward returns first
        signals_file = (
            SIGNALS_CSV if SIGNALS_CSV.exists() else PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
        )

        if not signals_file.exists():
            return {
                "phase": 225,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"rows_reconciled": 0, "discrepancies": 0, "reconciled_file": str(RECONCILED_CSV)},
                "errors": ["STEP 4: Signal generation did not create signals CSV"],
            }

        # Load data
        try:
            df = pd.read_csv(signals_file)
        except Exception:
            df = pd.read_csv(signals_file, engine="python", on_bad_lines="skip")

        # CRITICAL FIX: Preserve ts column or auto-heal from timestamp
        if "ts" in df.columns:
            # Check if ts is corrupted (all NaN)
            if df["ts"].isna().all() and "timestamp" in df.columns:
                df["ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
                errors.append("Auto-healed: Copied timestamp → ts column in Phase 225")
        elif "timestamp" in df.columns:
            # No ts column - create from timestamp
            df["ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
            errors.append("Created ts column from timestamp in Phase 225")

        if len(df) == 0:
            return {
                "phase": 225,
                "status": "WARN",
                "details": "No data to reconcile - signals CSV is empty",
                "outputs": {"rows_reconciled": 0, "discrepancies": 0, "reconciled_file": str(RECONCILED_CSV)},
                "errors": ["STEP 4: Signal generation produced no signals - check thresholds"],
            }

        # Check for forward returns
        forward_cols = [col for col in df.columns if col.startswith("forward_return") or col.startswith("fwd_ret_")]
        if len(forward_cols) == 0:
            return {
                "phase": 225,
                "status": "WARN",
                "details": "Forward returns not available (run Phase 221 first)",
                "outputs": {"rows_reconciled": 0, "discrepancies": 0, "reconciled_file": str(RECONCILED_CSV)},
                "errors": [],
            }

        # Rebuild labels based on forward returns
        df["reconciled_label"] = "HOLD"

        if forward_cols:
            forward_col = forward_cols[0]
            # Simple rule: positive return -> BUY signal was good, negative -> SELL signal was good
            if "final_score" in df.columns:
                df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")
                # Rebuild based on final_score and forward return
                df.loc[(df["final_score"] > 0.4) & (df[forward_col] > 0), "reconciled_label"] = "BUY"
                df.loc[(df["final_score"] < -0.4) & (df[forward_col] < 0), "reconciled_label"] = "SELL"

        # Compare old vs new labels
        discrepancies = 0
        if "pred_label" in df.columns:
            discrepancies = (df["pred_label"] != df["reconciled_label"]).sum()

        # Save reconciled dataset
        # Ensure ts column is preserved in output
        if "ts" in df.columns:
            ts_null_count = df["ts"].isna().sum()
            if ts_null_count == len(df) and "timestamp" in df.columns:
                df["ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
                errors.append("Final auto-heal: Copied timestamp → ts before save")

        df.to_csv(RECONCILED_CSV, index=False)

        status = "OK"
        details = f"Reconciled {len(df)} rows, {discrepancies} discrepancies found"

        return {
            "phase": 225,
            "status": status,
            "details": details,
            "outputs": {
                "rows_reconciled": len(df),
                "discrepancies": int(discrepancies),
                "reconciled_file": str(RECONCILED_CSV),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 225,
            "status": "ERROR",
            "details": f"Phase 225 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 225 - LABEL RECONCILIATION ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase225()

    print(f"Phase 225: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReconciled CSV: {result['outputs']['reconciled_file']}")
        print(f"Rows: {result['outputs']['rows_reconciled']}")
        print(f"Discrepancies: {result['outputs']['discrepancies']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
