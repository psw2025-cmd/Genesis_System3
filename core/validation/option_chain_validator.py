"""
Option Chain Validator — DISABLED (Angel One / SmartAPI path).

System3 is Dhan-only. This validator used AngelOneBroker to re-fetch missing
option chain data. That path is not operational.

The class interface is preserved so imports do not break; any instantiation
with broker=None (the auto-create path) raises RuntimeError.
Callers that pass an explicit broker will still get the disabled shim error
when AngelOneBroker itself raises.
"""

import sys
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from core.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

_DISABLED_REASON = (
    "OptionChainValidator auto-fetch path is disabled. "
    "System3 is Dhan-only. AngelOneBroker is not operational."
)


class OptionChainValidator:
    """
    Disabled Angel One option-chain validator.

    Preserved for backward-compatible imports only.
    Raises RuntimeError if broker auto-creation is attempted (broker=None).
    Static/pure validation methods that do not need a broker are kept functional.
    """

    CRITICAL_COLUMNS = ["ltp", "oi", "bidPrice", "offerPrice", "delta"]
    MIN_ROWS_NIFTY = 100
    MAX_NAN_RATE = 0.10

    def __init__(self, broker=None):
        if broker is None:
            raise RuntimeError(_DISABLED_REASON)
        self.broker = broker
        self.log_file = ROOT_DIR / "storage" / "logs" / "api_pull_validation.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def validate(self, *_args, **_kwargs):
        raise RuntimeError(_DISABLED_REASON)

    def auto_correct(self, *_args, **_kwargs):
        raise RuntimeError(_DISABLED_REASON)

    def validate_and_correct(self, *_args, **_kwargs):
        raise RuntimeError(_DISABLED_REASON)

    @staticmethod
    def validate_dataframe(df, min_rows: int = 0) -> dict:
        """Pure-data validation — no broker needed. Safe to use."""
        if df is None:
            return {"valid": False, "reason": "DataFrame is None"}
        if df.empty:
            return {"valid": False, "reason": "DataFrame is empty"}
        if min_rows and len(df) < min_rows:
            return {"valid": False, "reason": f"Too few rows: {len(df)} < {min_rows}"}
        return {"valid": True, "rows": len(df)}
