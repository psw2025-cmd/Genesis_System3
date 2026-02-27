"""
System3 Phase 228 - Snapshot Coverage Auditor

Verifies snapshot coverage for expected time buckets.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, time
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
COVERAGE_CSV = STORAGE_META / "system3_snapshot_coverage.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_snapshot_coverage_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"

TRADING_HOURS_START = time(9, 15)
TRADING_HOURS_END = time(15, 30)


def run_phase228(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 228: Snapshot Coverage Auditor.

    Returns:
        dict: {
            "phase": 228,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "time_buckets_checked": int,
                "missing_snapshots": int,
                "coverage_file": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 228,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"time_buckets_checked": 0, "missing_snapshots": 0, "coverage_file": str(COVERAGE_CSV)},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if "ts" not in df.columns:
            return {
                "phase": 228,
                "status": "WARN",
                "details": "Timestamp column not found",
                "outputs": {"time_buckets_checked": 0, "missing_snapshots": 0, "coverage_file": str(COVERAGE_CSV)},
                "errors": [],
            }

        # Parse timestamps
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"])

        # Create time buckets (15-minute intervals)
        df["time_bucket"] = df["ts"].dt.floor("15min")
        df["hour"] = df["ts"].dt.time

        # Filter to trading hours
        trading_df = df[(df["hour"] >= TRADING_HOURS_START) & (df["hour"] <= TRADING_HOURS_END)]

        # Count snapshots per bucket
        coverage = trading_df.groupby("time_bucket").size().reset_index(name="snapshot_count")
        coverage["status"] = coverage["snapshot_count"].apply(lambda x: "OK" if x > 0 else "MISSING")

        missing_count = (coverage["status"] == "MISSING").sum()

        # Save coverage
        coverage.to_csv(COVERAGE_CSV, index=False)

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Snapshot Coverage Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Time Buckets Checked**: {len(coverage)}\n")
            f.write(f"**Missing Snapshots**: {missing_count}\n")
            coverage_rate = (1 - missing_count / len(coverage)) * 100 if len(coverage) > 0 else 0.0
            f.write(f"**Coverage Rate**: {coverage_rate:.1f}%\n\n")

            if missing_count > 0:
                f.write("## Missing Time Buckets\n\n")
                missing_buckets = coverage[coverage["status"] == "MISSING"]
                f.write("| Time Bucket | Status |\n")
                f.write("|-------------|--------|\n")
                for _, row in missing_buckets.head(20).iterrows():
                    f.write(f"| {row['time_bucket']} | {row['status']} |\n")
            else:
                f.write("## Status\n\n")
                f.write("✅ All time buckets have snapshots.\n")

        status = "WARN" if missing_count > 0 else "OK"
        details = f"Checked {len(coverage)} buckets, {missing_count} missing"

        return {
            "phase": 228,
            "status": status,
            "details": details,
            "outputs": {
                "time_buckets_checked": len(coverage),
                "missing_snapshots": int(missing_count),
                "coverage_file": str(COVERAGE_CSV),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 228,
            "status": "ERROR",
            "details": f"Phase 228 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 228 - SNAPSHOT COVERAGE AUDITOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase228()

    print(f"Phase 228: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nCoverage CSV: {result['outputs']['coverage_file']}")
        print(f"Buckets: {result['outputs']['time_buckets_checked']}")
        print(f"Missing: {result['outputs']['missing_snapshots']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
