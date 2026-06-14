"""
Genesis System3 — Cloud Worker
================================
Single-process entrypoint for Render worker service.
Runs three background daemons as threads:

  Thread 1 — Token daemon      : refreshes DHAN_ACCESS_TOKEN daily at 08:30 IST
  Thread 2 — Token watchdog    : checks token validity every CHECK_INTERVAL_S
  Thread 3 — Job scheduler     : fires the 8 weekday analysis jobs on schedule

Requires these env vars (set in Render dashboard → Environment):
  DHAN_CLIENT_ID, DHAN_APP_ID, DHAN_APP_SECRET
  DHAN_PIN, DHAN_TOTP_SECRET
  DHAN_ACCESS_TOKEN  (initial; auto-refreshed afterward)
  CLOUD_WORKER=true  (set automatically in render.yaml — enables cloud fallback path)

Safety gate: LIVE_TRADING_ENABLED must be 0 (default). Do NOT change until
paper/analyzer proof passes and CI is fully green.
"""

import logging
import os
import sys
import threading
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CloudWorker] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("cloud_worker")

# ---------------------------------------------------------------------------
# Safety guard — must never run live trading in worker
# ---------------------------------------------------------------------------
os.environ.setdefault("CLOUD_WORKER", "true")
os.environ.setdefault("LIVE_TRADING_ENABLED", "0")
os.environ.setdefault("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
os.environ.setdefault("SYSTEM3_MODE", "analyzer")
os.environ.setdefault("ANALYZE_MODE", "1")

if os.environ.get("LIVE_TRADING_ENABLED", "0") not in ("0", "false", "False", ""):
    log.critical("LIVE_TRADING_ENABLED is set to a truthy value — refusing to start worker.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Thread 1: Token daemon
# ---------------------------------------------------------------------------
def _run_token_daemon():
    log.info("[token-daemon] starting")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dhan_token_auto_refresh",
            ROOT / "scripts" / "dhan_token_auto_refresh.py",
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        mod.run_daemon()
    except Exception as exc:
        log.exception(f"[token-daemon] crashed: {exc}")


# ---------------------------------------------------------------------------
# Thread 2: Token watchdog
# ---------------------------------------------------------------------------
def _run_watchdog():
    log.info("[watchdog] starting")
    try:
        from core.brokers.dhan.token_watchdog import run_watchdog_loop
        run_watchdog_loop()
    except Exception as exc:
        log.exception(f"[watchdog] crashed: {exc}")


# ---------------------------------------------------------------------------
# Thread 3: Job scheduler
# ---------------------------------------------------------------------------
def _run_job_scheduler():
    log.info("[job-scheduler] starting")
    try:
        from core.engine.system3_phase82_job_scheduler import run_daemon
        run_daemon()
    except Exception as exc:
        log.exception(f"[job-scheduler] crashed: {exc}")


# ---------------------------------------------------------------------------
# Startup: bootstrap token from PIN+TOTP before threads start
# ---------------------------------------------------------------------------
def _bootstrap_token():
    """Ensure a valid access token exists before daemons start."""
    token = os.environ.get("DHAN_ACCESS_TOKEN", "")
    if token and len(token) > 20:
        log.info(f"[bootstrap] DHAN_ACCESS_TOKEN already present (len={len(token)})")
        return

    log.info("[bootstrap] No access token — attempting initial refresh via PIN+TOTP...")
    try:
        from core.brokers.dhan.token_manager import refresh_token
        result = refresh_token()
        if result.get("success"):
            log.info(f"[bootstrap] Token obtained via {result['strategy']}")
        else:
            log.warning(f"[bootstrap] refresh_token failed: {result}")
    except Exception as exc:
        log.warning(f"[bootstrap] Could not refresh token at startup: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 60)
    log.info("Genesis System3 Cloud Worker starting")
    log.info(f"LIVE_TRADING_ENABLED={os.environ.get('LIVE_TRADING_ENABLED', '0')}")
    log.info(f"SYSTEM3_MODE={os.environ.get('SYSTEM3_MODE', 'analyzer')}")
    log.info("=" * 60)

    _bootstrap_token()

    threads = [
        threading.Thread(target=_run_token_daemon, name="token-daemon", daemon=True),
        threading.Thread(target=_run_watchdog, name="watchdog", daemon=True),
        threading.Thread(target=_run_job_scheduler, name="job-scheduler", daemon=True),
    ]

    for t in threads:
        t.start()
        log.info(f"[main] started thread: {t.name}")

    # Keep main thread alive; restart any dead thread every 60s
    while True:
        time.sleep(60)
        for t in threads:
            if not t.is_alive():
                log.warning(f"[main] thread '{t.name}' died — restarting")
                new_t = threading.Thread(
                    target=t._target,  # type: ignore[attr-defined]
                    name=t.name,
                    daemon=True,
                )
                new_t.start()
                threads[threads.index(t)] = new_t


if __name__ == "__main__":
    main()
