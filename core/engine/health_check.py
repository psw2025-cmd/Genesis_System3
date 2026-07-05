import os
import sys

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.data.storage_manager import save_json_snapshot
from core.utils.env_manager import env
from core.utils.logger import logger


def main():
    logger.info("=== Running System3 Health Check ===")

    # Check environment
    mode = "LIVE" if env.is_live() else "TEST"
    market = env.get_market()
    print(f"[ENV] Mode: {mode}, Market: {market}")

    # Check storage
    path = save_json_snapshot({"health": "ok"}, "HEALTHCHECK")
    print(f"[STORAGE] Test snapshot stored at: {path}")

    logger.info("Health check completed successfully.")


if __name__ == "__main__":
    main()
