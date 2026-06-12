"""
System3 Phase 157 - Misfire Breakdown Analysis

Analyzes misfires (failed predictions) from DRY-RUN data.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase157_misfire_breakdown.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase157_misfire_breakdown_report.md"


def run_phase157_misfire_breakdown() -> Dict[str, Any]:
    """
    Analyze misfires from PnL log.

    Returns:
        dict: {
            "phase": 157,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load PnL log
        df_pnl = pd.DataFrame()
        if PNL_LOG_CSV.exists():
            try:
                df_pnl = pd.read_csv(PNL_LOG_CSV)
            except Exception as e:
                errors.append(f"Error reading PnL log: {e}")

        if df_pnl.empty:
            df_result = pd.DataFrame(columns=["underlying", "pred_label", "result", "misfire_type", "pnl_pct"])
            status = "OK"
            details = "No PnL data available, created empty misfire breakdown"
        else:
            # Classify misfires
            misfire_rows = []
            for _, row in df_pnl.iterrows():
                underlying = row.get("underlying", "")
                pred_label = row.get("pred_label", "")
                result = row.get("result", "")
                pnl_pct = float(row.get("pnl_pct", 0) or 0)

                # Determine misfire type
                misfire_type = "NONE"
                if pred_label in ["BUY_CE", "BUY_PE"]:
                    if pnl_pct < -1.0:  # Loss > 1%
                        misfire_type = "LOSS"
                    elif result == "NO_DATA":
                        misfire_type = "NO_DATA"

                misfire_rows.append(
                    {
                        "underlying": underlying,
                        "pred_label": pred_label,
                        "result": result,
                        "misfire_type": misfire_type,
                        "pnl_pct": pnl_pct,
                    }
                )

            df_result = pd.DataFrame(misfire_rows)
            status = "OK"
            details = f"Misfire breakdown: {len(df_result)} trades analyzed"

        # Save CSV
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Misfire Breakdown Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if not df_result.empty:
                misfire_count = len(df_result[df_result["misfire_type"] != "NONE"])
                f.write(f"## Summary\n\n")
                f.write(f"- **Total Trades**: {len(df_result)}\n")
                f.write(f"- **Misfires**: {misfire_count}\n")
                f.write(f"- **Misfire Rate**: {(misfire_count / len(df_result) * 100):.2f}%\n")
            else:
                f.write("## Summary\n\n")
                f.write("No trade data available for misfire analysis.\n")

        return {
            "phase": 157,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "trade_count": len(df_result),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 157,
            "status": "ERROR",
            "details": f"Phase 157 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 157 - MISFIRE BREAKDOWN")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase157_misfire_breakdown()

    print(f"Phase157: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nTrades: {result['outputs']['trade_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
