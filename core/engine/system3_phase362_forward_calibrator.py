"""
System3 Phase 362 - Live Forward-Return Calibrator

Measures real-world predictive strength of signals using forward returns
and produces calibration metrics for thresholds.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def calibrate_forward_returns(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate calibration metrics from forward returns."""
    calibration = {}

    # Identify forward return columns
    fwd_cols = [col for col in df.columns if "fwd_ret" in col.lower() or "forward" in col.lower()]

    if not fwd_cols:
        return {"error": "No forward return columns found"}

    # Determine signal column
    signal_col = "signal" if "signal" in df.columns else ("pred_label" if "pred_label" in df.columns else None)

    if not signal_col:
        return {"error": "No signal column found"}

    # Group by signal type
    signal_groups = df.groupby(signal_col)

    for signal_type, group in signal_groups:
        signal_metrics = {"count": len(group), "horizons": {}}

        for fwd_col in fwd_cols:
            # Extract numeric values
            fwd_values = pd.to_numeric(group[fwd_col], errors="coerce").dropna()

            if len(fwd_values) == 0:
                continue

            # Calculate metrics
            horizon_metrics = {
                "mean_return": float(fwd_values.mean()),
                "median_return": float(fwd_values.median()),
                "std_return": float(fwd_values.std()),
                "win_rate": float((fwd_values > 0).sum() / len(fwd_values) * 100),
                "max_return": float(fwd_values.max()),
                "min_return": float(fwd_values.min()),
                "sample_size": len(fwd_values),
            }

            signal_metrics["horizons"][fwd_col] = horizon_metrics

        calibration[str(signal_type)] = signal_metrics

    # Calculate global calibration score
    total_win_rate = 0
    total_mean_return = 0
    count = 0

    for signal_type, metrics in calibration.items():
        for horizon, h_metrics in metrics.get("horizons", {}).items():
            total_win_rate += h_metrics["win_rate"]
            total_mean_return += h_metrics["mean_return"]
            count += 1

    if count > 0:
        calibration["global_score"] = {
            "avg_win_rate": total_win_rate / count,
            "avg_mean_return": total_mean_return / count,
            "overall_calibration": (total_win_rate / count + (total_mean_return / count * 1000)) / 2,
        }

    return calibration


def run_phase362(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 362: Live Forward-Return Calibrator.

    Returns:
        dict: Phase execution result
    """
    timestamp = datetime.now().isoformat()
    errors = []

    try:
        file_path = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"

        if not file_path.exists():
            return {
                "phase": 362,
                "status": "WARN",
                "details": "Forward return file not found",
                "outputs": {},
                "errors": ["File not found: dhan_index_ai_signals_with_forward.csv"],
            }

        # Load CSV
        df = pd.read_csv(file_path, on_bad_lines="skip", low_memory=False)

        if df.empty:
            return {
                "phase": 362,
                "status": "WARN",
                "details": "Forward return file is empty",
                "outputs": {},
                "errors": ["No data in forward return file"],
            }

        # Calibrate
        calibration = calibrate_forward_returns(df)

        if "error" in calibration:
            return {
                "phase": 362,
                "status": "ERROR",
                "details": calibration["error"],
                "outputs": {},
                "errors": [calibration["error"]],
            }

        # Prepare output
        output = {
            "phase": 362,
            "timestamp": timestamp,
            "file_analyzed": str(file_path.name),
            "total_rows": len(df),
            "calibration_metrics": calibration,
        }

        # Determine status
        global_score = calibration.get("global_score", {})
        avg_win_rate = global_score.get("avg_win_rate", 0)

        if avg_win_rate < 50:
            status = "WARN"
            message = f"Low win rate: {avg_win_rate:.1f}%"
        else:
            status = "OK"
            message = f"Win rate: {avg_win_rate:.1f}%"

        output["status"] = status
        output["status_message"] = message

        # Write JSON
        json_path = STORAGE_METRICS / "forward_calibration_362.json"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, default=str)

        # Write MD report
        md_path = REPORTS_DIR / "FORWARD_RETURN_CALIBRATION_362.md"
        with md_path.open("w", encoding="utf-8") as f:
            f.write("# FORWARD RETURN CALIBRATION — PHASE 362\n\n")
            f.write(f"**Generated:** {timestamp}  \n")
            f.write(f"**Status:** {status}  \n")
            f.write(f"**File:** {file_path.name}  \n")
            f.write(f"**Rows Analyzed:** {len(df)}  \n\n")

            if "global_score" in calibration:
                gs = calibration["global_score"]
                f.write("## Global Calibration Score\n\n")
                f.write(f"- **Average Win Rate:** {gs['avg_win_rate']:.2f}%\n")
                f.write(f"- **Average Mean Return:** {gs['avg_mean_return']:.4f}\n")
                f.write(f"- **Overall Calibration:** {gs['overall_calibration']:.2f}\n\n")

            f.write("## Signal Type Calibration\n\n")
            for signal_type, metrics in calibration.items():
                if signal_type == "global_score":
                    continue

                f.write(f"### {signal_type}\n\n")
                f.write(f"- **Sample Size:** {metrics.get('count', 0)}\n\n")

                if "horizons" in metrics:
                    for horizon, h_metrics in metrics["horizons"].items():
                        f.write(f"#### {horizon}\n\n")
                        f.write(f"- Mean Return: {h_metrics['mean_return']:.4f}\n")
                        f.write(f"- Median Return: {h_metrics['median_return']:.4f}\n")
                        f.write(f"- Std Dev: {h_metrics['std_return']:.4f}\n")
                        f.write(f"- Win Rate: {h_metrics['win_rate']:.2f}%\n")
                        f.write(f"- Max Return: {h_metrics['max_return']:.4f}\n")
                        f.write(f"- Min Return: {h_metrics['min_return']:.4f}\n\n")

        return {
            "phase": 362,
            "status": status,
            "details": message,
            "outputs": {
                "json": str(json_path),
                "report": str(md_path),
            },
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Phase 362 failed: {str(e)}"
        errors.append(error_msg)
        return {
            "phase": 362,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 362 - FORWARD RETURN CALIBRATION")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase362()

    print(f"Status: {result['status']}")
    print(f"Details: {result['details']}")

    if result.get("outputs"):
        print("\nOutputs:")
        for key, path in result["outputs"].items():
            print(f"  {key}: {path}")

    print("\n" + "=" * 70)

    return 0 if result["status"] in ["OK", "WARN"] else 1


if __name__ == "__main__":
    sys.exit(main())
