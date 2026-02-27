"""
System3 Watchdog - HARDENED VERSION
Monitors and Restarts Autorun Master with Enhanced Safety Checks

Checks if system3_autorun_master.py is running every 60 seconds.
If not running, restarts it automatically (only during market hours).
Enhanced with heartbeat staleness check and shutdown flag detection.

HARDENED: Enhanced error handling, retry logic, self-healing.
"""

# flake8: noqa

import sys
import os
import time
import json

# VENV ENFORCEMENT: Verify running inside System3 venv
from pathlib import Path as _Path
_EXPECTED_VENV = _Path(__file__).parent.absolute() / "venv"
if "venv" not in sys.executable and "virtualenv" not in sys.executable:
    # Not running inside any venv - try to restart with venv python
    _venv_python = _EXPECTED_VENV / "Scripts" / "python.exe"
    if _venv_python.exists():
        print(f"⚠️ Watchdog not running in venv - restarting with {_venv_python}")
        import subprocess as _subprocess
        sys.exit(_subprocess.call([str(_venv_python), __file__] + sys.argv[1:]))
    else:
        raise EnvironmentError(
            f"Watchdog not running inside System3 venv.\n"
            f"Current: {sys.executable}\n"
            f"Expected venv: {_EXPECTED_VENV}\n"
            f"Please run: {_venv_python} {__file__}"
        )

import subprocess
try:
    import psutil
except ImportError:
    print("ERROR: psutil not installed. Install with: pip install psutil")
    sys.exit(1)
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Optional, Tuple
import logging

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup logging
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / (
    f"system3_watchdog_{datetime.now().strftime('%Y%m%d')}.log"
)

VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
STATE_DIR = ROOT_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
MASTER_PID_FILE = STATE_DIR / "system3_master.pid"
WATCHDOG_PID_FILE = STATE_DIR / "system3_watchdog.pid"

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

# Health / restart thresholds
HEARTBEAT_STALE_THRESHOLD = 120  # seconds
HEARTBEAT_STALE_GRACE = 600      # treat as graceful if older than this
MAX_RESTARTS = 5                 # per watchdog session
HEALTH_LOG_INTERVAL = 300        # seconds
CPU_IDLE_THRESHOLD = 1.0         # percent
CPU_IDLE_STREAK_LIMIT = 3        # consecutive low CPU checks to call hang
STATUS_LOG_INTERVAL = 300        # structured status line interval
WATCHDOG_STATUS_FILE = STATE_DIR / "watchdog_runtime_status.json"


def _write_watchdog_status(
    master_proc: Optional['psutil.Process'],
    restart_count: int,
    restart_date: str,
    is_stale: bool,
    seconds_since_hb: Optional[float],
):
    """Write watchdog status to JSON file for external monitoring."""
    try:
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "watchdog_pid": os.getpid(),
            "master_pid": master_proc.pid if master_proc else None,
            "master_running": master_proc is not None,
            "restarts_today": restart_count,
            "restart_date": restart_date,
            "heartbeat_stale": is_stale,
            "heartbeat_age_seconds": seconds_since_hb,
            "overall_status": (
                "GREEN" if (master_proc and not is_stale) else
                "YELLOW" if (master_proc and is_stale and seconds_since_hb and seconds_since_hb < 600) else
                "RED"
            ),
        }
        WATCHDOG_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with WATCHDOG_STATUS_FILE.open("w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        logger.debug(f"Failed to write watchdog status file: {e}")


def enforce_venv_runtime() -> bool:
    if not VENV_PYTHON.exists():
        logger.error(f"Expected venv python missing at {VENV_PYTHON}")
        return False
    actual = os.path.abspath(sys.executable)
    expected = os.path.abspath(str(VENV_PYTHON))
    if actual != expected:
        logger.error(
            "Wrong interpreter for watchdog: "
            f"{actual} (expected {expected}). Exiting."
        )
        return False
    return True


def _read_pid_file(pid_file: Path) -> Optional[int]:
    if not pid_file.exists():
        return None
    try:
        with pid_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("pid")) if data.get("pid") else None
    except Exception:
        return None


def _write_pid(pid_file: Path, script_name: str):
    try:
        payload = {
            "pid": os.getpid(),
            "script": script_name,
            "started": datetime.now().isoformat(),
        }
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        with pid_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        logger.info(f"PID file written: {pid_file} -> {payload['pid']}")
    except Exception as e:
        logger.warning(f"Could not write PID file {pid_file}: {e}")


def _pid_alive(pid: int, marker: Optional[str] = None) -> bool:
    try:
        proc = psutil.Process(pid)
        if marker:
            cmdline = " ".join(proc.cmdline()) if proc.cmdline() else ""
            return marker in cmdline and proc.is_running()
        return proc.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    except Exception:
        return False


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


def check_heartbeat_staleness() -> Tuple[bool, Optional[float]]:
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
            or (
                heartbeat_data.get("system_info", {})
                if isinstance(heartbeat_data, dict)
                else {}
            ).get("timestamp")
        )
        if not timestamp_str:
            return True, None

        heartbeat_time = datetime.fromisoformat(timestamp_str)
        seconds_since_update = (
            datetime.now() - heartbeat_time
        ).total_seconds()
        
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
                        logger.debug(
                            f"Found master process: PID {proc.info['pid']}"
                        )
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        logger.error(f"Error checking processes: {e}")
        return False


