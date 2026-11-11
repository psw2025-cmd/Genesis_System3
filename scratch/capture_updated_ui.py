import asyncio
from playwright.async_api import async_playwright

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        print("Navigating to http://127.0.0.1:8008/ui...")
        await page.goto("http://127.0.0.1:8008/ui", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)  # Wait for JavaScript tick() to execute
        
        # Capture full page screenshot
        out_path = "reports/latest/ui_recovery/updated_ui_verified_0825.png"
        await page.screenshot(path=out_path, full_page=True)
        print(f"Full-page screenshot saved: {out_path}")

        # Capture top ticker bar clip
        ticker_clip = "reports/latest/ui_recovery/updated_ticker_bar.png"
        await page.screenshot(path=ticker_clip, clip={"x": 0, "y": 0, "width": 1440, "height": 180})
        print(f"Ticker bar clip saved: {ticker_clip}")

        # Capture ML & Paper Trade Ledger section clip
        ml_card = await page.query_selector(".bottom-validation-grid")
        if ml_card:
            box = await ml_card.bounding_box()
            if box:
                await page.screenshot(path="reports/latest/ui_recovery/updated_ml_paper_cards.png", clip=box)
                print("ML & Paper cards clip saved!")

        await browser.close()

asyncio.run(capture())
