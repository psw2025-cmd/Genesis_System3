"""
System3 Phase 343 - Signals Existence & Freshness Enforcer

Guarantees that dhan_index_ai_signals.csv and dhan_index_ai_signals_with_forward.csv
always exist and are fresh enough, or forces OP3 into NO-TRADE with clear logs.

Mode: Pre-market and each OP cycle before OP3.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def run_phase_343_signals_freshness_enforcer(root_path: str = None, logger_obj=None) -> str:
    """
    Phase 343: Enforce signal existence and freshness.

    Returns: 'OK' or 'WARN'
    """
    if logger_obj:
        logger = logger_obj

    if root_path is None:
        root_path = str(PROJECT_ROOT)

    root = Path(root_path)
    logger.info("[PH343] Starting Signals Freshness Enforcer")

    try:
        config_file = root / "config" / "system3_config.json"
        max_signal_age_minutes = 60
        min_row_count = 1

        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                max_signal_age_minutes = config.get("max_signal_age_minutes", 60)
                min_row_count = config.get("min_signal_rows", 1)

        status = "OK"
        signal_status = {
            "signals": {},
            "overall_status": "OK",
            "timestamp": datetime.now().isoformat(),
        }

        # Check signals.csv
        signals_file = root / "storage" / "live" / "dhan_index_ai_signals.csv"
        if signals_file.exists():
            try:
                df = pd.read_csv(signals_file)
                mtime = datetime.fromtimestamp(signals_file.stat().st_mtime)
                age_minutes = (datetime.now() - mtime).total_seconds() / 60

                if age_minutes > max_signal_age_minutes or len(df) < min_row_count:
                    signal_status["signals"]["dhan_index_ai_signals.csv"] = {
                        "status": "stale" if age_minutes > max_signal_age_minutes else "empty",
                        "age_minutes": age_minutes,
                        "rows": len(df),
                    }
                    status = "WARN"
                    logger.warning(f"[PH343] Signals CSV stale or empty: age={age_minutes:.1f}m, rows={len(df)}")
                else:
                    signal_status["signals"]["dhan_index_ai_signals.csv"] = {
                        "status": "ok",
                        "age_minutes": age_minutes,
                        "rows": len(df),
                    }
            except Exception as e:
                logger.error(f"[PH343] Error reading signals CSV: {e}")
                signal_status["signals"]["dhan_index_ai_signals.csv"] = {"status": "error"}
                status = "WARN"
        else:
            signal_status["signals"]["dhan_index_ai_signals.csv"] = {"status": "missing"}
            status = "WARN"
            logger.warning("[PH343] Signals CSV file missing")

        # Check signals_with_forward.csv
        signals_forward_file = root / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"
        if signals_forward_file.exists():
            try:
                df = pd.read_csv(signals_forward_file)
                mtime = datetime.fromtimestamp(signals_forward_file.stat().st_mtime)
                age_minutes = (datetime.now() - mtime).total_seconds() / 60

                if age_minutes > max_signal_age_minutes or len(df) < min_row_count:
                    signal_status["signals"]["dhan_index_ai_signals_with_forward.csv"] = {
                        "status": "stale" if age_minutes > max_signal_age_minutes else "empty",
                        "age_minutes": age_minutes,
                        "rows": len(df),
                    }
                    status = "WARN"
                    logger.warning(
                        f"[PH343] Signals with forward CSV stale or empty: age={age_minutes:.1f}m, rows={len(df)}"
                    )
                else:
                    signal_status["signals"]["dhan_index_ai_signals_with_forward.csv"] = {
                        "status": "ok",
                        "age_minutes": age_minutes,
                        "rows": len(df),
                    }
            except Exception as e:
                logger.error(f"[PH343] Error reading signals with forward CSV: {e}")
                signal_status["signals"]["dhan_index_ai_signals_with_forward.csv"] = {"status": "error"}
                status = "WARN"
        else:
            signal_status["signals"]["dhan_index_ai_signals_with_forward.csv"] = {"status": "missing"}
            status = "WARN"
            logger.warning("[PH343] Signals with forward CSV file missing")

        signal_status["overall_status"] = status

        # Write status file
        diag_dir = root / "storage" / "live" / "diagnostics"
        diag_dir.mkdir(parents=True, exist_ok=True)

        with open(diag_dir / "signal_status.json", "w") as f:
            json.dump(signal_status, f, indent=2)

        logger.info(f"[PH343] Signals Freshness Enforcer complete. Status: {status}")
        return status

    except Exception as e:
        logger.error(f"[PH343] Unexpected error: {e}", exc_info=True)
        return "WARN"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_phase_343_signals_freshness_enforcer()
    print(f"Phase 343 result: {result}")
