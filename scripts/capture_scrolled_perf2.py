import asyncio
import os
import sys
from playwright.async_api import async_playwright

BASE_URL = "https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab=performance"
OUT_PATH = r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\45742530-2fa1-4ac0-8b37-11b5500a9eb3\rev109_live_performance_tables.png"

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        print("Navigating to Performance Tab...")
        await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(4)
        print("Scrolling .overflow-y-auto container...")
        await page.evaluate("""() => {
            const el = document.querySelector('.overflow-y-auto');
            if (el) el.scrollTop = 1200;
        }""")
        await asyncio.sleep(2)
        await page.screenshot(path=OUT_PATH, full_page=False)
        print(f"Captured {OUT_PATH} ({os.path.getsize(OUT_PATH)} bytes)")
        await browser.close()

asyncio.run(capture())
sys.exit(0)
