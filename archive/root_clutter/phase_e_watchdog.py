"""
PHASE E WATCHDOG: Continuous Validation Loop

Runs validators every N seconds to detect production issues in real-time.
Monitors timestamp parsing, merge key alignment, and venv integrity.

Usage:
  python phase_e_watchdog.py --interval 60 --max-checks 0 --lock-venv
  
  Options:
    --interval N: Check interval in seconds (default: 60)
    --max-checks N: Max checks before exit (0 = infinite)
    --lock-venv: Enable venv integrity checks
    --watch-dir PATH: Directory to monitor (default: storage/live)
    --log-level INFO|DEBUG|WARNING
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.monitoring.continuous_validators import ContinuousMonitor


def setup_logging(log_level: str = "INFO"):
    """Setup root logger."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("storage/metrics/watchdog.log")
        ]
    )


def run_watchdog(
    interval_sec: int = 60,
    max_checks: Optional[int] = None,
    lock_venv: bool = True,
    watch_dir: str = "storage/live",
    log_level: str = "INFO"
):
    """Run continuous validation loop."""
    
    setup_logging(log_level)
    logger = logging.getLogger("Watchdog")
    
    logger.info("=" * 80)
    logger.info("PHASE E WATCHDOG STARTED")
    logger.info("=" * 80)
    logger.info(f"Check interval: {interval_sec}s")
    logger.info(f"Max checks: {max_checks or 'unlimited'}")
    logger.info(f"Venv lock mode: {lock_venv}")
    logger.info(f"Watch directory: {watch_dir}")
    logger.info("=" * 80)
    
    monitor = ContinuousMonitor(
        watch_dir=watch_dir,
        check_interval_sec=interval_sec,
        alert_on_threshold_miss=True,
        lock_venv_mode=lock_venv,
        log_file="storage/metrics/continuous_monitor.log"
    )
    
    check_num = 0
    start_time = datetime.utcnow()
    
    try:
        while True:
            # Check if we've hit max checks
            if max_checks is not None and check_num >= max_checks:
                logger.info(f"Reached max checks ({max_checks}), exiting")
                break
            
            check_num += 1
            
            # Run validation
            logger.info(f"\n[CHECK #{check_num}] Starting validation...")
            try:
                results = monitor.run_check()
                monitor.print_summary(results)
                
                # Log key metrics
                validators = results.get("validators", {})
                if "timestamp" in validators:
                    ts_results = validators["timestamp"]
                    valid_count = sum(r.get("valid_pct", 0) >= 80 for r in ts_results)
                    logger.info(f"[OK] Timestamp validation: {valid_count}/{len(ts_results)} phases OK")
                
                if "merge_keys" in validators:
                    mk = validators["merge_keys"]
                    logger.info(f"[OK] Merge keys alignment: {mk.get('alignment_score', 0):.1f}%")
                    if mk.get("recommendations"):
                        logger.warning(f"     {len(mk['recommendations'])} recommendations")
                
                if "venv" in validators:
                    venv = validators["venv"]
                    logger.info(f"[OK] Venv integrity: {venv.get('status', 'UNKNOWN')}")
                
            except Exception as e:
                logger.error(f"Check #{check_num} failed: {e}", exc_info=True)
            
            # Wait for next interval
            logger.info(f"Next check in {interval_sec}s...")
            time.sleep(interval_sec)
    
    except KeyboardInterrupt:
        logger.info("[STOP] Watchdog interrupted by user")
    except Exception as e:
        logger.error(f"Watchdog error: {e}", exc_info=True)
    finally:
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info("=" * 80)
        logger.info(f"PHASE E WATCHDOG STOPPED")
        logger.info(f"Total checks: {check_num}")
        logger.info(f"Elapsed time: {elapsed:.1f}s")
        logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Phase E Continuous Validation Watchdog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with 30-second interval (infinite)
  python phase_e_watchdog.py --interval 30
  
  # Run 10 checks and exit
  python phase_e_watchdog.py --max-checks 10
  
  # Run in debug mode
  python phase_e_watchdog.py --log-level DEBUG
  
  # Disable venv checks
  python phase_e_watchdog.py --no-lock-venv
        """
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--max-checks",
        type=int,
        default=None,
        help="Maximum number of checks before exit (default: unlimited)"
    )
    
    parser.add_argument(
        "--lock-venv",
        action="store_true",
        default=True,
        help="Enable venv integrity checks (default: enabled)"
    )
    
    parser.add_argument(
        "--no-lock-venv",
        action="store_false",
        dest="lock_venv",
        help="Disable venv integrity checks"
    )
    
    parser.add_argument(
        "--watch-dir",
        type=str,
        default="storage/live",
        help="Directory to monitor (default: storage/live)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    run_watchdog(
        interval_sec=args.interval,
        max_checks=args.max_checks,
        lock_venv=args.lock_venv,
        watch_dir=args.watch_dir,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
