import asyncio
from playwright.async_api import async_playwright

TABS = [
    ("overview", "rev107_live_overview.png"),
    ("prediction-audit", "rev107_live_prediction_audit.png"),
    ("ml", "rev107_live_ml.png"),
    ("performance", "rev107_live_performance.png"),
    ("data-integrity", "rev107_live_data_integrity.png"),
    ("alerts", "rev107_live_alerts.png"),
    ("system", "rev107_live_system.png"),
    ("system-readiness", "rev107_live_system_readiness.png"),
    ("chain", "rev107_live_chain.png")
]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        for tab, filename in TABS:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab}"
            print(f"Navigating to {tab}...")
            try:
                await page.goto(url, wait_until="networkidle", timeout=25000)
                await asyncio.sleep(2)
                out_path = f"C:/Users/ADMIN/.gemini/antigravity-cli/brain/45742530-2fa1-4ac0-8b37-11b5500a9eb3/{filename}"
                await page.screenshot(path=out_path, full_page=True)
                print(f"Saved {filename}")
            except Exception as e:
                print(f"Error on {tab}: {e}")

        await browser.close()

asyncio.run(run())
