import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path(r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\45742530-2fa1-4ac0-8b37-11b5500a9eb3")

TABS = [
    ("ml", "revision_101_ml.png"),
    ("prediction-audit", "revision_101_prediction_audit.png"),
    ("system-readiness", "revision_101_system_readiness.png"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        for tab_name, file_name in TABS:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab_name}"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)
            shot_path = OUT / file_name
            await page.screenshot(path=str(shot_path), full_page=True)
            print(f"Saved {shot_path}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
