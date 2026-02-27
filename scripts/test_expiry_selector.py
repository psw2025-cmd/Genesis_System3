"""
Test ExpirySelector - Verify expiry selection works for all indices
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.angel.expiry_selector import ExpirySelector


def main():
    """Test expiry selector for all indices."""
    print("=" * 80)
    print("EXPIRY SELECTOR TEST")
    print("=" * 80)
    print()

    indices = [
        {"name": "NIFTY", "exchange": "NFO"},
        {"name": "BANKNIFTY", "exchange": "NFO"},
        {"name": "FINNIFTY", "exchange": "NFO"},
        {"name": "MIDCPNIFTY", "exchange": "NFO"},
        {"name": "SENSEX", "exchange": "BFO"},
    ]

    selector = ExpirySelector()

    print("Testing expiry selection for all indices:")
    print()

    results = {}
    for idx in indices:
        name = idx["name"]
        exchange = idx["exchange"]

        try:
            expiry_str = selector.get_nearest_weekly_expiry(name, exchange)
            expiry_date = selector.get_expiry_date(name, exchange)

            if expiry_str:
                results[name] = {
                    "expiry_string": expiry_str,
                    "expiry_date": str(expiry_date) if expiry_date else "None",
                    "status": "SUCCESS",
                }
                print(f"[OK] {name} ({exchange}): {expiry_str} ({expiry_date})")
            else:
                results[name] = {"expiry_string": None, "expiry_date": None, "status": "FAILED"}
                print(f"[FAIL] {name} ({exchange}): No expiry found")
        except Exception as e:
            results[name] = {"expiry_string": None, "expiry_date": None, "status": f"ERROR: {e}"}
            print(f"[ERROR] {name} ({exchange}): Error - {e}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    success_count = sum(1 for r in results.values() if r["status"] == "SUCCESS")
    print(f"Success: {success_count}/{len(indices)}")

    for name, result in results.items():
        print(f"{name}: {result['status']}")
        if result["expiry_string"]:
            print(f"  Expiry: {result['expiry_string']} ({result['expiry_date']})")

    return success_count == len(indices)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
