"""
System3 Phase 222 - Signal Edge Estimator

Estimates expected value of BUY/SELL signals.
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

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_signal_edge_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"


def run_phase222(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 222: Signal Edge Estimator.

    Returns:
        dict: {
            "phase": 222,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "ev_tables_created": int,
                "report_path": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            # Fallback to regular signals CSV
            SIGNALS_CSV_FALLBACK = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
            if not SIGNALS_CSV_FALLBACK.exists():
                return {
                    "phase": 222,
                    "status": "WARN",
                    "details": "Signals CSV with forward returns not found",
                    "outputs": {"ev_tables_created": 0, "report_path": str(REPORT_PATH)},
                    "errors": [],
                }
            signals_file = SIGNALS_CSV_FALLBACK
        else:
            signals_file = SIGNALS_CSV

        # Load data with robust CSV loading (handles schema evolution gracefully)
        try:
            df = pd.read_csv(signals_file, engine="python", on_bad_lines="skip")
        except Exception as e:
            errors.append(f"Failed to load signals CSV: {e}")
            return {
                "phase": 222,
                "status": "ERROR",
                "details": f"Failed to load signals CSV: {e}",
                "outputs": {"ev_tables_created": 0, "report_path": str(REPORT_PATH)},
                "errors": errors,
            }

        if len(df) == 0:
            return {
                "phase": 222,
                "status": "WARN",
                "details": "No data to analyze",
                "outputs": {"ev_tables_created": 0, "report_path": str(REPORT_PATH)},
                "errors": [],
            }

        # Check for forward returns (use fwd_ret_1, fwd_ret_3, fwd_ret_5)
        forward_cols = [col for col in df.columns if col.startswith("fwd_ret_")]
        if len(forward_cols) == 0:
            # Try old naming convention
            forward_cols = [col for col in df.columns if col.startswith("forward_return")]

        if len(forward_cols) == 0:
            return {
                "phase": 222,
                "status": "WARN",
                "details": "Forward returns not available (run Phase 221 first)",
                "outputs": {"ev_tables_created": 0, "report_path": str(REPORT_PATH)},
                "errors": [],
            }

        # Ensure we have required columns
        if "underlying" not in df.columns or "final_score" not in df.columns:
            return {
                "phase": 222,
                "status": "WARN",
                "details": "Missing required columns (underlying, final_score)",
                "outputs": {"ev_tables_created": 0, "report_path": str(REPORT_PATH)},
                "errors": [],
            }

        # Convert final_score to numeric
        df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")

        # Define score bins: [-1.0, -0.5), [-0.5, -0.3), [-0.3, -0.1), [-0.1, 0.1), [0.1, 0.3), [0.3, 0.5), [0.5, 1.0]
        bins = [-1.0, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 1.0]
        bin_labels = [
            "[-1.0, -0.5)",
            "[-0.5, -0.3)",
            "[-0.3, -0.1)",
            "[-0.1, 0.1)",
            "[0.1, 0.3)",
            "[0.3, 0.5)",
            "[0.5, 1.0]",
        ]

        # Filter out NaN final_score values before binning
        df_valid = df[df["final_score"].notna()].copy()
        if len(df_valid) == 0:
            return {
                "phase": 222,
                "status": "WARN",
                "details": "No valid final_score values found",
                "outputs": {"ev_tables_created": 0, "report_path": str(REPORT_PATH)},
                "errors": [],
            }

        df_valid["score_bin"] = pd.cut(df_valid["final_score"], bins=bins, labels=bin_labels, include_lowest=True)

        # Compute EV by underlying and score bin
        ev_tables = []

        for underlying in df_valid["underlying"].unique():
            underlying_df = df_valid[df_valid["underlying"] == underlying]

            for bin_label in bin_labels:
                bin_df = underlying_df[underlying_df["score_bin"] == bin_label]
                if len(bin_df) == 0:
                    continue

                # Compute metrics for each forward return horizon
                for fwd_col in forward_cols:
                    horizon = fwd_col.replace("fwd_ret_", "").replace("forward_return_", "")

                    # Filter out NaN forward returns and ensure numeric
                    valid_df = bin_df[bin_df[fwd_col].notna()].copy()
                    if len(valid_df) == 0:
                        continue

                    # Convert forward return column to numeric
                    valid_df[fwd_col] = pd.to_numeric(valid_df[fwd_col], errors="coerce")
                    valid_df = valid_df[valid_df[fwd_col].notna()]

                    if len(valid_df) == 0:
                        continue

                    # Average forward return
                    avg_return = float(valid_df[fwd_col].mean())

                    # Trade count
                    trade_count = len(valid_df)

                    # Hit-rate (percentage of positive forward returns)
                    positive_count = (valid_df[fwd_col] > 0).sum()
                    hit_rate = (positive_count / trade_count * 100.0) if trade_count > 0 else 0.0

                    ev_tables.append(
                        {
                            "underlying": underlying,
                            "score_bin": bin_label,
                            "horizon": horizon,
                            "avg_forward_return": avg_return,
                            "trade_count": trade_count,
                            "hit_rate": hit_rate,
                        }
                    )

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Signal Edge Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**EV Tables Created**: {len(ev_tables)}\n\n")

            if ev_tables:
                # Group by underlying for better readability
                for underlying in sorted(df_valid["underlying"].unique()):
                    underlying_evs = [ev for ev in ev_tables if ev["underlying"] == underlying]
                    if not underlying_evs:
                        continue

                    f.write(f"## {underlying}\n\n")

                    # Group by horizon
                    for horizon in ["1", "3", "5"]:
                        horizon_evs = [ev for ev in underlying_evs if ev["horizon"] == horizon]
                        if not horizon_evs:
                            continue

                        f.write(f"### Forward Return Horizon: {horizon} snapshot(s)\n\n")
                        f.write("| Score Bin | Avg Forward Return | Trade Count | Hit Rate (%) |\n")
                        f.write("|-----------|-------------------|-------------|-------------|\n")

                        # Sort by score bin (low to high)
                        def get_bin_start(ev_item):
                            try:
                                bin_str = str(ev_item["score_bin"])
                                start_str = bin_str.split(",")[0].replace("[", "").replace("(", "")
                                return float(start_str)
                            except:
                                return 0.0

                        sorted_evs = sorted(horizon_evs, key=get_bin_start)
                        for ev in sorted_evs:
                            f.write(
                                f"| {ev['score_bin']} | {ev['avg_forward_return']:.4f} | "
                                f"{ev['trade_count']} | {ev['hit_rate']:.2f}% |\n"
                            )
                        f.write("\n")
            else:
                f.write("## Status\n\n")
                f.write("⚠️ No EV tables generated (insufficient data or no forward returns).\n")

        status = "OK" if ev_tables else "WARN"
        details = f"Created {len(ev_tables)} EV tables"

        return {
            "phase": 222,
            "status": status,
            "details": details,
            "outputs": {
                "ev_tables_created": len(ev_tables),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 222,
            "status": "ERROR",
            "details": f"Phase 222 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 222 - SIGNAL EDGE ESTIMATOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase222()

    print(f"Phase 222: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"EV Tables: {result['outputs']['ev_tables_created']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
