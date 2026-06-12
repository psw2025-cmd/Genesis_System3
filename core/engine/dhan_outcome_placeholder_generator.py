"""
Dhan Index Options - Outcome Placeholder Generator

Writes placeholders for Monday outcomes.
No scoring, no PnL calculation.
SAFE MODE ONLY - Read-only placeholders, no execution.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_SIGNALS_RAW_CSV = LEARNING_DIR / "real_signals_raw.csv"
OUTCOME_PLACEHOLDERS_CSV = LEARNING_DIR / "outcome_placeholders.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def generate_outcome_placeholders() -> Dict[str, Any]:
    """
    Generate placeholders for Monday outcomes.

    No scoring, no PnL calculation.
    Just creates placeholder structure.

    Returns:
        Dict with generation results
    """
    print("=== ANGEL ONE INDEX OPTIONS - OUTCOME PLACEHOLDER GENERATOR ===")
    print("[INFO] SAFE MODE - Placeholders only, no scoring, no PnL\n")

    if not REAL_SIGNALS_RAW_CSV.exists():
        return {
            "status": "NO_SOURCE",
            "message": "real_signals_raw.csv not found. Run signal collector first.",
        }

    try:
        df_signals = pd.read_csv(REAL_SIGNALS_RAW_CSV)
        if df_signals.empty:
            return {
                "status": "EMPTY",
                "message": "No signals to create placeholders for",
            }

        # Create placeholder structure
        placeholders = []

        for _, signal in df_signals.iterrows():
            placeholder = {
                "signal_timestamp": signal.get("ts", signal.get("timestamp", "")),
                "underlying": signal.get("underlying", ""),
                "strike": signal.get("strike", 0.0),
                "side": signal.get("side", ""),
                "entry_price": signal.get("ltp", 0.0),
                "entry_confidence": signal.get("pred_confidence", 0.0),
                "entry_score": signal.get("expected_move_score", 0.0),
                "placeholder_created_at": datetime.utcnow().isoformat(),
                "exit_price": None,  # To be filled later
                "exit_timestamp": None,  # To be filled later
                "pnl_pct": None,  # To be filled later
                "exit_reason": None,  # To be filled later
                "status": "PENDING",
            }
            placeholders.append(placeholder)

        df_placeholders = pd.DataFrame(placeholders)

        # Save placeholders
        df_placeholders.to_csv(OUTCOME_PLACEHOLDERS_CSV, index=False)

        return {
            "status": "SUCCESS",
            "placeholders_created": len(placeholders),
            "file_path": str(OUTCOME_PLACEHOLDERS_CSV),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def get_placeholder_stats() -> Dict[str, Any]:
    """
    Get placeholder statistics (read-only).

    Returns:
        Dict with placeholder stats
    """
    if not OUTCOME_PLACEHOLDERS_CSV.exists():
        return {
            "status": "EMPTY",
            "count": 0,
            "message": "No placeholders created yet",
        }

    try:
        df = pd.read_csv(OUTCOME_PLACEHOLDERS_CSV)
        stats = {
            "status": "SUCCESS",
            "total_placeholders": len(df),
        }

        if "status" in df.columns:
            stats["by_status"] = df["status"].value_counts().to_dict()

        if "underlying" in df.columns:
            stats["by_underlying"] = df["underlying"].value_counts().to_dict()

        return stats

    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    result = generate_outcome_placeholders()

    if result["status"] == "SUCCESS":
        print(f"[SUCCESS] Created {result['placeholders_created']} outcome placeholders")
        print(f"[INFO] File: {result['file_path']}")
        print("[NOTE] Placeholders contain no PnL or scoring - to be filled after market close")

        # Show stats
        stats = get_placeholder_stats()
        if stats["status"] == "SUCCESS":
            print(f"\n=== PLACEHOLDER STATISTICS ===")
            print(f"Total Placeholders: {stats['total_placeholders']}")
            if "by_status" in stats:
                print("\nBy Status:")
                for status, count in stats["by_status"].items():
                    print(f"  {status}: {count}")
    else:
        print(f"[INFO] {result.get('message', 'Placeholder generation not available')}")


if __name__ == "__main__":
    main()
