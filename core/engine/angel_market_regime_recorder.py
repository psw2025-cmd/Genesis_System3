"""
Angel One Index Options - Market Regime Recorder

Logs volatility, microtrend, regime classification.
Output: learning/market_regime_log.csv
SAFE MODE ONLY - Read-only logging, no execution.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from core.engine.angel_volatility_detector import detect_volatility_regime, classify_volatility_state
from core.engine.angel_microtrend_recognizer import detect_microtrend, classify_trend_direction
from core.engine.angel_market_regime_classifier import classify_market_regime

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
REGIME_LOG_CSV = LEARNING_DIR / "market_regime_log.csv"
LIVE_SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def record_market_regime() -> Dict[str, Any]:
    """
    Record current market regime classification.

    Logs volatility, microtrend, regime classification.
    Output: learning/market_regime_log.csv

    Returns:
        Dict with recording results
    """
    print("=== ANGEL ONE INDEX OPTIONS - MARKET REGIME RECORDER ===")
    print("[INFO] SAFE MODE - Read-only logging\n")

    if not LIVE_SIGNALS_CSV.exists():
        return {
            "status": "NO_SOURCE",
            "message": "Live signals CSV not found",
        }

    try:
        df = pd.read_csv(LIVE_SIGNALS_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "No signals available",
            }

        # Get latest snapshot
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts")
            latest = df.tail(100)  # Last 100 rows
        else:
            latest = df.tail(100)

        # Detect volatility regime
        df_vol = detect_volatility_regime(latest, window=5)
        vol_state = classify_volatility_state(df_vol)

        # Detect microtrend
        df_trend = detect_microtrend(latest, lookback=3)
        trend_dir = classify_trend_direction(df_trend)

        # Classify market regime
        regime = classify_market_regime(latest)

        # Create regime record
        regime_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "volatility_regime": vol_state,
            "trend_direction": trend_dir,
            "market_regime": regime,
            "data_points": len(latest),
        }

        # Append to regime log
        try:
            if REGIME_LOG_CSV.exists():
                df_existing = pd.read_csv(REGIME_LOG_CSV)
                df_combined = pd.concat([df_existing, pd.DataFrame([regime_record])], ignore_index=True)
            else:
                df_combined = pd.DataFrame([regime_record])

            df_combined.to_csv(REGIME_LOG_CSV, index=False)

            return {
                "status": "SUCCESS",
                "record": regime_record,
                "file_path": str(REGIME_LOG_CSV),
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to write regime log: {e}",
            }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def get_regime_log_stats() -> Dict[str, Any]:
    """
    Get regime log statistics (read-only).

    Returns:
        Dict with regime log stats
    """
    if not REGIME_LOG_CSV.exists():
        return {
            "status": "EMPTY",
            "count": 0,
            "message": "No regime records yet",
        }

    try:
        df = pd.read_csv(REGIME_LOG_CSV)
        stats = {
            "status": "SUCCESS",
            "total_records": len(df),
        }

        if "market_regime" in df.columns:
            stats["regime_distribution"] = df["market_regime"].value_counts().to_dict()

        if "volatility_regime" in df.columns:
            stats["volatility_distribution"] = df["volatility_regime"].value_counts().to_dict()

        if "trend_direction" in df.columns:
            stats["trend_distribution"] = df["trend_direction"].value_counts().to_dict()

        return stats

    except Exception as e:
        return {
            "status": "ERROR",
            "count": 0,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    result = record_market_regime()

    if result["status"] == "SUCCESS":
        record = result["record"]
        print(f"[SUCCESS] Market regime recorded")
        print(f"\n=== REGIME RECORD ===")
        print(f"Volatility Regime: {record['volatility_regime']}")
        print(f"Trend Direction: {record['trend_direction']}")
        print(f"Market Regime: {record['market_regime']}")
        print(f"Data Points: {record['data_points']}")
        print(f"\n[INFO] Logged to: {result['file_path']}")

        # Show stats
        stats = get_regime_log_stats()
        if stats["status"] == "SUCCESS":
            print(f"\n=== REGIME LOG STATISTICS ===")
            print(f"Total Records: {stats['total_records']}")
            if "regime_distribution" in stats:
                print("\nMarket Regime Distribution:")
                for regime, count in stats["regime_distribution"].items():
                    print(f"  {regime}: {count}")
    else:
        print(f"[INFO] {result.get('message', 'Regime recording not available')}")


if __name__ == "__main__":
    main()
