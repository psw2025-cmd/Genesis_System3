import asyncio
import os
import sys
from playwright.async_api import async_playwright

BASE_URL = "https://genesis-system3-web-802404398783.asia-south1.run.app/ui"
OUT_DIR = r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\45742530-2fa1-4ac0-8b37-11b5500a9eb3"

TABS = [
    ("performance", "rev108_live_performance.png"),
    ("data-integrity", "rev108_live_data_integrity.png"),
    ("alerts", "rev108_live_alerts.png"),
    ("ml", "rev108_live_ml.png"),
    ("prediction-audit", "rev108_live_prediction_audit.png"),
    ("option-chain", "rev108_live_option_chain.png"),
]

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        for tab_id, filename in TABS:
            url = f"{BASE_URL}?tab={tab_id}"
            print(f"Navigating to {url}...")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"Navigation warning for {tab_id}: {e}")
            await asyncio.sleep(4)  # wait for data fetching and rendering
            out_path = os.path.join(OUT_DIR, filename)
            await page.screenshot(path=out_path, full_page=False)
            print(f"Captured {filename} ({os.path.getsize(out_path)} bytes)")

        await browser.close()
        print("All live UI screenshots successfully captured!")

asyncio.run(capture())
sys.exit(0)
