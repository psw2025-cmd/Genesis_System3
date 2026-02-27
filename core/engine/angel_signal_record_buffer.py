"""
Angel One Index Options - Signal Record Buffer

Temporary buffer for storing Monday signals.
Does NOT touch existing signals file.
SAFE MODE ONLY - Read-only buffer, no overwrites.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
BUFFER_CSV = LEARNING_DIR / "real_signals_raw.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def buffer_signal(
    underlying: str,
    strike: float,
    side: str,
    ltp: float,
    spot: float,
    pred_label: str,
    pred_confidence: float,
    expected_move_score: float,
    **kwargs,
) -> bool:
    """
    Buffer a signal to temporary storage.

    Does NOT touch existing signals file.
    Writes ONLY to learning/real_signals_raw.csv

    Args:
        underlying: Underlying name
        strike: Strike price
        side: Option side (CE/PE)
        ltp: Last traded price
        spot: Spot price
        pred_label: Prediction label
        pred_confidence: Prediction confidence
        expected_move_score: Expected move score
        **kwargs: Additional signal data

    Returns:
        True if buffered successfully
    """
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "underlying": underlying,
        "strike": strike,
        "side": side,
        "ltp": ltp,
        "spot": spot,
        "pred_label": pred_label,
        "pred_confidence": pred_confidence,
        "expected_move_score": expected_move_score,
        **kwargs,
    }

    try:
        if BUFFER_CSV.exists():
            df = pd.read_csv(BUFFER_CSV)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])

        df.to_csv(BUFFER_CSV, index=False)
        return True
    except Exception as e:
        print(f"[BUFFER] Failed to buffer signal: {e}")
        return False


def get_buffer_stats() -> Dict[str, Any]:
    """
    Get buffer statistics (read-only).

    Returns:
        Dict with buffer stats
    """
    if not BUFFER_CSV.exists():
        return {
            "status": "EMPTY",
            "count": 0,
            "message": "Buffer is empty",
        }

    try:
        df = pd.read_csv(BUFFER_CSV)
        return {
            "status": "SUCCESS",
            "count": len(df),
            "first_timestamp": df["timestamp"].iloc[0] if "timestamp" in df.columns and len(df) > 0 else None,
            "last_timestamp": df["timestamp"].iloc[-1] if "timestamp" in df.columns and len(df) > 0 else None,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - SIGNAL RECORD BUFFER ===")
    print("[INFO] SAFE MODE - Does NOT touch existing signals file\n")
    print(f"[INFO] Buffer file: {BUFFER_CSV}\n")

    stats = get_buffer_stats()

    if stats["status"] == "SUCCESS":
        print(f"Buffer Status: ✅ ACTIVE")
        print(f"Signals Buffered: {stats['count']}")
        if stats["first_timestamp"]:
            print(f"First Signal: {stats['first_timestamp']}")
        if stats["last_timestamp"]:
            print(f"Last Signal: {stats['last_timestamp']}")
    elif stats["status"] == "EMPTY":
        print("Buffer Status: ⚪ EMPTY (ready for Monday signals)")
    else:
        print(f"Buffer Status: ❌ ERROR - {stats.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
