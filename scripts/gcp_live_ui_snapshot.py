#!/usr/bin/env python3
"""Capture fresh, request-scoped, read-only System3 production UI truth.

This is the authoritative browser path for claims about what the live UI shows now.
It opens the real public GCP service in a new Chrome/WebDriver session, captures every
canonical tab plus required Option Chain subviews, records visible text + timestamps,
and brackets the browser session with sanitized production APIs. Stored outputs become
historical after capture; consumers must apply SYSTEM3_TEMPORAL_TRUTH_V1 before calling
them current/live.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from frontend_local_runtime_smoke import Browser, TABS, _wait_tab

ROOT = Path(__file__).resolve().parents[1]
PROOF_DIR = ROOT / "live-production-ui-proof"
DEFAULT_BASE = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
BASE_URL = os.getenv("SYSTEM3_PUBLIC_BASE_URL", DEFAULT_BASE).rstrip("/")
MAX_AGE_SECONDS = int(os.getenv("SYSTEM3_LIVE_PROOF_MAX_AGE_SECONDS", "300"))
SETTLE_SECONDS = float(os.getenv("SYSTEM3_LIVE_TAB_SETTLE_SECONDS", "2.0"))
REQUIRED_CHAIN_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_get(url: str) -> dict:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "System3-Live-UI-Proof/3.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8") or "{}")
            return payload if isinstance(payload, dict) else {}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return {}


def _sanitize_broker(payload: dict) -> dict:
    token = payload.get("token_proof") if isinstance(payload.get("token_proof"), dict) else {}
    return {
        "connected": payload.get("connected"),
        "error": payload.get("error"),
        "latency_ms": payload.get("latency_ms"),
        "token_source": token.get("source"),
        "secret_version": token.get("secret_version"),
        "hours_remaining": token.get("hours_remaining"),
        "token_value_exposed": token.get("token_value_exposed"),
        "live_trading_enabled": payload.get("live_trading_enabled"),
        "order_placement_allowed": payload.get("order_placement_allowed"),
    }


def _sanitize_health(payload: dict) -> dict:
    return {
        "status": payload.get("status"),
        "ready": payload.get("ready"),
        "healthy": payload.get("healthy"),
        "live_trading_enabled": payload.get("live_trading_enabled"),
        "live_allowed": payload.get("live_allowed"),
        "live_blockers": payload.get("live_blockers"),
    }


def _sanitize_live_board(payload: dict) -> dict:
    rows = payload.get("indices") if isinstance(payload.get("indices"), list) else []
    return {
        "success": payload.get("success"),
        "source": payload.get("source"),
        "live_count": payload.get("live_count"),
        "feed_hits": payload.get("feed_hits"),
        "feed_errors": list(payload.get("feed_errors") or [])[:6],
        "indices": [
            {
                "symbol": row.get("symbol"),
                "ltp": row.get("ltp"),
                "change_pct": row.get("change_pct"),
                "live": row.get("live"),
                "source": row.get("source"),
            }
            for row in rows if isinstance(row, dict)
        ],
    }


def _api_snapshot() -> dict:
    return {
        "captured_at_utc": _utc_now(),
        "broker": _sanitize_broker(_json_get(f"{BASE_URL}/api/broker/status")),
        "health": _sanitize_health(_json_get(f"{BASE_URL}/api/health")),
        "live_board": _sanitize_live_board(_json_get(f"{BASE_URL}/api/market/live-board")),
    }


def _visible_text(browser: Browser) -> str:
    body = browser._execute("return (document.body && document.body.innerText) || '';", [])
    return body if isinstance(body, str) else ""


def _semantic_alerts(text: str) -> list[str]:
    """Return status-like visible lines, avoiding false positives from headings/prose."""
    found: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw.strip())
        if not line:
            continue
        upper = line.upper()
        status_start = re.match(r"^(DISCONNECTED|NO AUTH|API UNKNOWN|NOT READY|FAILED|DEGRADED|UNAVAILABLE|WAITING|LOADING|NO DATA)(\b|\s|·|:)", upper)
        loading_sentence = " IS LOADING" in upper
        if status_start or loading_sentence:
            if upper not in found:
                found.append(upper[:180])
    return found[:30]


def _number_after(label: str, text: str) -> int | None:
    match = re.search(rf"\b{re.escape(label)}\s+(\d+)\b", text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _click_chain_symbol(browser: Browser, symbol: str) -> bool:
    value = browser._execute(
        r"""
