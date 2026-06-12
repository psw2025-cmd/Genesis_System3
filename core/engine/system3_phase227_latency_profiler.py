"""
System3 Phase 227 - Data Latency Profiler

Measures delay between market timestamps and processing times.
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

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_latency_profile.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"


def run_phase227(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 227: Data Latency Profiler.

    Returns:
        dict: {
            "phase": 227,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "snapshots_analyzed": int,
                "avg_latency_seconds": float,
                "report_path": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 227,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"snapshots_analyzed": 0, "avg_latency_seconds": 0.0, "report_path": str(REPORT_PATH)},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if "ts" not in df.columns:
            return {
                "phase": 227,
                "status": "WARN",
                "details": "Timestamp column not found",
                "outputs": {"snapshots_analyzed": 0, "avg_latency_seconds": 0.0, "report_path": str(REPORT_PATH)},
                "errors": [],
            }

        # Parse timestamps
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"])

        # Estimate latency (if processing_time column exists, use it; otherwise estimate from file modification)
        if "processing_time" in df.columns:
            df["processing_time"] = pd.to_datetime(df["processing_time"], errors="coerce")
            df["latency_seconds"] = (df["processing_time"] - df["ts"]).dt.total_seconds()
        else:
            # Estimate based on file modification time (simplified)
            file_mtime = datetime.fromtimestamp(SIGNALS_CSV.stat().st_mtime)
            df["latency_seconds"] = (file_mtime - df["ts"]).dt.total_seconds()

        # Compute statistics
        latency_stats = df["latency_seconds"].describe()
        avg_latency = df["latency_seconds"].mean()

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Data Latency Profile\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Snapshots Analyzed**: {len(df)}\n\n")

            f.write("## Latency Statistics (seconds)\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Mean | {latency_stats['mean']:.2f} |\n")
            f.write(f"| Median | {latency_stats['50%']:.2f} |\n")
            f.write(f"| Min | {latency_stats['min']:.2f} |\n")
            f.write(f"| Max | {latency_stats['max']:.2f} |\n")
            f.write(f"| Std Dev | {latency_stats['std']:.2f} |\n")

        status = "OK"
        details = f"Profiled {len(df)} snapshots, avg latency: {avg_latency:.2f}s"

        return {
            "phase": 227,
            "status": status,
            "details": details,
            "outputs": {
                "snapshots_analyzed": len(df),
                "avg_latency_seconds": float(avg_latency),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 227,
            "status": "ERROR",
            "details": f"Phase 227 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 227 - DATA LATENCY PROFILER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase227()

    print(f"Phase 227: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Snapshots: {result['outputs']['snapshots_analyzed']}")
        print(f"Avg Latency: {result['outputs']['avg_latency_seconds']:.2f}s")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
