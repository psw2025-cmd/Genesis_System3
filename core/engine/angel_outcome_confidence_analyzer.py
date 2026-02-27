"""
Angel One Index Options - Outcome Confidence Curve Analyzer

Analyzes confidence vs actual outcomes to shape confidence curves.
SAFE MODE ONLY - Read-only analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from core.engine.angel_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def analyze_confidence_curve() -> Dict[str, Any]:
    """
    Analyze confidence curve vs actual outcomes.

    Returns:
        Dict with confidence curve analysis
    """
    df = load_outcomes()
    if df.empty:
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    if "signal_confidence" not in df.columns or "pnl_pct" not in df.columns:
        return {
            "status": "INCOMPLETE_DATA",
            "message": "Missing confidence or PnL data",
        }

    # Create confidence buckets
    df["conf_bucket"] = pd.cut(
        df["signal_confidence"],
        bins=[0, 0.6, 0.7, 0.8, 0.9, 1.0],
        labels=["0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0", "1.0"],
    )

    curve_analysis = {}

    for bucket in df["conf_bucket"].unique():
        if pd.isna(bucket):
            continue

        subset = df[df["conf_bucket"] == bucket]
        if len(subset) == 0:
            continue

        avg_pnl = subset["pnl_pct"].mean()
        win_rate = (subset["pnl_pct"] > 0).sum() / len(subset) * 100
        avg_confidence = subset["signal_confidence"].mean()

        curve_analysis[str(bucket)] = {
            "count": len(subset),
            "avg_confidence": float(avg_confidence),
            "avg_pnl": float(avg_pnl),
            "win_rate": float(win_rate),
        }

    # Compute calibration metrics
    calibration_score = _compute_calibration_score(df)

    return {
        "status": "SUCCESS",
        "curve_analysis": curve_analysis,
        "calibration_score": calibration_score,
        "recommendations": _generate_confidence_recommendations(curve_analysis),
    }


def _compute_calibration_score(df: pd.DataFrame) -> float:
    """Compute overall calibration score."""
    # Simplified: correlation between confidence and win rate
    if len(df) < 10:
        return 0.0

    df["conf_bucket"] = pd.cut(
        df["signal_confidence"],
        bins=[0, 0.7, 0.8, 0.9, 1.0],
        labels=["0.7-0.8", "0.8-0.9", "0.9-1.0", "1.0"],
    )

    bucket_win_rates = []
    bucket_confidences = []

    for bucket in df["conf_bucket"].unique():
        if pd.isna(bucket):
            continue
        subset = df[df["conf_bucket"] == bucket]
        if len(subset) > 0:
            win_rate = (subset["pnl_pct"] > 0).sum() / len(subset)
            avg_conf = subset["signal_confidence"].mean()
            bucket_win_rates.append(win_rate)
            bucket_confidences.append(avg_conf)

    if len(bucket_win_rates) < 2:
        return 0.0

    correlation = np.corrcoef(bucket_confidences, bucket_win_rates)[0, 1]
    return float(correlation) if not np.isnan(correlation) else 0.0


def _generate_confidence_recommendations(curve_analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on confidence curve."""
    recommendations = []

    if not curve_analysis:
        return ["Insufficient data for recommendations"]

    # Check if higher confidence = better outcomes
    buckets = sorted(curve_analysis.keys())
    if len(buckets) >= 2:
        first_bucket = curve_analysis[buckets[0]]
        last_bucket = curve_analysis[buckets[-1]]

        if last_bucket["win_rate"] > first_bucket["win_rate"]:
            recommendations.append("Confidence curve is well-calibrated (higher confidence = better outcomes)")
        else:
            recommendations.append(
                "Confidence curve may need recalibration (higher confidence not correlating with better outcomes)"
            )

    return recommendations


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - OUTCOME CONFIDENCE CURVE ANALYZER ===")
    print("[INFO] SAFE MODE - Read-only analysis\n")

    analysis = analyze_confidence_curve()

    if analysis["status"] == "SUCCESS":
        print("=== CONFIDENCE CURVE ANALYSIS ===\n")

        for bucket, data in analysis["curve_analysis"].items():
            print(f"Confidence {bucket}:")
            print(f"  Trades: {data['count']}")
            print(f"  Avg Confidence: {data['avg_confidence']:.3f}")
            print(f"  Avg PnL: {data['avg_pnl']:.2f}%")
            print(f"  Win Rate: {data['win_rate']:.1f}%")
            print()

        print(f"Calibration Score: {analysis['calibration_score']:.3f}")
        print("(Higher = better calibration between confidence and outcomes)")

        if analysis["recommendations"]:
            print("\n=== RECOMMENDATIONS ===")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
    else:
        print(f"[INFO] {analysis.get('message', 'Analysis not available')}")


if __name__ == "__main__":
    main()
