"""
Dhan Index Options - Signal vs Outcome Analyzer

Analyzes signal quality vs actual outcomes.
AUTO-UPDATE: DISABLED - Only analyzes and reports.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from core.engine.dhan_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def analyze_signal_vs_outcome() -> Dict[str, Any]:
    """
    Analyze signal quality vs actual outcomes.

    Returns:
        Dict with analysis results
    """
    df = load_outcomes()
    if df.empty:
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    # PnL vs confidence buckets
    confidence_buckets = _analyze_pnl_by_confidence(df)

    # PnL vs score buckets
    score_buckets = _analyze_pnl_by_score(df)

    # PnL vs moneyness/ATM distance
    moneyness_analysis = _analyze_pnl_by_moneyness(df)

    # Confusion-like table: signal vs actual direction
    confusion_table = _build_confusion_table(df)

    return {
        "status": "SUCCESS",
        "confidence_buckets": confidence_buckets,
        "score_buckets": score_buckets,
        "moneyness_analysis": moneyness_analysis,
        "confusion_table": confusion_table,
    }


def _analyze_pnl_by_confidence(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze PnL by confidence buckets."""
    if "signal_confidence" not in df.columns or "pnl_pct" not in df.columns:
        return {}

    df["conf_bucket"] = pd.cut(
        df["signal_confidence"],
        bins=[0, 0.7, 0.8, 0.9, 1.0],
        labels=["0.7-0.8", "0.8-0.9", "0.9-1.0", "1.0"],
    )

    bucket_stats = {}
    for bucket in df["conf_bucket"].unique():
        if pd.isna(bucket):
            continue
        subset = df[df["conf_bucket"] == bucket]
        bucket_stats[str(bucket)] = {
            "count": len(subset),
            "avg_pnl": float(subset["pnl_pct"].mean()) if len(subset) > 0 else 0.0,
            "win_rate": float((subset["pnl_pct"] > 0).sum() / len(subset) * 100) if len(subset) > 0 else 0.0,
        }

    return bucket_stats


def _analyze_pnl_by_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze PnL by score buckets."""
    if "score" not in df.columns or "pnl_pct" not in df.columns:
        return {}

    df["score_bucket"] = pd.cut(
        df["score"].abs(),
        bins=[0, 0.2, 0.3, 0.4, 1.0],
        labels=["0.0-0.2", "0.2-0.3", "0.3-0.4", "0.4+"],
    )

    bucket_stats = {}
    for bucket in df["score_bucket"].unique():
        if pd.isna(bucket):
            continue
        subset = df[df["score_bucket"] == bucket]
        bucket_stats[str(bucket)] = {
            "count": len(subset),
            "avg_pnl": float(subset["pnl_pct"].mean()) if len(subset) > 0 else 0.0,
            "win_rate": float((subset["pnl_pct"] > 0).sum() / len(subset) * 100) if len(subset) > 0 else 0.0,
        }

    return bucket_stats


def _analyze_pnl_by_moneyness(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze PnL by moneyness/ATM distance."""
    # Simplified: use strike vs entry price as proxy
    if "strike" not in df.columns or "entry_price" not in df.columns or "pnl_pct" not in df.columns:
        return {}

    # Compute moneyness proxy
    df["moneyness_proxy"] = abs(df["strike"] - df["entry_price"]) / df["entry_price"] * 100.0
    df["moneyness_bucket"] = pd.cut(
        df["moneyness_proxy"],
        bins=[0, 1.0, 2.0, 5.0, 100.0],
        labels=["ATM", "NEAR_ATM", "MID", "FAR"],
    )

    bucket_stats = {}
    for bucket in df["moneyness_bucket"].unique():
        if pd.isna(bucket):
            continue
        subset = df[df["moneyness_bucket"] == bucket]
        bucket_stats[str(bucket)] = {
            "count": len(subset),
            "avg_pnl": float(subset["pnl_pct"].mean()) if len(subset) > 0 else 0.0,
            "win_rate": float((subset["pnl_pct"] > 0).sum() / len(subset) * 100) if len(subset) > 0 else 0.0,
        }

    return bucket_stats


