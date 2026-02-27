"""
Angel One Index Options - Misfire Detector

Identifies false positives and false negatives.
AUTO-UPDATE: DISABLED - Only detects and tags, never auto-fixes.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from core.engine.angel_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
MISFIRES_CSV = LEARNING_DIR / "angel_misfires.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def detect_misfires() -> pd.DataFrame:
    """
    Detect misfires (false positives and false negatives).

    Returns:
        DataFrame with tagged misfires
    """
    df = load_outcomes()
    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    # False positives: strong BUY signals with negative PnL
    df["false_positive"] = (df["signal_confidence"] >= 0.80) & (df["score"].abs() >= 0.30) & (df["pnl_pct"] < -2.0)

    # False negatives: HOLD when there was a large move
    # (Simplified: trades with large positive PnL that might have been missed)
    df["false_negative"] = (df["signal_confidence"] < 0.70) & (df["pnl_pct"] > 5.0)

    # Tag misfires
    df["misfire_type"] = df.apply(
        lambda row: (
            "FALSE_POSITIVE" if row["false_positive"] else "FALSE_NEGATIVE" if row["false_negative"] else "NONE"
        ),
        axis=1,
    )

    # Filter to only misfires
    misfires = df[df["misfire_type"] != "NONE"].copy()

    # Add analysis columns
    misfires["misfire_severity"] = misfires.apply(_compute_severity, axis=1)
    misfires["misfire_reason"] = misfires.apply(_compute_reason, axis=1)

    return misfires


def _compute_severity(row: pd.Series) -> str:
    """Compute misfire severity."""
    if row["misfire_type"] == "FALSE_POSITIVE":
        loss = abs(row["pnl_pct"])
        if loss > 10.0:
            return "CRITICAL"
        elif loss > 5.0:
            return "HIGH"
        else:
            return "MEDIUM"
    elif row["misfire_type"] == "FALSE_NEGATIVE":
        gain = row["pnl_pct"]
        if gain > 10.0:
            return "CRITICAL"
        elif gain > 5.0:
            return "HIGH"
        else:
            return "MEDIUM"
    return "LOW"


def _compute_reason(row: pd.Series) -> str:
    """Compute misfire reason."""
    if row["misfire_type"] == "FALSE_POSITIVE":
        return f"High confidence ({row['signal_confidence']:.2f}) but negative PnL ({row['pnl_pct']:.2f}%)"
    elif row["misfire_type"] == "FALSE_NEGATIVE":
        return f"Low confidence ({row['signal_confidence']:.2f}) but large positive PnL ({row['pnl_pct']:.2f}%)"
    return "NONE"


def save_misfires(misfires: pd.DataFrame) -> Path:
    """
    Save misfires to CSV.

    Returns:
        Path to saved CSV
    """
    if misfires.empty:
        return MISFIRES_CSV

    # Select relevant columns
    cols = [
        "timestamp",
        "underlying",
        "strike",
        "side",
        "entry_price",
        "exit_price",
        "pnl_pct",
        "signal_confidence",
        "score",
        "misfire_type",
        "misfire_severity",
        "misfire_reason",
    ]

    available_cols = [c for c in cols if c in misfires.columns]
    df_save = misfires[available_cols].copy()

    # Append to existing or create new
    if MISFIRES_CSV.exists():
        try:
            df_existing = pd.read_csv(MISFIRES_CSV)
            df_save = pd.concat([df_existing, df_save], ignore_index=True)
            df_save = df_save.drop_duplicates(subset=["timestamp", "underlying", "strike", "side"], keep="last")
        except Exception:
            pass

    df_save.to_csv(MISFIRES_CSV, index=False)
    return MISFIRES_CSV


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - MISFIRE DETECTOR ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Detection only\n")

    misfires = detect_misfires()

    if misfires.empty:
        print("[INFO] No misfires detected.")
        return

    print(f"[DETECTED] {len(misfires)} misfires found\n")

    print("=== MISFIRE SUMMARY ===")
    print(f"False Positives: {len(misfires[misfires['misfire_type'] == 'FALSE_POSITIVE'])}")
    print(f"False Negatives: {len(misfires[misfires['misfire_type'] == 'FALSE_NEGATIVE'])}")

    print("\n=== SEVERITY BREAKDOWN ===")
    severity_counts = misfires["misfire_severity"].value_counts()
    for severity, count in severity_counts.items():
        print(f"{severity}: {count}")

    # Save
    save_path = save_misfires(misfires)
    print(f"\n[SAVE] Misfires saved to: {save_path}")


if __name__ == "__main__":
    main()
