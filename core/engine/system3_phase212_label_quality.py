"""
System3 Phase 212 - Label Quality Inspector

Analyzes label distribution and quality.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_label_quality_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"


def run_phase212(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 212: Label Quality Inspector.

    Returns:
        dict: {
            "phase": 212,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "total_rows": int,
                "label_counts": dict,
                "imbalance_ratio": float,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 212,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"total_rows": 0, "label_counts": {}, "imbalance_ratio": 0.0},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        total_rows = len(df)

        if "pred_label" not in df.columns:
            return {
                "phase": 212,
                "status": "WARN",
                "details": "pred_label column not found",
                "outputs": {"total_rows": total_rows, "label_counts": {}, "imbalance_ratio": 0.0},
                "errors": [],
            }

        # Analyze label distribution
        label_counts = Counter(df["pred_label"].dropna())
        total_labels = sum(label_counts.values())

        if total_labels > 0:
            max_count = max(label_counts.values())
            min_count = min(label_counts.values()) if len(label_counts) > 1 else max_count
            imbalance_ratio = max_count / min_count if min_count > 0 else float("inf")
        else:
            imbalance_ratio = 0.0

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Label Quality Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Rows**: {total_rows}\n\n")

            f.write("## Label Distribution\n\n")
            f.write("| Label | Count | Percentage |\n")
            f.write("|-------|-------|------------|\n")
            for label, count in label_counts.most_common():
                pct = (count / total_labels * 100) if total_labels > 0 else 0
                f.write(f"| {label} | {count} | {pct:.2f}% |\n")

            f.write(f"\n**Imbalance Ratio**: {imbalance_ratio:.2f}\n\n")

            if imbalance_ratio > 10:
                f.write("⚠️ **WARNING**: Severe label imbalance detected.\n")
            else:
                f.write("✅ Label distribution is acceptable.\n")

        status = "WARN" if imbalance_ratio > 10 else "OK"
        details = f"Analyzed {total_rows} rows, imbalance ratio: {imbalance_ratio:.2f}"

        return {
            "phase": 212,
            "status": status,
            "details": details,
            "outputs": {
                "total_rows": total_rows,
                "label_counts": dict(label_counts),
                "imbalance_ratio": imbalance_ratio,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 212,
            "status": "ERROR",
            "details": f"Phase 212 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 212 - LABEL QUALITY INSPECTOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase212()

    print(f"Phase 212: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Total: {result['outputs']['total_rows']}")
        print(f"Imbalance: {result['outputs']['imbalance_ratio']:.2f}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
