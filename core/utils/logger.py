import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_log_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")


class SanitizedFormatter(logging.Formatter):
    """Formatter that sanitizes log messages to mask secrets"""

    def format(self, record):
        # Get original message
        original_msg = super().format(record)

        # Sanitize it
        try:
            from core.utils.log_sanitizer import sanitize_log_message

            return sanitize_log_message(original_msg)
        except ImportError:
            # If sanitizer not available, return original (shouldn't happen)
            return original_msg


def setup_logger(name="SYSTEM3"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(get_log_file(), encoding="utf-8")
        formatter = SanitizedFormatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Also add console handler with sanitization
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()
