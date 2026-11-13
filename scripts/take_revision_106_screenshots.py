import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\45742530-2fa1-4ac0-8b37-11b5500a9eb3")

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        tabs = [
            ("options-chain", "revision_106_options_chain.png"),
            ("prediction-audit", "revision_106_prediction_audit.png"),
            ("ml", "revision_106_ml.png"),
            ("data-integrity", "revision_106_data_integrity.png"),
            ("alerts", "revision_106_alerts.png"),
            ("system", "revision_106_system.png"),
            ("performance", "revision_106_performance.png"),
            ("system-readiness", "revision_106_system_readiness.png"),
            ("overview", "revision_106_overview.png"),
        ]

        for tab, filename in tabs:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab}"
            print(f"Navigating to {url}...")
            try:
                await page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception as e:
                print(f"Networkidle timeout on {tab}, proceeding...")
            await page.wait_for_timeout(3000)
            out_path = ARTIFACT_DIR / filename
            await page.screenshot(path=str(out_path), full_page=True)
            print(f"Captured {tab} -> {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
