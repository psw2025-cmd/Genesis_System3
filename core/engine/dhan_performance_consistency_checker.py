"""
Dhan Index Options - Performance Consistency Checker

Evaluates consistency of signals across time and underlyings.
Heatmap & stats - read-only analysis.
SAFE MODE ONLY - Read-only evaluation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from core.engine.dhan_unified_outcome_logger_v3 import get_outcome_stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def check_performance_consistency() -> Dict[str, Any]:
    """
    Evaluate consistency of signals.

    Generates heatmap & stats.
    Read-only analysis.

    Returns:
        Dict with consistency analysis
    """
    print("=== ANGEL ONE INDEX OPTIONS - PERFORMANCE CONSISTENCY CHECKER ===")
    print("[INFO] SAFE MODE - Read-only evaluation\n")

    if not REAL_OUTCOMES_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    try:
        df = pd.read_csv(REAL_OUTCOMES_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Outcomes CSV is empty",
            }

        consistency_results = {}

        # Consistency by underlying
        if "underlying" in df.columns and "pnl_pct" in df.columns:
            underlying_consistency = {}
            for underlying in df["underlying"].unique():
                df_u = df[df["underlying"] == underlying]
                if len(df_u) < 2:
                    continue

                pnl_std = df_u["pnl_pct"].std()
                pnl_mean = df_u["pnl_pct"].mean()
                consistency_score = 1.0 / (1.0 + pnl_std) if pnl_std > 0 else 1.0

                underlying_consistency[underlying] = {
                    "count": len(df_u),
                    "mean_pnl": float(pnl_mean),
                    "std_pnl": float(pnl_std),
                    "consistency_score": float(consistency_score),
                }

            consistency_results["by_underlying"] = underlying_consistency

        # Consistency by confidence bucket
        if "entry_confidence" in df.columns and "pnl_pct" in df.columns:
            df["conf_bucket"] = pd.cut(
                df["entry_confidence"],
                bins=[0, 0.7, 0.8, 0.9, 1.0],
                labels=["0.7-0.8", "0.8-0.9", "0.9-1.0", "1.0"],
            )

            confidence_consistency = {}
            for bucket in df["conf_bucket"].unique():
                if pd.isna(bucket):
                    continue
                subset = df[df["conf_bucket"] == bucket]
                if len(subset) < 2:
                    continue

                pnl_std = subset["pnl_pct"].std()
                consistency_score = 1.0 / (1.0 + pnl_std) if pnl_std > 0 else 1.0

                confidence_consistency[str(bucket)] = {
                    "count": len(subset),
                    "mean_pnl": float(subset["pnl_pct"].mean()),
                    "std_pnl": float(pnl_std),
                    "consistency_score": float(consistency_score),
                }

            consistency_results["by_confidence"] = confidence_consistency

        # Overall consistency
        if "pnl_pct" in df.columns:
            overall_std = df["pnl_pct"].std()
            overall_consistency = 1.0 / (1.0 + overall_std) if overall_std > 0 else 1.0
            consistency_results["overall"] = {
                "consistency_score": float(overall_consistency),
                "std_pnl": float(overall_std),
                "mean_pnl": float(df["pnl_pct"].mean()),
            }

        return {
            "status": "SUCCESS",
            "consistency_results": consistency_results,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def generate_consistency_heatmap(consistency_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate consistency heatmap data.

    Returns:
        Dict with heatmap data (JSON-serializable)
    """
    heatmap_data = {}

    if "by_underlying" in consistency_results:
        heatmap_data["underlying"] = {}
        for u, data in consistency_results["by_underlying"].items():
            heatmap_data["underlying"][u] = {
                "consistency": data["consistency_score"],
                "mean_pnl": data["mean_pnl"],
            }

    if "by_confidence" in consistency_results:
        heatmap_data["confidence"] = {}
        for bucket, data in consistency_results["by_confidence"].items():
            heatmap_data["confidence"][bucket] = {
                "consistency": data["consistency_score"],
                "mean_pnl": data["mean_pnl"],
            }

    return heatmap_data


def save_consistency_report(analysis: Dict[str, Any]) -> Path:
    """
    Save consistency report to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = REPORTS_DIR / f"performance_consistency_{today}.json"

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "analysis": analysis,
        "heatmap": generate_consistency_heatmap(analysis.get("consistency_results", {})),
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    analysis = check_performance_consistency()

    if analysis["status"] == "SUCCESS":
        results = analysis["consistency_results"]

        print("=== PERFORMANCE CONSISTENCY ANALYSIS ===\n")

        if "overall" in results:
            overall = results["overall"]
            print(f"Overall Consistency Score: {overall['consistency_score']:.3f}")
            print(f"Overall Mean PnL: {overall['mean_pnl']:.2f}%")
            print(f"Overall Std PnL: {overall['std_pnl']:.2f}%")

        if "by_underlying" in results:
            print("\n=== CONSISTENCY BY UNDERLYING ===")
            for u, data in results["by_underlying"].items():
                print(f"{u}:")
                print(f"  Consistency: {data['consistency_score']:.3f}")
                print(f"  Mean PnL: {data['mean_pnl']:.2f}%")
                print(f"  Std PnL: {data['std_pnl']:.2f}%")
                print(f"  Count: {data['count']}")

        if "by_confidence" in results:
            print("\n=== CONSISTENCY BY CONFIDENCE BUCKET ===")
            for bucket, data in results["by_confidence"].items():
                print(f"{bucket}:")
                print(f"  Consistency: {data['consistency_score']:.3f}")
                print(f"  Mean PnL: {data['mean_pnl']:.2f}%")
                print(f"  Count: {data['count']}")

        # Save report
        save_path = save_consistency_report(analysis)
        print(f"\n[SAVE] Consistency report saved to: {save_path}")
        print("[NOTE] Heatmap data included in JSON file.")
    else:
        print(f"[INFO] {analysis.get('message', 'Consistency analysis not available')}")


if __name__ == "__main__":
    main()
