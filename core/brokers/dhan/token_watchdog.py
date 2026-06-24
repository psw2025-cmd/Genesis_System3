"""
Dhan Token Watchdog — Multi-Layer Safety Net
=============================================
Runs as a lightweight background thread/process alongside the main system.

Checks token health every 30 minutes:
  - Token expired             → refresh immediately
  - Token < 2h remaining      → refresh immediately (proactive)
  - Token > 22h old           → refresh immediately (preventive)
  - Daemon not running        → restart it
  - Refresh failed 3x in row  → alert and log CRITICAL

This is Layer 2. The daemon (dhan_token_auto_refresh.py) is Layer 1.
The startup check (dhan_startup_check.py) is Layer 0.
The pre-flight check (ensure_valid_token) is Layer 3 (called before trades).
"""

import logging
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

LOG_FILE = ROOT_DIR / "logs" / "dhan_watchdog.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Watchdog] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("dhan_watchdog")

CHECK_INTERVAL_S   = 30 * 60   # check every 30 minutes
PROACTIVE_HOURS    = 2.0        # refresh if < 2h left
PREVENTIVE_HOURS   = 22.0       # refresh if token > 22h old (before 24h expiry)
MAX_FAIL_STREAK    = 3          # CRITICAL alert after 3 consecutive failures
_fail_streak       = 0


def _token_hours_remaining() -> float | None:
    """Returns hours left on current token, or None if can't determine."""
    import base64
    import json
    try:
        from core.utils.env_loader import get_dhan_credentials
        creds = get_dhan_credentials()
    except ImportError:
        from dotenv import load_dotenv
        load_dotenv(ROOT_DIR / ".secrets" / "dhan.env", override=False)
        creds = {
            "client_id": os.getenv("DHAN_CLIENT_ID", ""),
            "access_token": os.getenv("DHAN_ACCESS_TOKEN", ""),
        }

    token = creds.get("access_token", "")
    if not token:
        return None
    try:
        parts = token.split(".")
        pad = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad))
        exp = payload.get("exp")
        if not exp:
            return None
        exp_dt = datetime.fromtimestamp(exp)
        return (exp_dt - datetime.now()).total_seconds() / 3600
    except Exception:
        return None


def _daemon_running() -> bool:
    import subprocess
    result = subprocess.run(
        ["pgrep", "-f", "dhan_token_auto_refresh.py"],
        capture_output=True
    )
    return result.returncode == 0


def _restart_daemon() -> None:
    import subprocess
    daemon_script = ROOT_DIR / "scripts" / "dhan_token_auto_refresh.py"
    python = sys.executable
    p = subprocess.Popen(
        [python, "-u", str(daemon_script)],
        stdout=open(ROOT_DIR / "logs" / "dhan_token_daemon.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    logger.info(f"Daemon restarted — PID {p.pid}")


def _do_refresh() -> bool:
    """Attempt token refresh. Returns True on success."""
    global _fail_streak
    try:
        # Reload env fresh before refresh (picks up latest token)
        from dotenv import load_dotenv
        load_dotenv(ROOT_DIR / ".secrets" / "dhan.env", override=True)
        from core.brokers.dhan.token_manager import refresh_token
        result = refresh_token()
        if result.get("success"):
            logger.info(f"Token refreshed via {result['strategy']} — expires {result.get('expires_at','?')}")
            _fail_streak = 0
            return True
        else:
            _fail_streak += 1
            logger.error(f"Refresh failed (streak {_fail_streak}): {result['message']}")
            if _fail_streak >= MAX_FAIL_STREAK:
                logger.critical(
                    f"TOKEN REFRESH FAILED {_fail_streak} TIMES IN A ROW. "
                    f"Manual intervention required. Run: "
                    f"python scripts/dhan_token_auto_refresh.py --oauth"
                )
            return False
    except Exception as e:
        _fail_streak += 1
        logger.error(f"Refresh exception (streak {_fail_streak}): {e}")
        return False


def watchdog_cycle() -> str:
    """Run one watchdog cycle. Returns action taken."""
    hours = _token_hours_remaining()

    if hours is None:
        logger.warning("Cannot read token expiry — attempting refresh")
        _do_refresh()
        return "refreshed_unknown_state"

    if hours < 0:
        logger.warning(f"Token EXPIRED {abs(hours):.1f}h ago — refreshing now")
        _do_refresh()
        return "refreshed_expired"

    if hours < PROACTIVE_HOURS:
        logger.info(f"Token < {PROACTIVE_HOURS}h remaining ({hours:.2f}h) — proactive refresh")
        _do_refresh()
        return "refreshed_proactive"

    # Check if token age > 22h (even if not yet expired — preventive)
    if 0 < hours < (24 - PREVENTIVE_HOURS):
        logger.info(f"Token > {PREVENTIVE_HOURS}h old — preventive refresh")
        _do_refresh()
        return "refreshed_preventive"

    logger.info(f"Token OK — {hours:.2f}h remaining")

    # Ensure daemon is also running
    if not _daemon_running():
        logger.warning("Daemon not running — restarting")
        _restart_daemon()
        return "daemon_restarted"

    return "ok"


def run_watchdog_loop():
    """Main watchdog loop — runs forever, checks every 30 min."""
    logger.info(f"Watchdog started — checking every {CHECK_INTERVAL_S//60} minutes")
    while True:
        try:
            action = watchdog_cycle()
        except Exception as e:
            logger.error(f"Watchdog cycle error: {e}")
        time.sleep(CHECK_INTERVAL_S)


def start_watchdog_thread() -> threading.Thread:
    """Start watchdog as a background daemon thread (non-blocking)."""
    t = threading.Thread(target=run_watchdog_loop, name="DhanTokenWatchdog", daemon=True)
    t.start()
    logger.info("Watchdog thread started (daemon=True, won't block main process)")
    return t


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Dhan Token Watchdog")
    parser.add_argument("--once",  action="store_true", help="Run one check cycle and exit")
    parser.add_argument("--loop",  action="store_true", help="Run watchdog loop forever")
    parser.add_argument("--hours", action="store_true", help="Print hours remaining on current token")
    args = parser.parse_args()

    if args.hours:
        h = _token_hours_remaining()
        print(f"Hours remaining: {h:.2f}h" if h is not None else "Cannot determine")
    elif args.once:
        action = watchdog_cycle()
        print(f"Action: {action}")
    else:
        run_watchdog_loop()
