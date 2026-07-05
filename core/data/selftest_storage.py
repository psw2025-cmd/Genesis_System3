import os
import sys

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.data.storage_manager import list_files, save_json_snapshot
from core.utils.logger import logger


def main():
    logger.info("Running storage self-test...")
    dummy_data = {"price": 100.5, "volume": 12345}
    symbol = "TESTSYM"

    path = save_json_snapshot(dummy_data, symbol)
    logger.info(f"Snapshot saved at: {path}")
    print(f"Snapshot saved at: {path}")

    files = list_files(symbol)
    logger.info(f"Files for {symbol}: {files}")
    print(f"Files for {symbol}: {files}")


if __name__ == "__main__":
    main()
