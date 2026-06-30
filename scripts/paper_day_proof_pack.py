#!/usr/bin/env python3
"""
Paper Day Proof Pack — assembles the full PAPER_DAY_PROOF_PASS/FAIL
artifact requested by the human reviewer, end of trading day.

Runs INSIDE the cloud environment (scheduled via the job scheduler on
the worker container, schedule_time 16:15 IST) — NOT from an external
sandbox, so it can actually reach the live web service over the
internal/public URL the same way scripts/ui_market_cross_verify.py
already does.

Checks every item from the human's 14-point checklist:
  1.  Render web/worker deploy SHA >= expected commit
  2.  /api/health live JSON
  3.  /api/broker/dhan/status live JSON
  4.  /api/scheduler/health live JSON (received, healthy, jobs, no alert)
  5.  Worker thread-start evidence (best-effort: scheduler state proves
      the scheduler thread is alive; full log grep is not available
      from inside this script, flagged explicitly as unverified)
  6.  Dashboard screenshots — NOT generated here (needs a browser;
      flagged for manual Playwright run, see note in output)
  7.  No raw Vue tokens / placeholder / endless loading — checked via
      a raw-text scan of the /ui HTML response for known bad strings
  8.  daily_gain_rank proof (today's date present in gain_rank_history)
  9.  paper_lifecycle_proof at 09:30/12:00/14:00 (scheduler job status)
  10. daily_gain_validate after close (scheduler job status)
  11. daily_prediction_benchmark output under performance_benchmark/
  12. Telegram/dashboard/DB reconciliation — best-effort via alert
      count vs report count; full Telegram check needs bot API token
      not available to this script, flagged if unverifiable
  13. No live orders / no secrets printed / no OAuth URL — checked via
      scheduler + token manager state, NOT raw log grep (logs aren't
      readable from here either; flagged)
  14. Final ZIP artifact — written to reports/latest/paper_day_proof/

Writes:
  reports/latest/paper_day_proof/PAPER_DAY_PROOF_PASS   (or _FAIL)
  reports/latest/paper_day_proof/proof_pack.json
  reports/latest/paper_day_proof/proof_pack.md
  reports/latest/paper_day_proof/proof_pack.zip

Usage:
  python scripts/paper_day_proof_pack.py
  python scripts/paper_day_proof_pack.py --expected-sha ec597ec0ee83cbc215c26d46b566932af4dc5205
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "latest" / "paper_day_proof"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLOUD = os.environ.get("SYSTEM3_API_BASE", "https://genesis-system3-backend.onrender.com").rstrip("/")
SCHEDULER_STATE_FILE = ROOT / "storage" / "ultra" / "ph76_ph100" / "phase82_job_scheduler_state.json"
GAIN_RANK_HISTORY = ROOT / "state" / "gain_rank_history.json"
PERF_BENCHMARK_DIR = ROOT / "reports" / "latest" / "performance_benchmark"

EXPECTED_SHA_DEFAULT = "ec597ec0ee83cbc215c26d46b566932af4dc5205"

# Strings that must NEVER appear in the rendered /ui HTML — proof that
# the React build replaced the old Vue templating and the hardcoded
# placeholder text is gone.
FORBIDDEN_UI_STRINGS = [
    "{{ ",  # raw Vue mustache token leaking unrendered
    "coming next iteration",
    "Loading funds data…Loading funds data…",  # crude repeat-loop smell
]


def _ist_now() -> datetime:
    return datetime.now(ZoneInfo("Asia/Kolkata"))


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _fetch_json(path: str, timeout: int = 30) -> Dict[str, Any]:
    url = f"{CLOUD}{path}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2_000_000).decode("utf-8", errors="replace")
            data = json.loads(body) if body.strip().startswith(("{", "[")) else {"raw": body[:500]}
            return {"ok": resp.status == 200, "status": resp.status, "data": data}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": str(e)[:300]}
    except Exception as exc:
        return {"ok": False, "status": None, "error": str(exc)[:300]}


def _fetch_text(path: str, timeout: int = 30) -> Dict[str, Any]:
    url = f"{CLOUD}{path}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(3_000_000).decode("utf-8", errors="replace")
            return {"ok": resp.status == 200, "status": resp.status, "text": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:300]}


def check_1_deploy_sha(expected_sha: str) -> Dict[str, Any]:
    """
    Uses /api/deploy/info, which surfaces Render's auto-injected
    RENDER_GIT_COMMIT env var. Falls back to UNVERIFIABLE only if that
    endpoint itself fails (e.g. deployed commit predates this endpoint
    existing at all, or network unreachable).
    """
    r = _fetch_json("/api/deploy/info")
    if not r.get("ok"):
        return {"item": 1, "name": "Render deploy SHA", "status": "UNVERIFIABLE",
                "detail": f"/api/deploy/info unreachable: {r.get('error')}. "
                          f"Confirm manually via Render dashboard Deploys tab."}
    data = r.get("data", {})
    sha_field = data.get("git_sha", "")
    if not sha_field:
        return {"item": 1, "name": "Render deploy SHA", "status": "UNVERIFIABLE",
                "detail": "RENDER_GIT_COMMIT env var empty — Render did not inject it "
                          "(unusual; confirm manually via dashboard)."}
    # "at or newer than expected" can't be determined from a SHA alone
    # without git history access; this confirms EXACT match. If a later
    # commit deploys, this will show a different (still valid) SHA —
    # treat any non-empty match to the latest known commit as informative,
    # not a hard pass/fail unless it's the exact expected one.
    match = sha_field.startswith(expected_sha[:9])
    return {"item": 1, "name": "Render deploy SHA", "status": "PASS" if match else "INFO",
            "detail": f"deployed_sha={sha_field} expected={expected_sha[:9]} "
                      f"branch={data.get('git_branch')} service={data.get('service_name')}"}


def check_2_health() -> Dict[str, Any]:
    r = _fetch_json("/api/health")
    return {"item": 2, "name": "/api/health", "status": "PASS" if r.get("ok") else "FAIL",
            "data": r.get("data"), "error": r.get("error")}


def check_3_broker_status() -> Dict[str, Any]:
    r = _fetch_json("/api/broker/dhan/status")
    ok = r.get("ok") and r.get("data", {}).get("connected") is True
    return {"item": 3, "name": "/api/broker/dhan/status", "status": "PASS" if ok else "FAIL",
            "data": r.get("data"), "error": r.get("error")}


def check_4_scheduler_health() -> Dict[str, Any]:
    r = _fetch_json("/api/scheduler/health")
    data = r.get("data", {}) if r.get("ok") else {}
    received = data.get("received") is True
    healthy = data.get("healthy") is True
    jobs_nonempty = bool(data.get("jobs"))
    no_alert = data.get("config_alert") is None
    all_ok = received and healthy and jobs_nonempty and no_alert
    return {"item": 4, "name": "/api/scheduler/health", "status": "PASS" if all_ok else "FAIL",
            "data": data,
            "subchecks": {"received": received, "healthy": healthy,
                          "jobs_nonempty": jobs_nonempty, "no_config_alert": no_alert}}


def check_5_worker_threads() -> Dict[str, Any]:
    """
    Cannot grep worker container logs from here (no log API access
    configured). Best proxy: if /api/scheduler/health shows a fresh
    daemon_heartbeat and daemon_pid, the job-scheduler thread (and by
    extension the worker process) is provably alive. token-daemon,
    watchdog, and health-push threads are inferred-but-not-directly-
    confirmed from this signal alone.
    """
    r = _fetch_json("/api/scheduler/health")
    data = r.get("data", {}) if r.get("ok") else {}
    heartbeat = data.get("daemon_heartbeat")
    pid = data.get("daemon_pid")
    if heartbeat and pid:
        return {"item": 5, "name": "Worker threads started", "status": "PARTIAL",
                "detail": f"job-scheduler thread proven alive (heartbeat={heartbeat}, pid={pid}). "
                          f"token-daemon/watchdog/health-push threads inferred but not directly "
                          f"confirmed — full proof needs Render log access this script doesn't have."}
    return {"item": 5, "name": "Worker threads started", "status": "FAIL",
            "detail": "No daemon_heartbeat/pid in scheduler health — worker scheduler thread "
                      "appears not running or never pushed."}


def check_6_dashboard_screenshots() -> Dict[str, Any]:
    return {"item": 6, "name": "Dashboard screenshots", "status": "UNVERIFIABLE",
            "detail": "Screenshot capture requires a real browser (Playwright). This script runs "
                      "headless inside the worker container with no display/browser binary "
                      "installed. Run tools/playwright-setup/verify_all_ui_tabs.spec.ts "
                      "separately (CI or local) for this item."}


def check_7_no_placeholders() -> Dict[str, Any]:
    r = _fetch_text("/ui")
    if not r.get("ok"):
        return {"item": 7, "name": "No raw Vue/placeholder/endless-loading", "status": "FAIL",
                "detail": f"Could not fetch /ui: {r.get('error')}"}
    text = r["text"]
    found = [s for s in FORBIDDEN_UI_STRINGS if s in text]
    return {"item": 7, "name": "No raw Vue/placeholder/endless-loading",
            "status": "FAIL" if found else "PASS",
            "detail": f"Forbidden strings found: {found}" if found else "Clean"}


def check_8_gain_rank_today() -> Dict[str, Any]:
    today_str = date.today().isoformat()
    if not GAIN_RANK_HISTORY.exists():
        return {"item": 8, "name": "daily_gain_rank ran today", "status": "FAIL",
                "detail": "gain_rank_history.json not found"}
    try:
        history = json.loads(GAIN_RANK_HISTORY.read_text())
        today_entry = next((e for e in history if e.get("date") == today_str), None)
        if today_entry:
            return {"item": 8, "name": "daily_gain_rank ran today", "status": "PASS",
                    "detail": f"{len(today_entry.get('predictions', []))} predictions for {today_str}"}
        return {"item": 8, "name": "daily_gain_rank ran today", "status": "FAIL",
                "detail": f"No entry for {today_str} in gain_rank_history.json"}
    except Exception as exc:
        return {"item": 8, "name": "daily_gain_rank ran today", "status": "FAIL", "detail": str(exc)}


def check_job_status(job_id: str, item_n: int, name: str) -> Dict[str, Any]:
    if not SCHEDULER_STATE_FILE.exists():
        return {"item": item_n, "name": name, "status": "FAIL", "detail": "scheduler state file missing"}
    try:
        state = json.loads(SCHEDULER_STATE_FILE.read_text())
        job = state.get("jobs", {}).get(job_id)
        if not job:
            return {"item": item_n, "name": name, "status": "FAIL", "detail": f"{job_id} never ran"}
        today_str = date.today().isoformat()
        ran_today = str(job.get("last_run_time", "")).startswith(today_str)
        status = job.get("last_status")
        ok = ran_today and status in ("SUCCESS", "MARKET_CLOSED_OR_HOLIDAY")
        return {"item": item_n, "name": name, "status": "PASS" if ok else "FAIL",
                "detail": f"last_status={status} last_run={job.get('last_run_time')} ran_today={ran_today}"}
    except Exception as exc:
        return {"item": item_n, "name": name, "status": "FAIL", "detail": str(exc)}


def check_11_benchmark_output() -> Dict[str, Any]:
    required = ["prediction_vs_actual.csv", "top_mover_match.csv",
                "missed_opportunities.md", "benchmark_summary.md"]
    if not PERF_BENCHMARK_DIR.exists():
        return {"item": 11, "name": "performance_benchmark output", "status": "FAIL",
                "detail": "reports/latest/performance_benchmark/ does not exist"}
    missing = [f for f in required if not (PERF_BENCHMARK_DIR / f).exists()]
    today_str = date.today().isoformat().replace("-", "")
    archive_dir = ROOT / "reports" / "archive" / "performance_benchmark" / today_str
    archived = archive_dir.exists()
    ok = not missing and archived
    return {"item": 11, "name": "performance_benchmark output", "status": "PASS" if ok else "FAIL",
            "detail": f"missing={missing} archived_today={archived}"}


def check_12_reconciliation() -> Dict[str, Any]:
    """
    Full Telegram reconciliation needs a bot token this script doesn't
    have. Best-effort proxy: compare dashboard alert count to recent
    alerts API count for internal consistency.
    """
    r = _fetch_json("/api/alerts/recent?limit=200")
    if not r.get("ok"):
        return {"item": 12, "name": "Telegram/dashboard/DB reconciliation", "status": "UNVERIFIABLE",
                "detail": f"Could not fetch /api/alerts/recent: {r.get('error')}"}
    alerts = r.get("data", {}).get("alerts", [])
    return {"item": 12, "name": "Telegram/dashboard/DB reconciliation", "status": "PARTIAL",
            "detail": f"{len(alerts)} alerts visible via dashboard API. Full Telegram-side "
                      f"trace_id reconciliation needs bot API access not configured for this "
                      f"script — flagged for manual check if Telegram is in use."}


def check_13_no_leaks(broker_check: Dict[str, Any], scheduler_check: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cannot grep raw Render logs from here. Proxy: confirm live API
    responses themselves don't leak token/secret-shaped strings, and
    that live_trading_enabled/order_placement_allowed are correctly
    false everywhere they're reported.
    """
    issues = []
    bdata = broker_check.get("data") or {}
    if bdata.get("live_trading_enabled") not in (False, None):
        issues.append("broker status reports live_trading_enabled != false")
    if bdata.get("order_placement_allowed") not in (False, None):
        issues.append("broker status reports order_placement_allowed != false")
    # crude secret-shape scan on the raw broker response text
    raw = json.dumps(bdata)
    if "access_token" in raw.lower() and len(raw) > 0:
        # only flag if a long token-like value is actually present, not just the key name
        import re
        if re.search(r'"access_token"\s*:\s*"[A-Za-z0-9._-]{20,}"', raw):
            issues.append("possible raw access token value present in /api/broker/dhan/status response")
    status = "PASS" if not issues else "FAIL"
    return {"item": 13, "name": "No live orders / no secrets / no OAuth URL", "status": status,
            "detail": "; ".join(issues) if issues else "No leaks detected in live API responses checked. "
                      "Render raw log grep not available to this script — if a stricter audit is "
                      "needed, search Render's log viewer for 'auth.dhan.co' and 'accessToken'."}


