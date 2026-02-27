"""
System3 Phase 137 - Expiry & Calendar Map

Creates expiry calendar mapping for supported underlyings.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

UNIVERSE_CSV_PATH = STORAGE_ULTRA / "phase136_angel_symbol_universe.csv"
OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase137_expiry_calendar_map.csv"


# Approximate expiry calculation (if live API not available)
def get_next_expiries(base_date: datetime, count: int = 4) -> list:
    """Calculate next 4 weekly/monthly expiries."""
    expiries = []
    current = base_date

    # Find next Thursday (typical weekly expiry)
    days_until_thursday = (3 - current.weekday()) % 7
    if days_until_thursday == 0 and current.hour >= 15:  # After market close
        days_until_thursday = 7

    next_thursday = current + timedelta(days=days_until_thursday)

    for i in range(count):
        expiry = next_thursday + timedelta(weeks=i)
        expiries.append(expiry.strftime("%Y-%m-%d"))

    return expiries


def run_phase137_expiry_calendar_map() -> Dict[str, Any]:
    """
    Create expiry calendar map.

    Returns:
        dict: {
            "phase": 137,
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

        # Try to get live expiries (safe API call if available)
        # For now, use approximation
        today = datetime.now()
        expiry_rows = []

        for underlying in underlyings:
            # Get next 4 expiries (approximate)
            expiries = get_next_expiries(today, count=4)

            for i, expiry_date in enumerate(expiries):
                expiry_rows.append(
                    {
                        "underlying": underlying,
                        "expiry_date": expiry_date,
                        "type": "WEEKLY" if i < 3 else "MONTHLY",  # Approximate
                        "priority": i + 1,  # 1 = nearest
                    }
                )

        # Create dataframe
        df = pd.DataFrame(expiry_rows)

        # Save CSV
        df.to_csv(OUTPUT_CSV_PATH, index=False)

        status = "OK"
        details = f"Expiry calendar created: {len(df)} entries for {len(underlyings)} underlyings"

        return {
            "phase": 137,
            "status": status,
            "details": details,
            "outputs": {
                "csv_path": str(OUTPUT_CSV_PATH),
                "entry_count": len(df),
                "underlying_count": len(underlyings),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 137,
            "status": "ERROR",
            "details": f"Phase 137 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 137 - EXPIRY & CALENDAR MAP")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase137_expiry_calendar_map()

    print(f"Phase137: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nEntries: {result['outputs']['entry_count']}")
        print(f"Underlyings: {result['outputs']['underlying_count']}")
        print(f"CSV: {result['outputs']['csv_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