const wanted = String(arguments[0] || '').trim().toUpperCase();
const buttons = Array.from(document.querySelectorAll('button'));
const button = buttons.find((el) => String(el.textContent || '').trim().toUpperCase() === wanted);
if (!button) return false;
button.click();
return true;
""",
        [symbol],
    )
    return bool(value)


def _capture_required_chain_subviews(browser: Browser) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if not browser.activate("chain"):
        return {symbol: {"ready": False, "reason": "CHAIN_TAB_NOT_ACTIVATABLE"} for symbol in REQUIRED_CHAIN_SYMBOLS}
    _wait_tab(browser, "chain", 8)
    for symbol in REQUIRED_CHAIN_SYMBOLS:
        clicked = _click_chain_symbol(browser, symbol)
        if not clicked:
            result[symbol] = {"captured_at_utc": _utc_now(), "ready": False, "reason": "SYMBOL_BUTTON_MISSING"}
            continue
        # Store-backed default chain changes immediately; allow expiry/discovery UI and table to settle.
        time.sleep(max(2.5, SETTLE_SECONDS))
        text = _visible_text(browser)
        upper = text.upper()
        contracts = _number_after("CONTRACTS", text)
        strikes = _number_after("STRIKES", text)
        symbol_visible = bool(re.search(rf"\bSYMBOL\s+{re.escape(symbol)}\b", upper))
        dhan_source = bool(re.search(r"SOURCE\s*=\s*DHAN|DATA\s+DHAN|DHAN\s+(?:VERIFIED|SESSION|LIVE|SNAPSHOT)", upper))
        bad_source = bool(re.search(r"SOURCE\s*=.*\b(CSV|YAHOO|SYNTHETIC|MOCK|FAKE)\b", upper))
        populated = (contracts or 0) > 0 and (strikes or 0) > 0
        ready = clicked and symbol_visible and dhan_source and not bad_source and populated
        screenshot = f"chain-{symbol.lower()}-live.png"
        text_file = f"chain-{symbol.lower()}-body.txt"
        browser.screenshot(PROOF_DIR / screenshot)
        (PROOF_DIR / text_file).write_text(text[:50000], encoding="utf-8")
        result[symbol] = {
            "captured_at_utc": _utc_now(),
            "ready": ready,
            "clicked": clicked,
            "symbol_visible": symbol_visible,
            "dhan_source_visible": dhan_source,
            "bad_source_visible": bad_source,
            "contracts_visible": contracts,
            "strikes_visible": strikes,
            "screenshot": screenshot,
            "visible_text": text_file,
            "semantic_alerts": _semantic_alerts(text),
            "reason": "READY" if ready else "REQUIRED_CHAIN_SEMANTIC_PROOF_INCOMPLETE",
        }
        print("LIVE_CHAIN_SUBVIEW", symbol, json.dumps(result[symbol], sort_keys=True))
    return result


def main() -> int:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    for old in PROOF_DIR.iterdir():
        if old.is_file():
            old.unlink()

    capture_started = _utc_now()
    api_start = _api_snapshot()
    tabs: dict[str, dict] = {}
    render_failures: list[str] = []
    required_chain_subviews: dict[str, dict] = {}

    with Browser() as browser:
        browser.navigate(f"{BASE_URL}/ui/?tab=decision-intel")
        first = _wait_tab(browser, "decision-intel", 10)
        if first.get("rootChildren", 0) <= 0 or not first.get("system3"):
            render_failures.append("initial_mount:react_root_or_system3_missing")

        for tab_id in TABS:
            activated = browser.activate(tab_id)
            if not activated:
                render_failures.append(f"{tab_id}:sidebar_button_missing")
                tabs[tab_id] = {
                    "captured_at_utc": _utc_now(),
                    "rendered": False,
                    "failure": "sidebar_button_missing",
                }
                continue
            snap = _wait_tab(browser, tab_id, 6)
            time.sleep(SETTLE_SECONDS)
            text = _visible_text(browser)
            captured_at = _utc_now()
            screenshot = f"{tab_id}-live.png"
            text_file = f"{tab_id}-body.txt"
            browser.screenshot(PROOF_DIR / screenshot)
            (PROOF_DIR / text_file).write_text(text[:50000], encoding="utf-8")
            rendered = (
                snap.get("rootChildren", 0) > 0
                and snap.get("system3") is True
                and snap.get("active") is True
                and snap.get("keyPrompt") is not True
                and (PROOF_DIR / screenshot).is_file()
                and (PROOF_DIR / screenshot).stat().st_size > 0
            )
            if not rendered:
                render_failures.append(f"{tab_id}:render_contract_failed")
            tabs[tab_id] = {
                "captured_at_utc": captured_at,
                "rendered": rendered,
                "active": snap.get("active"),
                "ready_state": snap.get("readyState"),
                "root_children": snap.get("rootChildren"),
                "credential_prompt_rendered": snap.get("keyPrompt"),
                "screenshot": screenshot,
                "visible_text": text_file,
                "visible_text_chars": len(text),
                "semantic_alerts": _semantic_alerts(text),
            }
            print("LIVE_TAB_CAPTURE", tab_id, json.dumps(tabs[tab_id], sort_keys=True))

        required_chain_subviews = _capture_required_chain_subviews(browser)

    api_end = _api_snapshot()
    capture_finished = _utc_now()
    all_rendered = len(tabs) == len(TABS) and all(item.get("rendered") is True for item in tabs.values())
    all_required_chains_ready = len(required_chain_subviews) == len(REQUIRED_CHAIN_SYMBOLS) and all(
        required_chain_subviews.get(symbol, {}).get("ready") is True for symbol in REQUIRED_CHAIN_SYMBOLS
    )
    semantic_attention = {
        tab_id: item.get("semantic_alerts", [])
        for tab_id, item in tabs.items()
        if item.get("semantic_alerts")
    }
    manifest = {
        "schema": "system3-live-production-ui-proof-v3",
        "policy": "SYSTEM3_TEMPORAL_TRUTH_V1",
        "evidence_class": "REQUEST_SCOPED_LIVE_BROWSER",
        "capture_started_at_utc": capture_started,
        "capture_finished_at_utc": capture_finished,
        "captured_at_utc": capture_finished,
        "max_age_seconds": MAX_AGE_SECONDS,
        "base_url": BASE_URL,
        "source_authority": "GCP_PRODUCTION_PUBLIC_URL",
        "github": {
            "sha": os.getenv("GITHUB_SHA"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "event_name": os.getenv("GITHUB_EVENT_NAME"),
        },
        "tabs_expected": list(TABS),
        "tabs_captured": len(tabs),
        "all_tabs_rendered": all_rendered,
        "render_failures": render_failures,
        "semantic_attention": semantic_attention,
        "required_chain_symbols": list(REQUIRED_CHAIN_SYMBOLS),
        "required_chain_subviews": required_chain_subviews,
        "all_required_chain_subviews_ready": all_required_chains_ready,
        "api_start": api_start,
        "api_end": api_end,
        "tabs": tabs,
        "safety": {
            "read_only_capture": True,
            "mutation_endpoints_called": False,
            "order_endpoints_called": False,
            "secret_values_exposed": False,
            "analyze_mode_required": True,
            "live_trading_changed": False,
        },
        "interpretation": {
            "render_pass_is_not_semantic_data_pass": True,
            "required_chain_subviews_are_semantically_checked": True,
            "stored_artifact_becomes_historical_after_capture": True,
            "new_current_request_requires_new_capture": True,
        },
    }
    (PROOF_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print("LIVE_PRODUCTION_UI_PROOF", json.dumps(manifest, sort_keys=True))
    if not all_rendered:
        print("LIVE_PRODUCTION_UI_CAPTURE=FAIL reason=TAB_RENDER")
        return 1
    if not all_required_chains_ready:
        print("LIVE_PRODUCTION_UI_CAPTURE=FAIL reason=REQUIRED_CHAIN_SUBVIEW_SEMANTICS")
        return 4
    print(f"LIVE_PRODUCTION_UI_CAPTURE=PASS tabs={len(tabs)} required_chains={len(required_chain_subviews)} semantic_attention_tabs={len(semantic_attention)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
