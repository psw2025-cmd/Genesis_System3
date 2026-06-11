"""
System3 Watchdog - HARDENED VERSION
Monitors and Restarts Autorun Master with Enhanced Safety Checks

Checks if system3_autorun_master.py is running every 60 seconds.
If not running, restarts it automatically (only during market hours).
Enhanced with heartbeat staleness check and shutdown flag detection.

HARDENED: Enhanced error handling, retry logic, self-healing.
"""

import sys
import os
import time
import json
import subprocess
try:
    import psutil
except ImportError:
    print("ERROR: psutil not installed. Install with: pip install psutil")
    sys.exit(1)
from pathlib import Path
from datetime import datetime, time as dt_time, timedelta
from typing import Optional
import logging

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup logging
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"system3_watchdog_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

MASTER_SCRIPT = ROOT_DIR / "system3_autorun_master.py"
BAT_SCRIPT = ROOT_DIR / "start_system3_autorun.bat"
HEARTBEAT_FILE = ROOT_DIR / "system3_daily_heartbeat.json"
SHUTDOWN_FLAG_FILE = ROOT_DIR / "system3_shutdown_flag.json"


def is_market_hours() -> bool:
    """Check if current time is during market hours (9:15-16:00) on weekday."""
    now = datetime.now()
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    current_time = now.time()
    market_open = dt_time(9, 15)
    market_close = dt_time(16, 0)
    return market_open <= current_time <= market_close


def check_shutdown_flag() -> bool:
    """Check if shutdown flag file exists (prevents restart after shutdown)."""
    if SHUTDOWN_FLAG_FILE.exists():
        try:
            with SHUTDOWN_FLAG_FILE.open("r") as f:
                flag_data = json.load(f)
            shutdown_date = flag_data.get("shutdown_date")
            if shutdown_date == datetime.now().strftime("%Y-%m-%d"):
                return True
        except Exception as e:
            logger.warning(f"Error reading shutdown flag: {e}")
    return False


def check_heartbeat_staleness() -> tuple[bool, Optional[float]]:
    """
    Check if heartbeat file is stale (not updated recently).
    Returns: (is_stale, seconds_since_update)
    """
    if not HEARTBEAT_FILE.exists():
        return True, None
    
    try:
        with HEARTBEAT_FILE.open("r") as f:
            heartbeat_data = json.load(f)

        timestamp_str = (
            heartbeat_data.get("_last_updated")
            or heartbeat_data.get("timestamp")
            or (heartbeat_data.get("system_info", {}) if isinstance(heartbeat_data, dict) else {}).get("timestamp")
        )
        if not timestamp_str:
            return True, None

        heartbeat_time = datetime.fromisoformat(timestamp_str)
        seconds_since_update = (datetime.now() - heartbeat_time).total_seconds()
        
        # Consider stale if > 3 minutes (180 seconds)
        is_stale = seconds_since_update > 180
        
        return is_stale, seconds_since_update
    except Exception as e:
        logger.warning(f"Error checking heartbeat: {e}")
        return True, None


def is_master_running() -> bool:
    """Check if system3_autorun_master.py is running."""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if 'system3_autorun_master.py' in cmdline_str:
                        logger.debug(f"Found master process: PID {proc.info['pid']}")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        logger.error(f"Error checking processes: {e}")
        return False