def _build_confusion_table(df: pd.DataFrame) -> Dict[str, Any]:
    """Build confusion-like table: signal vs actual direction."""
    if "pnl_pct" not in df.columns:
        return {}

    # Determine actual direction from PnL
    df["actual_direction"] = df["pnl_pct"].apply(lambda x: "UP" if x > 2.0 else "DOWN" if x < -2.0 else "FLAT")

    # Signal direction (simplified: use side)
    if "side" in df.columns:
        df["signal_direction"] = df["side"].apply(lambda x: "UP" if x == "CE" else "DOWN")
    else:
        df["signal_direction"] = "UNKNOWN"

    # Build confusion matrix
    confusion = {}
    for signal_dir in df["signal_direction"].unique():
        for actual_dir in df["actual_direction"].unique():
            key = f"{signal_dir}_vs_{actual_dir}"
            count = len(df[(df["signal_direction"] == signal_dir) & (df["actual_direction"] == actual_dir)])
            confusion[key] = count

    return confusion


def save_analysis_report(analysis: Dict[str, Any]) -> Path:
    """
    Save analysis report to CSV.

    Returns:
        Path to saved report
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    report_path = REPORTS_DIR / f"real_learning_summary_{today}.csv"

    # Build report DataFrame
    rows = []

    # Confidence buckets
    for bucket, stats in analysis.get("confidence_buckets", {}).items():
        rows.append(
            {
                "metric": "confidence",
                "bucket": bucket,
                "count": stats["count"],
                "avg_pnl": stats["avg_pnl"],
                "win_rate": stats["win_rate"],
            }
        )

    # Score buckets
    for bucket, stats in analysis.get("score_buckets", {}).items():
        rows.append(
            {
                "metric": "score",
                "bucket": bucket,
                "count": stats["count"],
                "avg_pnl": stats["avg_pnl"],
                "win_rate": stats["win_rate"],
            }
        )

    # Moneyness analysis
    for bucket, stats in analysis.get("moneyness_analysis", {}).items():
        rows.append(
            {
                "metric": "moneyness",
                "bucket": bucket,
                "count": stats["count"],
                "avg_pnl": stats["avg_pnl"],
                "win_rate": stats["win_rate"],
            }
        )

    if rows:
        df_report = pd.DataFrame(rows)
        df_report.to_csv(report_path, index=False)

    return report_path


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - SIGNAL VS OUTCOME ANALYZER ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Analysis only\n")

    analysis = analyze_signal_vs_outcome()

    if analysis["status"] == "SUCCESS":
        print("=== CONFIDENCE BUCKETS ===")
        for bucket, stats in analysis["confidence_buckets"].items():
            print(
                f"{bucket}: {stats['count']} trades, avg_pnl={stats['avg_pnl']:.2f}%, win_rate={stats['win_rate']:.1f}%"
            )

        print("\n=== SCORE BUCKETS ===")
        for bucket, stats in analysis["score_buckets"].items():
            print(
                f"{bucket}: {stats['count']} trades, avg_pnl={stats['avg_pnl']:.2f}%, win_rate={stats['win_rate']:.1f}%"
            )

        print("\n=== MONEYNESS ANALYSIS ===")
        for bucket, stats in analysis["moneyness_analysis"].items():
            print(
                f"{bucket}: {stats['count']} trades, avg_pnl={stats['avg_pnl']:.2f}%, win_rate={stats['win_rate']:.1f}%"
            )

        print("\n=== CONFUSION TABLE ===")
        for key, count in analysis["confusion_table"].items():
            print(f"{key}: {count}")

        # Save report
        report_path = save_analysis_report(analysis)
        print(f"\n[SAVE] Analysis report saved to: {report_path}")
    else:
        print(f"[INFO] {analysis.get('message', 'Analysis not available')}")


if __name__ == "__main__":
    main()
