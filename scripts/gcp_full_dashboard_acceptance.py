#!/usr/bin/env python3
"""Canonical fail-closed production acceptance for the Genesis System3 dashboard.

Read-only evidence only. The proof requires exact-serving-SHA API truth, broker/account
read consistency, all 22 current dashboard tabs, four required Dhan option-chain
subviews, desktop/mobile screenshots, and LIVE/order locks. It never calls a mutation,
order, token-rotation, IAM, Secret Manager write, or control-plane endpoint.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from scripts.gcp_live_ui_semantic_proof import (
    BASE,
    EXPECTED_SHA,
    IST,
    _expected_market_open,
    _get,
    _publish_status,
    _sha_matches,
    _unwrap,
    _wait_api_ready,
)
from scripts.gcp_ui_tab_visual_proof import ChromeDriverSession, TABS

OUT = Path("reports/latest/full_dashboard_acceptance")
SCREENSHOTS = OUT / "screenshots"
TEXT = OUT / "text"
REQUIRED_CHAINS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")
EXPECTED_TAB_IDS = tuple(tab_id for tab_id, _label in TABS)

# These markers are allowed only when they are truthful for the current state. A final
# dashboard PASS requires that persistent loading/auth/readiness defects are absent.
TAB_FORBIDDEN_ALWAYS: dict[str, tuple[str, ...]] = {
    "decision-intel": ("DISCONNECTED / NO AUTH", "NO AUTH"),
    "truth": ("READINESS_NOT_PROVEN",),
    "genesis": ("LOADING GENESIS", "WAITING FOR MODEL EVIDENCE"),
    "e2e-proof": ("WAITING · BROKER", "WAITING · 4 CHAINS"),
    "overview": ("WAITING FOR MARKET DATA", "NO TIME-SERIES DATA"),
    "sim-live": ("LOADING SIM",),
    "options-intel": ("LOADING OPTIONS", "NO VERIFIED OPTION CHAIN"),
    "chain": ("READ-ONLY / NO SNAPSHOT", "NO CONTRACTS RETURNED BY BACKEND", "NO VERIFIED BROKER CHAIN ROWS"),
    "signals": ("LOADING SIGNALS",),
    "trade": ("LOADING MARKET TOP",),
    "paper": ("LOADING PAPER POSITIONS",),
    "positions": ("LOADING POSITIONS",),
    "risk-scenarios": ("LOADING READ-ONLY PORTFOLIO RISK", "RISK SERVICE UNAVAILABLE"),
    "multibagger": ("LOADING MULTIBAGGER",),
    "prediction-audit": ("LOADING PREDICTION",),
    "performance": ("LOADING PERFORMANCE",),
    "ml": ("LOADING ML", "NO MODEL REGISTRY"),
    "data-integrity": ("LOADING DATA INTEGRITY",),
    "broker": ("TOKEN_EXPIRED_OR_INVALID", "DHAN · WAITING", "BROKER PROOF NOT READY", "AUTH_NEEDED"),
    "alerts": ("LOADING ALERTS",),
    "system": ("BROKER NOT PROVEN",),
    "gates": ("CHECKING",),
}

TAB_FORBIDDEN_MARKET_OPEN: dict[str, tuple[str, ...]] = {
    "decision-intel": ("MARKET CLOSED", "AFTER HOURS"),
    "overview": ("MARKET CLOSED", "AFTER HOURS"),
    "chain": ("POLLING / DEGRADED",),
}

GLOBAL_FATAL = (
    "TOKEN_EXPIRED_OR_INVALID",
    "DASHBOARD API KEY",
    "ENTER API KEY",
    "APPLICATION ERROR",
)


def _body_text(browser: ChromeDriverSession) -> str:
    value = browser._request(
        "POST",
        f"/session/{browser.session_id}/execute/sync",
        {"script": "return (document.body && document.body.innerText) || '';", "args": []},
        timeout=15,
    )
    return str(value or "")


def _status_lines(text: str) -> list[str]:
    rows: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw.strip())
        upper = line.upper()
        if not line:
            continue
        if any(word in upper for word in ("READY", "WAIT", "LOAD", "ERROR", "FAIL", "DEGRADED", "LOCK", "CONNECTED", "SOURCE=")):
            rows.append(line[:220])
    return rows[:40]


def _tab_failures(tab_id: str, text: str, *, expect_open: bool) -> list[str]:
    upper = text.upper()
    failures: list[str] = []
    if len(text.strip()) < 200 or len([line for line in text.splitlines() if line.strip()]) < 8:
        failures.append("insufficient_visible_content")
    for marker in TAB_FORBIDDEN_ALWAYS.get(tab_id, ()):
        if marker in upper:
            failures.append(f"forbidden:{marker}")
    if expect_open:
        for marker in TAB_FORBIDDEN_MARKET_OPEN.get(tab_id, ()):
            if marker in upper:
                failures.append(f"forbidden_open:{marker}")
    # Fatal auth/application prompts are rejected on data/truth surfaces. Alerts can
    # legitimately describe historic incidents, so do not globally scan that tab.
    if tab_id != "alerts":
        for marker in GLOBAL_FATAL:
            if marker in upper and f"forbidden:{marker}" not in failures:
                failures.append(f"fatal:{marker}")
    return failures


def _safe_section_state(section: object) -> dict:
    if not isinstance(section, dict):
        return {"present": False, "ok": False, "status": None, "error_present": True}
    status = str(section.get("status") or section.get("state") or "").strip()
    error = section.get("error")
    success = section.get("success")
    normalized = section.get("normalized") if isinstance(section.get("normalized"), dict) else {}
    raw = normalized.get("raw") if isinstance(normalized.get("raw"), dict) else {}
    raw_status = str(raw.get("status") or "").strip()
    remarks = raw.get("remarks") if isinstance(raw.get("remarks"), dict) else {}
    error_code = remarks.get("error_code")
    bad_status = status.upper() in {"ERROR", "FAIL", "FAILED", "FAILURE", "AUTH_NEEDED", "TOKEN_EXPIRED_OR_INVALID"}
    bad_raw = raw_status.lower() in {"error", "failure", "failed"}
    ok = success is not False and not bool(error) and not bad_status and not bad_raw
    return {
        "present": True,
        "ok": ok,
        "status": status or None,
        "success": success if isinstance(success, bool) else None,
        "error_present": bool(error) or bad_raw,
        "safe_error_code": str(error_code)[:80] if error_code else None,
    }


def _strict_broker_snapshot() -> dict:
    try:
        batch = _get("/api/batch/positions-holdings", timeout=30)
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}
    payload = _unwrap(batch)
    broker = payload.get("broker_status") if isinstance(payload.get("broker_status"), dict) else {}
    sections = {
        "funds": _safe_section_state(payload.get("funds")),
        "holdings": _safe_section_state(payload.get("holdings")),
        "positions": _safe_section_state(payload.get("positions")),
    }
    connected = bool(broker.get("connected", False))
    error_present = bool(broker.get("error"))
    ok = connected and not error_present and all(section["ok"] for section in sections.values())
    return {
        "ok": ok,
        "broker_connected": connected,
        "broker_error_present": error_present,
        "sections": sections,
        "secret_payload_exposed": False,
    }


def _api_acceptance_snapshot(expect_open: bool) -> tuple[dict, list[dict], list[str]]:
    base_snapshot, attempts = _wait_api_ready(expect_open)
    failures: list[str] = []
    if EXPECTED_SHA and not _sha_matches(EXPECTED_SHA, str(base_snapshot.get("deploy_sha") or "")):
        failures.append("exact_serving_sha_mismatch")
    if base_snapshot.get("live_trading_enabled"):
        failures.append("live_trading_enabled")
    if base_snapshot.get("order_placement_allowed"):
        failures.append("order_placement_allowed")
    # Final product acceptance requires a verified broker and four usable Dhan chains
    # even after-hours; market closure is not an authentication exemption.
    if not base_snapshot.get("broker_connected"):
        failures.append("broker_not_connected")
    if base_snapshot.get("broker_error"):
        failures.append("broker_error_present")
    for symbol in REQUIRED_CHAINS:
        chain = (base_snapshot.get("chains") or {}).get(symbol) or {}
        if int(chain.get("contracts") or 0) <= 0:
            failures.append(f"{symbol}_contracts_zero")
        if not chain.get("source_is_dhan"):
            failures.append(f"{symbol}_source_not_dhan")
        if chain.get("stale"):
            failures.append(f"{symbol}_stale")
        if float(chain.get("spot") or 0) <= 0:
            failures.append(f"{symbol}_spot_missing")
    strict = _strict_broker_snapshot()
    if not strict.get("ok"):
        failures.append("strict_broker_account_reads_not_verified")
    base_snapshot["strict_broker"] = strict
    return base_snapshot, attempts, failures


def _click_exact_button(browser: ChromeDriverSession, label: str) -> bool:
    value = browser._request(
        "POST",
        f"/session/{browser.session_id}/execute/sync",
        {
            "script": """