def start_master() -> bool:
    """Start the autorun master script with retry logic (enforces heartbeat continuous mode)."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting system3_autorun_master.py (attempt {attempt + 1}/{max_retries})...")
            base_env = os.environ.copy()
            base_env.setdefault("HEARTBEAT_CONTINUOUS", "1")
            base_env.setdefault("HEARTBEAT_INTERVAL_SECONDS", "60")
            
            # Use the batch file to start (ensures venv activation)
            if BAT_SCRIPT.exists():
                process = subprocess.Popen(
                    [str(BAT_SCRIPT)],
                    cwd=str(ROOT_DIR),
                    env=base_env,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
                )
                logger.info(f"Master started via batch file (PID: {process.pid})")
                return True
            elif MASTER_SCRIPT.exists():
                # Fallback: start Python directly
                process = subprocess.Popen(
                    [sys.executable, str(MASTER_SCRIPT)],
                    cwd=str(ROOT_DIR),
                    env=base_env,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
                )
                logger.info(f"Master started directly (PID: {process.pid})")
                return True
            else:
                logger.error(f"Master script not found: {MASTER_SCRIPT}")
                return False
        except (OSError, subprocess.SubprocessError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to start master (attempt {attempt + 1}/{max_retries}): {e}, retrying...")
                time.sleep(5)
                continue
            else:
                logger.error(f"Failed to start master after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error starting master: {e}")
            return False
    
    return False


def main():
    """Main watchdog loop."""
    logger.info("=" * 70)
    logger.info("SYSTEM3 WATCHDOG - STARTING (HARDENED)")
    logger.info("=" * 70)
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Monitoring: {MASTER_SCRIPT}")
    logger.info("=" * 70)
    
    consecutive_failures = 0
    max_failures = 5
    last_heartbeat_check = datetime.now()
    
    try:
        while True:
            # Check shutdown flag first (prevents restart after shutdown)
            if check_shutdown_flag():
                logger.info("=" * 70)
                logger.info("Shutdown flag detected - Master shut down today.")
                logger.info("Watchdog will NOT restart master (as intended).")
                logger.info("=" * 70)
                # Still check every 60 seconds, but don't restart
                time.sleep(60)
                continue
            
            # Only restart master during market hours (9:15 AM - 4:00 PM) on weekdays
            if is_market_hours():
                master_running = is_master_running()
                
                # Check heartbeat staleness every 5 minutes
                if (datetime.now() - last_heartbeat_check).total_seconds() >= 300:
                    is_stale, seconds_since = check_heartbeat_staleness()
                    if is_stale and master_running:
                        logger.warning(f"Heartbeat appears stale ({seconds_since:.0f} seconds old) but master is running")
                    last_heartbeat_check = datetime.now()
                
                if master_running:
                    logger.debug("Master is running - OK")
                    consecutive_failures = 0
                else:
                    logger.warning("Master is NOT running - checking heartbeat...")
                    
                    # Check heartbeat to see if master just shut down gracefully
                    is_stale, seconds_since = check_heartbeat_staleness()
                    if is_stale and seconds_since and seconds_since > 300:
                        logger.info(f"Heartbeat is stale ({seconds_since:.0f} seconds old) - master likely shut down")
                        # Don't restart if heartbeat is very stale (likely graceful shutdown)
                        if seconds_since > 600:  # 10 minutes
                            logger.info("Heartbeat too stale - assuming graceful shutdown, not restarting")
                            consecutive_failures = 0
                            time.sleep(60)
                            continue
                    
                    logger.warning("Master is NOT running - attempting restart...")
                    consecutive_failures += 1
                    
                    if consecutive_failures <= max_failures:
                        if start_master():
                            logger.info("Master restart successful")
                            consecutive_failures = 0
                            # Wait a bit before checking again
                            time.sleep(30)
                        else:
                            logger.error(f"Master restart failed (attempt {consecutive_failures}/{max_failures})")
                    else:
                        logger.error(f"Max restart attempts reached ({max_failures}). Stopping watchdog.")
                        break
            else:
                # Outside market hours - don't restart master
                if is_master_running():
                    logger.debug("Master is running (outside market hours) - OK")
                else:
                    logger.info("Outside market hours - Master not running (expected). Not restarting.")
                    consecutive_failures = 0  # Reset counter
            
            # Check every 60 seconds
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("\n[INFO] Watchdog interrupted by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"\n[ERROR] Fatal error: {e}", exc_info=True)
        return 1
    
    logger.info("=" * 70)
    logger.info("SYSTEM3 WATCHDOG - SHUTDOWN")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
