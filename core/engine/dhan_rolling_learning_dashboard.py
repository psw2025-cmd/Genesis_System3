"""
Dhan Index Options - Rolling 7-Day Learning Dashboard

Aggregates last 7 trading days of learning data.
AUTO-UPDATE: DISABLED - Only reads and reports.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from core.engine.dhan_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_rolling_dashboard(days: int = 7) -> Dict[str, Any]:
    """
    Generate rolling learning dashboard.

    Args:
        days: Number of days to aggregate

    Returns:
        Dict with dashboard data
    """
    df = load_outcomes()
    if df.empty:
        return {
            "status": "NO_DATA",
            "message": "No outcome data available",
        }

    # Filter to last N days
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        cutoff = datetime.utcnow() - timedelta(days=days)
        df = df[df["timestamp"] >= cutoff]

    if df.empty:
        return {
            "status": "NO_RECENT_DATA",
            "message": f"No data in last {days} days",
        }

    # Average PnL per underlying
    avg_pnl_by_underlying = {}
    if "underlying" in df.columns and "pnl_pct" in df.columns:
        for underlying in df["underlying"].unique():
            df_u = df[df["underlying"] == underlying]
            avg_pnl_by_underlying[underlying] = float(df_u["pnl_pct"].mean())

    # Hit rate per confidence bucket
    hit_rate_by_confidence = {}
    if "signal_confidence" in df.columns and "pnl_pct" in df.columns:
        df["conf_bucket"] = pd.cut(
            df["signal_confidence"],
            bins=[0, 0.7, 0.8, 0.9, 1.0],
            labels=["0.7-0.8", "0.8-0.9", "0.9-1.0", "1.0"],
        )
        for bucket in df["conf_bucket"].unique():
            if pd.isna(bucket):
                continue
            subset = df[df["conf_bucket"] == bucket]
            hit_rate = (subset["pnl_pct"] > 0).sum() / len(subset) * 100 if len(subset) > 0 else 0.0
            hit_rate_by_confidence[str(bucket)] = float(hit_rate)

    # Top 3 most reliable patterns (simplified: by underlying + side)
    reliable_patterns = []
    if "underlying" in df.columns and "side" in df.columns and "pnl_pct" in df.columns:
        pattern_stats = (
            df.groupby(["underlying", "side"])
            .agg(
                {
                    "pnl_pct": ["mean", "count"],
                }
            )
            .reset_index()
        )
        pattern_stats.columns = ["underlying", "side", "avg_pnl", "count"]
        pattern_stats = pattern_stats[pattern_stats["count"] >= 3]  # At least 3 trades
        pattern_stats = pattern_stats.sort_values("avg_pnl", ascending=False)
        reliable_patterns = pattern_stats.head(3).to_dict("records")

    # Top 3 risky conditions (by worst PnL)
    risky_conditions = []
    if "underlying" in df.columns and "regime" in df.columns and "pnl_pct" in df.columns:
        condition_stats = (
            df.groupby(["underlying", "regime"])
            .agg(
                {
                    "pnl_pct": ["mean", "count"],
                }
            )
            .reset_index()
        )
        condition_stats.columns = ["underlying", "regime", "avg_pnl", "count"]
        condition_stats = condition_stats[condition_stats["count"] >= 2]  # At least 2 trades
        condition_stats = condition_stats.sort_values("avg_pnl", ascending=True)
        risky_conditions = condition_stats.head(3).to_dict("records")

    return {
        "status": "SUCCESS",
        "period_days": days,
        "total_trades": len(df),
        "avg_pnl_by_underlying": avg_pnl_by_underlying,
        "hit_rate_by_confidence": hit_rate_by_confidence,
        "reliable_patterns": reliable_patterns,
        "risky_conditions": risky_conditions,
    }


def save_dashboard_csv(dashboard: Dict[str, Any]) -> Path:
    """
    Save dashboard to CSV.

    Returns:
        Path to saved CSV
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    csv_path = REPORTS_DIR / f"rolling_learning_dashboard_{today}.csv"

    rows = []

    # Average PnL by underlying
    for underlying, avg_pnl in dashboard.get("avg_pnl_by_underlying", {}).items():
        rows.append(
            {
                "metric": "avg_pnl",
                "category": underlying,
                "value": avg_pnl,
            }
        )

    # Hit rate by confidence
    for bucket, hit_rate in dashboard.get("hit_rate_by_confidence", {}).items():
        rows.append(
            {
                "metric": "hit_rate",
                "category": f"confidence_{bucket}",
                "value": hit_rate,
            }
        )

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False)

    return csv_path


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - ROLLING 7-DAY LEARNING DASHBOARD ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Dashboard only\n")

    dashboard = generate_rolling_dashboard(days=7)

    if dashboard["status"] == "SUCCESS":
        print(f"=== ROLLING {dashboard['period_days']}-DAY DASHBOARD ===\n")
        print(f"Total Trades: {dashboard['total_trades']}")

        print("\n=== AVERAGE PnL BY UNDERLYING ===")
        for underlying, avg_pnl in dashboard["avg_pnl_by_underlying"].items():
            print(f"{underlying}: {avg_pnl:.2f}%")

        print("\n=== HIT RATE BY CONFIDENCE BUCKET ===")
        for bucket, hit_rate in dashboard["hit_rate_by_confidence"].items():
            print(f"{bucket}: {hit_rate:.1f}%")

        print("\n=== TOP 3 RELIABLE PATTERNS ===")
        for i, pattern in enumerate(dashboard["reliable_patterns"], 1):
            print(
                f"{i}. {pattern['underlying']} {pattern['side']}: avg_pnl={pattern['avg_pnl']:.2f}%, count={pattern['count']}"
            )

        print("\n=== TOP 3 RISKY CONDITIONS ===")
        for i, condition in enumerate(dashboard["risky_conditions"], 1):
            print(
                f"{i}. {condition['underlying']} {condition['regime']}: avg_pnl={condition['avg_pnl']:.2f}%, count={condition['count']}"
            )

        # Save CSV
        csv_path = save_dashboard_csv(dashboard)
        print(f"\n[SAVE] Dashboard CSV saved to: {csv_path}")
    else:
        print(f"[INFO] {dashboard.get('message', 'Dashboard not available')}")


if __name__ == "__main__":
    main()
