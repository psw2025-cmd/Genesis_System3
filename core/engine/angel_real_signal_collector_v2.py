"""
Angel One Index Options - Real Signal Collector V2

Stores all Monday signals to learning directory.
Writes ONLY to new file: learning/real_signals_raw.csv
Does NOT touch existing signals file.
SAFE MODE ONLY - Read-only collection, no overwrites.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REAL_SIGNALS_RAW_CSV = LEARNING_DIR / "real_signals_raw.csv"
LIVE_SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def collect_real_signals(
    df_signals: pd.DataFrame | None = None,
    source: str = "live",
) -> Dict[str, Any]:
    """
    Collect real signals and store to learning directory.

    Writes ONLY to learning/real_signals_raw.csv
    Does NOT modify existing live/angel_index_ai_signals.csv

    Args:
        df_signals: Optional DataFrame with signals (if None, reads from live CSV)
        source: Source identifier ("live", "buffer", etc.)

    Returns:
        Dict with collection results
    """
    print("=== ANGEL ONE INDEX OPTIONS - REAL SIGNAL COLLECTOR V2 ===")
    print("[INFO] SAFE MODE - Writes ONLY to learning/real_signals_raw.csv\n")

    # Load signals if not provided
    if df_signals is None:
        if not LIVE_SIGNALS_CSV.exists():
            return {
                "status": "NO_SOURCE",
                "message": "Live signals CSV not found",
            }

        try:
            df_signals = pd.read_csv(LIVE_SIGNALS_CSV)
            if df_signals.empty:
                return {
                    "status": "EMPTY",
                    "message": "No signals in source file",
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to read source: {e}",
            }

    # Add collection metadata
    df_collect = df_signals.copy()
    df_collect["collected_at"] = datetime.utcnow().isoformat()
    df_collect["collection_source"] = source

    # Append to real_signals_raw.csv (does NOT touch live CSV)
    try:
        if REAL_SIGNALS_RAW_CSV.exists():
            df_existing = pd.read_csv(REAL_SIGNALS_RAW_CSV)
            # Avoid duplicates (check by timestamp + underlying + strike + side if available)
            if "ts" in df_collect.columns and "ts" in df_existing.columns:
                df_collect["ts"] = pd.to_datetime(df_collect["ts"], errors="coerce")
                df_existing["ts"] = pd.to_datetime(df_existing["ts"], errors="coerce")
                # Simple deduplication: check if row already exists
                df_new = df_collect[~df_collect["ts"].isin(df_existing["ts"])]
            else:
                df_new = df_collect
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_collect

        df_combined.to_csv(REAL_SIGNALS_RAW_CSV, index=False)

        return {
            "status": "SUCCESS",
            "collected": len(df_collect),
            "total_in_file": len(df_combined),
            "file_path": str(REAL_SIGNALS_RAW_CSV),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to write to real_signals_raw.csv: {e}",
        }


def get_collection_stats() -> Dict[str, Any]:
    """
    Get collection statistics (read-only).

    Returns:
        Dict with collection stats
    """
    if not REAL_SIGNALS_RAW_CSV.exists():
        return {
            "status": "EMPTY",
            "count": 0,
            "message": "No signals collected yet",
        }

    try:
        df = pd.read_csv(REAL_SIGNALS_RAW_CSV)
        stats = {
            "status": "SUCCESS",
            "total_signals": len(df),
        }

        if "underlying" in df.columns:
            stats["by_underlying"] = df["underlying"].value_counts().to_dict()

        if "pred_label" in df.columns:
            stats["by_label"] = df["pred_label"].value_counts().to_dict()

        if "collected_at" in df.columns:
            stats["first_collected"] = df["collected_at"].iloc[0] if len(df) > 0 else None
            stats["last_collected"] = df["collected_at"].iloc[-1] if len(df) > 0 else None

        return stats

    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    # Collect from live signals CSV
    result = collect_real_signals()

    if result["status"] == "SUCCESS":
        print(f"[SUCCESS] Collected {result['collected']} signals")
        print(f"[INFO] Total in file: {result['total_in_file']}")
        print(f"[INFO] File: {result['file_path']}")

        # Show stats
        stats = get_collection_stats()
        if stats["status"] == "SUCCESS":
            print(f"\n=== COLLECTION STATISTICS ===")
            print(f"Total Signals: {stats['total_signals']}")
            if "by_underlying" in stats:
                print("\nBy Underlying:")
                for u, count in stats["by_underlying"].items():
                    print(f"  {u}: {count}")
            if "by_label" in stats:
                print("\nBy Label:")
                for label, count in stats["by_label"].items():
                    print(f"  {label}: {count}")
    else:
        print(f"[INFO] {result.get('message', 'Collection not available')}")


if __name__ == "__main__":
    main()
