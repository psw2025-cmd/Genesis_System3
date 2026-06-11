"""
System3 Phase 238 - Virtual Orders Schema Guard

Ensure angel_virtual_orders.csv is consistent and well-formed.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "execution"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_virtual_orders_schema_report.md"

REQUIRED_COLS = [
    "ts", "underlying", "strike", "option_type", "side", "expiry",
    "ltp", "final_score", "ai_score", "lots", "approved",
    "adjusted_lots", "risk_reason", "risk_flags_json", "snapshot_id"
]
# Optional for merge compatibility (Phase 239 adds if missing; avoid ERROR here)
OPTIONAL_MERGE_COLS = ["underlying", "strike"]
REQUIRED_STRICT = [c for c in REQUIRED_COLS if c not in OPTIONAL_MERGE_COLS]
# Only missing critical columns cause ERROR; other missing → WARN (minimal CSV still usable)
CRITICAL_COLS = ["ts"]


def run_phase238() -> dict:
    """Run Phase 238: Virtual Orders Schema Guard."""
    errors = []
    warnings = []
    
    if not VIRTUAL_ORDERS_CSV.exists():
        report = f"""# System3 Virtual Orders Schema Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status

⚠️ **WARN**: File not found: `{VIRTUAL_ORDERS_CSV}`

STEP 4: No virtual orders generated yet. This happens when:
- Signal generation has not produced BUY/SELL signals
- Check signals CSV: storage/live/angel_index_ai_signals.csv
- If signals CSV is empty, signal generation thresholds are too strict
"""
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write(report)
        return {
            "phase": 238,
            "status": "WARN",
            "details": "File not found - no orders generated (check signal generation)",
            "outputs": {"file_exists": False},
            "errors": ["STEP 4: No virtual orders because no BUY/SELL signals were generated"]
        }
    
    try:
        df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        
        # Add optional merge columns if missing (Phase 239 compatibility)
        for col in OPTIONAL_MERGE_COLS:
            if col not in df.columns:
                df[col] = pd.NA
                warnings.append(f"Added missing column '{col}' as NA for merge compatibility")
        # Allow timestamp as alias for ts (minimal CSV schema)
        if "ts" not in df.columns and "timestamp" in df.columns:
            df["ts"] = df["timestamp"]
            warnings.append("Using 'timestamp' as 'ts' for schema compatibility")
        # Check required columns: critical missing → ERROR; others → WARN
        missing_strict = [col for col in REQUIRED_STRICT if col not in df.columns]
        missing_critical = [c for c in CRITICAL_COLS if c not in df.columns]
        if missing_critical:
            errors.append(f"Missing critical columns: {missing_critical}")
        if missing_strict:
            warnings.append(f"Missing recommended columns: {[c for c in missing_strict if c not in missing_critical]}")
        missing_cols = missing_strict
        
        # Check data types
        if "lots" in df.columns:
            try:
                pd.to_numeric(df["lots"], errors="coerce")
            except Exception as e:
                warnings.append(f"Non-numeric values in 'lots': {e}")
        
        # Generate report
        report_lines = [
            "# System3 Virtual Orders Schema Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "## Status\n",
            f"✅ File exists: `{VIRTUAL_ORDERS_CSV}`\n",
            f"**Total Rows**: {len(df)}\n",
            "## Schema Validation\n"
        ]
        
        if missing_cols:
            report_lines.append(f"❌ **Missing Required Columns**: {', '.join(missing_cols)}\n")
        else:
            report_lines.append("✅ **All Required Columns Present**\n")
        
        if df.empty:
            report_lines.append("⚠️ **File is Empty**\n")
        else:
            first_ts = df["ts"].iloc[0] if "ts" in df.columns else "N/A"
            last_ts = df["ts"].iloc[-1] if "ts" in df.columns else "N/A"
            report_lines.append(f"**First Timestamp**: {first_ts}\n")
            report_lines.append(f"**Last Timestamp**: {last_ts}\n")
        
        if warnings:
            report_lines.append("\n## Warnings\n")
            for warn in warnings:
                report_lines.append(f"- {warn}\n")
        
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)
        
        status = "ERROR" if missing_critical else ("WARN" if (warnings or missing_strict) else "OK")
        
        return {
            "phase": 238,
            "status": status,
            "details": f"Schema check complete: {len(df)} rows, {len(missing_cols)} missing cols",
            "outputs": {
                "file_exists": True,
                "row_count": len(df),
                "missing_cols": missing_cols
            },
            "errors": errors
        }
        
    except Exception as e:
        error_msg = f"Error reading CSV: {e}"
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write(f"# System3 Virtual Orders Schema Report\n\n**ERROR**: {error_msg}\n")
        return {
            "phase": 238,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": [error_msg]
        }


if __name__ == "__main__":
    result = run_phase238()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

