import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger


def main():
    logger.info("=== AngelOne API Test Start ===")
    print("Initializing AngelOne broker...")

    try:
        broker = AngelOneBroker(allow_data_only=True)  # Data fetching doesn't require live trading permission
    except Exception as e:
        print(f"[ERROR] AngelOne login failed: {e}")
        logger.error(f"AngelOne login failed: {e}")
        return

    print("Login successful.")

    # 1) Fetch profile
    profile = broker.get_profile()
    if profile:
        print("[PROFILE] status:", profile.get("status"))
        print("[PROFILE] clientcode:", profile.get("data", {}).get("clientcode"))
    else:
        print("[PROFILE] Failed to fetch profile")

    # 2) Fetch LTP for a known symbol (example: SBIN-EQ, token 3045)
    print("\nRequesting LTP for NSE: SBIN-EQ (token 3045)...")
    ltp = broker.get_ltp("NSE", "SBIN-EQ", "3045")
    if ltp:
        print("[LTP RAW]", ltp)
        try:
            ltp_value = ltp["data"]["ltp"]
            print(f"[LTP] SBIN-EQ: {ltp_value}")
        except Exception:
            print("[LTP] Could not parse ltp field from response.")
    else:
        print("[LTP] Failed to fetch LTP")

    print("\nAngelOne API test completed.")
    logger.info("=== AngelOne API Test Completed ===")


if __name__ == "__main__":
    main()