const wanted = String(arguments[0] || '').trim().toUpperCase();
const button = Array.from(document.querySelectorAll('button')).find(
  el => String(el.textContent || '').trim().toUpperCase() === wanted
);
if (!button) return false;
button.click();
return true;
""",
            "args": [label],
        },
        timeout=15,
    )
    return bool(value)


def _number_after(label: str, text: str) -> int | None:
    match = re.search(rf"\b{re.escape(label)}\s+(\d+)\b", text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _parse_chain_visible(text: str, symbol: str) -> dict:
    """Parse current OptionChain layout without assuming metadata shares one line.

    Current UI renders SYMBOL/CONTRACTS/STRIKES in the controls row and source=...
    in a separate provenance row. Requiring them on one line is a false-negative.
    """
    symbol_visible = bool(re.search(rf"\bSYMBOL\s+{re.escape(symbol)}\b", text, flags=re.IGNORECASE))
    source_match = re.search(r"\bsource\s*=\s*([A-Za-z0-9_.:-]+)", text, flags=re.IGNORECASE)
    source = str(source_match.group(1)).lower() if source_match else ""
    return {
        "symbol_visible": symbol_visible,
        "source": source or None,
        "source_is_dhan": source == "dhan" or source.startswith("dhan_") or source.startswith("dhan-"),
        "contracts": _number_after("CONTRACTS", text),
        "strikes": _number_after("STRIKES", text),
        "expiries": _number_after("EXPIRIES", text),
    }


def _capture_chain_subviews(browser: ChromeDriverSession, api_snapshot: dict) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    failures: list[str] = []
    browser.set_viewport(1600, 1000)
    browser.navigate(f"{BASE}/ui?{urlencode({'tab': 'chain'})}")
    browser.wait_for_active("chain")
    for symbol in REQUIRED_CHAINS:
        clicked = _click_exact_button(browser, symbol)
        deadline = time.monotonic() + 30
        parsed: dict = {}
        text = ""
        while clicked and time.monotonic() < deadline:
            text = _body_text(browser)
            parsed = _parse_chain_visible(text, symbol)
            if parsed.get("symbol_visible") and parsed.get("source_is_dhan") and int(parsed.get("contracts") or 0) > 0 and int(parsed.get("strikes") or 0) > 0:
                break
            time.sleep(1)
        backend_count = int((((api_snapshot.get("chains") or {}).get(symbol) or {}).get("contracts")) or 0)
        visible_count = int(parsed.get("contracts") or 0)
        row_failures: list[str] = []
        if not clicked:
            row_failures.append("symbol_button_missing")
        if not parsed.get("symbol_visible"):
            row_failures.append("symbol_not_active_visible")
        if not parsed.get("source_is_dhan"):
            row_failures.append("visible_source_not_dhan")
        if visible_count <= 0:
            row_failures.append("visible_contracts_zero")
        if int(parsed.get("strikes") or 0) <= 0:
            row_failures.append("visible_strikes_zero")
        if backend_count <= 0:
            row_failures.append("backend_contracts_zero")
        if backend_count > 0 and visible_count != backend_count:
            row_failures.append(f"api_ui_contract_count_mismatch:{backend_count}!={visible_count}")
        shot = SCREENSHOTS / f"chain-{symbol.lower()}-desktop.png"
        browser.screenshot(shot)
        (TEXT / f"chain-{symbol.lower()}.txt").write_text(text[:60000], encoding="utf-8")
        rows.append({
            "symbol": symbol,
            "clicked": clicked,
            "backend_contracts": backend_count,
            "visible": parsed,
            "failures": row_failures,
            "screenshot": str(shot),
        })
        failures.extend(f"chain:{symbol}:{failure}" for failure in row_failures)
    return rows, failures


def _capture_all_tabs(browser: ChromeDriverSession, *, expect_open: bool) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    failures: list[str] = []
    for index, (tab_id, label) in enumerate(TABS, start=1):
        url = f"{BASE}/ui?{urlencode({'tab': tab_id})}"
        browser.set_viewport(1600, 1000)
        browser.navigate(url)
        snap = browser.wait_for_active(tab_id)
        deadline = time.monotonic() + 30
        text = ""
        row_failures: list[str] = []
        while time.monotonic() < deadline:
            text = _body_text(browser)
            row_failures = _tab_failures(tab_id, text, expect_open=expect_open)
            if snap.get("active") and not row_failures:
                break
            snap = browser.proof_snapshot(tab_id)
            time.sleep(1)
        if not snap.get("active"):
            row_failures.append("active_tab_not_proven")
        if not snap.get("system3"):
            row_failures.append("system3_marker_missing")
        desktop = SCREENSHOTS / f"{index:02d}-{tab_id}-desktop.png"
        mobile = SCREENSHOTS / f"{index:02d}-{tab_id}-mobile.png"
        browser.set_viewport(1600, 1000)
        browser.screenshot(desktop)
        browser.set_viewport(430, 932)
        time.sleep(0.4)
        browser.screenshot(mobile)
        (TEXT / f"{index:02d}-{tab_id}.txt").write_text(text[:60000], encoding="utf-8")
        unique_failures = list(dict.fromkeys(row_failures))
        rows.append({
            "id": tab_id,
            "label": label,
            "active": bool(snap.get("active")),
            "system3": bool(snap.get("system3")),
            "visible_status_lines": _status_lines(text),
            "failures": unique_failures,
            "desktop_screenshot": str(desktop),
            "mobile_screenshot": str(mobile),
        })
        failures.extend(f"tab:{tab_id}:{failure}" for failure in unique_failures)
    return rows, failures


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    TEXT.mkdir(parents=True, exist_ok=True)
    for directory in (SCREENSHOTS, TEXT):
        for old in directory.iterdir():
            if old.is_file():
                old.unlink()

    structural_failures: list[str] = []
    if len(TABS) != 22 or len(set(EXPECTED_TAB_IDS)) != 22:
        structural_failures.append(f"canonical_tab_contract_not_22:{len(TABS)}")

    expect_open = _expected_market_open()
    api_snapshot, attempts, api_failures = _api_acceptance_snapshot(expect_open)
    browser_rows: list[dict] = []
    chain_rows: list[dict] = []
    browser_failures: list[str] = []
    chain_failures: list[str] = []

    if not api_failures and not structural_failures:
        try:
            with ChromeDriverSession(page_load_timeout_s=60) as browser:
                browser_rows, browser_failures = _capture_all_tabs(browser, expect_open=expect_open)
                chain_rows, chain_failures = _capture_chain_subviews(browser, api_snapshot)
        except Exception as exc:
            browser_failures.append(f"browser_harness:{type(exc).__name__}:{str(exc)[:140]}")

    failures = structural_failures + api_failures + browser_failures + chain_failures
    summary = {
        "schema": "system3-full-dashboard-acceptance-v1",
        "generated_at_ist": datetime.now(IST).isoformat(),
        "expected_sha": EXPECTED_SHA,
        "expected_market_open": expect_open,
        "canonical_tab_count": len(TABS),
        "canonical_tab_ids": list(EXPECTED_TAB_IDS),
        "api_snapshot": api_snapshot,
        "api_attempts": attempts,
        "tabs": browser_rows,
        "chain_subviews": chain_rows,
        "failures": failures,
        "safety": {
            "read_only": True,
            "mutation_endpoints_called": False,
            "order_endpoints_called": False,
            "token_rotation_called": False,
            "secret_values_exposed": False,
            "live_trading_enabled": bool(api_snapshot.get("live_trading_enabled", False)),
            "order_placement_allowed": bool(api_snapshot.get("order_placement_allowed", False)),
        },
        "state": "PASS" if not failures and len(browser_rows) == 22 and len(chain_rows) == 4 else "FAIL",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    if summary["state"] == "PASS":
        _publish_status("success", "Exact-SHA 22-tab + 4-chain visual/API acceptance passed; LIVE/orders OFF")
        print("FULL_DASHBOARD_ACCEPTANCE " + json.dumps({"state": "PASS", "tabs": 22, "chains": 4}, sort_keys=True))
        return 0

    _publish_status("failure", "Full dashboard acceptance failed; inspect 22-tab/4-chain visual artifact")
    print("FULL_DASHBOARD_ACCEPTANCE " + json.dumps({"state": "FAIL", "failures": failures[:20]}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
