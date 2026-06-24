"""
System3 Phase 138 - Angel Risk Tier Assignment

Assigns risk tiers to underlyings deterministically.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

UNIVERSE_CSV_PATH = STORAGE_ULTRA / "phase136_dhan_symbol_universe.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase138_risk_tiers.csv"

# Risk tier mapping (deterministic)
RISK_TIER_MAP = {
    "BANKNIFTY": "HIGH",
    "MIDCPNIFTY": "HIGH",
    "NIFTY": "MEDIUM",
    "FINNIFTY": "MEDIUM",
    "SENSEX": "LOW",
}

# Max trades per tier
MAX_TRADES_BY_TIER = {
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
}


def run_phase138_risk_tier_assignment() -> Dict[str, Any]:
    """
    Assign risk tiers to underlyings.

    Returns:
        dict: {
            "phase": 138,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load universe
        underlyings = []
        if UNIVERSE_CSV_PATH.exists():
            try:
                df_universe = pd.read_csv(UNIVERSE_CSV_PATH)
                underlyings = df_universe["underlying"].tolist()
            except Exception as e:
                errors.append(f"Error reading universe: {e}")
        else:
            # Fallback to hard-coded list
            underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

        # Assign tiers
        tier_rows = []
        for underlying in underlyings:
            risk_tier = RISK_TIER_MAP.get(underlying, "MEDIUM")  # Default to MEDIUM
            max_trades = MAX_TRADES_BY_TIER.get(risk_tier, 3)

            tier_rows.append(
                {
                    "underlying": underlying,
                    "risk_tier": risk_tier,
                    "max_trades": max_trades,
                    "max_lot_per_trade": 1,  # Always 1 for now
                }
            )

        # Create dataframe
        df = pd.DataFrame(tier_rows)

        # Save CSV
        df.to_csv(OUTPUT_CSV_PATH, index=False)

        status = "OK"
        details = f"Risk tiers assigned: {len(df)} underlyings"

        return {
            "phase": 138,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "underlying_count": len(df),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 138,
            "status": "ERROR",
            "details": f"Phase 138 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 138 - ANGEL RISK TIER ASSIGNMENT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase138_risk_tier_assignment()

    print(f"Phase138: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nUnderlyings: {result['outputs']['underlying_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
