
import os, sys
# Ensure project root in path
ROOT_DIR = r"C:\Genesis_System3"
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.brokers.angel_one.broker import AngelOneBroker
import json

def test_fetch():
    print("Testing AngelOneBroker Option Chain Fetch...")
    try:
        # Initialize in data-only mode
        broker = AngelOneBroker(allow_data_only=True)
        
        # Test NIFTY (most liquid)
        print("Fetching NIFTY Option Chain...")
        chain = broker.get_option_chain_by_underlying("NIFTY", exchange="NFO")
        
        if chain and len(chain) > 0:
            print(f"[SUCCESS] Fetched {len(chain)} contracts for NIFTY")
            print(f"Sample contract: {chain[0]['symbol']} | LTP: {chain[0]['ltp']}")
            return True
        else:
            print("[FAILURE] No data returned from Angel API")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fetch()
