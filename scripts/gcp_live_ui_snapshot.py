#!/usr/bin/env python3
"""Capture fresh, request-scoped, read-only System3 production UI truth.

This is the authoritative browser path for claims about what the live UI shows now.
It opens the real public GCP service in a new Chrome/WebDriver session, captures every
canonical tab, records visible text + timestamps, and brackets the browser session with
sanitized broker/health API snapshots. Stored outputs become historical after capture;
consumers must apply SYSTEM3_TEMPORAL_TRUTH_V1 before calling them current/live.
"""
from __future__ import annotations

import json
import os
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

VISIBLE_ALERT_MARKERS = (
    "DISCONNECTED",
    "NO AUTH",
    "API UNKNOWN",
    "NOT READY",
    "ERROR",
    "FAILED",
    "DEGRADED",
    "UNAVAILABLE",
    "WAITING",
    "LOADING",
    "NO DATA",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_get(url: str) -> dict:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "System3-Live-UI-Proof/2.0"})
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


def _api_snapshot() -> dict:
    return {
        "captured_at_utc": _utc_now(),
        "broker": _sanitize_broker(_json_get(f"{BASE_URL}/api/broker/status")),
        "health": _sanitize_health(_json_get(f"{BASE_URL}/api/health")),
    }


def _visible_text(browser: Browser) -> str:
    body = browser._execute("return (document.body && document.body.innerText) || '';", [])
    return body if isinstance(body, str) else ""


def _alert_markers(text: str) -> list[str]:
    upper = text.upper()
    return [marker for marker in VISIBLE_ALERT_MARKERS if marker in upper]


def main() -> int:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    for old in PROOF_DIR.iterdir():
        if old.is_file():
            old.unlink()

    capture_started = _utc_now()
    api_start = _api_snapshot()
    tabs: dict[str, dict] = {}
    render_failures: list[str] = []

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
                "alert_markers": _alert_markers(text),
            }
            print("LIVE_TAB_CAPTURE", tab_id, json.dumps(tabs[tab_id], sort_keys=True))

    api_end = _api_snapshot()
    capture_finished = _utc_now()
    all_rendered = len(tabs) == len(TABS) and all(item.get("rendered") is True for item in tabs.values())
    semantic_attention = {
        tab_id: item.get("alert_markers", [])
        for tab_id, item in tabs.items()
        if item.get("alert_markers")
    }
    manifest = {
        "schema": "system3-live-production-ui-proof-v2",
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
            "stored_artifact_becomes_historical_after_capture": True,
            "new_current_request_requires_new_capture": True,
        },
    }
    (PROOF_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print("LIVE_PRODUCTION_UI_PROOF", json.dumps(manifest, sort_keys=True))
    if not all_rendered:
        print("LIVE_PRODUCTION_UI_CAPTURE=FAIL")
        return 1
    print(f"LIVE_PRODUCTION_UI_CAPTURE=PASS tabs={len(tabs)} semantic_attention_tabs={len(semantic_attention)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
