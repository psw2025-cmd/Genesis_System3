"""
System3 Phase 220 - Cross-Underlying Correlation Map

Computes rolling correlations between major indices.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
CORRELATION_CSV = STORAGE_META / "system3_correlation_matrices.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_correlation_report.md"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def run_phase220(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 220: Cross-Underlying Correlation Map.

    Returns:
        dict: {
            "phase": 220,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "correlation_matrix_path": str,
                "underlyings_analyzed": int,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 220,
                "status": "WARN",
                "details": "Signals CSV not found - signal generation may not have run",
                "outputs": {"correlation_matrix_path": str(CORRELATION_CSV), "underlyings_analyzed": 0},
                "errors": ["STEP 4: Signal generation phase did not populate " + str(SIGNALS_CSV)],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if df.empty:
            return {
                "phase": 220,
                "status": "WARN",
                "details": "Signals CSV is empty - no signals to analyze",
                "outputs": {"correlation_matrix_path": str(CORRELATION_CSV), "underlyings_analyzed": 0},
                "errors": [
                    "STEP 4: Signals CSV contains only headers or is empty - check signal generation thresholds"
                ],
            }

        if "underlying" not in df.columns or "spot" not in df.columns:
            return {
                "phase": 220,
                "status": "WARN",
                "details": "Required columns not found",
                "outputs": {"correlation_matrix_path": str(CORRELATION_CSV), "underlyings_analyzed": 0},
                "errors": ["STEP 4: Signals CSV missing required columns (underlying, spot)"],
            }

        # Prepare price series by underlying
        price_series = {}
        for underlying in UNDERLYINGS:
            underlying_df = df[df["underlying"] == underlying]
            if len(underlying_df) > 0 and "spot" in underlying_df.columns:
                if "ts" in underlying_df.columns:
                    underlying_df = underlying_df.sort_values("ts")
                    price_series[underlying] = underlying_df["spot"].dropna()
                else:
                    price_series[underlying] = underlying_df["spot"].dropna()

        if len(price_series) < 2:
            return {
                "phase": 220,
                "status": "WARN",
                "details": "Insufficient data for correlation",
                "outputs": {"correlation_matrix_path": str(CORRELATION_CSV), "underlyings_analyzed": len(price_series)},
                "errors": [],
            }

        # Align series and compute correlation
        price_df = pd.DataFrame(price_series)

        # Filter out series with zero variance before correlation
        valid_cols = []
        for col in price_df.columns:
            if price_df[col].std() > 0 and not price_df[col].isna().all():
                valid_cols.append(col)

        if len(valid_cols) < 2:
            return {
                "phase": 220,
                "status": "WARN",
                "details": "Insufficient variance for correlation",
                "outputs": {"correlation_matrix_path": str(CORRELATION_CSV), "underlyings_analyzed": len(price_series)},
                "errors": [],
            }

        # Compute correlation only on valid columns
        price_df_valid = price_df[valid_cols]
        correlation_matrix = price_df_valid.corr()

        # Save correlation matrix
        correlation_matrix.to_csv(CORRELATION_CSV)

        # Detect special regimes
        high_corr_pairs = []
        low_corr_pairs = []
        for i, idx1 in enumerate(correlation_matrix.index):
            for j, idx2 in enumerate(correlation_matrix.columns):
                if i < j:  # Upper triangle only
                    corr = correlation_matrix.loc[idx1, idx2]
                    if corr > 0.9:
                        high_corr_pairs.append((idx1, idx2, corr))
                    elif corr < 0.3:
                        low_corr_pairs.append((idx1, idx2, corr))

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Cross-Underlying Correlation Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Underlyings Analyzed**: {len(price_series)}\n\n")

            f.write("## Correlation Matrix\n\n")
            f.write("| Underlying | " + " | ".join(correlation_matrix.columns) + " |\n")
            f.write("|" + "---|" * (len(correlation_matrix.columns) + 1) + "\n")
            for idx in correlation_matrix.index:
                f.write(
                    f"| {idx} | "
                    + " | ".join([f"{correlation_matrix.loc[idx, col]:.3f}" for col in correlation_matrix.columns])
                    + " |\n"
                )

            if high_corr_pairs:
                f.write("\n## High Correlation Pairs (>0.9)\n\n")
                for idx1, idx2, corr in high_corr_pairs:
                    f.write(f"- {idx1} ↔ {idx2}: {corr:.3f}\n")

            if low_corr_pairs:
                f.write("\n## Low Correlation Pairs (<0.3)\n\n")
                for idx1, idx2, corr in low_corr_pairs:
                    f.write(f"- {idx1} ↔ {idx2}: {corr:.3f}\n")

        status = "OK"
        details = f"Computed correlations for {len(price_series)} underlyings"

        return {
            "phase": 220,
            "status": status,
            "details": details,
            "outputs": {
                "correlation_matrix_path": str(CORRELATION_CSV),
                "underlyings_analyzed": len(price_series),
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 220,
            "status": "ERROR",
            "details": f"Phase 220 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 220 - CROSS-UNDERLYING CORRELATION MAP")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase220()

    print(f"Phase 220: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nCorrelation CSV: {result['outputs']['correlation_matrix_path']}")
        print(f"Underlyings: {result['outputs']['underlyings_analyzed']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
