"""Production-grade structured logging"""
import logging
import json
import time
import traceback
from datetime import datetime
from typing import Optional
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "traceback": traceback.format_exc(),
            }
        return json.dumps(log_data)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    
    return logger

logger = setup_logger("genesis_system3_backend")
