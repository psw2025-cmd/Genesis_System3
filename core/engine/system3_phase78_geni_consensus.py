"""
System3 Phase 78 - GENI Multi-Model Consensus Engine

Combine Baseline model, Ultra model, and any heuristic signals into a single
consensus signal per option leg.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files (baseline predictions = live signals, ultra = same or separate)
BASELINE_SIGNALS = STORAGE_LIVE / "dhan_index_ai_signals.csv"
ULTRA_SIGNALS = STORAGE_LIVE / "dhan_index_ai_signals.csv"  # Can be same or separate

# Output files
OUTPUT_PARQUET = STORAGE_ULTRA / "phase78_geni_consensus.parquet"
OUTPUT_MD = STORAGE_ULTRA / "phase78_geni_consensus.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

HIGH_THRESHOLD = 0.85  # For consensus when one says BUY and other HOLD


def load_predictions() -> Dict[str, pd.DataFrame]:
    """Load baseline and ultra predictions."""
    data = {}

    if BASELINE_SIGNALS.exists():
        try:
            data["baseline"] = pd.read_csv(BASELINE_SIGNALS)
            print(f"[PH78] Loaded baseline predictions: {len(data['baseline'])} rows")
        except Exception as e:
            print(f"[PH78] Error loading baseline: {e}")
            data["baseline"] = pd.DataFrame()
    else:
        data["baseline"] = pd.DataFrame()

    if ULTRA_SIGNALS.exists():
        try:
            data["ultra"] = pd.read_csv(ULTRA_SIGNALS)
            print(f"[PH78] Loaded ultra predictions: {len(data['ultra'])} rows")
        except Exception as e:
            print(f"[PH78] Error loading ultra: {e}")
            data["ultra"] = pd.DataFrame()
    else:
        data["ultra"] = pd.DataFrame()

    return data


def compute_heuristic_label(row: pd.Series) -> Optional[str]:
    """Derive heuristic label from simple rule-based logic."""
    # Simple heuristic: if expected_move_score > 0.3, suggest BUY_CE, else HOLD
    expected_move = row.get("expected_move_score", 0.0)
    if expected_move > 0.3:
        return "BUY_CE"
    elif expected_move < -0.3:
        return "BUY_PE"
    return "HOLD"


def compute_consensus(
    baseline_row: pd.Series, ultra_row: Optional[pd.Series], heuristic_label: Optional[str]
) -> Dict[str, Any]:
    """Compute consensus signal from baseline, ultra, and heuristic."""
    baseline_label = baseline_row.get("pred_label", "HOLD")
    baseline_conf = baseline_row.get("pred_confidence", 0.0)

    ultra_label = ultra_row.get("pred_label", "HOLD") if ultra_row is not None else "HOLD"
    ultra_conf = ultra_row.get("pred_confidence", 0.0) if ultra_row is not None else 0.0

    consensus_label = "HOLD"
    consensus_conf = 0.0
    conflict = False

    # Consensus rules
    if baseline_label == ultra_label and baseline_label in ["BUY_CE", "BUY_PE"]:
        # Both agree on direction
        consensus_label = baseline_label
        consensus_conf = (baseline_conf + ultra_conf) / 2.0
    elif baseline_label in ["BUY_CE", "BUY_PE"] and ultra_label == "HOLD":
        # Baseline says BUY, ultra says HOLD
        if baseline_conf > HIGH_THRESHOLD:
            consensus_label = baseline_label
            consensus_conf = baseline_conf
        else:
            consensus_label = "HOLD"
            consensus_conf = baseline_conf
    elif ultra_label in ["BUY_CE", "BUY_PE"] and baseline_label == "HOLD":
        # Ultra says BUY, baseline says HOLD
        if ultra_conf > HIGH_THRESHOLD:
            consensus_label = ultra_label
            consensus_conf = ultra_conf
        else:
            consensus_label = "HOLD"
            consensus_conf = ultra_conf
    elif (
        baseline_label in ["BUY_CE", "BUY_PE"] and ultra_label in ["BUY_CE", "BUY_PE"] and baseline_label != ultra_label
    ):
        # Disagree on direction
        consensus_label = "HOLD"
        consensus_conf = (baseline_conf + ultra_conf) / 2.0
        conflict = True

    return {
        "consensus_label": consensus_label,
        "consensus_conf": consensus_conf,
        "conflict": conflict,
    }


def generate_consensus() -> pd.DataFrame:
    """Generate consensus table."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 78 - GENI MULTI-MODEL CONSENSUS ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load predictions
    data = load_predictions()
    baseline_df = data["baseline"]
    ultra_df = data["ultra"]

    if baseline_df.empty:
        print("[PH78] No baseline predictions found. Creating empty consensus.")
        return pd.DataFrame()

    # Create consensus rows
    consensus_rows = []

    for idx, baseline_row in baseline_df.iterrows():
        # Find matching ultra row
        ts = baseline_row.get("ts", "")
        underlying = baseline_row.get("underlying", "")
        strike = baseline_row.get("strike", 0)
        side = baseline_row.get("side", "")

        ultra_match = None
        if not ultra_df.empty:
            ultra_matches = ultra_df[
                (ultra_df["ts"] == ts)
                & (ultra_df["underlying"] == underlying)
                & (ultra_df["strike"] == strike)
                & (ultra_df["side"] == side)
            ]
            if not ultra_matches.empty:
                ultra_match = ultra_matches.iloc[0]

        # Compute heuristic
        heuristic_label = compute_heuristic_label(baseline_row)

        # Compute consensus
        consensus = compute_consensus(baseline_row, ultra_match, heuristic_label)

        # Create consensus row
        consensus_row = baseline_row.to_dict()
        consensus_row.update(
            {
                "baseline_label": baseline_row.get("pred_label", "HOLD"),
                "baseline_conf": baseline_row.get("pred_confidence", 0.0),
                "ultra_label": ultra_match.get("pred_label", "HOLD") if ultra_match is not None else "HOLD",
                "ultra_conf": ultra_match.get("pred_confidence", 0.0) if ultra_match is not None else 0.0,
                "heuristic_label": heuristic_label,
                "consensus_label": consensus["consensus_label"],
                "consensus_conf": consensus["consensus_conf"],
                "conflict": consensus["conflict"],
            }
        )

        consensus_rows.append(consensus_row)

    df_consensus = pd.DataFrame(consensus_rows)

    # Save parquet
    if not df_consensus.empty:
        df_consensus.to_parquet(OUTPUT_PARQUET, index=False)
        print(f"[PH78] Consensus table saved to {OUTPUT_PARQUET}")

    # Generate MD
    generate_markdown(df_consensus)
    print(f"[PH78] Markdown report written to {OUTPUT_MD}")

    return df_consensus


def generate_markdown(df: pd.DataFrame) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 78 - GENI Multi-Model Consensus Report\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        if df.empty:
            f.write("No consensus data available.\n")
            return

        f.write(f"**Total Rows**: {len(df)}\n\n")

        # Count consensus labels
        if "consensus_label" in df.columns:
            label_counts = df["consensus_label"].value_counts()
            f.write("## Consensus Label Distribution\n\n")
            for label, count in label_counts.items():
                f.write(f"- **{label}**: {count}\n")
            f.write("\n")

        # Count conflicts
        if "conflict" in df.columns:
            conflict_count = df["conflict"].sum()
            f.write(f"**Conflicts**: {conflict_count}\n\n")


def main():
    """Main entry point."""
    try:
        df = generate_consensus()
        print("\n[PH78] Consensus generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH78] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
