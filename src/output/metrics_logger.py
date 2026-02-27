"""
Metrics Logger - One-line per cycle logging
"""
import logging
from pathlib import Path
import sys
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup metrics logger
metrics_log_path = ROOT_DIR / "logs" / "metrics.log"
metrics_log_path.parent.mkdir(parents=True, exist_ok=True)

metrics_logger = logging.getLogger("metrics")
metrics_logger.setLevel(logging.INFO)
metrics_handler = logging.FileHandler(metrics_log_path, encoding='utf-8')
metrics_handler.setFormatter(logging.Formatter('%(message)s'))
metrics_logger.addHandler(metrics_handler)
metrics_logger.propagate = False


def log_cycle_metrics(
    cycle: int,
    timestamp: str,
    qc_passed: bool,
    top_underlying: str,
    trade_action: str,
    underlying_count: int,
    contract_count: int
):
    """
    Log one-line metrics for a cycle.
    
    Args:
        cycle: Cycle number
        timestamp: Timestamp string
        qc_passed: QC pass status
        top_underlying: Top underlying selected
        trade_action: Trade action (TRADE/NO_TRADE)
        underlying_count: Number of underlyings processed
        contract_count: Total contracts processed
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    line = (
        f"{now.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"CYCLE={cycle} | "
        f"QC={'PASS' if qc_passed else 'FAIL'} | "
        f"TOP={top_underlying or 'NONE'} | "
        f"ACTION={trade_action} | "
        f"UNDERLYINGS={underlying_count} | "
        f"CONTRACTS={contract_count}"
    )
    
    metrics_logger.info(line)
