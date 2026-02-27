"""
System3 Auto-Heal Scheduler

Runs auto-heal orchestrator on a schedule:
- Every 10 minutes during market hours (9:15 AM - 3:30 PM)
- Every 30 minutes outside market hours
- On-demand via trigger file

Integrates with autorun master and watchdog.
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Optional

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.system3_auto_heal_orchestrator import AutoHealOrchestrator

# Setup logging
LOG_DIR = PROJECT_ROOT / "logs" / "auto_heal"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Scheduler configuration
MARKET_START = dt_time(9, 15)  # 9:15 AM
MARKET_END = dt_time(15, 30)   # 3:30 PM
MARKET_INTERVAL_MINUTES = 10
OFF_MARKET_INTERVAL_MINUTES = 30

TRIGGER_FILE = PROJECT_ROOT / "storage" / "meta" / "system3_heal_trigger.json"
SHUTDOWN_FLAG = PROJECT_ROOT / "system3_shutdown_flag.json"


class AutoHealScheduler:
    """Schedules and runs auto-heal operations."""
    
    def __init__(self):
        self.orchestrator = AutoHealOrchestrator()
        self.last_run = None
        self.run_count = 0
        self.total_issues_fixed = 0
    
    def is_market_hours(self) -> bool:
        """Check if currently in market hours."""
        now = datetime.now().time()
        return MARKET_START <= now <= MARKET_END
    
    def should_run(self) -> bool:
        """Determine if auto-heal should run."""
        # Check for trigger file (immediate run)
        if TRIGGER_FILE.exists():
            logger.info("🚨 Auto-heal trigger file detected - running immediately")
            return True
        
        # Check time-based schedule
        if self.last_run is None:
            return True
        
        elapsed_minutes = (datetime.now() - self.last_run).total_seconds() / 60
        
        if self.is_market_hours():
            return elapsed_minutes >= MARKET_INTERVAL_MINUTES
        else:
            return elapsed_minutes >= OFF_MARKET_INTERVAL_MINUTES
    
    def check_shutdown_flag(self) -> bool:
        """Check if system shutdown is requested."""
        if SHUTDOWN_FLAG.exists():
            try:
                with SHUTDOWN_FLAG.open("r") as f:
                    flag_data = json.load(f)
                shutdown_date = flag_data.get("shutdown_date")
                if shutdown_date == datetime.now().strftime("%Y-%m-%d"):
                    return True
            except Exception:
                pass
        return False
    
    def run_healing_cycle(self) -> None:
        """Run a single healing cycle."""
        logger.info("=" * 70)
        logger.info(f"AUTO-HEAL CYCLE #{self.run_count + 1}")
        logger.info(f"Market hours: {self.is_market_hours()}")
        logger.info("=" * 70)
        
        # Clear trigger file if it exists
        if TRIGGER_FILE.exists():
            try:
                TRIGGER_FILE.unlink()
                logger.info("✓ Cleared trigger file")
            except Exception as e:
                logger.warning(f"Could not clear trigger file: {e}")
        
        # Run orchestrator
        report = self.orchestrator.run_full_healing_cycle()
        
        # Update stats
        self.last_run = datetime.now()
        self.run_count += 1
        self.total_issues_fixed += len(report["actions_taken"])
        
        # Log summary
        logger.info(f"✓ Cycle complete: {len(report['issues_detected'])} issues, {len(report['actions_taken'])} actions, {len(report['errors'])} errors")
    
    def run_scheduled(self, max_cycles: Optional[int] = None) -> None:
        """Run auto-heal on schedule.
        
        Args:
            max_cycles: Maximum number of cycles to run (None = infinite)
        """
        logger.info("=" * 70)
        logger.info("AUTO-HEAL SCHEDULER STARTED")
        logger.info("=" * 70)
        logger.info(f"Market hours: {MARKET_START.strftime('%H:%M')} - {MARKET_END.strftime('%H:%M')}")
        logger.info(f"Market interval: {MARKET_INTERVAL_MINUTES} minutes")
        logger.info(f"Off-market interval: {OFF_MARKET_INTERVAL_MINUTES} minutes")
        logger.info(f"Max cycles: {max_cycles if max_cycles else 'infinite'}")
        logger.info("=" * 70)
        
        try:
            while True:
                # Check shutdown flag
                if self.check_shutdown_flag():
                    logger.info("Shutdown flag detected - stopping scheduler")
                    break
                
                # Check if should run
                if self.should_run():
                    self.run_healing_cycle()
                    
                    # Check max cycles
                    if max_cycles and self.run_count >= max_cycles:
                        logger.info(f"Reached max cycles ({max_cycles}) - stopping")
                        break
                else:
                    # Calculate next run time
                    if self.last_run:
                        interval = MARKET_INTERVAL_MINUTES if self.is_market_hours() else OFF_MARKET_INTERVAL_MINUTES
                        next_run = self.last_run.timestamp() + (interval * 60)
                        wait_seconds = max(0, next_run - datetime.now().timestamp())
                        
                        if wait_seconds > 60:
                            logger.info(f"Next run in {wait_seconds / 60:.1f} minutes...")
                
                # Sleep for a bit before checking again
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\nScheduler interrupted by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        finally:
            logger.info("=" * 70)
            logger.info("AUTO-HEAL SCHEDULER STOPPED")
            logger.info("=" * 70)
            logger.info(f"Total cycles run: {self.run_count}")
            logger.info(f"Total issues fixed: {self.total_issues_fixed}")
            logger.info("=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System3 Auto-Heal Scheduler")
    parser.add_argument("--cycles", type=int, help="Maximum number of cycles to run")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    scheduler = AutoHealScheduler()
    
    if args.once:
        logger.info("Running single healing cycle...")
        scheduler.run_healing_cycle()
    else:
        max_cycles = args.cycles if args.cycles else None
        scheduler.run_scheduled(max_cycles=max_cycles)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
