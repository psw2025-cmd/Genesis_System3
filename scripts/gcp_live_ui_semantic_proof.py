#!/usr/bin/env python3
"""Fail-closed post-deploy semantic proof for the authoritative GCP dashboard.

This gate is deliberately stricter than route/screenshot existence. During an
expected NSE market session it waits for exact-SHA API readiness, a connected
read-only Dhan broker, and four fresh required index chains, then verifies the
rendered browser no longer shows the known cold-start/false-closed markers.

The browser phase deliberately loads the SPA exactly once and switches tabs by
clicking the existing dashboard navigation. This preserves one continuously
hydrated frontend document/store epoch across the semantic scan and records a
stable document marker for every captured tab.

Read-only only: GET/browser reads. No token mint, Secret Manager write, order,
LIVE toggle, IAM mutation, or control-plane mutation is performed here.
"""
from __future__ import annotations

import json
import os
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

SESSION_OPEN_ONLY_FORBIDDEN = frozenset({"MARKET CLOSED", "AFTER HOURS"})


def _effective_forbidden(forbidden: tuple[str, ...], *, expect_open: bool) -> tuple[str, ...]:
    if expect_open:
        return forbidden
    return tuple(marker for marker in forbidden if marker not in SESSION_OPEN_ONLY_FORBIDDEN)


def _expected_market_open(now: datetime | None = None) -> bool:
    now = (now or datetime.now(IST)).astimezone(IST)
    if now.weekday() >= 5:
        return False
    return dt_time(9, 15) <= now.time().replace(tzinfo=None) <= dt_time(15, 30)


def _unwrap(payload: dict) -> dict:
    data = payload.get("data")
    return data if isinstance(data, dict) else payload


def _get(path: str, timeout: int = 20) -> dict:
    response = requests.get(BASE + path, timeout=timeout, headers={"Accept": "application/json"})
    response.raise_for_status()
    value = response.json()
    if not isinstance(value, dict):
        raise RuntimeError(f"non_object_json:{path}")
    return value


def _contract_count(payload: dict) -> int:
    payload = _unwrap(payload)
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
    payload = _unwrap(payload)
    source = str(payload.get("data_source") or payload.get("source") or "").lower()
    priority = str(payload.get("source_priority") or "").lower()
    return source == "dhan" or priority.startswith("dhan") or "dhan" in priority


def _api_snapshot() -> dict:
    deploy = _unwrap(_get("/api/deploy/info"))
    state = _unwrap(_get("/api/state"))
    broker = _unwrap(_get("/api/broker/status"))
    chains: dict[str, dict] = {}
    for symbol in REQUIRED_CHAINS:
        raw = _get(f"/api/chain/{symbol}", timeout=30)
        payload = _unwrap(raw)
        try:
            spot = float(payload.get("spot") or payload.get("spot_price") or payload.get("underlying_spot") or 0)
        except (TypeError, ValueError):
            spot = 0.0
        chains[symbol] = {
            "contracts": _contract_count(raw),
            "source_is_dhan": _source_is_dhan(raw),
            "stale": bool(payload.get("stale", False)),
            "spot": spot,
            "status": str(payload.get("status") or ""),
        }
    return {
        "deploy_sha": str(deploy.get("git_sha") or deploy.get("github_sha") or deploy.get("sha") or deploy.get("deploy_git_sha") or ""),
        "revision": str(deploy.get("revision") or deploy.get("cloud_run_revision") or deploy.get("revision_name") or ""),
        "market_open": bool((state.get("market") or {}).get("is_open", False)),
        "market_reason": str((state.get("market") or {}).get("reason") or ""),
        "broker_connected": bool(broker.get("connected", False)),
        "broker_error": broker.get("error"),
        "live_trading_enabled": bool(broker.get("live_trading_enabled", False)),
        "order_placement_allowed": bool(broker.get("order_placement_allowed", False)),
        "chains": chains,
    }


def _sha_matches(expected: str, actual: str) -> bool:
    expected = expected.strip().lower()
    actual = actual.strip().lower()
    if not expected or not actual:
        return False
    return expected == actual or (len(actual) >= 7 and expected.startswith(actual)) or (len(expected) >= 7 and actual.startswith(expected))


def _api_ready(snapshot: dict, expect_open: bool) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if EXPECTED_SHA and not _sha_matches(EXPECTED_SHA, str(snapshot.get("deploy_sha") or "")):
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
                "deploy_sha": last.get("deploy_sha"),
                "revision": last.get("revision"),
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


def _execute(browser, script: str, args: list | None = None):
    return browser._request(
        "POST",
        f"/session/{browser.session_id}/execute/sync",
        {"script": script, "args": args or []},
        timeout=15,
    )


