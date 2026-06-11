"""Test script to verify getOptionGreeks() fix - should return delta/gamma"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker

print("="*80)
print("TESTING getOptionGreeks() FIX")
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

# Test with NIFTY and current expiry
test_name = "NIFTY"
test_expiry = "24JAN2026"  # Adjust to current expiry

print(f"Testing Greeks fetch for:")
print(f"  Underlying: {test_name}")
print(f"  Expiry: {test_expiry}")
print()

print("Fetching Greeks...")
try:
    # Test wrapper method
    greeks = broker.getOptionGreeks(test_name, test_expiry)
    
    print()
    print("="*80)
    print("GREEKS RESPONSE:")
    print("="*80)
    
    if greeks:
        print(f"Status: {greeks.get('status')}")
        print()
        
        if greeks.get('status') and greeks.get('data'):
            data = greeks['data']
            print(f"Response type: {type(data)}")
            print()
            
            # Data is organized by strike (as string keys)
            if isinstance(data, dict):
                print(f"Number of strikes: {len(data)}")
                print()
                
                # Show first few strikes
                strikes = list(data.keys())[:5]
                print("Sample strikes (first 5):")
                for strike_key in strikes:
                    strike_data = data[strike_key]
                    print(f"  Strike {strike_key}:")
                    if isinstance(strike_data, dict):
                        # May have CE/PE or direct fields
                        if 'CE' in strike_data:
                            ce_data = strike_data['CE']
                            print(f"    CE - delta: {ce_data.get('delta')}, gamma: {ce_data.get('gamma')}")
                        if 'PE' in strike_data:
                            pe_data = strike_data['PE']
                            print(f"    PE - delta: {pe_data.get('delta')}, gamma: {pe_data.get('gamma')}")
                        # Direct fields
                        if 'delta' in strike_data:
                            print(f"    delta: {strike_data.get('delta')}, gamma: {strike_data.get('gamma')}")
                    print()
            else:
                print(f"Data structure: {data}")
            
            print("="*80)
            print("VALIDATION:")
            print("="*80)
            
            if isinstance(data, dict) and len(data) > 0:
                # Check first strike for Greeks
                first_strike = list(data.keys())[0]
                first_data = data[first_strike]
                
                has_delta = False
                has_gamma = False
                
                if isinstance(first_data, dict):
                    if 'CE' in first_data:
                        has_delta = first_data['CE'].get('delta') is not None
                        has_gamma = first_data['CE'].get('gamma') is not None
                    elif 'delta' in first_data:
                        has_delta = first_data.get('delta') is not None
                        has_gamma = first_data.get('gamma') is not None
                
                print(f"  Data structure valid: [OK]")
                print(f"  Delta present: {'[OK]' if has_delta else '[MISSING]'}")
                print(f"  Gamma present: {'[OK]' if has_gamma else '[MISSING]'}")
                
                if has_delta and has_gamma:
                    print()
                    print("[SUCCESS] Greeks data available!")
                else:
                    print()
                    print("[WARNING] Greeks fields may be in different structure")
            else:
                print("[ERROR] No strike data found")
        else:
            print("[ERROR] No data in response")
            print(f"Full response: {greeks}")
    else:
        print("[ERROR] No response from API")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
