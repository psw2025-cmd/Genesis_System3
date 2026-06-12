"""
System3 Phase 208 - Signal Consistency Engine

Validates signal consistency and auto-corrects contradictions.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "signals"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_signal_consistency_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"


def run_phase208(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 208: Signal Consistency Engine.

    Returns:
        dict: {
            "phase": 208,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "total_rows": int,
                "inconsistent_rows": int,
                "fixed_rows": int,
            },
            "errors": [],
        }
    """
    errors = []
    inconsistent_rows = 0
    fixed_rows = 0

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 208,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"total_rows": 0, "inconsistent_rows": 0, "fixed_rows": 0},
                "errors": [],
            }

        # Load with robust parser
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        total_rows = len(df)

        # Check for impossible combinations
        if "pred_label" in df.columns and "final_score" in df.columns:
            # BUY with very negative score
            buy_negative = (df["pred_label"] == "BUY") & (df["final_score"] < -0.5)
            # SELL with very positive score
            sell_positive = (df["pred_label"] == "SELL") & (df["final_score"] > 0.5)

            inconsistent_mask = buy_negative | sell_positive
            inconsistent_rows = inconsistent_mask.sum()

            # Auto-correct based on final_score
            if inconsistent_rows > 0:
                df.loc[buy_negative, "pred_label"] = "SELL"
                df.loc[sell_positive, "pred_label"] = "BUY"
                fixed_rows = inconsistent_rows

        # Check for duplicate (ts, underlying, strike, side) with different signals
        if all(col in df.columns for col in ["ts", "underlying", "strike", "side", "pred_label"]):
            duplicates = df.groupby(["ts", "underlying", "strike", "side"]).size()
            dup_keys = duplicates[duplicates > 1].index
            if len(dup_keys) > 0:
                for key in dup_keys:
                    subset = df[
                        (df["ts"] == key[0])
                        & (df["underlying"] == key[1])
                        & (df["strike"] == key[2])
                        & (df["side"] == key[3])
                    ]
                    if "final_score" in df.columns:
                        # Keep row with highest absolute final_score
                        best_idx = subset["final_score"].abs().idxmax()
                        df = df.drop(subset.index[subset.index != best_idx])
                        fixed_rows += len(subset) - 1

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Signal Consistency Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Rows**: {total_rows}\n")
            f.write(f"**Inconsistent Rows**: {inconsistent_rows}\n")
            f.write(f"**Fixed Rows**: {fixed_rows}\n\n")

            if inconsistent_rows > 0:
                f.write("## Corrections Applied\n\n")
                f.write("- Auto-corrected contradictory signal labels based on final_score\n")
                f.write("- Removed duplicate entries, keeping highest confidence\n")
            else:
                f.write("## Status\n\n")
                f.write("✅ All signals are consistent.\n")

        status = "OK" if inconsistent_rows == 0 else "WARN"
        details = f"Checked {total_rows} rows"
        if inconsistent_rows > 0:
            details += f", fixed {fixed_rows} inconsistencies"

        return {
            "phase": 208,
            "status": status,
            "details": details,
            "outputs": {
                "total_rows": total_rows,
                "inconsistent_rows": inconsistent_rows,
                "fixed_rows": fixed_rows,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 208,
            "status": "ERROR",
            "details": f"Phase 208 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 208 - SIGNAL CONSISTENCY ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase208()

    print(f"Phase 208: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Total: {result['outputs']['total_rows']}")
        print(f"Inconsistent: {result['outputs']['inconsistent_rows']}")
        print(f"Fixed: {result['outputs']['fixed_rows']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
