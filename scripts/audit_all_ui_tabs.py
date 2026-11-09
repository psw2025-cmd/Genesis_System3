"""Audit every Genesis UI sidebar tab and save full-page screenshots.

Run: python scripts/audit_all_ui_tabs.py
Requires: pip install playwright && python -m playwright install chromium
Read-only: no orders, no mutations, no login tokens.
"""
from __future__ import annotations
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("GENESIS_UI_URL", "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui")
DASHBOARD_TAB_IDS = {
    "Decision Intel": "decision-intel", "Truth Control": "truth",
    "Genesis Brain": "genesis", "E2E Proof": "e2e-proof",
    "Overview": "overview", "Sim Live": "sim-live",
    "Options Intel": "options-intel", "Option Chain": "chain",
    "Signals": "signals", "Trade": "trade", "Paper Trades": "paper",
    "Positions": "positions", "Risk & Scenarios": "risk-scenarios",
    "Multibagger": "multibagger", "Prediction Audit": "prediction-audit",
    "Performance": "performance", "ML Model": "ml",
    "Data Integrity": "data-integrity", "Broker": "broker",
    "Alerts": "alerts", "System": "system",
    "System readiness": "system-readiness", "Live Gate": "gates",
}
TABS = (
    "Decision Intel", "Truth Control", "Genesis Brain", "E2E Proof",
    "Overview", "Sim Live", "Options Intel", "Option Chain", "Signals",
    "Trade", "Paper Trades", "Positions", "Risk & Scenarios",
    "Multibagger", "Prediction Audit", "Performance", "ML Model",
    "Data Integrity", "Broker", "Alerts", "System", "System readiness",
    "Live Gate",
)
OUT = Path(os.environ.get("GENESIS_UI_AUDIT_DIR", "reports/latest/all_ui_tabs"))
OUT.mkdir(parents=True, exist_ok=True)
rows = []
js_errors = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.on("pageerror", lambda error: js_errors.append(str(error)))
    try:
        page.goto(BASE_URL, wait_until="commit", timeout=30000)
        page.wait_for_timeout(1500)
        for index, name in enumerate(TABS, 1):
            row = {"tab": name, "opened": False, "screenshot": None, "error": None, "flags": [], "active_tab_verified": False}
            try:
                page.locator(`[data-dashboard-tab="${DASHBOARD_TAB_IDS[name]}"]`).click(timeout=4000)
                page.wait_for_timeout(900)
                content = page.locator("body").inner_text()
                path = OUT / f"{index:02d}_{re.sub('[^a-zA-Z0-9]', '_', name)}.png"
                page.screenshot(path=str(path), full_page=True, timeout=15000)
                row.update(opened=True, screenshot=str(path), active_tab_verified=page.locator(`[data-dashboard-tab="${DASHBOARD_TAB_IDS[name]}"]`).get_attribute("aria-current") == "page", flags=[
                    flag for flag in ("STALE", "BLOCKED", "NOT_VERIFIED", "NO_PREDICTION_SOURCE_FOUND")
                    if flag.casefold() in content.casefold()
                ])
            except Exception as error:
                row["error"] = str(error)[:400]
            rows.append(row)
    finally:
        browser.close()
result = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "url": BASE_URL,
    "tabs_expected": len(TABS),
    "tabs_opened": sum(row["opened"] for row in rows),
    "javascript_errors": js_errors,
    "tabs": rows,
    "ui_navigation_pass": len(rows) == len(TABS) and all(row["opened"] and row["active_tab_verified"] for row in rows) and not js_errors,
    "data_truth_pass": False,
    "data_truth_note": "Navigation and screenshots cannot certify freshness, predictions, or paper-trade lifecycle.",
}
(OUT / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({key: result[key] for key in ("tabs_expected", "tabs_opened", "javascript_errors", "ui_navigation_pass", "data_truth_pass")}, indent=2))
raise SystemExit(0 if result["ui_navigation_pass"] else 1)
