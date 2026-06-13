"""
System3 Phase 141 - Spread & Liquidity Estimation

Estimates spread and liquidity from existing snapshot data.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase141_spread_liquidity_metrics.csv"


def estimate_spread(ltp: float, bid: float = None, ask: float = None) -> float:
    """
    Estimate spread from available data.

    If bid/ask available, use actual spread.
    Otherwise, approximate synthetic spread (0.1% of LTP).
    """
    if bid is not None and ask is not None and bid > 0 and ask > 0:
        return ask - bid
    elif ltp > 0:
        # Synthetic spread: 0.1% of LTP
        return ltp * 0.001
    else:
        return 0.0


def estimate_liquidity_score(spread: float, ltp: float) -> float:
    """
    Estimate liquidity score (0-1, higher is better).

    Simple heuristic: lower spread relative to LTP = higher liquidity.
    """
    if ltp <= 0:
        return 0.0

    spread_pct = (spread / ltp) * 100
    if spread_pct < 0.5:
        return 1.0
    elif spread_pct < 1.0:
        return 0.8
    elif spread_pct < 2.0:
        return 0.6
    elif spread_pct < 5.0:
        return 0.4
    else:
        return 0.2


def run_phase141_spread_liquidity_estimator() -> Dict[str, Any]:
    """
    Estimate spread and liquidity from snapshot data.

    Returns:
        dict: {
            "phase": 141,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load signals/snapshot data
        df_signals = pd.DataFrame()
        if SIGNALS_CSV.exists():
            try:
                df_signals = pd.read_csv(SIGNALS_CSV)
                # Take last 100 rows for recent data
                if len(df_signals) > 100:
                    df_signals = df_signals.tail(100)
            except Exception as e:
                errors.append(f"Error reading signals CSV: {e}")

        if df_signals.empty:
            # Create empty result
            df_result = pd.DataFrame(
                columns=["timestamp", "underlying", "strike", "side", "ltp", "spread_estimate", "liquidity_score"]
            )
            status = "OK"
            details = "No snapshot data available, created empty metrics file"
        else:
            # Extract relevant columns
            metrics_rows = []

            for _, row in df_signals.iterrows():
                timestamp = row.get("ts", datetime.now().isoformat())
                underlying = row.get("underlying", "")
                strike = row.get("strike", 0)
                side = row.get("side", "")
                ltp = float(row.get("ltp", 0) or row.get("entry_price", 0) or 0)

                # Try to get bid/ask if available
                bid = row.get("bid", None)
                ask = row.get("ask", None)

                # Estimate spread
                spread = estimate_spread(ltp, bid, ask)

                # Estimate liquidity
                liquidity_score = estimate_liquidity_score(spread, ltp)

                metrics_rows.append(
                    {
                        "timestamp": timestamp,
                        "underlying": underlying,
                        "strike": strike,
                        "side": side,
                        "ltp": ltp,
                        "spread_estimate": round(spread, 2),
                        "liquidity_score": round(liquidity_score, 3),
                    }
                )

            df_result = pd.DataFrame(metrics_rows)
            status = "OK"
            details = f"Spread/liquidity metrics computed: {len(df_result)} rows"

        # Save CSV
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)

        return {
            "phase": 141,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "row_count": len(df_result),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 141,
            "status": "ERROR",
            "details": f"Phase 141 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 141 - SPREAD & LIQUIDITY ESTIMATION")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase141_spread_liquidity_estimator()

    print(f"Phase141: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nRows: {result['outputs']['row_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
