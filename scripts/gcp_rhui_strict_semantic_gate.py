#!/usr/bin/env python3
"""Strict RHUI semantic gate for the authoritative GCP dashboard.

This read-only gate exists to prevent false-green acceptance when REST broker/data
truth is healthy but the rendered dashboard still shows stale WAITING/LOADING or
broker-disconnected state. Broker/API/UI parity is session-independent; only
market-open/closed banners are session-dependent.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from scripts.gcp_live_ui_semantic_proof import (
    BASE,
    EXPECTED_SHA,
    IST,
    REQUIRED_CHAINS,
    _contract_count,
    _get,
    _publish_status,
    _sha_matches,
    _source_is_dhan,
    _unwrap,
)
from scripts.gcp_ui_tab_visual_proof import ChromeDriverSession, TABS

OUT = Path("reports/latest/rhui_strict_semantic_gate")

# These contradictions are never acceptable when the same-session broker API says
# connected=true. Market-closed banners are deliberately absent from this list.
GLOBAL_BROKER_CONTRADICTIONS = (
    "DHAN · WAITING",
    "BROKER DISCONNECTED",
    "RECONNECTING · BROKER DISCONNECTED",
)

# These are current known non-terminal states that must not be called semantic PASS.
TAB_FORBIDDEN = {
    "genesis": (
        "WAITING FOR MODEL EVIDENCE",
        "NO VERIFIED FORECAST-DISTRIBUTION SERIES",
        "NO VERIFIED CONFIDENCE-BAND SERIES",
    ),
    "e2e-proof": ("WAITING · FULL E2E", "WAITING · BROKER", "WAITING · 4 CHAINS"),
    "chain": (
        "NO VERIFIED BROKER CHAIN ROWS",
        "NO CONTRACTS RETURNED BY BACKEND",
        "READ-ONLY / NO SNAPSHOT",
    ),
    "prediction-audit": (
        "LOADING VALIDATION",
        "WAITING FOR /API/ACCURACY_TREND",
        "WAITING FOR /API/AUTO_GATES",
    ),
    "performance": ("/API/PNL LOADING",),
    "data-integrity": ("NO VERIFIED OPTION CONTRACTS", "BACKEND_DEPENDENCY"),
    "alerts": ("FEED LOADING",),
    "ml": ("VALIDATION PENDING",),
    "broker": ("BROKER PROOF NOT READY", "TOKEN_EXPIRED_OR_INVALID", "AUTH_NEEDED"),
    "system": ("PENDING PROOF", "DEGRADED / UNPROVEN", "BROKER NOT PROVEN"),
}


def _safe_float(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _api_snapshot() -> dict:
    deploy = _unwrap(_get("/api/deploy/info"))
    broker = _unwrap(_get("/api/broker/status"))
    chains: dict[str, dict] = {}
    for symbol in REQUIRED_CHAINS:
        raw = _get(f"/api/chain/{symbol}", timeout=30)
        payload = _unwrap(raw)
        chains[symbol] = {
            "contracts": _contract_count(raw),
            "source_is_dhan": _source_is_dhan(raw),
            "stale": bool(payload.get("stale", False)),
            "spot": _safe_float(
                payload.get("spot")
                or payload.get("spot_price")
                or payload.get("underlying_spot")
            ),
        }
    return {
        "deploy_sha": str(
            deploy.get("git_sha")
            or deploy.get("github_sha")
            or deploy.get("sha")
            or deploy.get("deploy_git_sha")
            or ""
        ),
        "revision": str(
            deploy.get("revision")
            or deploy.get("cloud_run_revision")
            or deploy.get("revision_name")
            or ""
        ),
        "broker_connected": bool(broker.get("connected", False)),
        "broker_error": broker.get("error"),
        "live_trading_enabled": bool(broker.get("live_trading_enabled", False)),
        "order_placement_allowed": bool(broker.get("order_placement_allowed", False)),
        "chains": chains,
    }


def _api_failures(snapshot: dict) -> list[str]:
    failures: list[str] = []
    if EXPECTED_SHA and not _sha_matches(EXPECTED_SHA, str(snapshot.get("deploy_sha") or "")):
        failures.append("exact_serving_sha_mismatch")
    if not snapshot.get("revision"):
        failures.append("serving_revision_missing")
    if snapshot.get("live_trading_enabled"):
        failures.append("live_trading_enabled")
    if snapshot.get("order_placement_allowed"):
        failures.append("order_placement_allowed")
    if not snapshot.get("broker_connected"):
        failures.append("broker_not_connected")
    if snapshot.get("broker_error"):
        failures.append("broker_error_present")
    for symbol in REQUIRED_CHAINS:
        chain = (snapshot.get("chains") or {}).get(symbol) or {}
        if int(chain.get("contracts") or 0) <= 0:
            failures.append(f"{symbol}_contracts_zero")
        if not chain.get("source_is_dhan"):
            failures.append(f"{symbol}_source_not_dhan")
        if chain.get("stale"):
            failures.append(f"{symbol}_stale")
        if _safe_float(chain.get("spot")) <= 0:
            failures.append(f"{symbol}_spot_missing")
    return failures


def _body_text(browser: ChromeDriverSession) -> str:
    value = browser._request(
        "POST",
        f"/session/{browser.session_id}/execute/sync",
        {
            "script": "return (document.body && document.body.innerText || '').toUpperCase();",
            "args": [],
        },
        timeout=15,
    )
    return str(value or "")


def _text_failures(tab_id: str, text: str, *, broker_connected: bool) -> list[str]:
    upper = text.upper()
    failures: list[str] = []
    if broker_connected:
        for marker in GLOBAL_BROKER_CONTRADICTIONS:
            if marker in upper:
                failures.append(f"broker_ui_contradiction:{marker}")
    for marker in TAB_FORBIDDEN.get(tab_id, ()):
        if marker in upper:
            failures.append(f"non_terminal:{marker}")
    return failures


def _browser_check(snapshot: dict) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    failures: list[str] = []
    with ChromeDriverSession(page_load_timeout_s=60) as browser:
        for tab_id, label in TABS:
            browser.set_viewport(1600, 1000)
            browser.navigate(f"{BASE}/ui?{urlencode({'tab': tab_id})}")
            snap = browser.wait_for_active(tab_id)
            deadline = time.monotonic() + 15
            last_text = ""
            row_failures: list[str] = []
            while time.monotonic() < deadline:
                last_text = _body_text(browser)
                row_failures = _text_failures(
                    tab_id,
                    last_text,
                    broker_connected=bool(snapshot.get("broker_connected")),
                )
                if snap.get("active") and not row_failures:
                    break
                snap = browser.proof_snapshot(tab_id)
                time.sleep(1)
            if not snap.get("active"):
                row_failures.append("active_tab_not_proven")
            unique = list(dict.fromkeys(row_failures))
            rows.append({"tab": tab_id, "label": label, "failures": unique})
            failures.extend(f"{tab_id}:{item}" for item in unique)
    return rows, failures


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot: dict = {}
    failures: list[str] = []
    rows: list[dict] = []
    try:
        snapshot = _api_snapshot()
        failures.extend(_api_failures(snapshot))
        if not failures:
            rows, browser_failures = _browser_check(snapshot)
            failures.extend(browser_failures)
    except Exception as exc:
        failures.append(f"gate_exception:{type(exc).__name__}:{str(exc)[:160]}")

    summary = {
        "schema": "system3-rhui-strict-semantic-v1",
        "generated_at_ist": datetime.now(IST).isoformat(),
        "expected_sha": EXPECTED_SHA,
        "api_snapshot": snapshot,
        "tabs": rows,
        "failures": failures,
        "safety": {
            "read_only": True,
            "live_trading_required_false": True,
            "orders_required_false": True,
        },
        "state": "PASS" if not failures and len(rows) == len(TABS) else "FAIL",
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    if summary["state"] == "PASS":
        _publish_status(
            "success",
            "Strict RHUI broker/API/UI + 22-tab semantics passed; LIVE/orders OFF",
        )
        print("RHUI_STRICT_SEMANTIC " + json.dumps({"state": "PASS", "tabs": len(rows)}))
        return 0

    _publish_status(
        "failure",
        "Strict RHUI semantic proof failed; current UI/API contradictions remain",
    )
    print(
        "RHUI_STRICT_SEMANTIC "
        + json.dumps({"state": "FAIL", "failures": failures[:20]}, sort_keys=True)
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
