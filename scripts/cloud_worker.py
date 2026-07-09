"""
Genesis System3 — Cloud Worker
================================
Single-process entrypoint for Render worker service.
Runs six background daemons as threads:

  Thread 1 — Token daemon       : refreshes DHAN_ACCESS_TOKEN daily at 08:30 IST
  Thread 2 — Token watchdog     : checks token validity every CHECK_INTERVAL_S
  Thread 3 — Job scheduler      : fires the scheduled weekday analysis jobs
  Thread 4 — Health push        : pushes scheduler heartbeat/job-status to the
                                   web service every ~30s (see ARCHITECTURE note)
  Thread 5 — Chain push         : precomputes official Dhan option chains for
                                   the default underlyings, persists them for
                                   the paper/analyzer pipeline, and pushes them
                                   to the web service.
  Thread 6 — Core Pipeline V8   : analyzer/paper ledger from real-data forecasts

ARCHITECTURE NOTE: Render's `web` and `worker` services run as separate
containers with separate ephemeral filesystems — no shared disk. The
job scheduler (Thread 3) writes its state to LOCAL files on THIS
(worker) container. The web service's /api/scheduler/health endpoint
cannot read those files directly, so Thread 4 actively pushes the
state over HTTP to the web service's /api/scheduler/health/push
endpoint instead. If WEB_SERVICE_URL is not set, Thread 4 logs a
warning once and stays idle (does not crash the worker).

Thread 5 moves Dhan option-chain work off the request-serving web dyno.
It also writes the exact Dhan chain payload to local worker files consumed by
Core Pipeline V8, so the paper/analyzer path uses the same official Dhan chain
truth that the dashboard sees. There is no CSV/Yahoo/synthetic substitute here.

Requires these env vars (set in Render dashboard → Environment):
  DHAN_CLIENT_ID, DHAN_APP_ID, DHAN_APP_SECRET
  DHAN_PIN, DHAN_TOTP_SECRET
  DHAN_ACCESS_TOKEN     (initial; auto-refreshed afterward)
  CLOUD_WORKER=true     (set automatically in render.yaml)
  WEB_SERVICE_URL        e.g. https://genesis-system3-backend.onrender.com
                          (defaults to the production URL if unset)
  WORKER_PUSH_TOKEN      shared secret; must match the web service's
                          WORKER_PUSH_TOKEN env var exactly.

Safety gate: LIVE_TRADING_ENABLED must be 0 (default). Do NOT change until
paper/analyzer proof passes and CI is fully green.
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))  # needed for `from utils.market_hours import ...`

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
            "[health-push] WORKER_PUSH_TOKEN not set — pushes will be rejected when the web service requires it. "
            "Set the same value on both Render services."
        )

    try:
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
                state = json.loads(_SCHEDULER_STATE_FILE.read_text(encoding="utf-8"))
                payload["daemon_heartbeat"] = state.get("daemon_heartbeat")
                payload["daemon_pid"] = state.get("daemon_pid")
                payload["jobs"] = state.get("jobs", {})
                payload["config_jobs_total"] = state.get("config_jobs_total")
                payload["config_jobs_enabled"] = state.get("config_jobs_enabled")
                payload["jobs_status_today"] = state.get("jobs_status_today", {})
                payload["fired_keys_today"] = state.get("fired_keys_today", [])

            if _SCHEDULER_ALERT_FILE.exists():
                payload["config_alert"] = json.loads(_SCHEDULER_ALERT_FILE.read_text(encoding="utf-8"))

            body = json.dumps(payload).encode("utf-8")
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
        except _urlerr.HTTPError as exc:
            if exc.code == 401:
                log.warning("[health-push] 401 from web service — WORKER_PUSH_TOKEN missing or different between Render web and worker")
            else:
                log.warning(f"[health-push] HTTP error from web service ({web_url}): {exc}")
        except _urlerr.URLError as exc:
            log.warning(f"[health-push] could not reach web service ({web_url}): {exc}")
        except Exception as exc:
            log.warning(f"[health-push] push failed: {exc}")

        time.sleep(_PUSH_INTERVAL_S)


# ---------------------------------------------------------------------------
# Thread 5: Chain push (worker -> web + worker-local paper/analyzer file proof)
# ---------------------------------------------------------------------------
_CHAIN_PUSH_SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
_CHAIN_PUSH_INTERVAL_S = 20
_CHAIN_PUSH_CLOSED_INTERVAL_S = 300
# Dhan option-chain endpoint is rate-limited. Keep a gap between each unique
# underlying request so one loop does not self-throttle all 5 symbols.
_CHAIN_FETCH_SPACING_S = float(os.environ.get("DHAN_OPTION_CHAIN_FETCH_SPACING_S", "3.25"))


def _persist_chain_for_paper_pipeline(symbol: str, data: dict) -> None:
    """Persist official Dhan chain JSON locally for Core Pipeline V8.

    The web service receives in-memory pushes, but the worker paper/analyzer
    thread reads local files. Without this write, Truth Control can show Dhan
    chain in the UI while paper/analyzer still sees NO_LIVE_OPTION_QUOTE.
    """
    payload = dict(data)
    payload.setdefault("data_source", "dhan")
    payload.setdefault("source", "dhan")
    payload.setdefault("stale", False)
    payload["persisted_at_utc"] = datetime.now(timezone.utc).isoformat()
    payload["paper_pipeline_visible"] = True
    for path in (
        ROOT / "state" / f"chain_{symbol.upper()}.json",
        ROOT / "src" / "outputs" / f"chain_{symbol.upper()}.json",
    ):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
            os.replace(tmp, path)
        except Exception as exc:
            log.warning(f"[chain-push] could not persist {symbol} chain to {path}: {exc}")


def _run_chain_push():
    log.info("[chain-push] starting")
    web_url = os.environ.get("WEB_SERVICE_URL", _DEFAULT_WEB_URL).rstrip("/")
    if not web_url.lower().startswith(("http://", "https://")):
        log.error(f"[chain-push] WEB_SERVICE_URL has an unexpected scheme ({web_url!r}) — thread exiting")
        return
    push_token = os.environ.get("WORKER_PUSH_TOKEN", "").strip()

    try:
        import urllib.error as _urlerr
        import urllib.request as _urlreq
    except Exception as exc:
        log.exception(f"[chain-push] import failed: {exc}")
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

                dsm = DataSourceManager()
                chains = {}
                for idx, sym in enumerate(_CHAIN_PUSH_SYMBOLS):
                    try:
                        data = fetch_chain_for_api(dsm, sym)
                        if data and data.get("contracts"):
                            chains[sym] = data
                            _persist_chain_for_paper_pipeline(sym, data)
                            log.info(
                                "[chain-push] official Dhan chain ready: %s contracts=%s spot=%s expiry=%s",
                                sym,
                                data.get("total_contracts"),
                                data.get("spot"),
                                data.get("expiry_date"),
                            )
                        else:
                            log.warning("[chain-push] no Dhan chain for %s: %s", sym, getattr(dsm, "last_error", None))
                    except Exception as exc:
                        log.warning(f"[chain-push] fetch failed for {sym}: {exc}")
                    if idx < len(_CHAIN_PUSH_SYMBOLS) - 1:
                        time.sleep(_CHAIN_FETCH_SPACING_S)

                if not mkt_open:
                    last_closed_push = time.time()

                if chains:
                    body = json.dumps({"chains": chains, "market_open": mkt_open}).encode("utf-8")
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
                    except _urlerr.HTTPError as exc:
                        if exc.code == 401:
                            log.warning("[chain-push] 401 from web service — WORKER_PUSH_TOKEN missing or different between Render web and worker")
                        else:
                            log.warning(f"[chain-push] HTTP error from web service ({web_url}): {exc}")
                    except _urlerr.URLError as exc:
                        log.warning(f"[chain-push] could not reach web service ({web_url}): {exc}")
        except Exception as exc:
            log.warning(f"[chain-push] error (continuing): {exc}")

        time.sleep(_CHAIN_PUSH_INTERVAL_S)


# ---------------------------------------------------------------------------
# Thread 6: Core Pipeline V8 paper/analyzer ledger
# ---------------------------------------------------------------------------
_PAPER_PIPELINE_V8_INTERVAL_S = int(os.environ.get("SYSTEM3_PAPER_PIPELINE_V8_INTERVAL_S", "120"))


def _run_paper_pipeline_v8():
    log.info("[paper-pipeline-v8] starting")
    if os.environ.get("SYSTEM3_PAPER_PIPELINE_V8_ENABLED", "1") in ("0", "false", "False"):
        log.info("[paper-pipeline-v8] disabled via SYSTEM3_PAPER_PIPELINE_V8_ENABLED=0")
        return
    while True:
        try:
            from dashboard.backend.paper_pipeline_v8 import run_pipeline_once

            result = run_pipeline_once(ROOT, create_paper_orders=True, source="cloud_worker")
            log.info(
                "[paper-pipeline-v8] status=%s forecasts=%s paper_orders=%s blocked=%s",
                result.get("status"),
                result.get("forecasts_seen"),
                result.get("paper_orders_written"),
                result.get("blocked_written"),
            )
        except Exception as exc:
            log.warning(f"[paper-pipeline-v8] tick failed: {exc}")
        time.sleep(_PAPER_PIPELINE_V8_INTERVAL_S)


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
    log.info("=== Genesis System3 Cloud Worker starting ===")
    log.info(f"ROOT={ROOT}")
    _bootstrap_token()

    threads = [
        ("token-daemon", _run_token_daemon),
        ("watchdog", _run_watchdog),
        ("job-scheduler", _run_job_scheduler),
        ("health-push", _run_health_push),
        ("chain-push", _run_chain_push),
        ("paper-pipeline-v8", _run_paper_pipeline_v8),
    ]

    for name, target in threads:
        t = threading.Thread(target=target, name=name, daemon=True)
        t.start()
        log.info(f"[{name}] thread launched")

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
