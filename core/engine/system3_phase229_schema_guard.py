"""
System3 Phase 229 - Data Shape and Schema Guard

Verifies CSV/JSON files match expected schemas.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "data"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_schema_guard.log"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"

# Expected schema for signals CSV
EXPECTED_SIGNALS_SCHEMA = {
    "critical": ["ts", "underlying", "strike", "side", "final_score"],
    "optional": ["delta", "gamma", "theta", "vega", "pred_label", "ai_score"],
}


def run_phase229(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 229: Data Shape and Schema Guard.

    Returns:
        dict: {
            "phase": 229,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "files_checked": int,
                "schema_mismatches": int,
                "auto_fixes": int,
            },
            "errors": [],
        }
    """
    errors = []
    schema_mismatches = 0
    auto_fixes = 0

    try:
        files_checked = []

        # Check signals CSV
        if SIGNALS_CSV.exists():
            files_checked.append(str(SIGNALS_CSV))
            try:
                df = pd.read_csv(SIGNALS_CSV, nrows=1)  # Just read header
                actual_columns = set(df.columns)
                expected_critical = set(EXPECTED_SIGNALS_SCHEMA["critical"])

                missing_critical = expected_critical - actual_columns
                if missing_critical:
                    schema_mismatches += 1
                    # Auto-add missing optional columns with defaults
                    missing_optional = set(EXPECTED_SIGNALS_SCHEMA["optional"]) - actual_columns
                    if missing_optional:
                        # Read full file and add columns
                        df_full = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
                        for col in missing_optional:
                            df_full[col] = 0.0  # Default value
                        df_full.to_csv(SIGNALS_CSV, index=False)
                        auto_fixes += len(missing_optional)
            except Exception as e:
                errors.append(f"Failed to check {SIGNALS_CSV}: {e}")

        # Log results
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Schema Guard Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Files Checked: {len(files_checked)}\n")
            f.write(f"Schema Mismatches: {schema_mismatches}\n")
            f.write(f"Auto-Fixes Applied: {auto_fixes}\n\n")

            for file_path in files_checked:
                f.write(f"File: {file_path}\n")
                f.write(f"  Status: {'OK' if schema_mismatches == 0 else 'WARN'}\n\n")

        status = "WARN" if schema_mismatches > 0 else "OK"
        details = f"Checked {len(files_checked)} file(s)"
        if schema_mismatches > 0:
            details += f", {schema_mismatches} mismatch(es)"
        if auto_fixes > 0:
            details += f", {auto_fixes} auto-fix(es)"

        return {
            "phase": 229,
            "status": status,
            "details": details,
            "outputs": {
                "files_checked": len(files_checked),
                "schema_mismatches": schema_mismatches,
                "auto_fixes": auto_fixes,
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 229,
            "status": "ERROR",
            "details": f"Phase 229 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 229 - DATA SHAPE AND SCHEMA GUARD")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase229()

    print(f"Phase 229: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nLog: {result['outputs']['log_path']}")
        print(f"Files: {result['outputs']['files_checked']}")
        print(f"Mismatches: {result['outputs']['schema_mismatches']}")
        print(f"Auto-fixes: {result['outputs']['auto_fixes']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
