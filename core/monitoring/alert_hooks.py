"""
System3 Phase 242 - Alert Hooks (Log-Only)

Prepare a minimal alert hook (log-only, no external calls).
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "monitoring"
LOG_DIR.mkdir(parents=True, exist_ok=True)
ALERT_LOG = LOG_DIR / "system3_alerts.log"


def log_virtual_trade_alert(message: str) -> None:
    """
    Log alert message to file.

    Args:
        message: Alert message to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    try:
        with ALERT_LOG.open("a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        # Fallback to standard logger if file write fails
        from core.utils.logger import logger

        logger.warning(f"Failed to write alert log: {e}")
