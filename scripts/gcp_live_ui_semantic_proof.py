#!/usr/bin/env python3
"""Fail-closed post-deploy semantic proof for the authoritative GCP dashboard.

This gate is deliberately stricter than route/screenshot existence. During an
expected NSE market session it waits for exact-SHA API readiness, a connected
read-only Dhan broker, and four fresh required index chains, then verifies the
rendered browser no longer shows the known cold-start/false-closed markers.

Read-only only: GET/browser reads. No token mint, Secret Manager write, order,
LIVE toggle, IAM mutation, or control-plane mutation is performed here.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, time as dt_time
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests

BASE = os.getenv(
    "SYSTEM3_PRODUCTION_URL",
    "https://genesis-system3-web-doq2wplepa-el.a.run.app",
).rstrip("/")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path("reports/latest/live_ui_semantic_proof")
REQUIRED_CHAINS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")
WAIT_SECONDS = int(os.getenv("SYSTEM3_LIVE_UI_READY_WAIT_S", "240"))
POLL_SECONDS = 10
IST = ZoneInfo("Asia/Kolkata")

KEY_TAB_FORBIDDEN = {
    "decision-intel": ("MARKET CLOSED", "AFTER HOURS", "DISCONNECTED / NO AUTH"),
    "truth": ("READINESS_NOT_PROVEN",),
    "e2e-proof": ("WAITING · BROKER", "WAITING · 4 CHAINS"),
    "overview": ("WAITING FOR MARKET DATA", "NO TIME-SERIES DATA"),
    "chain": ("READ-ONLY / NO SNAPSHOT", "NO CONTRACTS RETURNED BY BACKEND"),
    "signals": ("LOADING SIGNALS",),
    "trade": ("LOADING MARKET TOP",),
    "paper": ("LOADING PAPER POSITIONS",),
    "broker": ("TOKEN_EXPIRED_OR_INVALID", "DHAN · WAITING"),
    "system": ("BROKER NOT PROVEN",),
}


def _expected_market_open(now: datetime | None = None) -> bool:
    now = (now or datetime.now(IST)).astimezone(IST)
    if now.weekday() >= 5:
        return False
    return dt_time(9, 15) <= now.time().replace(tzinfo=None) <= dt_time(15, 30)


def _get(path: str, timeout: int = 20) -> dict:
    response = requests.get(BASE + path, timeout=timeout, headers={"Accept": "application/json"})
    response.raise_for_status()
    value = response.json()
    if not isinstance(value, dict):
        raise RuntimeError(f"non_object_json:{path}")
    return value


def _contract_count(payload: dict) -> int:
    for key in ("total_contracts", "contract_count", "count"):
        try:
            value = int(payload.get(key) or 0)
            if value > 0:
                return value
        except (TypeError, ValueError):
            pass
    contracts = payload.get("contracts")
    return len(contracts) if isinstance(contracts, list) else 0


def _source_is_dhan(payload: dict) -> bool:
    source = str(payload.get("data_source") or payload.get("source") or "").lower()
    priority = str(payload.get("source_priority") or "").lower()
    return source == "dhan" or priority.startswith("dhan") or "dhan" in priority


def _api_snapshot() -> dict:
    deploy = _get("/api/deploy/info")
    state = _get("/api/state")
    broker = _get("/api/broker/status")
    chains: dict[str, dict] = {}
    for symbol in REQUIRED_CHAINS:
        payload = _get(f"/api/chain/{symbol}", timeout=30)
        chains[symbol] = {
            "contracts": _contract_count(payload),
            "source_is_dhan": _source_is_dhan(payload),
            "stale": bool(payload.get("stale", False)),
            "spot": float(payload.get("spot") or 0),
            "status": str(payload.get("status") or ""),
        }
    return {
        "deploy_sha": str(deploy.get("git_sha") or deploy.get("sha") or deploy.get("deploy_git_sha") or ""),
        "market_open": bool((state.get("market") or {}).get("is_open", False)),
        "market_reason": str((state.get("market") or {}).get("reason") or ""),
        "broker_connected": bool(broker.get("connected", False)),
        "broker_error": broker.get("error"),
        "live_trading_enabled": bool(broker.get("live_trading_enabled", False)),
        "order_placement_allowed": bool(broker.get("order_placement_allowed", False)),
        "chains": chains,
    }


def _api_ready(snapshot: dict, expect_open: bool) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if EXPECTED_SHA and snapshot.get("deploy_sha") != EXPECTED_SHA:
        failures.append("exact_serving_sha_mismatch")
    if snapshot.get("live_trading_enabled"):
        failures.append("live_trading_enabled")
    if snapshot.get("order_placement_allowed"):
        failures.append("order_placement_allowed")
    if expect_open:
        if not snapshot.get("market_open"):
            failures.append("market_false_closed_during_expected_session")
        if not snapshot.get("broker_connected"):
            failures.append("broker_not_connected")
        for symbol, chain in snapshot.get("chains", {}).items():
            if chain.get("contracts", 0) <= 0:
                failures.append(f"{symbol}_contracts_zero")
            if not chain.get("source_is_dhan"):
                failures.append(f"{symbol}_source_not_dhan")
            if chain.get("stale"):
                failures.append(f"{symbol}_stale")
            if chain.get("spot", 0) <= 0:
                failures.append(f"{symbol}_spot_missing")
    return not failures, failures


def _wait_api_ready(expect_open: bool) -> tuple[dict, list[dict]]:
    deadline = time.monotonic() + WAIT_SECONDS
    attempts: list[dict] = []
    last: dict = {}
    while True:
        try:
            last = _api_snapshot()
            ready, failures = _api_ready(last, expect_open)
            attempts.append({
                "at": datetime.now(IST).isoformat(),
                "ready": ready,
                "failures": failures,
                "market_open": last.get("market_open"),
                "broker_connected": last.get("broker_connected"),
                "chain_contracts": {k: v.get("contracts") for k, v in last.get("chains", {}).items()},
            })
            if ready:
                return last, attempts
        except Exception as exc:
            attempts.append({
                "at": datetime.now(IST).isoformat(),
                "ready": False,
                "error_type": type(exc).__name__,
                "error": str(exc)[:160],
            })
        if time.monotonic() >= deadline:
            return last, attempts
        time.sleep(POLL_SECONDS)


def _browser_semantic_check(expect_open: bool) -> dict:
    from scripts.gcp_ui_tab_visual_proof import ChromeDriverSession

    failures: list[str] = []
    rows: list[dict] = []
    with ChromeDriverSession(page_load_timeout_s=60) as browser:
        for tab_id, forbidden in KEY_TAB_FORBIDDEN.items():
            url = f"{BASE}/ui?{urlencode({'tab': tab_id})}"
            browser.set_viewport(1600, 1000)
            browser.navigate(url)
            browser.wait_for_active(tab_id)
            deadline = time.monotonic() + 25
            last_text = ""
            active = False
            while time.monotonic() < deadline:
                snapshot = browser.proof_snapshot(tab_id)
                active = bool(snapshot.get("active"))
                value = browser._request(
                    "POST",
                    f"/session/{browser.session_id}/execute/sync",
                    {
                        "script": "return (document.body && document.body.innerText || '').toUpperCase();",
                        "args": [],
                    },
                    timeout=15,
                )
                last_text = str(value or "")
                bad = [marker for marker in forbidden if marker in last_text]
                global_bad = []
                if expect_open:
                    if "MARKET CLOSED" in last_text or "AFTER HOURS" in last_text:
                        global_bad.append("false_closed_market_banner")
                    if "DHAN · WAITING" in last_text:
                        global_bad.append("broker_waiting_after_api_ready")
                if active and not bad and not global_bad:
                    break
                time.sleep(1)
            bad = [marker for marker in forbidden if marker in last_text]
            global_bad = []
            if expect_open:
                if "MARKET CLOSED" in last_text or "AFTER HOURS" in last_text:
                    global_bad.append("false_closed_market_banner")
                if "DHAN · WAITING" in last_text:
                    global_bad.append("broker_waiting_after_api_ready")
            row_failures = ([] if active else ["active_tab_not_proven"]) + [f"forbidden:{x}" for x in bad] + global_bad
            failures.extend(f"{tab_id}:{item}" for item in row_failures)
            rows.append({"tab": tab_id, "active": active, "failures": row_failures})
    return {"state": "PASS" if not failures else "FAIL", "rows": rows, "failures": failures}


def _publish_status(state: str, description: str) -> None:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    api = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    if not (token and repo and EXPECTED_SHA):
        return
    payload = json.dumps({
        "state": state,
        "context": "live-ui/semantic-proof",
        "description": description[:140],
    }).encode()
    request = urllib.request.Request(
        f"{api}/repos/{repo}/statuses/{EXPECTED_SHA}",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30):
        pass


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    expect_open = _expected_market_open()
    api_snapshot, attempts = _wait_api_ready(expect_open)
    api_ok, api_failures = _api_ready(api_snapshot, expect_open)
    browser = {"state": "SKIPPED", "rows": [], "failures": []}
    if api_ok:
        browser = _browser_semantic_check(expect_open)

    failures = list(api_failures) + list(browser.get("failures") or [])
    summary = {
        "generated_at_ist": datetime.now(IST).isoformat(),
        "expected_sha": EXPECTED_SHA,
        "expected_market_open": expect_open,
        "api_ready": api_ok,
        "api_snapshot": api_snapshot,
        "attempts": attempts,
        "browser": browser,
        "failures": failures,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "state": "PASS" if not failures and browser.get("state") == "PASS" else "FAIL",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    if summary["state"] == "PASS":
        _publish_status("success", "Exact-SHA live API + rendered UI semantics passed; LIVE/orders OFF")
        print("LIVE_UI_SEMANTIC_PROOF " + json.dumps({"state": "PASS", "expected_market_open": expect_open}, sort_keys=True))
        return 0

    _publish_status("failure", "Live UI semantic proof failed; route/screenshot PASS is insufficient")
    print("LIVE_UI_SEMANTIC_PROOF " + json.dumps({"state": "FAIL", "failures": failures[:12]}, sort_keys=True), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
