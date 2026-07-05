import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.data.data_router import fetch_and_store_history, fetch_and_store_live
from core.utils.logger import logger


def main():
    logger.info("=== System3 Data Pipeline Test ===")

    print("Fetching live data...")
    live_path = fetch_and_store_live("BTCUSDT")
    print(f"Live saved at: {live_path}")

    print("Fetching history...")
    hist_path = fetch_and_store_history("BTCUSDT", "1h", 5)
    print(f"History saved at: {hist_path}")

    print("Test completed.")


if __name__ == "__main__":
    main()
