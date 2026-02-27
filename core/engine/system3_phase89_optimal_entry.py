"""
System3 Phase 89 - Optimal Entry Engine

Assess quality of entry timing for trades.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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
OUTPUT_PARQUET = STORAGE_ULTRA / "phase89_optimal_entry.parquet"
OUTPUT_MD = STORAGE_ULTRA / "phase89_optimal_entry.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def evaluate_entry_quality(row: pd.Series) -> str:
    """Evaluate entry quality for a trade."""
    # Simplified: if max_fav_pct is high and entry was early, mark as EARLY
    # If max_fav_pct is low, mark as LATE
    # Otherwise GOOD

    max_fav_pct = row.get("max_fav_pct", 0.0)
    entry_price = row.get("entry_price", 0.0)

    # Heuristic: if max favorable was >20% but we entered early, could have been better
    if max_fav_pct > 20.0:
        return "EARLY"  # Could have entered later for better price
    elif max_fav_pct < -5.0:
        return "LATE"  # Entry was after price moved against us
    else:
        return "GOOD"


def generate_entry_analysis() -> pd.DataFrame:
    """Generate entry quality analysis."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 89 - OPTIMAL ENTRY ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load PnL data
    if not PNL_LOG_CSV.exists():
        print("[PH89] No PnL data found. Creating empty report.")
        return pd.DataFrame()

    try:
        pnl_df = pd.read_csv(PNL_LOG_CSV)
    except Exception as e:
        print(f"[PH89] Error loading PnL: {e}")
        return pd.DataFrame()

    if pnl_df.empty:
        print("[PH89] PnL data is empty. Creating empty report.")
        return pd.DataFrame()

    # Evaluate entry quality
    entry_qualities = []
    for _, row in pnl_df.iterrows():
        quality = evaluate_entry_quality(row)
        entry_qualities.append(
            {
                "ts": row.get("ts", ""),
                "underlying": row.get("underlying", ""),
                "strike": row.get("strike", 0),
                "side": row.get("side", ""),
                "entry_price": row.get("entry_price", 0.0),
                "entry_quality": quality,
                "max_fav_pct": row.get("max_fav_pct", 0.0),
            }
        )

    df_entry = pd.DataFrame(entry_qualities)

    # Save parquet
    if not df_entry.empty:
        df_entry.to_parquet(OUTPUT_PARQUET, index=False)
        print(f"[PH89] Entry quality evaluated for {len(df_entry)} trades")

    # Generate MD
    generate_markdown(df_entry)
    print(f"[PH89] Markdown report written to {OUTPUT_MD}")

    return df_entry


def generate_markdown(df: pd.DataFrame) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 89 - Optimal Entry Analysis\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        if df.empty:
            f.write("No entry quality data available.\n")
            return

        # Counts per class
        if "entry_quality" in df.columns:
            quality_counts = df["entry_quality"].value_counts()
            f.write("## Entry Quality Distribution\n\n")
            for quality, count in quality_counts.items():
                f.write(f"- **{quality}**: {count}\n")
            f.write("\n")

        # Detailed examples (2-3)
        f.write("## Detailed Examples\n\n")
        examples = df.head(3)
        for idx, row in examples.iterrows():
            f.write(f"### Example {idx + 1}\n\n")
            f.write(f"- **Underlying**: {row.get('underlying', 'N/A')}\n")
            f.write(f"- **Strike**: {row.get('strike', 0)}\n")
            f.write(f"- **Side**: {row.get('side', 'N/A')}\n")
            f.write(f"- **Entry Price**: {row.get('entry_price', 0.0):.2f}\n")
            f.write(f"- **Entry Quality**: {row.get('entry_quality', 'N/A')}\n")
            f.write(f"- **Max Favorable %**: {row.get('max_fav_pct', 0.0):.2f}%\n\n")


def main():
    """Main entry point."""
    try:
        df = generate_entry_analysis()
        print("\n[PH89] Entry quality evaluation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH89] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
