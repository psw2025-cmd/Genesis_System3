import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path("reports/latest/live_verified")
OUT.mkdir(parents=True, exist_ok=True)

TABS = ["ml", "prediction-audit", "system-readiness", "truth", "genesis"]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        for tab in TABS:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab}"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            shot_path = OUT / f"verified_{tab}.png"
            await page.screenshot(path=str(shot_path), full_page=True)
            print(f"Saved {shot_path}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