def _document_probe(browser, *, initialize: bool = False) -> dict:
    script = r"""
if (arguments[0] && !window.__SYSTEM3_SEMANTIC_PROOF_DOCUMENT_ID__) {
  const randomPart = (globalThis.crypto && crypto.randomUUID) ? crypto.randomUUID() : Math.random().toString(36).slice(2);
  window.__SYSTEM3_SEMANTIC_PROOF_DOCUMENT_ID__ = String(performance.timeOrigin) + ':' + randomPart;
}
return {
  document_id: String(window.__SYSTEM3_SEMANTIC_PROOF_DOCUMENT_ID__ || ''),
  time_origin: Number(performance.timeOrigin || 0),
  href: String(location.href || ''),
  ready_state: String(document.readyState || '')
};
"""
    value = _execute(browser, script, [bool(initialize)])
    return value if isinstance(value, dict) else {}


def _click_dashboard_tab(browser, tab_id: str) -> bool:
    script = r"""
const id = String(arguments[0] || '');
const button = document.querySelector('[data-dashboard-tab="' + CSS.escape(id) + '"]');
if (!button) return false;
button.click();
return true;
"""
    return bool(_execute(browser, script, [tab_id]))


def _body_text_upper(browser) -> str:
    value = _execute(browser, "return (document.body && document.body.innerText || '').toUpperCase();")
    return str(value or "")


def _scan_tabs_same_document(browser, expect_open: bool) -> dict:
    """Switch dashboard tabs without navigation and prove document continuity."""
    failures: list[str] = []
    rows: list[dict] = []
    initial = _document_probe(browser, initialize=True)
    document_id = str(initial.get("document_id") or "")
    if not document_id:
        return {"state": "FAIL", "rows": [], "failures": ["document_identity_missing"], "document_id": None}

    for tab_id, forbidden in KEY_TAB_FORBIDDEN.items():
        effective_forbidden = _effective_forbidden(forbidden, expect_open=expect_open)
        clicked = _click_dashboard_tab(browser, tab_id)
        deadline = time.monotonic() + 25
        last_text = ""
        active = False
        probe: dict = {}
        if clicked:
            browser.wait_for_active(tab_id)
        while clicked and time.monotonic() < deadline:
            snapshot = browser.proof_snapshot(tab_id)
            active = bool(snapshot.get("active"))
            probe = _document_probe(browser)
            last_text = _body_text_upper(browser)
            bad = [marker for marker in effective_forbidden if marker in last_text]
            global_bad = []
            if expect_open:
                if "MARKET CLOSED" in last_text or "AFTER HOURS" in last_text:
                    global_bad.append("false_closed_market_banner")
                if "DHAN · WAITING" in last_text:
                    global_bad.append("broker_waiting_after_api_ready")
            if active and str(probe.get("document_id") or "") == document_id and not bad and not global_bad:
                break
            time.sleep(1)

        probe = probe or _document_probe(browser)
        bad = [marker for marker in effective_forbidden if marker in last_text]
        global_bad = []
        if expect_open:
            if "MARKET CLOSED" in last_text or "AFTER HOURS" in last_text:
                global_bad.append("false_closed_market_banner")
            if "DHAN · WAITING" in last_text:
                global_bad.append("broker_waiting_after_api_ready")
        row_failures = ([] if clicked else ["tab_button_missing"])
        row_failures += ([] if active else ["active_tab_not_proven"])
        if str(probe.get("document_id") or "") != document_id:
            row_failures.append("document_reloaded_during_tab_scan")
        row_failures += [f"forbidden:{x}" for x in bad] + global_bad
        failures.extend(f"{tab_id}:{item}" for item in row_failures)
        rows.append({
            "tab": tab_id,
            "clicked": clicked,
            "active": active,
            "document_id": probe.get("document_id"),
            "document_time_origin": probe.get("time_origin"),
            "href": probe.get("href"),
            "captured_at_ist": datetime.now(IST).isoformat(),
            "failures": row_failures,
        })
    return {
        "state": "PASS" if not failures else "FAIL",
        "rows": rows,
        "failures": failures,
        "document_id": document_id,
        "initial_document": initial,
        "navigation_mode": "single_document_dashboard_tab_clicks",
    }


def _browser_semantic_check(expect_open: bool) -> dict:
    from scripts.gcp_ui_tab_visual_proof import ChromeDriverSession

    first_tab = next(iter(KEY_TAB_FORBIDDEN))
    with ChromeDriverSession(page_load_timeout_s=60) as browser:
        browser.set_viewport(1600, 1000)
        browser.navigate(f"{BASE}/ui?{urlencode({'tab': first_tab})}")
        browser.wait_for_active(first_tab)
        return _scan_tabs_same_document(browser, expect_open)


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
        _publish_status("success", "Exact-SHA same-document API + rendered UI semantics passed; LIVE/orders OFF")
        print("LIVE_UI_SEMANTIC_PROOF " + json.dumps({"state": "PASS", "expected_market_open": expect_open}, sort_keys=True))
        return 0

    _publish_status("failure", "Live UI semantic proof failed; route/screenshot PASS is insufficient")
    print("LIVE_UI_SEMANTIC_PROOF " + json.dumps({"state": "FAIL", "failures": failures[:12]}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
