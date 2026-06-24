"""
System3 Phase 210 - Historical Timegap Analyzer

Detects gaps in historical data timestamps.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
FLAGS_CSV = STORAGE_META / "system3_timegap_flags.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "history"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_timegap_analyzer_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
GAP_THRESHOLD_MINUTES = 2


def run_phase210(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 210: Historical Timegap Analyzer.

    Returns:
        dict: {
            "phase": 210,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "total_gaps": int,
                "large_gaps": int,
                "flags_file": str,
            },
            "errors": [],
        }
    """
    errors = []
    gaps = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 210,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"total_gaps": 0, "large_gaps": 0, "flags_file": str(FLAGS_CSV)},
                "errors": [],
            }

        # Load with robust parser
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if "ts" not in df.columns or len(df) < 2:
            return {
                "phase": 210,
                "status": "WARN",
                "details": "Insufficient data for gap analysis",
                "outputs": {"total_gaps": 0, "large_gaps": 0, "flags_file": str(FLAGS_CSV)},
                "errors": [],
            }

        # Parse timestamps and sort
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts").dropna(subset=["ts"])

        # Compute gaps
        df["gap_minutes"] = df["ts"].diff().dt.total_seconds() / 60.0
        large_gaps = df[df["gap_minutes"] > GAP_THRESHOLD_MINUTES]

        # Create flags DataFrame
        if len(large_gaps) > 0:
            flags_df = pd.DataFrame(
                {
                    "start_time": large_gaps["ts"].shift(1),
                    "end_time": large_gaps["ts"],
                    "gap_minutes": large_gaps["gap_minutes"],
                    "reason_code": "GAP_EXCEEDS_THRESHOLD",
                }
            )
            flags_df.to_csv(FLAGS_CSV, index=False)
        else:
            # Create empty file with header
            pd.DataFrame(columns=["start_time", "end_time", "gap_minutes", "reason_code"]).to_csv(
                FLAGS_CSV, index=False
            )

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Timegap Analyzer Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Threshold**: {GAP_THRESHOLD_MINUTES} minutes\n\n")
            f.write(f"**Total Data Points**: {len(df)}\n")
            f.write(f"**Large Gaps Detected**: {len(large_gaps)}\n\n")

            if len(large_gaps) > 0:
                f.write("## Gap Details\n\n")
                f.write("| Start Time | End Time | Gap (minutes) |\n")
                f.write("|------------|----------|---------------|\n")
                for idx, row in large_gaps.iterrows():
                    prev_ts = df.loc[df.index < idx, "ts"].iloc[-1] if len(df.loc[df.index < idx]) > 0 else None
                    f.write(f"| {prev_ts} | {row['ts']} | {row['gap_minutes']:.2f} |\n")
            else:
                f.write("## Status\n\n")
                f.write("✅ No large gaps detected.\n")

        status = "WARN" if len(large_gaps) > 0 else "OK"
        details = f"Detected {len(large_gaps)} gaps > {GAP_THRESHOLD_MINUTES} minutes"

        return {
            "phase": 210,
            "status": status,
            "details": details,
            "outputs": {
                "total_gaps": len(df) - 1,
                "large_gaps": len(large_gaps),
                "flags_file": str(FLAGS_CSV),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 210,
            "status": "ERROR",
            "details": f"Phase 210 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 210 - HISTORICAL TIMEGAP ANALYZER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase210()

    print(f"Phase 210: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nFlags: {result['outputs']['flags_file']}")
        print(f"Large Gaps: {result['outputs']['large_gaps']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
