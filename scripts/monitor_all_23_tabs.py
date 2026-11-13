import asyncio
import json
import os
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("TARGET_URL", "https://genesis-system3-web-802404398783.asia-south1.run.app/ui")
OUT_DIR = Path("reports/latest/tab_audit_snaps")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TABS = [
    ("decision-intel", "Decision Intel"),
    ("truth", "Truth Control"),
    ("genesis", "Genesis Brain"),
    ("e2e-proof", "E2E Proof"),
    ("overview", "Overview"),
    ("sim-live", "Sim Live"),
    ("options-intel", "Options Intel"),
    ("chain", "Option Chain"),
    ("signals", "Signals"),
    ("trade", "Trade"),
    ("paper", "Paper Trades"),
    ("positions", "Positions"),
    ("risk-scenarios", "Risk & Scenarios"),
    ("multibagger", "Multibagger"),
    ("prediction-audit", "Prediction Audit"),
    ("performance", "Performance"),
    ("ml", "ML Model"),
    ("data-integrity", "Data Integrity"),
    ("broker", "Broker"),
    ("alerts", "Alerts"),
    ("system", "System"),
    ("system-readiness", "System readiness"),
    ("gates", "Live Gate"),
]

async def audit_tab(page, tab_id, tab_label):
    console_errors = []
    http_errors = []
    
    def on_console(msg):
        if msg.type in ["error", "warning"]:
            console_errors.append(f"[{msg.type}] {msg.text}")

    def on_page_error(err):
        console_errors.append(f"[pageerror] {str(err)}")

    def on_response(resp):
        if resp.status >= 400 and not resp.url.endswith("favicon.ico"):
            http_errors.append(f"[{resp.status}] {resp.url}")

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    page.on("response", on_response)

    tab_url = f"{BASE_URL}?tab={tab_id}"
    t0 = time.time()
    print(f"\n>>> [START] Monitoring Tab: {tab_label} ({tab_id}) -> {tab_url}")
    
    try:
        await page.goto(tab_url, wait_until="networkidle", timeout=30000)
    except Exception as e:
        print(f"    Navigation timeout or error: {e}")
        try:
            await page.wait_for_timeout(2000)
        except Exception:
            pass

    # Wait an extra 3 seconds for async hooks / rendering
    await page.wait_for_timeout(3000)
    elapsed = round(time.time() - t0, 2)

    # Take screenshot
    snap_path = OUT_DIR / f"{tab_id}.png"
    await page.screenshot(path=str(snap_path), full_page=True)

    # Evaluate visible blockers or errors in DOM
    page_text = await page.evaluate("() => document.body.innerText")
    
    # Check for known blocker keywords
    found_blockers = []
    for line in page_text.split("\n"):
        line_clean = line.strip()
        if any(kw in line_clean.upper() for kw in ["BLOCKED", "RETRAIN_NEEDED", "NO_PREDICTION_SOURCE_FOUND", "SYS3-BLK", "FAILED TO FETCH", "UNHANDLED EXCEPTION"]):
            if line_clean not in found_blockers and len(line_clean) < 120:
                found_blockers.append(line_clean)

    # Cleanup listeners
    page.remove_listener("console", on_console)
    page.remove_listener("pageerror", on_page_error)
    page.remove_listener("response", on_response)

    result = {
        "tab_id": tab_id,
        "tab_label": tab_label,
        "elapsed_sec": elapsed,
        "snap_path": str(snap_path),
        "console_errors": console_errors[:10],
        "http_errors": http_errors[:10],
        "blockers": found_blockers[:10]
    }
    
    print(f"    Loaded in {elapsed}s | Console Errs: {len(console_errors)} | HTTP Errs: {len(http_errors)} | Blockers: {len(found_blockers)}")
    if found_blockers:
        print(f"    Detected blockers: {found_blockers[:3]}")
    if http_errors:
        print(f"    HTTP failures: {http_errors[:3]}")
    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        results = []
        for tab_id, tab_label in TABS:
            res = await audit_tab(page, tab_id, tab_label)
            results.append(res)

        await browser.close()

        summary_file = OUT_DIR / "audit_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\n[DONE] Audit complete across {len(TABS)} tabs. Summary saved to {summary_file}")

if __name__ == "__main__":
    asyncio.run(main())