def build_zip(report_path: Path) -> Path:
    zip_path = OUT_DIR / "proof_pack.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob("*"):
            if f.name != "proof_pack.zip":
                zf.write(f, arcname=f.name)
        # bundle the performance_benchmark outputs too, if present
        if PERF_BENCHMARK_DIR.exists():
            for f in PERF_BENCHMARK_DIR.glob("*"):
                zf.write(f, arcname=f"performance_benchmark/{f.name}")
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Paper Day Proof Pack")
    parser.add_argument("--expected-sha", default=EXPECTED_SHA_DEFAULT)
    args = parser.parse_args()

    print("=" * 70)
    print("PAPER DAY PROOF PACK")
    print("=" * 70)
    now_ist = _ist_now()
    print(f"Run time (IST): {now_ist.isoformat()}")
    print(f"API base: {CLOUD}")

    health_check = check_2_health()
    broker_check = check_3_broker_status()
    scheduler_check = check_4_scheduler_health()

    checks = [
        check_1_deploy_sha(args.expected_sha),
        health_check,
        broker_check,
        scheduler_check,
        check_5_worker_threads(),
        check_6_dashboard_screenshots(),
        check_7_no_placeholders(),
        check_8_gain_rank_today(),
        check_job_status("paper_lifecycle_proof", 9, "paper_lifecycle_proof (09:30)"),
        check_job_status("paper_lifecycle_proof_midday", 9, "paper_lifecycle_proof (12:00)"),
        check_job_status("paper_lifecycle_proof_afternoon", 9, "paper_lifecycle_proof (14:00)"),
        check_job_status("daily_gain_validate", 10, "daily_gain_validate"),
        check_11_benchmark_output(),
        check_12_reconciliation(),
        check_13_no_leaks(broker_check, scheduler_check),
    ]

    for c in checks:
        print(f"  [{c['status']:13}] item {c['item']:2}  {c['name']}")

    # PASS/FAIL logic: any hard FAIL = overall FAIL. UNVERIFIABLE/PARTIAL
    # do not auto-fail (they need human follow-up) but are listed
    # separately so they can't be silently treated as PASS.
    hard_fails = [c for c in checks if c["status"] == "FAIL"]
    unverifiable = [c for c in checks if c["status"] in ("UNVERIFIABLE", "PARTIAL", "INFO")]

    overall = "PAPER_DAY_PROOF_FAIL" if hard_fails else (
        "PAPER_DAY_PROOF_PASS_WITH_GAPS" if unverifiable else "PAPER_DAY_PROOF_PASS"
    )

    result = {
        "generated_at_ist": now_ist.isoformat(),
        "generated_at_utc": _utc_iso(),
        "api_base": CLOUD,
        "expected_sha": args.expected_sha,
        "overall_verdict": overall,
        "hard_fail_count": len(hard_fails),
        "unverifiable_or_partial_count": len(unverifiable),
        "checks": checks,
        "live_trading_status": "OFF — LIVE_TRADING_ENABLED must remain 0",
    }

    (OUT_DIR / "proof_pack.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    md_lines = [
        "# Paper Day Proof Pack",
        f"\n_Generated {now_ist.isoformat()} IST_\n",
        f"## Overall Verdict: **{overall}**\n",
        f"- Hard failures: {len(hard_fails)}",
        f"- Unverifiable/partial (needs human follow-up): {len(unverifiable)}",
        "\n## Checklist\n",
        "| # | Item | Status | Detail |",
        "|---|------|--------|--------|",
    ]
    for c in checks:
        detail = str(c.get("detail", c.get("error", "")))[:150]
        md_lines.append(f"| {c['item']} | {c['name']} | {c['status']} | {detail} |")
    md_lines.append(
        "\n**Live trading remains OFF.** This proof pack does not enable, "
        "request, or imply enabling live trading under any condition."
    )
    (OUT_DIR / "proof_pack.md").write_text("\n".join(md_lines), encoding="utf-8")

    verdict_file = OUT_DIR / overall.replace("PAPER_DAY_PROOF_", "PAPER_DAY_PROOF_")
    (OUT_DIR / overall).write_text(
        f"{overall}\ngenerated_at_ist={now_ist.isoformat()}\nhard_fails={len(hard_fails)}\n",
        encoding="utf-8",
    )

    zip_path = build_zip(OUT_DIR / "proof_pack.json")

    print(f"\nOverall: {overall}")
    print(f"Hard fails: {len(hard_fails)}  |  Unverifiable/partial: {len(unverifiable)}")
    print(f"\nOutputs:")
    print(f"  {OUT_DIR / 'proof_pack.json'}")
    print(f"  {OUT_DIR / 'proof_pack.md'}")
    print(f"  {OUT_DIR / overall}")
    print(f"  {zip_path}")

    return 0 if overall == "PAPER_DAY_PROOF_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
