"""
Genesis System3 — Cloud Worker
================================
Single-process entrypoint for Render worker service.
Runs five background daemons as threads:

  Thread 1 — Token daemon       : refreshes DHAN_ACCESS_TOKEN daily at 08:30 IST
  Thread 2 — Token watchdog     : checks token validity every CHECK_INTERVAL_S
  Thread 3 — Job scheduler      : fires the scheduled weekday analysis jobs
  Thread 4 — Health push        : pushes scheduler heartbeat/job-status to the
                                   web service every ~30s (see ARCHITECTURE note)
  Thread 5 — Chain push         : precomputes option chains for the default
                                   underlyings and pushes them to the web
                                   service every ~20s during market hours,
                                   and every ~5min while the market is closed
                                   (EOD/bhavcopy snapshot barely changes
                                   between pushes off-hours — see ARCHITECTURE
                                   note)

ARCHITECTURE NOTE: Render's `web` and `worker` services run as separate
containers with separate ephemeral filesystems — no shared disk. The
job scheduler (Thread 3) writes its state to LOCAL files on THIS
(worker) container. The web service's /api/scheduler/health endpoint
cannot read those files directly, so Thread 4 actively pushes the
state over HTTP to the web service's /api/scheduler/health/push
endpoint instead. If WEB_SERVICE_URL is not set, Thread 4 logs a
warning once and stays idle (does not crash the worker).

Thread 5 exists because GET /api/chain/{underlying} on the web service used
to do its DataSourceManager() + live Dhan fetch INLINE on the request path —
polled every 5s by every open browser tab, on the same single-worker
(--workers 1) 512MB web container that also has to stay responsive for
Render's own health checks. That was a leading suspect for the web dyno's
502 crash-loop during market hours (2026-07-02 forensic investigation, see
CHANGE_LOG.md). Thread 5 moves that cost here instead: this worker container
is not request-serving, so a slow/heavy tick here never produces a 502 for a
real user, and if this thread's own memory use becomes a problem it can be
tuned/throttled independently of the user-facing web dyno.

Thread 5 originally only ran `if mkt_open`, which meant the pushed snapshot
went stale the instant the market closed and every after-hours page view fell
back to the same expensive inline DataSourceManager() fetch on the web dyno
that this thread exists to avoid — reproduced live on 2026-07-02: /api/chain
returned an empty MARKET_CLOSED stub and the dashboard showed a permanent
"Market Closed" lock screen even though bhavcopy/EOD data was available. It
now also pushes off-hours, just far less often (`_CHAIN_PUSH_CLOSED_INTERVAL_S`)
since EOD data doesn't change between pushes.

Requires these env vars (set in Render dashboard → Environment):
  DHAN_CLIENT_ID, DHAN_APP_ID, DHAN_APP_SECRET
  DHAN_PIN, DHAN_TOTP_SECRET
  DHAN_ACCESS_TOKEN     (initial; auto-refreshed afterward)
  CLOUD_WORKER=true     (set automatically in render.yaml)
  WEB_SERVICE_URL        e.g. https://genesis-system3-backend.onrender.com
                          (defaults to the production URL if unset)
  WORKER_PUSH_TOKEN      shared secret; must match the web service's
                          WORKER_PUSH_TOKEN env var exactly. If unset on
                          either side, push proceeds unauthenticated
                          (logged once, for local/dev use only).

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
sys.path.insert(0, str(ROOT / "src"))  # needed for `from utils.market_hours import ...`
# (dashboard/backend/app.py adds this same path for the same reason — see its
# sys.path.insert(0, str(ROOT_DIR / "src")) — this worker needs it too for
# Thread 5's is_market_open() check below.)

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
# Thread 4: Scheduler health push (worker -> web, see ARCHITECTURE note above)
# ---------------------------------------------------------------------------
_DEFAULT_WEB_URL = "https://genesis-system3-backend.onrender.com"
_SCHEDULER_STATE_FILE = ROOT / "storage" / "ultra" / "ph76_ph100" / "phase82_job_scheduler_state.json"
_SCHEDULER_ALERT_FILE = ROOT / "state" / "scheduler_config_alert.json"
_PUSH_INTERVAL_S = 30


def _run_health_push():
    log.info("[health-push] starting")
    web_url = os.environ.get("WEB_SERVICE_URL", _DEFAULT_WEB_URL).rstrip("/")
    if not web_url.lower().startswith(("http://", "https://")):
        log.error(f"[health-push] WEB_SERVICE_URL has an unexpected scheme ({web_url!r}) — thread exiting")
        return
    push_token = os.environ.get("WORKER_PUSH_TOKEN", "").strip()

    if not push_token:
        log.warning(
            "[health-push] WORKER_PUSH_TOKEN not set — pushes will be "
            "unauthenticated. Set this env var identically on both the "
            "web and worker Render services for production."
        )

    try:
        import json as _json
        import urllib.error as _urlerr
        import urllib.request as _urlreq
    except Exception as exc:
        log.exception(f"[health-push] import failed, thread exiting: {exc}")
        return

    while True:
        try:
            payload = {
                "daemon_heartbeat": None,
                "daemon_pid": None,
                "jobs": {},
                "config_alert": None,
                "config_jobs_total": None,
                "config_jobs_enabled": None,
                "jobs_status_today": {},
                "fired_keys_today": [],
            }

            if _SCHEDULER_STATE_FILE.exists():
                state = _json.loads(_SCHEDULER_STATE_FILE.read_text(encoding="utf-8"))
                payload["daemon_heartbeat"] = state.get("daemon_heartbeat")
                payload["daemon_pid"] = state.get("daemon_pid")
                payload["jobs"] = state.get("jobs", {})
                payload["config_jobs_total"] = state.get("config_jobs_total")
                payload["config_jobs_enabled"] = state.get("config_jobs_enabled")
                payload["jobs_status_today"] = state.get("jobs_status_today", {})
                payload["fired_keys_today"] = state.get("fired_keys_today", [])

            if _SCHEDULER_ALERT_FILE.exists():
                payload["config_alert"] = _json.loads(_SCHEDULER_ALERT_FILE.read_text(encoding="utf-8"))

            body = _json.dumps(payload).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            if push_token:
                headers["X-Worker-Token"] = push_token

            req = _urlreq.Request(
                f"{web_url}/api/scheduler/health/push",
                data=body,
                headers=headers,
                method="POST",
            )
            with _urlreq.urlopen(req, timeout=10) as resp:  # nosec B310 - scheme validated at thread start
                if resp.status != 200:
                    log.warning(f"[health-push] non-200 response: {resp.status}")
        except _urlerr.URLError as exc:
            log.warning(f"[health-push] could not reach web service ({web_url}): {exc}")
        except Exception as exc:
            log.warning(f"[health-push] push failed: {exc}")

        time.sleep(_PUSH_INTERVAL_S)


# ---------------------------------------------------------------------------
# Thread 5: Chain push (worker -> web, see ARCHITECTURE note above)
# ---------------------------------------------------------------------------
# Must match dashboard/backend/app.py's DEFAULT_UNDERLYINGS. GET
# /api/chain/{underlying} on the web service only serves from this push for
# exactly these symbols; anything else still falls back to an inline fetch
# on the web dyno (rare — the dashboard's default watchlist is these four).
_CHAIN_PUSH_SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
_CHAIN_PUSH_INTERVAL_S = 20
# EOD/bhavcopy data doesn't change between market close and the next
# pre-market session, so off-hours pushes happen far less often than the
# 20s live cadence — this is a throttle on the *fetch+push*, the outer loop
# still ticks every _CHAIN_PUSH_INTERVAL_S so it reacts quickly once the
# market reopens. Must stay well under _PUSHED_CHAIN_FRESH_S_CLOSED in
# dashboard/backend/app.py or the web dyno will treat pushes as stale between
# ticks and fall back to the (slow) inline fetch anyway.
_CHAIN_PUSH_CLOSED_INTERVAL_S = 300


def _run_chain_push():
    log.info("[chain-push] starting")
    web_url = os.environ.get("WEB_SERVICE_URL", _DEFAULT_WEB_URL).rstrip("/")
    if not web_url.lower().startswith(("http://", "https://")):
        log.error(f"[chain-push] WEB_SERVICE_URL has an unexpected scheme ({web_url!r}) — thread exiting")
        return
    push_token = os.environ.get("WORKER_PUSH_TOKEN", "").strip()

    try:
        import json as _json
        import urllib.error as _urlerr
        import urllib.request as _urlreq
    except Exception as exc:
        log.exception(f"[chain-push] import failed, thread exiting: {exc}")
        return

    last_closed_push = 0.0
    while True:
        try:
            mkt_open = False
            try:
                from utils.market_hours import is_market_open

                mkt_open, _reason = is_market_open()
            except Exception as exc:
                log.warning(f"[chain-push] market-hours check failed: {exc}")

            due_for_closed_push = (time.time() - last_closed_push) >= _CHAIN_PUSH_CLOSED_INTERVAL_S
            if mkt_open or due_for_closed_push:
                try:
                    from core.data.datasource_manager import DataSourceManager
                    from dashboard.backend.chain_adapter import fetch_chain_for_api
                except Exception as exc:
                    log.warning(f"[chain-push] import failed: {exc}")
                    time.sleep(_CHAIN_PUSH_INTERVAL_S)
                    continue

                # One DataSourceManager for the whole tick — avoid reconstructing
                # it (instrument master lookup etc.) per symbol.
                dsm = DataSourceManager()
                chains = {}
                for sym in _CHAIN_PUSH_SYMBOLS:
                    try:
                        data = fetch_chain_for_api(dsm, sym)
                        if data and data.get("contracts"):
                            chains[sym] = data
                    except Exception as exc:
                        log.warning(f"[chain-push] fetch failed for {sym}: {exc}")

                if not mkt_open:
                    last_closed_push = time.time()

                if chains:
                    body = _json.dumps({"chains": chains, "market_open": mkt_open}).encode("utf-8")
                    headers = {"Content-Type": "application/json"}
                    if push_token:
                        headers["X-Worker-Token"] = push_token
                    req = _urlreq.Request(
                        f"{web_url}/api/chain/push",
                        data=body,
                        headers=headers,
                        method="POST",
                    )
                    try:
                        with _urlreq.urlopen(req, timeout=15) as resp:  # nosec B310 - scheme validated at thread start
                            if resp.status != 200:
                                log.warning(f"[chain-push] non-200 response: {resp.status}")
                    except _urlerr.URLError as exc:
                        log.warning(f"[chain-push] could not reach web service ({web_url}): {exc}")
        except Exception as exc:
            log.warning(f"[chain-push] error (continuing): {exc}")

        time.sleep(_CHAIN_PUSH_INTERVAL_S)


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
            log.warning(f"[bootstrap] refresh_token failed: {result.get('message', result)}")
            log.warning("[bootstrap] Add DHAN_CLIENT_ID/DHAN_ACCESS_TOKEN/DHAN_PIN/DHAN_TOTP_SECRET to worker env vars")
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
        threading.Thread(target=_run_health_push, name="health-push", daemon=True),
        threading.Thread(target=_run_chain_push, name="chain-push", daemon=True),
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
