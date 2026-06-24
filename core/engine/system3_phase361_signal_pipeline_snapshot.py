"""
System3 Phase 361 - Signal Pipeline Snapshot & Quality Summary

Creates a consolidated snapshot of the current signal pipeline state
and writes human-readable report and machine-readable JSON.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Signal files to analyze
SIGNAL_FILES = {
    "signals": STORAGE_LIVE / "dhan_index_ai_signals.csv",
    "curated": STORAGE_LIVE / "dhan_index_ai_signals_curated.csv",
    "with_forward": STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv",
    "virtual_orders": STORAGE_LIVE / "dhan_virtual_orders.csv",
}


def analyze_signal_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single signal CSV file."""
    if not file_path.exists():
        return {"exists": False, "error": "File not found"}

    try:
        # Read with bad lines skip to handle corrupted data
        df = pd.read_csv(file_path, on_bad_lines="skip", low_memory=False)

        analysis = {
            "exists": True,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
        }

        # Analyze signal distribution if signal column exists
        if "signal" in df.columns:
            signal_counts = df["signal"].value_counts().to_dict()
            analysis["signal_distribution"] = signal_counts
        elif "pred_label" in df.columns:
            signal_counts = df["pred_label"].value_counts().to_dict()
            analysis["signal_distribution"] = signal_counts

        # Count distinct instruments
        if "symbol" in df.columns:
            analysis["unique_symbols"] = int(df["symbol"].nunique())

        if "underlying" in df.columns:
            analysis["unique_underlyings"] = list(df["underlying"].unique())

        if "expiry" in df.columns:
            analysis["unique_expiries"] = int(df["expiry"].nunique())

        if "strike" in df.columns:
            analysis["unique_strikes"] = int(df["strike"].nunique())

        # Calculate missing value percentages
        missing_pct = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_pct[col] = round(missing_count / len(df) * 100, 2)

        analysis["missing_value_percentages"] = missing_pct

        # Detect obvious issues
        issues = []
        if len(df) == 0:
            issues.append("File has zero rows")

        if "signal" in df.columns:
            signal_vals = df["signal"].value_counts()
            if len(signal_vals) == 1 and signal_vals.index[0] in ["HOLD", "FLAT", "NONE"]:
                issues.append(f"All signals are {signal_vals.index[0]} - no actionable signals")

        if missing_pct:
            high_missing = {k: v for k, v in missing_pct.items() if v > 50}
            if high_missing:
                issues.append(f"High missing values (>50%): {list(high_missing.keys())}")

        analysis["issues"] = issues

        return analysis

    except Exception as e:
        return {"exists": True, "error": f"Failed to analyze: {str(e)}"}


def run_phase361(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 361: Signal Pipeline Snapshot & Quality Summary.

    Returns:
        dict: Phase execution result
    """
    timestamp = datetime.now().isoformat()
    errors = []

    try:
        # Analyze all signal files
        file_analyses = {}
        for file_key, file_path in SIGNAL_FILES.items():
            file_analyses[file_key] = analyze_signal_file(file_path)

        # Create summary
        summary = {
            "phase": 361,
            "timestamp": timestamp,
            "files_analyzed": len(SIGNAL_FILES),
            "files_found": sum(1 for a in file_analyses.values() if a.get("exists")),
            "file_analyses": file_analyses,
        }

        # Compute overall metrics
        total_rows = sum(a.get("row_count", 0) for a in file_analyses.values() if a.get("exists"))
        total_issues = sum(len(a.get("issues", [])) for a in file_analyses.values())

        summary["total_signal_rows"] = total_rows
        summary["total_issues_detected"] = total_issues

        # Determine overall status
        if summary["files_found"] == 0:
            summary["status"] = "ERROR"
            summary["status_message"] = "No signal files found"
        elif total_issues > 5:
            summary["status"] = "WARN"
            summary["status_message"] = f"{total_issues} issues detected across signal files"
        elif total_rows == 0:
            summary["status"] = "WARN"
            summary["status_message"] = "All signal files are empty"
        else:
            summary["status"] = "OK"
            summary["status_message"] = f"{total_rows} signals across {summary['files_found']} files"

        # Write JSON output
        json_path = STORAGE_METRICS / "signal_pipeline_snapshot_361.json"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        # Write MD report
        md_path = REPORTS_DIR / "SIGNAL_PIPELINE_SNAPSHOT_361.md"
        with md_path.open("w", encoding="utf-8") as f:
            f.write("# SIGNAL PIPELINE SNAPSHOT — PHASE 361\n\n")
            f.write(f"**Generated:** {timestamp}  \n")
            f.write(f"**Status:** {summary['status']}  \n")
            f.write(f"**Message:** {summary['status_message']}  \n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Analyzed:** {summary['files_analyzed']}\n")
            f.write(f"- **Files Found:** {summary['files_found']}\n")
            f.write(f"- **Total Signal Rows:** {summary['total_signal_rows']}\n")
            f.write(f"- **Issues Detected:** {summary['total_issues_detected']}\n\n")

            f.write("## File Analysis\n\n")
            for file_key, analysis in file_analyses.items():
                f.write(f"### {file_key}\n\n")

                if not analysis.get("exists"):
                    f.write(f"❌ **File not found**\n\n")
                    continue

                if "error" in analysis:
                    f.write(f"⚠️ **Error:** {analysis['error']}\n\n")
                    continue

                f.write(f"✅ **File exists**\n\n")
                f.write(f"- **Rows:** {analysis.get('row_count', 0)}\n")
                f.write(f"- **Columns:** {analysis.get('column_count', 0)}\n")

                if "signal_distribution" in analysis:
                    f.write(f"- **Signal Distribution:**\n")
                    for signal, count in analysis["signal_distribution"].items():
                        f.write(f"  - {signal}: {count}\n")

                if "unique_symbols" in analysis:
                    f.write(f"- **Unique Symbols:** {analysis['unique_symbols']}\n")

                if "unique_underlyings" in analysis:
                    f.write(f"- **Underlyings:** {', '.join(analysis['unique_underlyings'])}\n")

                if analysis.get("issues"):
                    f.write(f"- **Issues:**\n")
                    for issue in analysis["issues"]:
                        f.write(f"  - ⚠️ {issue}\n")

                f.write("\n")

        return {
            "phase": 361,
            "status": summary["status"],
            "details": summary["status_message"],
            "outputs": {
                "json": str(json_path),
                "report": str(md_path),
            },
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Phase 361 failed: {str(e)}"
        errors.append(error_msg)
        return {
            "phase": 361,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 361 - SIGNAL PIPELINE SNAPSHOT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase361()

    print(f"Status: {result['status']}")
    print(f"Details: {result['details']}")

    if result.get("outputs"):
        print("\nOutputs:")
        for key, path in result["outputs"].items():
            print(f"  {key}: {path}")

    if result.get("errors"):
        print(f"\nErrors: {len(result['errors'])}")
        for error in result["errors"]:
            print(f"  - {error}")

    print("\n" + "=" * 70)

    return 0 if result["status"] in ["OK", "WARN"] else 1


if __name__ == "__main__":
    sys.exit(main())
