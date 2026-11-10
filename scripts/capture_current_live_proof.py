import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path(r"C:\Users\ADMIN\Genesis_System3\Genesis_System3\live-production-ui-proof\current-live-check")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
TABS = ["overview", "paper", "chain", "broker", "decision-intel"]

async def capture_current_live():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1080})
        
        for tab in TABS:
            url = f"{BASE_URL}/ui/?tab={tab}"
            print(f"Loading {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            shot_path = OUT_DIR / f"current_{tab}_live.png"
            await page.screenshot(path=str(shot_path), full_page=False)
            print(f"  Captured: {shot_path}")
            
        await browser.close()
    print("All live screenshots captured successfully.")

if __name__ == "__main__":
    asyncio.run(capture_current_live())
