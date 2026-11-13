import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        tabs = ["overview", "prediction-audit", "ml", "performance", "data-integrity", "alerts", "system", "chain"]
        for tab in tabs:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab}"
            await page.goto(url, wait_until="networkidle", timeout=25000)
            await asyncio.sleep(2)
            print(f"==================== TAB: {tab} ====================")

            if tab == "overview":
                tickers = await page.locator(".ticker-bar, .vitals-bar, .top-bar, div:has-text('NIFTY')").all_text_contents()
                print("Ticker text sample:", " ".join(tickers[:5]))

            elif tab == "prediction-audit":
                gates = await page.locator("div:has-text('proof-gate'), div:has-text('ML Accuracy')").all_text_contents()
                print("Gates text sample:", " ".join(gates[:4]))

            elif tab == "ml":
                ml_text = await page.locator("div:has-text('System readiness'), div:has-text('Validation checklist'), div:has-text('Model Performance Records')").all_text_contents()
                print("ML text sample:", " ".join(ml_text[:3]))

            elif tab == "performance":
                perf_text = await page.locator("div:has-text('Cumulative Paper Equity Curve'), div:has-text('ML ACCURACY')").all_text_contents()
                print("Perf text sample:", " ".join(perf_text[:3]))

            elif tab == "data-integrity":
                di_text = await page.locator("div:has-text('Costed walk-forward'), div:has-text('Paper lifecycle')").all_text_contents()
                print("Data Integrity text sample:", " ".join(di_text[:3]))

            elif tab == "alerts":
                alert_text = await page.locator("div:has-text('Alerts & Activity Intelligence'), div:has-text('LIVE ALERT STREAM')").all_text_contents()
                print("Alerts text sample:", " ".join(alert_text[:3]))

            elif tab == "system":
                sys_text = await page.locator("div:has-text('Runtime Performance'), div:has-text('Cycle Count')").all_text_contents()
                print("System text sample:", " ".join(sys_text[:3]))

            elif tab == "chain":
                chain_text = await page.locator("div:has-text('SYMBOL NIFTY'), div:has-text('SPOT'), div:has-text('ATM')").all_text_contents()
                print("Chain text sample:", " ".join(chain_text[:3]))

        await browser.close()

asyncio.run(inspect())
