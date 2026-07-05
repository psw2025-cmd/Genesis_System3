"""
System3 Phase 136 - Angel Symbol Universe

Creates static metadata for supported Angel index symbols.
"""

import json
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

OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase136_dhan_symbol_universe.csv"
OUTPUT_JSON_PATH = STORAGE_ULTRA / "phase136_dhan_symbol_universe.json"

# Supported underlyings (hard-coded)
SUPPORTED_UNDERLYINGS = [
    {"underlying": "NIFTY", "dhan_symbol": "NIFTY", "segment": "NSEFO"},
    {"underlying": "BANKNIFTY", "dhan_symbol": "BANKNIFTY", "segment": "NSEFO"},
    {"underlying": "FINNIFTY", "dhan_symbol": "FINNIFTY", "segment": "NSEFO"},
    {"underlying": "MIDCPNIFTY", "dhan_symbol": "MIDCPNIFTY", "segment": "NSEFO"},
    {"underlying": "SENSEX", "dhan_symbol": "SENSEX", "segment": "BSEFO"},
]


def run_phase136_dhan_symbol_universe() -> Dict[str, Any]:
    """
    Create Angel symbol universe metadata.

    Returns:
        dict: {
            "phase": 136,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Create dataframe
        df = pd.DataFrame(SUPPORTED_UNDERLYINGS)
        df["enabled"] = True  # Default all enabled

        # Save CSV
        df.to_csv(OUTPUT_CSV_PATH, index=False)

        # Save JSON
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "symbols": df.to_dict(orient="records"),
        }
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        status = "OK"
        details = f"Symbol universe created: {len(df)} symbols"

        return {
            "phase": 136,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "json_path": str(OUTPUT_JSON_PATH),
                "symbol_count": len(df),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 136,
            "status": "ERROR",
            "details": f"Phase 136 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 136 - ANGEL SYMBOL UNIVERSE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase136_dhan_symbol_universe()

    print(f"Phase136: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nSymbols: {result['outputs']['symbol_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")
        print(f"JSON: {result['outputs']['json_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
