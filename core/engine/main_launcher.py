import os
import sys

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.env_manager import env
from core.utils.logger import logger


def main():
    logger.info("=== Genesis System 3 Booting ===")

    current_mode = "LIVE" if env.is_live() else "TEST"
    msg1 = f"System running in {current_mode} mode"
    msg2 = f"Market: {env.get_market()}"
    msg3 = "System ready."

    # Log
    logger.info(msg1)
    logger.info(msg2)
    logger.info(msg3)

    # Also print to terminal so you can SEE it
    print(msg1)
    print(msg2)
    print(msg3)


if __name__ == "__main__":
    main()