def get_master_process() -> Optional['psutil.Process']:
    """Return psutil Process for master if running, else None."""
    pid_from_file = _read_pid_file(MASTER_PID_FILE)
    if pid_from_file and _pid_alive(pid_from_file, "system3_autorun_master"):
        try:
            return psutil.Process(pid_from_file)
        except Exception:
            pass
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'system3_autorun_master.py' in ' '.join(cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.warning(f"Failed to fetch master process: {e}")
    return None


def kill_duplicate_processes():
    """Kill duplicate watchdog/master processes before starting new ones."""
    import psutil
    killed_count = 0
    
    try:
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip current process
                if proc.info['pid'] == current_pid:
                    continue
                    
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                    
                cmdline_str = ' '.join(cmdline).lower()
                
                # Kill duplicate watchdogs
                if 'system3_watchdog.py' in cmdline_str:
                    logger.warning(
                        f"Killing duplicate watchdog PID {proc.info['pid']}"
                    )
                    proc.kill()
                    killed_count += 1
                    
                # Kill existing autorun masters (they'll be restarted)
                if 'system3_autorun_master.py' in cmdline_str:
                    logger.warning(
                        f"Killing existing master PID {proc.info['pid']}"
                    )
                    proc.kill()
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")
    
    if killed_count > 0:
        logger.info(f"Cleaned up {killed_count} duplicate processes")
        time.sleep(2)  # Wait for processes to terminate
    
    return killed_count


def _heartbeat_age_seconds() -> Optional[float]:
    if not HEARTBEAT_FILE.exists():
        return None
    try:
        with HEARTBEAT_FILE.open("r") as f:
            heartbeat_data = json.load(f)

        timestamp_str = (
            heartbeat_data.get("_last_updated")
            or heartbeat_data.get("timestamp")
            or (
                heartbeat_data.get("system_info", {})
                if isinstance(heartbeat_data, dict)
                else {}
            ).get("timestamp")
        )
        if not timestamp_str:
            return None

        heartbeat_time = datetime.fromisoformat(timestamp_str)
        return (datetime.now() - heartbeat_time).total_seconds()
    except Exception as e:
        logger.warning(f"Error checking heartbeat: {e}")
        return None


def _log_status(
    master_proc: Optional['psutil.Process'], restart_count: int, restart_date: str
):
    hb_age = _heartbeat_age_seconds()
    master_pid = master_proc.pid if master_proc else "none"
    line = (
        f"STATUS ts={datetime.now().strftime('%H:%M:%S')} "
        f"master_pid={master_pid} "
        f"hb_age_s={int(hb_age) if hb_age is not None else 'n/a'} "
        f"restarts_today={restart_count} date={restart_date}"
    )
    logger.info(line)


def start_master() -> bool:
    """Start autorun master with venv interpreter and retry logic."""
    # Kill duplicates before starting
    kill_duplicate_processes()
    
    if not VENV_PYTHON.exists():
        logger.error(f"Venv python missing at {VENV_PYTHON}")
        return False

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(
                "Starting system3_autorun_master.py "
                f"(attempt {attempt + 1}/{max_retries})..."
            )
            base_env = os.environ.copy()
            base_env.setdefault("HEARTBEAT_CONTINUOUS", "1")
            base_env.setdefault("HEARTBEAT_INTERVAL_SECONDS", "60")
            
            if MASTER_SCRIPT.exists():
                process = subprocess.Popen(
                    [str(VENV_PYTHON), str(MASTER_SCRIPT)],
                    cwd=str(ROOT_DIR),
                    env=base_env,
                )
                logger.info(
                    f"Master started with venv python (PID: {process.pid})"
                )
                return True
            elif BAT_SCRIPT.exists():
                process = subprocess.Popen(
                    [str(BAT_SCRIPT)],
                    cwd=str(ROOT_DIR),
                    env=base_env,
                )
                logger.info(
                    f"Master started via batch fallback (PID: {process.pid})"
                )
                return True
            else:
                logger.error(f"Master script not found: {MASTER_SCRIPT}")
                return False
        except (OSError, subprocess.SubprocessError) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    "Failed to start master "
                    f"(attempt {attempt + 1}/{max_retries}): {e}, retrying..."
                )
                time.sleep(5)
                continue
            else:
                logger.error(
                    f"Failed to start master after {max_retries} attempts: {e}"
                )
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
    
    if not enforce_venv_runtime():
        return 1

    existing_wd = _read_pid_file(WATCHDOG_PID_FILE)
    if (
        existing_wd
        and existing_wd != os.getpid()
        and _pid_alive(existing_wd, "system3_watchdog")
    ):
        logger.warning(
            f"Another watchdog already running (PID {existing_wd}). Exiting for idempotence."
        )
        return 0
    _write_pid(WATCHDOG_PID_FILE, "system3_watchdog.py")
    
    consecutive_failures = 0
    restart_count = 0
    restart_date = datetime.now().strftime("%Y-%m-%d")
    last_health_log = datetime.now()
    last_status_log = datetime.now()
    cpu_idle_streak = 0
    
    try:
        while True:
            # Check shutdown flag first (prevents restart after shutdown)
            if check_shutdown_flag():
                logger.info("=" * 70)
                logger.info("Shutdown flag detected - Master shut down today.")
                logger.info("Watchdog will NOT restart master (as intended).")
                logger.info("=" * 70)
                time.sleep(60)
                continue
            
            # Reset restart counter each day
            today = datetime.now().strftime("%Y-%m-%d")
            if today != restart_date:
                restart_date = today
                restart_count = 0
                consecutive_failures = 0

            master_proc = get_master_process()
            master_running = master_proc is not None

            is_stale, seconds_since = check_heartbeat_staleness()

            # CPU/RAM health logging every HEALTH_LOG_INTERVAL
            if (
                master_proc
                and (datetime.now() - last_health_log).total_seconds()
                >= HEALTH_LOG_INTERVAL
            ):
                try:
                    cpu = master_proc.cpu_percent(interval=0.1)
                    mem_mb = master_proc.memory_info().rss / (1024 * 1024)
                    logger.info(
                        "Master health: "
                        f"CPU={cpu:.1f}% MEM={mem_mb:.1f} MB "
                        f"staleness={seconds_since if seconds_since is not None else 'n/a'}s"
                    )
                except Exception as e:
                    logger.debug(f"Health check failed: {e}")
                last_health_log = datetime.now()

            # Silent hang detection: stale heartbeat + low CPU for sustained window
            if (
                master_proc
                and is_stale
                and seconds_since
                and seconds_since > HEARTBEAT_STALE_THRESHOLD
            ):
                try:
                    cpu_now = master_proc.cpu_percent(interval=0.1)
                    if cpu_now < CPU_IDLE_THRESHOLD:
                        cpu_idle_streak += 1
                    else:
                        cpu_idle_streak = 0
                except Exception:
                    cpu_idle_streak = 0
                if cpu_idle_streak >= CPU_IDLE_STREAK_LIMIT:
                    logger.warning(
                        "MASTER_SILENT_HANG – restarting master "
                        "(stale heartbeat + idle CPU)"
                    )
                    try:
                        master_proc.terminate()
                        master_proc.wait(timeout=5)
                    except Exception as e:
                        logger.warning(f"Failed to terminate hung master: {e}")
                    master_running = False
                    cpu_idle_streak = 0

            if is_market_hours():
                if (
                    master_running
                    and is_stale
                    and seconds_since
                    and seconds_since > HEARTBEAT_STALE_THRESHOLD
                ):
                    logger.warning(
                        "Heartbeat stale "
                        f"({seconds_since:.0f}s) while master running - treating as hang, restarting master"
                    )
                    try:
                        master_proc.terminate()
                        time.sleep(2)
                    except Exception as e:
                        logger.warning(f"Failed to terminate hung master: {e}")
                    master_running = False

                if master_running:
                    consecutive_failures = 0
                else:
                    logger.warning(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Master is NOT running - attempting restart..."
                    )

                    if (
                        is_stale
                        and seconds_since
                        and seconds_since > HEARTBEAT_STALE_GRACE
                    ):
                        logger.info(
                            "Heartbeat stale "
                            f"{seconds_since:.0f}s - assuming graceful shutdown. Skipping restart."
                        )
                        consecutive_failures = 0
                        time.sleep(60)
                        continue

                    consecutive_failures += 1
                    if restart_count >= MAX_RESTARTS:
                        logger.error(
                            f"Max restarts reached ({MAX_RESTARTS}) for {restart_date}. Stopping watchdog."
                        )
                        break

                    if start_master():
                        restart_count += 1
                        consecutive_failures = 0
                        logger.info(
                            "Master restart successful "
                            f"(total restarts: {restart_count}/{MAX_RESTARTS})"
                        )
                        time.sleep(30)
                    else:
                        logger.error(
                            f"Master restart failed (attempt {consecutive_failures})"
                        )
            else:
                if master_running:
                    logger.debug("Master is running (outside market hours) - OK")
                else:
                    logger.info(
                        "Outside market hours - Master not running (expected). Not restarting."
                    )
                    consecutive_failures = 0

            if (
                (datetime.now() - last_status_log).total_seconds()
                >= STATUS_LOG_INTERVAL
            ):
                _log_status(master_proc, restart_count, restart_date)
                _write_watchdog_status(
                    master_proc, restart_count, restart_date, is_stale, seconds_since
                )
                last_status_log = datetime.now()
            
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("\n[INFO] Watchdog interrupted by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"\n[ERROR] Fatal error: {e}", exc_info=True)
        return 1
    
    try:
        if WATCHDOG_PID_FILE.exists():
            WATCHDOG_PID_FILE.unlink()
    except Exception:
        pass

    logger.info("=" * 70)
    logger.info("SYSTEM3 WATCHDOG - SHUTDOWN")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

