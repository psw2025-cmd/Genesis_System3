"""
P2.2: Structured JSON logging for backend.
Outputs JSON lines to logs/backend.jsonl for ELK/CloudWatch ingestion.
"""

import sys
from pathlib import Path
from loguru import logger

ROOT_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = ROOT_DIR / "logs"
LOG_FILE = LOGS_DIR / "backend.jsonl"


def setup_structured_logging():
    """Configure loguru for structured JSON file + human-readable stdout."""
    logger.remove()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    # JSON to file (for ELK/CloudWatch) - serialize=True outputs JSON lines
    logger.add(
        LOG_FILE,
        serialize=True,
        level="INFO",
        rotation="10 MB",
        retention="7 days",
    )
    # Human-readable to stdout
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    return logger
