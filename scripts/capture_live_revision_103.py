import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACTS_DIR = Path(r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\45742530-2fa1-4ac0-8b37-11b5500a9eb3")

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        tabs = [
            ("chain", "revision_103_option_chain.png"),
            ("prediction-audit", "revision_103_prediction_audit.png"),
            ("ml", "revision_103_ml_model.png"),
        ]

        for tab_name, filename in tabs:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab_name}"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000) # Let state stream populate
            out_path = ARTIFACTS_DIR / filename
            await page.screenshot(path=str(out_path), full_page=True)
            print(f"Saved screenshot: {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
