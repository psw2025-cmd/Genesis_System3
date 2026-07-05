"""
Dhan Index Options - Adaptive Volatility Map

Maps and tracks volatility patterns across underlyings.
SAFE MODE ONLY - Read-only analysis.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"


def build_volatility_map(days: int = 7) -> Dict[str, Any]:
    """
    Build adaptive volatility map from recent signals.

    Args:
        days: Number of days to analyze

    Returns:
        Dict with volatility map
    """
    if not SIGNALS_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "Signals CSV not found",
        }

    try:
        df = pd.read_csv(SIGNALS_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "No signals available",
            }

        # Filter by date
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            cutoff = datetime.utcnow() - timedelta(days=days)
            df = df[df["ts"] >= cutoff]

        if df.empty:
            return {
                "status": "NO_RECENT_DATA",
                "message": f"No data in last {days} days",
            }

        volatility_map = {}

        # Per underlying
        if "underlying" in df.columns and "spot" in df.columns:
            for underlying in df["underlying"].unique():
                df_u = df[df["underlying"] == underlying]

                if "spot" in df_u.columns:
                    spot_series = df_u["spot"].dropna()
                    if len(spot_series) > 1:
                        volatility = spot_series.std()
                        volatility_pct = (volatility / spot_series.mean() * 100) if spot_series.mean() > 0 else 0.0

                        volatility_map[underlying] = {
                            "volatility": float(volatility),
                            "volatility_pct": float(volatility_pct),
                            "volatility_regime": _classify_volatility_regime(volatility_pct),
                            "data_points": len(spot_series),
                        }

        return {
            "status": "SUCCESS",
            "period_days": days,
            "volatility_map": volatility_map,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def _classify_volatility_regime(volatility_pct: float) -> str:
    """Classify volatility regime."""
    if volatility_pct < 0.5:
        return "LOW"
    elif volatility_pct < 1.0:
        return "NORMAL"
    elif volatility_pct < 2.0:
        return "HIGH"
    else:
        return "EXTREME"


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - ADAPTIVE VOLATILITY MAP ===")
    print("[INFO] SAFE MODE - Read-only analysis\n")

    volatility_map = build_volatility_map(days=7)

    if volatility_map["status"] == "SUCCESS":
        print(f"=== VOLATILITY MAP (Last {volatility_map['period_days']} Days) ===\n")

        for underlying, data in volatility_map["volatility_map"].items():
            print(f"{underlying}:")
            print(f"  Volatility: {data['volatility']:.2f} ({data['volatility_pct']:.2f}%)")
            print(f"  Regime: {data['volatility_regime']}")
            print(f"  Data Points: {data['data_points']}")
            print()
    else:
        print(f"[INFO] {volatility_map.get('message', 'Volatility map not available')}")


if __name__ == "__main__":
    main()
