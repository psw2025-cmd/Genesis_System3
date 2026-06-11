"""Test script to verify get_quote() fix - should return OI/volume/bid/ask"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker

print("="*80)
print("TESTING get_quote() FIX")
print("="*80)
print()

# Initialize broker
print("Initializing broker...")
try:
    broker = AngelOneBroker(allow_data_only=True)
    print("[OK] Broker initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize broker: {e}")
    sys.exit(1)

print()

# Test with a real NIFTY option from CSV
test_symbol = "NIFTY24FEB2624150CE"  # From actual CSV
test_token = "64794"  # From actual CSV
test_exchange = "NFO"

print(f"Testing quote fetch for:")
print(f"  Exchange: {test_exchange}")
print(f"  Symbol: {test_symbol}")
print(f"  Token: {test_token}")
print()

print("Fetching quote...")
try:
    # Also test direct SmartAPI call to see raw response
    print("Testing direct SmartAPI getMarketData call...")
    raw_response = broker.smart.getMarketData("FULL", {test_exchange: [test_token]})
    print(f"Raw response type: {type(raw_response)}")
    if raw_response:
        print(f"Raw response keys: {list(raw_response.keys()) if isinstance(raw_response, dict) else 'N/A'}")
    if isinstance(raw_response, dict) and raw_response.get('data'):
        print(f"Data type: {type(raw_response['data'])}")
        if isinstance(raw_response['data'], dict):
            print(f"Data dict keys: {list(raw_response['data'].keys())}")
            # Check fetched key
            if 'fetched' in raw_response['data']:
                fetched = raw_response['data']['fetched']
                print(f"Fetched type: {type(fetched)}")
                if isinstance(fetched, list) and len(fetched) > 0:
                    print(f"Fetched list length: {len(fetched)}")
                    print(f"First fetched item keys: {list(fetched[0].keys()) if isinstance(fetched[0], dict) else 'N/A'}")
                    print(f"First fetched item (full): {fetched[0]}")
                elif isinstance(fetched, dict):
                    print(f"Fetched keys: {list(fetched.keys())}")
                    if 'NFO' in fetched:
                        nfo_data = fetched['NFO']
                        print(f"NFO data type: {type(nfo_data)}")
                        if isinstance(nfo_data, list) and len(nfo_data) > 0:
                            print(f"NFO list length: {len(nfo_data)}")
                            print(f"First NFO item keys: {list(nfo_data[0].keys()) if isinstance(nfo_data[0], dict) else 'N/A'}")
                            print(f"First NFO item (full): {nfo_data[0]}")
                        elif isinstance(nfo_data, dict):
                            print(f"NFO dict keys: {list(nfo_data.keys())}")
                            print(f"NFO dict (full): {nfo_data}")
            # Check unfetched
            if 'unfetched' in raw_response['data']:
                unfetched = raw_response['data']['unfetched']
                print(f"Unfetched: {unfetched}")
    print()
    
    quote = broker.get_quote(test_exchange, test_symbol, test_token)
    
    print()
    print("="*80)
    print("QUOTE RESPONSE (from get_quote):")
    print("="*80)
    
    if quote:
        print(f"Status: {quote.get('status')}")
        print()
        
        if quote.get('status') and quote.get('data'):
            data = quote['data']
            print("Data fields:")
            print(f"  ltp: {data.get('ltp')}")
            print(f"  oi: {data.get('oi')}")
            print(f"  volume: {data.get('volume')}")
            print(f"  bidPrice: {data.get('bidPrice')}")
            print(f"  bidQty: {data.get('bidQty')}")
            print(f"  offerPrice: {data.get('offerPrice')}")
            print(f"  offerQty: {data.get('offerQty')}")
            print(f"  open: {data.get('open')}")
            print(f"  high: {data.get('high')}")
            print(f"  low: {data.get('low')}")
            print(f"  close: {data.get('close')}")
            print(f"  exchangeTimestamp: {data.get('exchangeTimestamp')}")
            
            print()
            print("="*80)
            print("VALIDATION:")
            print("="*80)
            
            has_oi = data.get('oi') is not None
            has_volume = data.get('volume') is not None
            has_bid = data.get('bidPrice') is not None
            has_ask = data.get('offerPrice') is not None
            
            print(f"  OI present: {'[OK]' if has_oi else '[MISSING]'}")
            print(f"  Volume present: {'[OK]' if has_volume else '[MISSING]'}")
            print(f"  BidPrice present: {'[OK]' if has_bid else '[MISSING]'}")
            print(f"  OfferPrice present: {'[OK]' if has_ask else '[MISSING]'}")
            
            if has_oi and has_volume and has_bid and has_ask:
                print()
                print("[SUCCESS] All required fields present!")
            else:
                print()
                print("[WARNING] Some fields missing (may be market hours issue)")
        else:
            print("[ERROR] No data in response")
            print(f"Full response: {quote}")
    else:
        print("[ERROR] No response from API")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
