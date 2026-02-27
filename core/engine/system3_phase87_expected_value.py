"""
System3 Phase 87 - Expected Value Calculator

Compute Expected Value (EV) per signal/trade based on historical performance.
"""

import sys
import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files
PNL_LOG_CSV = STORAGE_LIVE / "angel_index_ai_pnl_log.csv"

# Output files
OUTPUT_PARQUET = STORAGE_ULTRA / "phase87_expected_value.parquet"
OUTPUT_MD = STORAGE_ULTRA / "phase87_expected_value.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def load_pnl_data() -> pd.DataFrame:
    """Load PnL log data."""
    if not PNL_LOG_CSV.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(PNL_LOG_CSV)
    except Exception as e:
        print(f"[PH87] Error loading PnL: {e}")
        return pd.DataFrame()


def compute_ev_by_group(pnl_df: pd.DataFrame, group_key: str) -> List[Dict[str, Any]]:
    """Compute EV for each group."""
    ev_results = []

    if pnl_df.empty or "pnl_pct" not in pnl_df.columns:
        return ev_results

    for group_value, group_df in pnl_df.groupby(group_key):
        pnl_values = group_df["pnl_pct"].dropna()

        if len(pnl_values) == 0:
            continue

        wins = pnl_values[pnl_values > 0]
        losses = pnl_values[pnl_values <= 0]

        p_win = len(wins) / len(pnl_values) if len(pnl_values) > 0 else 0.0
        p_loss = len(losses) / len(pnl_values) if len(pnl_values) > 0 else 0.0
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(losses.mean()) if len(losses) > 0 else 0.0
        ev = (p_win * avg_win) + (p_loss * avg_loss)

        ev_results.append(
            {
                "group_key": group_key,
                "group_value": str(group_value),
                "p_win": float(p_win),
                "p_loss": float(p_loss),
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "ev": float(ev),
                "count": len(pnl_values),
            }
        )

    return ev_results


def generate_expected_value() -> pd.DataFrame:
    """Generate expected value analysis."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 87 - EXPECTED VALUE CALCULATOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load PnL data
    pnl_df = load_pnl_data()

    if pnl_df.empty:
        print("[PH87] No PnL data found. Creating empty report.")
        return pd.DataFrame()

    # Compute EV by different groupings
    all_ev_results = []

    # By underlying
    if "underlying" in pnl_df.columns:
        all_ev_results.extend(compute_ev_by_group(pnl_df, "underlying"))

    # By direction (pred_label)
    if "pred_label" in pnl_df.columns:
        all_ev_results.extend(compute_ev_by_group(pnl_df, "pred_label"))

    if not all_ev_results:
        print("[PH87] No EV results computed. Creating empty report.")
        return pd.DataFrame()

    df_ev = pd.DataFrame(all_ev_results)

    # Save parquet
    df_ev.to_parquet(OUTPUT_PARQUET, index=False)
    print(f"[PH87] Expected value computed for {len(df_ev)} pattern buckets")

    # Generate MD
    generate_markdown(df_ev)
    print(f"[PH87] Markdown report written to {OUTPUT_MD}")

    return df_ev


def generate_markdown(df: pd.DataFrame) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 87 - Expected Value Report\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        if df.empty:
            f.write("No EV data available.\n")
            return

        # Top 5 positive EV
        positive_ev = df[df["ev"] > 0].nlargest(5, "ev")
        if not positive_ev.empty:
            f.write("## Top 5 Positive EV Patterns\n\n")
            f.write("| Group | Value | EV | P(Win) | Avg Win | Count |\n")
            f.write("|-------|-------|----|--------|---------|-------|\n")
            for _, row in positive_ev.iterrows():
                f.write(
                    f"| {row['group_key']} | {row['group_value']} | {row['ev']:.4f} | "
                    f"{row['p_win']:.2f} | {row['avg_win']:.2f} | {row['count']} |\n"
                )
            f.write("\n")

        # Bottom 5 negative EV
        negative_ev = df[df["ev"] < 0].nsmallest(5, "ev")
        if not negative_ev.empty:
            f.write("## Bottom 5 Negative EV Patterns\n\n")
            f.write("| Group | Value | EV | P(Win) | Avg Loss | Count |\n")
            f.write("|-------|-------|----|--------|----------|-------|\n")
            for _, row in negative_ev.iterrows():
                f.write(
                    f"| {row['group_key']} | {row['group_value']} | {row['ev']:.4f} | "
                    f"{row['p_win']:.2f} | {row['avg_loss']:.2f} | {row['count']} |\n"
                )


def main():
    """Main entry point."""
    try:
        df = generate_expected_value()
        print("\n[PH87] Expected value calculation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH87] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
