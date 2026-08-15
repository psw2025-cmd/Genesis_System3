#!/usr/bin/env python3
"""Capture a sanitized, read-only screenshot of the live System3 production UI.

This proof never calls mutation/order endpoints. It opens the public PAPER dashboard
through Chrome/WebDriver, captures Decision Intel, and records only sanitized broker
and health fields so operators can distinguish "page rendered" from "live data ready".
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from frontend_local_runtime_smoke import Browser, _wait_tab

ROOT = Path(__file__).resolve().parents[1]
PROOF_DIR = ROOT / "live-production-ui-proof"
DEFAULT_BASE = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
BASE_URL = os.getenv("SYSTEM3_PUBLIC_BASE_URL", DEFAULT_BASE).rstrip("/")
UI_URL = f"{BASE_URL}/ui/?tab=decision-intel"


def _json_get(url: str) -> dict:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "System3-Live-UI-Proof/1.0"})
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
    }


def main() -> int:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    for old in PROOF_DIR.iterdir():
        if old.is_file():
            old.unlink()

    broker = _sanitize_broker(_json_get(f"{BASE_URL}/api/broker/status"))
    health = _sanitize_health(_json_get(f"{BASE_URL}/api/health"))

    body_text = ""
    snap: dict = {}
    screenshot_path = PROOF_DIR / "decision-intel-live.png"
    with Browser() as browser:
        browser.navigate(UI_URL)
        snap = _wait_tab(browser, "decision-intel", 10)
        # Allow the dashboard's read-only polling to settle after the initial mount.
        time.sleep(5)
        body = browser._execute("return (document.body && document.body.innerText) || '';", [])
        body_text = body if isinstance(body, str) else ""
        browser.screenshot(screenshot_path)

    captured_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema": "system3-live-production-ui-proof-v1",
        "captured_at_utc": captured_at,
        "base_url": BASE_URL,
        "ui_url": UI_URL,
        "tab": "decision-intel",
        "screenshot": screenshot_path.name,
        "page": {
            "ready_state": snap.get("readyState"),
            "root_children": snap.get("rootChildren"),
            "active": snap.get("active"),
            "system3_marker": snap.get("system3"),
            "credential_prompt_rendered": snap.get("keyPrompt"),
        },
        "broker": broker,
        "health": health,
        "safety": {
            "read_only_capture": True,
            "mutation_endpoints_called": False,
            "order_endpoints_called": False,
            "secret_values_exposed": False,
        },
    }
    (PROOF_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (PROOF_DIR / "decision-intel-body.txt").write_text(body_text[:30000], encoding="utf-8")

    rendered = (
        snap.get("rootChildren", 0) > 0
        and snap.get("system3") is True
        and snap.get("active") is True
        and snap.get("keyPrompt") is not True
        and screenshot_path.is_file()
        and screenshot_path.stat().st_size > 0
    )
    print("LIVE_PRODUCTION_UI_PROOF", json.dumps(manifest, sort_keys=True))
    if not rendered:
        print("LIVE_PRODUCTION_UI_CAPTURE=FAIL")
        return 1
    print("LIVE_PRODUCTION_UI_CAPTURE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
