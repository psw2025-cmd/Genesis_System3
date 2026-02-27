"""
System3 Phase 143 - Execution Quality & Fill Heatmap

Classifies execution quality based on slippage.
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
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

SLIPPAGE_CSV = STORAGE_ULTRA / "phase142_slippage_results.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase143_execution_quality.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase143_execution_quality.md"

# Slippage thresholds for quality classification
SLIPPAGE_THRESHOLDS = {
    "GOOD": 0.1,  # < 0.1% slippage
    "OK": 0.5,  # < 0.5% slippage
    "POOR": float("inf"),  # >= 0.5% slippage
}


def classify_quality(slippage_percent: float) -> str:
    """Classify execution quality based on slippage."""
    if slippage_percent < SLIPPAGE_THRESHOLDS["GOOD"]:
        return "GOOD"
    elif slippage_percent < SLIPPAGE_THRESHOLDS["OK"]:
        return "OK"
    else:
        return "POOR"


def run_phase143_execution_quality() -> Dict[str, Any]:
    """
    Classify execution quality from slippage data.

    Returns:
        dict: {
            "phase": 143,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load slippage results
        df_slippage = pd.DataFrame()
        if SLIPPAGE_CSV.exists():
            try:
                df_slippage = pd.read_csv(SLIPPAGE_CSV)
            except Exception as e:
                errors.append(f"Error reading slippage CSV: {e}")

        if df_slippage.empty:
            # Create empty result
            df_result = pd.DataFrame(columns=["local_order_id", "underlying", "slippage_percent", "execution_quality"])
            status = "OK"
            details = "No slippage data available, created empty quality file"
        else:
            # Classify quality
            df_result = df_slippage.copy()
            df_result["execution_quality"] = df_result["slippage_percent"].apply(classify_quality)

            # Compute metrics by underlying
            quality_metrics = {}
            for underlying in df_result["underlying"].unique():
                underlying_data = df_result[df_result["underlying"] == underlying]
                total = len(underlying_data)
                good_count = len(underlying_data[underlying_data["execution_quality"] == "GOOD"])
                ok_count = len(underlying_data[underlying_data["execution_quality"] == "OK"])
                poor_count = len(underlying_data[underlying_data["execution_quality"] == "POOR"])

                quality_metrics[underlying] = {
                    "total": total,
                    "good_fill_rate": (good_count / total * 100) if total > 0 else 0,
                    "ok_fill_rate": (ok_count / total * 100) if total > 0 else 0,
                    "poor_fill_rate": (poor_count / total * 100) if total > 0 else 0,
                }

            status = "OK"
            details = f"Execution quality classified: {len(df_result)} trades"

        # Save CSV
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)

        # Generate MD summary with heatmap-style table
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Execution Quality Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if quality_metrics:
                f.write("## Execution Quality Heatmap (by Underlying)\n\n")
                f.write("| Underlying | Total | GOOD % | OK % | POOR % |\n")
                f.write("|------------|-------|--------|------|--------|\n")
                for underlying, metrics in quality_metrics.items():
                    f.write(
                        f"| {underlying} | {metrics['total']} | {metrics['good_fill_rate']:.1f}% | {metrics['ok_fill_rate']:.1f}% | {metrics['poor_fill_rate']:.1f}% |\n"
                    )
            else:
                f.write("## Summary\n\n")
                f.write("No execution data available for quality analysis.\n")

        return {
            "phase": 143,
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
            "phase": 143,
            "status": "ERROR",
            "details": f"Phase 143 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 143 - EXECUTION QUALITY & FILL HEATMAP")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase143_execution_quality()

    print(f"Phase143: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nTrades analyzed: {result['outputs']['trade_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
