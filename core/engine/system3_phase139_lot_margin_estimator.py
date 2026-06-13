"""
System3 Phase 139 - Lot Size & Margin Estimation

Estimates lot sizes and margins for each underlying (approximate metadata).
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
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

UNIVERSE_CSV_PATH = STORAGE_ULTRA / "phase136_dhan_symbol_universe.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase139_lot_margin.csv"

# Known lot sizes (hard-coded constants)
LOT_SIZES = {
    "NIFTY": 50,
    "BANKNIFTY": 15,
    "FINNIFTY": 50,
    "MIDCPNIFTY": 50,
    "SENSEX": 10,
}

# Estimated margin per lot (approximate, in INR)
EST_MARGIN_PER_LOT = {
    "NIFTY": 50000,
    "BANKNIFTY": 60000,
    "FINNIFTY": 40000,
    "MIDCPNIFTY": 35000,
    "SENSEX": 45000,
}


def run_phase139_lot_margin_estimator() -> Dict[str, Any]:
    """
    Estimate lot sizes and margins.

    Returns:
        dict: {
            "phase": 139,
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

        # Build lot/margin data
        lot_margin_rows = []
        for underlying in underlyings:
            lot_size = LOT_SIZES.get(underlying, 50)  # Default 50
            est_margin = EST_MARGIN_PER_LOT.get(underlying, 50000)  # Default 50k
            base_capital_unit = lot_size * est_margin  # Simplified calculation

            lot_margin_rows.append(
                {
                    "underlying": underlying,
                    "lot_size": lot_size,
                    "est_margin_per_lot": est_margin,
                    "base_capital_unit": base_capital_unit,
                }
            )

        # Create dataframe
        df = pd.DataFrame(lot_margin_rows)

        # Save CSV
        df.to_csv(OUTPUT_CSV_PATH, index=False)

        status = "OK"
        details = f"Lot/margin estimates created: {len(df)} underlyings"

        return {
            "phase": 139,
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
            "phase": 139,
            "status": "ERROR",
            "details": f"Phase 139 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 139 - LOT SIZE & MARGIN ESTIMATION")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase139_lot_margin_estimator()

    print(f"Phase139: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nUnderlyings: {result['outputs']['underlying_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
