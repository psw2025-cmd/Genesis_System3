import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.brokers.angel_one.instruments import (
    load_instruments,
    find_by_tradingsymbol,
    find_options_for_underlying,
)
from core.utils.logger import logger


def main():
    logger.info("=== AngelOne Instruments Test ===")
    print("Testing AngelOne instruments master...")

    df = load_instruments()
    if df is None:
        print("[ERROR] Instruments file missing or unreadable.")
        print("Expected JSON file at:")
        print("  storage/instruments/OpenAPIScripMaster.json")
        return

    print(f"[INFO] Total instruments loaded: {len(df)}")

    # Example equity lookup
    row = find_by_tradingsymbol("NSE", "SBIN-EQ")
    if row:
        print("[LOOKUP] SBIN-EQ:", row)
    else:
        print("[LOOKUP] Could not find SBIN-EQ in master.")

    # Example NIFTY options subset
    nifty_opts = find_options_for_underlying("NIFTY", "NFO")
    if nifty_opts is not None:
        print(f"[NIFTY OPTIONS] Found {len(nifty_opts)} option contracts for NIFTY (NFO).")
        print(nifty_opts.head().to_string(index=False))
    else:
        print("[NIFTY OPTIONS] No NIFTY options found (check columns & file).")

    print("AngelOne instruments test completed.")
    logger.info("=== AngelOne Instruments Test Completed ===")


if __name__ == "__main__":
    main()
