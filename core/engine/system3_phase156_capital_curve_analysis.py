"""
System3 Phase 156 - Capital Curve & Drawdown Analysis

Analyzes capital curve and drawdown from DRY-RUN PnL data.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase156_capital_curve.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase156_capital_curve_report.md"


def run_phase156_capital_curve_analysis(initial_capital: float = 50000.0) -> Dict[str, Any]:
    """
    Analyze capital curve and drawdown from DRY-RUN PnL.

    Args:
        initial_capital: Initial test capital in INR (default 50k)

    Returns:
        dict: {
            "phase": 156,
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
                # Sort by timestamp
                if "ts" in df_pnl.columns:
                    df_pnl = df_pnl.sort_values("ts")
            except Exception as e:
                errors.append(f"Error reading PnL log: {e}")

        if df_pnl.empty:
            # Create empty result
            df_result = pd.DataFrame(columns=["timestamp", "running_capital", "drawdown", "drawdown_percent"])
            status = "OK"
            details = "No PnL data available, created empty capital curve file"
        else:
            # Compute running capital
            capital_curve_rows = []
            running_capital = initial_capital
            peak_capital = initial_capital
            max_drawdown = 0.0
            max_drawdown_percent = 0.0

            for _, row in df_pnl.iterrows():
                timestamp = row.get("ts", datetime.now().isoformat())
                pnl_pct = float(row.get("pnl_pct", 0) or 0)

                # Update running capital
                running_capital = running_capital * (1 + pnl_pct / 100)

                # Update peak
                if running_capital > peak_capital:
                    peak_capital = running_capital

                # Calculate drawdown
                drawdown = peak_capital - running_capital
                drawdown_percent = (drawdown / peak_capital * 100) if peak_capital > 0 else 0

                # Track max drawdown
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_percent = drawdown_percent

                capital_curve_rows.append(
                    {
                        "timestamp": timestamp,
                        "running_capital": round(running_capital, 2),
                        "drawdown": round(drawdown, 2),
                        "drawdown_percent": round(drawdown_percent, 3),
                    }
                )

            df_result = pd.DataFrame(capital_curve_rows)

            # Calculate recovery periods (simplified)
            recovery_periods = []
            if len(df_result) > 1:
                # Count periods where drawdown decreases (recovery)
                in_recovery = False
                recovery_start = None
                for i, row in df_result.iterrows():
                    if row["drawdown"] > 0:
                        if not in_recovery:
                            in_recovery = True
                            recovery_start = row["timestamp"]
                    else:
                        if in_recovery:
                            recovery_periods.append(
                                {
                                    "start": recovery_start,
                                    "end": row["timestamp"],
                                }
                            )
                            in_recovery = False

            status = "OK"
            details = f"Capital curve analyzed: {len(df_result)} data points, max drawdown {max_drawdown_percent:.2f}%"

        # Save CSV
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Capital Curve & Drawdown Analysis\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if not df_result.empty:
                final_capital = df_result.iloc[-1]["running_capital"]
                f.write("## Summary\n\n")
                f.write(f"- **Initial Capital**: ₹{initial_capital:,.2f}\n")
                f.write(f"- **Final Capital**: ₹{final_capital:,.2f}\n")
                f.write(f"- **Max Drawdown**: ₹{max_drawdown:,.2f} ({max_drawdown_percent:.2f}%)\n")
                f.write(f"- **Recovery Periods**: {len(recovery_periods)}\n")
            else:
                f.write("## Summary\n\n")
                f.write("No PnL data available for capital curve analysis.\n")

        return {
            "phase": 156,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "data_points": len(df_result),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 156,
            "status": "ERROR",
            "details": f"Phase 156 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="System3 Phase 156 - Capital Curve & Drawdown Analysis")
    parser.add_argument("--initial-capital", type=float, default=50000.0, help="Initial test capital in INR")
    args = parser.parse_args()

    print("=" * 70)
    print("SYSTEM3 PHASE 156 - CAPITAL CURVE & DRAWDOWN ANALYSIS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase156_capital_curve_analysis(initial_capital=args.initial_capital)

    print(f"Phase156: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nData points: {result['outputs']['data_points']}")
        print(f"CSV: {result['outputs']['csv_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
