"""
Dhan Index Options - Misfire Classifier V2

Classifies misfires: Wrong Direction, Weak Move, Low Confidence.
Generates report only.
SAFE MODE ONLY - Read-only classification, no changes.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from core.engine.dhan_unified_outcome_logger_v3 import get_outcome_stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"
MISFIRES_CSV = LEARNING_DIR / "misfires_classified_v2.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def classify_misfires() -> pd.DataFrame:
    """
    Classify misfires from outcomes.

    Classifications:
    - Wrong Direction: Signal predicted move but went opposite
    - Weak Move: Signal predicted strong move but got weak result
    - Low Confidence: High confidence signal resulted in loss

    Returns:
        DataFrame with classified misfires
    """
    if not REAL_OUTCOMES_CSV.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(REAL_OUTCOMES_CSV)
        if df.empty:
            return pd.DataFrame()

        df = df.copy()

        # Classification logic
        misfire_types = []

        for _, row in df.iterrows():
            pnl = row.get("pnl_pct", 0.0)
            confidence = row.get("entry_confidence", 0.0)
            score = abs(row.get("entry_score", 0.0))
            side = row.get("side", "")

            misfire_reasons = []

            # Wrong Direction: Strong signal but negative PnL
            if confidence >= 0.80 and score >= 0.30 and pnl < -2.0:
                misfire_reasons.append("WRONG_DIRECTION")

            # Weak Move: Expected strong move but got weak result
            if score >= 0.40 and abs(pnl) < 1.0:
                misfire_reasons.append("WEAK_MOVE")

            # Low Confidence: High confidence but poor outcome
            if confidence >= 0.85 and pnl < -3.0:
                misfire_reasons.append("LOW_CONFIDENCE")

            # No misfire
            if not misfire_reasons:
                misfire_types.append("NONE")
            else:
                misfire_types.append("|".join(misfire_reasons))

        df["misfire_type"] = misfire_types
        df["is_misfire"] = df["misfire_type"] != "NONE"

        # Filter to only misfires
        misfires = df[df["is_misfire"]].copy()

        # Add severity
        misfires["misfire_severity"] = misfires.apply(_compute_misfire_severity, axis=1)

        return misfires

    except Exception as e:
        print(f"[MISFIRE CLASSIFIER] Error: {e}")
        return pd.DataFrame()


def _compute_misfire_severity(row: pd.Series) -> str:
    """Compute misfire severity."""
    pnl = abs(row.get("pnl_pct", 0.0))
    confidence = row.get("entry_confidence", 0.0)

    if pnl > 10.0 or confidence >= 0.90:
        return "CRITICAL"
    elif pnl > 5.0 or confidence >= 0.85:
        return "HIGH"
    else:
        return "MEDIUM"


def save_misfires(misfires: pd.DataFrame) -> Path:
    """
    Save classified misfires to CSV.

    Returns:
        Path to saved CSV
    """
    if misfires.empty:
        return MISFIRES_CSV

    # Select relevant columns
    cols = [
        "signal_timestamp",
        "underlying",
        "strike",
        "side",
        "entry_price",
        "exit_price",
        "pnl_pct",
        "entry_confidence",
        "entry_score",
        "misfire_type",
        "misfire_severity",
        "exit_reason",
    ]

    available_cols = [c for c in cols if c in misfires.columns]
    df_save = misfires[available_cols].copy()

    # Append to existing or create new
    if MISFIRES_CSV.exists():
        try:
            df_existing = pd.read_csv(MISFIRES_CSV)
            df_save = pd.concat([df_existing, df_save], ignore_index=True)
            df_save = df_save.drop_duplicates(subset=["signal_timestamp", "underlying", "strike", "side"], keep="last")
        except Exception:
            pass

    df_save.to_csv(MISFIRES_CSV, index=False)
    return MISFIRES_CSV


def generate_misfire_report() -> Dict[str, Any]:
    """
    Generate misfire classification report.

    Returns:
        Dict with report data
    """
    misfires = classify_misfires()

    if misfires.empty:
        return {
            "status": "NO_MISFIRES",
            "message": "No misfires detected",
        }

    # Count by type
    type_counts = {}
    for misfire_type in misfires["misfire_type"].unique():
        count = len(misfires[misfires["misfire_type"] == misfire_type])
        type_counts[misfire_type] = count

    # Count by severity
    severity_counts = {}
    if "misfire_severity" in misfires.columns:
        severity_counts = misfires["misfire_severity"].value_counts().to_dict()

    return {
        "status": "SUCCESS",
        "total_misfires": len(misfires),
        "by_type": type_counts,
        "by_severity": severity_counts,
        "misfires": misfires,
    }


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - MISFIRE CLASSIFIER V2 ===")
    print("[INFO] SAFE MODE - Classification only, generates report\n")

    report = generate_misfire_report()

    if report["status"] == "SUCCESS":
        print(f"\n=== MISFIRE CLASSIFICATION REPORT ===")
        print(f"Total Misfires: {report['total_misfires']}")

        print("\n=== BY TYPE ===")
        for misfire_type, count in report["by_type"].items():
            print(f"  {misfire_type}: {count}")

        print("\n=== BY SEVERITY ===")
        for severity, count in report["by_severity"].items():
            print(f"  {severity}: {count}")

        # Save misfires
        save_path = save_misfires(report["misfires"])
        print(f"\n[SAVE] Misfires saved to: {save_path}")

        # Show examples
        print("\n=== SAMPLE MISFIRES (First 3) ===")
        sample = report["misfires"].head(3)
        for idx, row in sample.iterrows():
            print(f"\nMisfire #{idx+1}:")
            print(f"  Underlying: {row.get('underlying', 'N/A')}")
            print(f"  Type: {row.get('misfire_type', 'N/A')}")
            print(f"  Severity: {row.get('misfire_severity', 'N/A')}")
            print(f"  PnL: {row.get('pnl_pct', 0.0):.2f}%")
            print(f"  Confidence: {row.get('entry_confidence', 0.0):.3f}")
    else:
        print(f"[INFO] {report.get('message', 'No misfires to classify')}")


if __name__ == "__main__":
    main()
