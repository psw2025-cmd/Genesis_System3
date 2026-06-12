"""
Debug Greeks Calculation - Find why it's not working
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from src.metrics.greeks import calculate_greeks_from_market_price


def debug():
    """Debug Greeks calculation."""
    print("=" * 80)
    print("  DEBUGGING GREEKS CALCULATION")
    print("=" * 80)

    broker = AngelOneBroker(allow_data_only=True)
    chain_data = broker.get_option_chain_by_underlying("NIFTY", exchange="NFO")

    if not chain_data:
        print("No data")
        return

    # Get first option with LTP
    sample = None
    for opt in chain_data:
        if opt.get("ltp") and opt.get("ltp") > 0:
            sample = opt
            break

    if not sample:
        sample = chain_data[0]

    print(f"\nSample Option:")
    print(f"  Symbol: {sample.get('symbol')}")
    print(f"  Strike: {sample.get('strike')}")
    print(f"  Expiry: {sample.get('expiry')}")
    print(f"  Expiry Date: {sample.get('expiry_date')}")
    print(f"  LTP: {sample.get('ltp')}")
    print(f"  Spot: {sample.get('spot_price')}")
    print(f"  Option Type: {sample.get('option_type')}")

    # Try to parse expiry
    expiry_date_str = sample.get("expiry_date", "")
    print(f"\nParsing Expiry Date: '{expiry_date_str}'")

    expiry_date = None
    if expiry_date_str:
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y%m%d"]:
            try:
                expiry_date = datetime.strptime(str(expiry_date_str).split()[0], fmt)
                print(f"  Parsed with format {fmt}: {expiry_date}")
                break
            except Exception as e:
                print(f"  Failed with format {fmt}: {e}")
                continue

    if expiry_date:
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        time_to_expiry = (expiry_date.replace(tzinfo=ist) - now).total_seconds() / (365.25 * 24 * 3600)
        print(f"\nTime to Expiry: {time_to_expiry} years")

        if time_to_expiry > 0:
            mid_price = sample.get("ltp")
            if sample.get("bidPrice") and sample.get("offerPrice"):
                mid_price = (sample.get("bidPrice") + sample.get("offerPrice")) / 2.0
                print(f"Using mid price: {mid_price}")

            print(f"\nCalculating Greeks...")
            print(f"  Spot: {sample.get('spot_price')}")
            print(f"  Strike: {sample.get('strike')}")
            print(f"  Time: {time_to_expiry}")
            print(f"  Price: {mid_price}")
            print(f"  Type: {sample.get('option_type')}")

            try:
                greeks = calculate_greeks_from_market_price(
                    spot=sample.get("spot_price"),
                    strike=float(sample.get("strike")),
                    time_to_expiry=time_to_expiry,
                    option_type=sample.get("option_type"),
                    market_price=mid_price,
                    risk_free_rate=0.06,
                )

                if greeks:
                    print(f"\n[SUCCESS] Greeks calculated:")
                    print(f"  Delta: {greeks.get('delta')}")
                    print(f"  Gamma: {greeks.get('gamma')}")
                    print(f"  Theta: {greeks.get('theta')}")
                    print(f"  Vega: {greeks.get('vega')}")
                    print(f"  IV: {greeks.get('iv')}")
                else:
                    print("\n[FAILED] calculate_greeks_from_market_price returned None")
            except Exception as e:
                print(f"\n[ERROR] Calculation failed: {e}")
                import traceback

                traceback.print_exc()
        else:
            print(f"\n[WARNING] Time to expiry is <= 0")
    else:
        print("\n[ERROR] Could not parse expiry date")


if __name__ == "__main__":
    debug()
