"""
System3 Phase 90 - Optimal Exit Engine

Assess quality of exit logic for trades.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files
PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"

# Output files
OUTPUT_PARQUET = STORAGE_ULTRA / "phase90_optimal_exit.parquet"
OUTPUT_MD = STORAGE_ULTRA / "phase90_optimal_exit.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def evaluate_exit_quality(row: pd.Series) -> Dict[str, Any]:
    """Evaluate exit quality for a trade."""
    actual_pnl = row.get("pnl_pct", 0.0)
    best_case = row.get("max_fav_pct", 0.0)
    worst_case = row.get("max_adv_pct", 0.0)  # Maximum adverse

    # Determine exit quality
    if actual_pnl > 0 and actual_pnl >= best_case * 0.8:
        exit_quality = "GOOD"
    elif actual_pnl > 0 and actual_pnl < best_case * 0.5:
        exit_quality = "TOO_SOON"
    elif actual_pnl < 0 and worst_case < -10.0:
        exit_quality = "TOO_LATE"
    else:
        exit_quality = "GOOD"

    # Calculate improvable PnL %
    if best_case > actual_pnl and best_case > 0:
        improvable_pnl_pct = ((best_case - actual_pnl) / best_case) * 100.0
    else:
        improvable_pnl_pct = 0.0

    return {
        "exit_quality": exit_quality,
        "improvable_pnl_pct": improvable_pnl_pct,
    }


def generate_exit_analysis() -> pd.DataFrame:
    """Generate exit quality analysis."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 90 - OPTIMAL EXIT ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load PnL data
    if not PNL_LOG_CSV.exists():
        print("[PH90] No PnL data found. Creating empty report.")
        return pd.DataFrame()

    try:
        pnl_df = pd.read_csv(PNL_LOG_CSV)
    except Exception as e:
        print(f"[PH90] Error loading PnL: {e}")
        return pd.DataFrame()

    if pnl_df.empty:
        print("[PH90] PnL data is empty. Creating empty report.")
        return pd.DataFrame()

    # Evaluate exit quality
    exit_results = []
    for _, row in pnl_df.iterrows():
        eval_result = evaluate_exit_quality(row)
        exit_results.append(
            {
                "ts": row.get("ts", ""),
                "underlying": row.get("underlying", ""),
                "strike": row.get("strike", 0),
                "side": row.get("side", ""),
                "actual_pnl": row.get("pnl_pct", 0.0),
                "best_case_pnl": row.get("max_fav_pct", 0.0),
                "worst_case_pnl": row.get("max_adv_pct", 0.0),
                "exit_quality": eval_result["exit_quality"],
                "improvable_pnl_pct": eval_result["improvable_pnl_pct"],
            }
        )

    df_exit = pd.DataFrame(exit_results)

    # Save parquet
    if not df_exit.empty:
        df_exit.to_parquet(OUTPUT_PARQUET, index=False)
        print(f"[PH90] Exit quality evaluated for {len(df_exit)} trades")

    # Generate MD
    generate_markdown(df_exit)
    print(f"[PH90] Markdown report written to {OUTPUT_MD}")

    return df_exit


def generate_markdown(df: pd.DataFrame) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 90 - Optimal Exit Analysis\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        if df.empty:
            f.write("No exit quality data available.\n")
            return

        # Distribution of exit_quality
        if "exit_quality" in df.columns:
            quality_counts = df["exit_quality"].value_counts()
            f.write("## Exit Quality Distribution\n\n")
            for quality, count in quality_counts.items():
                f.write(f"- **{quality}**: {count}\n")
            f.write("\n")

        # Average improvable PnL for improvable trades
        if "improvable_pnl_pct" in df.columns and "exit_quality" in df.columns:
            improvable_trades = df[df["exit_quality"].isin(["TOO_SOON", "TOO_LATE"])]
            if not improvable_trades.empty:
                avg_improvable = improvable_trades["improvable_pnl_pct"].mean()
                f.write(f"## Average Improvable PnL\n\n")
                f.write(f"**Average improvable PnL % for improvable trades**: {avg_improvable:.2f}%\n\n")


def main():
    """Main entry point."""
    try:
        df = generate_exit_analysis()
        print("\n[PH90] Exit quality evaluation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH90] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
