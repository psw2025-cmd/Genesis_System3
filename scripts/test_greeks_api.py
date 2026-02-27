"""
Test Greeks API - Debug why Greeks are not being fetched
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger


def test_greeks_api():
    """Test Greeks API directly."""
    print("=" * 80)
    print("  TESTING GREEKS API")
    print("=" * 80)

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Day: {now.strftime('%A')}")

    # Check market hours
    market_open = now.weekday() < 5 and now.hour >= 9 and (now.hour < 15 or (now.hour == 15 and now.minute <= 30))
    print(f"Market Open: {market_open}")

    # Initialize broker
    print("\n[STEP 1] Initializing Broker...")
    try:
        broker = AngelOneBroker(allow_data_only=True)
        print("  [OK] Broker initialized")
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        return False

    # Test with a known NIFTY option
    print("\n[STEP 2] Testing Greeks API for NIFTY...")

    # Get a sample option from the chain
    print("  Fetching option chain to get sample contract...")
    chain_data = broker.get_option_chain_by_underlying("NIFTY", exchange="NFO")

    if not chain_data or len(chain_data) == 0:
        print("  [ERROR] No option chain data")
        return False

    # Get first ATM option
    sample_option = None
    for opt in chain_data:
        if opt.get("moneyness") == "ATM" or abs(opt.get("strike", 0) - opt.get("spot_price", 0)) < 200:
            sample_option = opt
            break

    if not sample_option:
        sample_option = chain_data[0]

    print(f"\n  Sample Option:")
    print(f"    Symbol: {sample_option.get('symbol')}")
    print(f"    Strike: {sample_option.get('strike')}")
    print(f"    Expiry: {sample_option.get('expiry')}")
    print(f"    Option Type: {sample_option.get('option_type')}")
    print(f"    Token: {sample_option.get('token')}")

    # Test get_option_greeks directly
    print("\n[STEP 3] Testing get_option_greeks() method...")
    try:
        expiry_str = str(sample_option.get("expiry", "")).replace("-", "").upper()
        greeks_result = broker.get_option_greeks(
            exchange="NFO",
            tradingsymbol=sample_option.get("symbol"),
            symboltoken=str(sample_option.get("token")),
            strike_price=float(sample_option.get("strike")),
            expiry_date=expiry_str,
            option_type=sample_option.get("option_type"),
        )

        print(f"  Result Status: {greeks_result.get('status') if greeks_result else 'None'}")

        if greeks_result and greeks_result.get("status"):
            greeks_data = greeks_result.get("data", {})
            print(f"  [SUCCESS] Greeks data received:")
            print(f"    Delta: {greeks_data.get('delta')}")
            print(f"    Gamma: {greeks_data.get('gamma')}")
            print(f"    Theta: {greeks_data.get('theta')}")
            print(f"    Vega: {greeks_data.get('vega')}")
            print(f"    Rho: {greeks_data.get('rho')}")
            print(f"    IV: {greeks_data.get('iv')}")
        else:
            print(f"  [FAILED] No Greeks data")
            print(f"  Response: {greeks_result}")

            # Try alternative method - getOptionGreeks (bulk)
            print("\n[STEP 4] Trying alternative method - getOptionGreeks (bulk)...")
            underlying_name = sample_option.get("underlying", "NIFTY")
            expiry_normalized = expiry_str

            # Try to normalize expiry format
            if len(expiry_normalized) == 8 and expiry_normalized.isdigit():
                # DDMMYYYY -> DDMMMYYYY
                day = expiry_normalized[:2]
                month = expiry_normalized[2:4]
                year = expiry_normalized[4:8]
                month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
                try:
                    month_name = month_names[int(month) - 1]
                    expiry_normalized = f"{day}{month_name}{year}"
                except:
                    pass

            print(f"  Calling getOptionGreeks with:")
            print(f"    Name: {underlying_name}")
            print(f"    Expiry: {expiry_normalized}")

            bulk_greeks = broker.getOptionGreeks(underlying_name, expiry_normalized)

            if bulk_greeks and bulk_greeks.get("status"):
                print(f"  [SUCCESS] Bulk Greeks data received")
                greeks_data = bulk_greeks.get("data", {})

                # Handle different response structures
                if isinstance(greeks_data, list):
                    print(f"  Response is a LIST with {len(greeks_data)} items")
                    if len(greeks_data) > 0:
                        print(f"  First item type: {type(greeks_data[0])}")
                        print(f"  First item: {greeks_data[0]}")
                        # Try to find our strike
                        strike_key = int(sample_option.get("strike"))
                        opt_type = sample_option.get("option_type")
                        for item in greeks_data:
                            if isinstance(item, dict):
                                if item.get("strikePrice") == strike_key and item.get("optionType") == opt_type:
                                    print(f"  Found matching option:")
                                    print(f"    Delta: {item.get('delta')}")
                                    print(f"    Gamma: {item.get('gamma')}")
                                    print(f"    Theta: {item.get('theta')}")
                                    print(f"    Vega: {item.get('vega')}")
                                    print(f"    IV: {item.get('iv')}")
                                    break
                elif isinstance(greeks_data, dict):
                    strike_key = str(int(sample_option.get("strike")))

                    if strike_key in greeks_data:
                        strike_data = greeks_data[strike_key]
                        opt_type = sample_option.get("option_type")
                        option_data = (
                            strike_data.get(opt_type, {}) or strike_data.get(opt_type.lower(), {}) or strike_data
                        )

                        print(f"  Greeks for strike {strike_key}, {opt_type}:")
                        print(f"    Delta: {option_data.get('delta')}")
                        print(f"    Gamma: {option_data.get('gamma')}")
                        print(f"    Theta: {option_data.get('theta')}")
                        print(f"    Vega: {option_data.get('vega')}")
                        print(f"    IV: {option_data.get('iv')}")
                    else:
                        print(f"  [WARNING] Strike {strike_key} not found in bulk data")
                        if len(greeks_data) > 0:
                            print(f"  Available strikes: {list(greeks_data.keys())[:10]}")
                else:
                    print(f"  [WARNING] Unknown response structure: {type(greeks_data)}")
                    print(f"  Data: {greeks_data}")
            else:
                print(f"  [FAILED] Bulk Greeks API failed")
                print(f"  Response: {bulk_greeks}")

                # Check if API method exists
                print("\n[STEP 5] Checking available API methods...")
                if hasattr(broker.smart, "optionGreek"):
                    print("  [OK] optionGreek method exists")
                else:
                    print("  [ERROR] optionGreek method NOT found")

                # Try to see what methods are available
                print("\n  Available SmartAPI methods (containing 'greeks' or 'greek'):")
                methods = [m for m in dir(broker.smart) if "greek" in m.lower() and not m.startswith("_")]
                if methods:
                    for m in methods:
                        print(f"    - {m}")
                else:
                    print("    None found")

                # Check raw API response
                print("\n[STEP 6] Testing raw API call...")
                try:
                    params = {"name": underlying_name, "expirydate": expiry_normalized}
                    print(f"  Params: {params}")
                    raw_response = broker.smart.optionGreek(params)
                    print(f"  Raw Response Type: {type(raw_response)}")
                    print(f"  Raw Response: {raw_response}")
                except Exception as e:
                    print(f"  [ERROR] Raw API call failed: {e}")
                    import traceback

                    traceback.print_exc()

    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    return True


if __name__ == "__main__":
    test_greeks_api()
