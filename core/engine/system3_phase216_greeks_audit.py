"""
System3 Phase 216 - Greeks Calculation Auditor

Verifies numerical stability of Greeks calculations.
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

LOG_DIR = PROJECT_ROOT / "logs" / "risk"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_greeks_audit_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
TOLERANCE = 0.1  # 10% deviation tolerance


def run_phase216(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 216: Greeks Calculation Auditor.

    Returns:
        dict: {
            "phase": 216,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "instruments_checked": int,
                "flagged_instruments": int,
            },
            "errors": [],
        }
    """
    errors = []
    flagged_instruments = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 216,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"instruments_checked": 0, "flagged_instruments": 0},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        # Check for Greeks columns
        greeks_cols = ["delta", "gamma", "theta", "vega"]
        available_greeks = [col for col in greeks_cols if col in df.columns]

        if len(available_greeks) == 0:
            return {
                "phase": 216,
                "status": "WARN",
                "details": "No Greeks columns found",
                "outputs": {"instruments_checked": 0, "flagged_instruments": 0},
                "errors": [],
            }

        # Check for numerical stability (NaN, Inf, extreme values)
        flagged = []
        for col in available_greeks:
            nan_count = df[col].isna().sum()
            inf_count = np.isinf(df[col]).sum()
            extreme_count = (df[col].abs() > 100).sum()  # Unrealistic values

            if nan_count > 0 or inf_count > 0 or extreme_count > 0:
                flagged.append(
                    {
                        "greeks": col,
                        "nan_count": nan_count,
                        "inf_count": inf_count,
                        "extreme_count": extreme_count,
                    }
                )

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Greeks Calculation Audit Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Instruments Checked**: {len(df)}\n")
            f.write(f"**Greeks Columns**: {', '.join(available_greeks)}\n\n")

            if flagged:
                f.write("## Issues Detected\n\n")
                f.write("| Greeks | NaN Count | Inf Count | Extreme Count |\n")
                f.write("|--------|-----------|-----------|---------------|\n")
                for item in flagged:
                    f.write(
                        f"| {item['greeks']} | {item['nan_count']} | "
                        f"{item['inf_count']} | {item['extreme_count']} |\n"
                    )
                f.write("\n⚠️ **WARNING**: Numerical stability issues detected.\n")
            else:
                f.write("## Status\n\n")
                f.write("✅ All Greeks calculations appear numerically stable.\n")

        status = "WARN" if flagged else "OK"
        details = f"Checked {len(df)} instruments, {len(flagged)} Greeks with issues"

        return {
            "phase": 216,
            "status": status,
            "details": details,
            "outputs": {
                "instruments_checked": len(df),
                "flagged_instruments": len(flagged),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 216,
            "status": "ERROR",
            "details": f"Phase 216 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 216 - GREEKS CALCULATION AUDITOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase216()

    print(f"Phase 216: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Checked: {result['outputs']['instruments_checked']}")
        print(f"Flagged: {result['outputs']['flagged_instruments']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
