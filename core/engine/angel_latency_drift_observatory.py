"""
Angel One Index Options - Latency Drift Observatory

Latency / drift detection.
Plots or JSON outputs.
SAFE MODE ONLY - Read-only observation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
ULTRA_OBS_DIR = REPORTS_DIR / "ultra_obs"

ULTRA_OBS_DIR.mkdir(parents=True, exist_ok=True)


def analyze_latency_drift() -> Dict[str, Any]:
    """
    Analyze latency and drift in signals.

    Read-only observation.

    Returns:
        Dict with latency/drift analysis
    """
    print("=== ANGEL ONE INDEX OPTIONS - LATENCY DRIFT OBSERVATORY ===")
    print("[INFO] SAFE MODE - Read-only observation\n")

    if not SIGNALS_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "Signals CSV not found",
        }

    try:
        df = pd.read_csv(SIGNALS_CSV)

        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Signals CSV is empty",
            }

        # Parse timestamps
        timestamp_col = None
        for col in ["timestamp", "ts", "time"]:
            if col in df.columns:
                timestamp_col = col
                break

        if timestamp_col is None:
            return {
                "status": "NO_TIMESTAMP",
                "message": "No timestamp column found",
            }

        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
        df = df.dropna(subset=[timestamp_col])
        df = df.sort_values(timestamp_col)

        # Calculate latency (time between consecutive signals)
        df["time_diff"] = df[timestamp_col].diff()
        latencies = df["time_diff"].dropna().dt.total_seconds()

        # Latency statistics
        latency_stats = {
            "mean_seconds": float(latencies.mean()) if len(latencies) > 0 else 0.0,
            "median_seconds": float(latencies.median()) if len(latencies) > 0 else 0.0,
            "std_seconds": float(latencies.std()) if len(latencies) > 0 else 0.0,
            "min_seconds": float(latencies.min()) if len(latencies) > 0 else 0.0,
            "max_seconds": float(latencies.max()) if len(latencies) > 0 else 0.0,
        }

        # Detect latency drift (increasing latency over time)
        if len(latencies) >= 10:
            first_half = latencies.iloc[: len(latencies) // 2].mean()
            second_half = latencies.iloc[len(latencies) // 2 :].mean()
            drift_ratio = (second_half - first_half) / (first_half + 1e-10)
            latency_drift = {
                "detected": abs(drift_ratio) > 0.2,
                "drift_ratio": float(drift_ratio),
                "first_half_mean": float(first_half),
                "second_half_mean": float(second_half),
                "severity": _classify_drift_severity(abs(drift_ratio)),
            }
        else:
            latency_drift = {
                "detected": False,
                "message": "Insufficient data for drift detection",
            }

        # Signal distribution over time
        df["hour"] = df[timestamp_col].dt.hour
        hourly_counts = df["hour"].value_counts().sort_index().to_dict()

        # Confidence drift (if confidence column exists)
        confidence_drift = {}
        if "pred_confidence" in df.columns:
            conf_values = df["pred_confidence"].dropna()
            if len(conf_values) >= 10:
                first_half_conf = conf_values.iloc[: len(conf_values) // 2].mean()
                second_half_conf = conf_values.iloc[len(conf_values) // 2 :].mean()
                conf_drift_ratio = (second_half_conf - first_half_conf) / (first_half_conf + 1e-10)
                confidence_drift = {
                    "detected": abs(conf_drift_ratio) > 0.1,
                    "drift_ratio": float(conf_drift_ratio),
                    "first_half_mean": float(first_half_conf),
                    "second_half_mean": float(second_half_conf),
                }

        return {
            "status": "SUCCESS",
            "total_signals": len(df),
            "time_span": {
                "start": df[timestamp_col].min().isoformat(),
                "end": df[timestamp_col].max().isoformat(),
            },
            "latency_stats": latency_stats,
            "latency_drift": latency_drift,
            "confidence_drift": confidence_drift,
            "hourly_distribution": hourly_counts,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def _classify_drift_severity(drift_ratio: float) -> str:
    """Classify drift severity."""
    if drift_ratio > 0.5:
        return "CRITICAL"
    elif drift_ratio > 0.3:
        return "HIGH"
    elif drift_ratio > 0.2:
        return "MEDIUM"
    else:
        return "LOW"


def save_latency_drift_analysis(analysis: Dict[str, Any]) -> Path:
    """
    Save latency/drift analysis to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = ULTRA_OBS_DIR / f"latency_drift_{today}.json"

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "analysis": analysis,
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    analysis = analyze_latency_drift()

    if analysis["status"] == "SUCCESS":
        print("=== LATENCY & DRIFT ANALYSIS ===\n")

        print(f"Total Signals: {analysis['total_signals']}")
        print(f"Time Span: {analysis['time_span']['start']} to {analysis['time_span']['end']}")

        print("\n=== LATENCY STATISTICS ===")
        stats = analysis["latency_stats"]
        print(f"Mean: {stats['mean_seconds']:.2f} seconds")
        print(f"Median: {stats['median_seconds']:.2f} seconds")
        print(f"Std Dev: {stats['std_seconds']:.2f} seconds")
        print(f"Min: {stats['min_seconds']:.2f} seconds")
        print(f"Max: {stats['max_seconds']:.2f} seconds")

        print("\n=== LATENCY DRIFT ===")
        drift = analysis["latency_drift"]
        if drift.get("detected"):
            print(f"⚠️  Drift Detected: {drift['severity']}")
            print(f"   Drift Ratio: {drift['drift_ratio']:.3f}")
            print(f"   First Half Mean: {drift['first_half_mean']:.2f}s")
            print(f"   Second Half Mean: {drift['second_half_mean']:.2f}s")
        else:
            print("✅ No significant latency drift detected")

        if analysis.get("confidence_drift"):
            print("\n=== CONFIDENCE DRIFT ===")
            conf_drift = analysis["confidence_drift"]
            if conf_drift.get("detected"):
                print(f"⚠️  Confidence Drift Detected")
                print(f"   Drift Ratio: {conf_drift['drift_ratio']:.3f}")
            else:
                print("✅ No significant confidence drift detected")

        # Save
        save_path = save_latency_drift_analysis(analysis)
        print(f"\n[SAVE] Latency/drift analysis saved to: {save_path}")
        print("\n[NOTE] This is read-only observation. No changes made.")
    else:
        print(f"[INFO] {analysis.get('message', 'Analysis not available')}")


if __name__ == "__main__":
    main()
