import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab=alerts", wait_until="networkidle")
        await asyncio.sleep(2)
        text = await page.locator("body").inner_text()
        print("Alerts body text snippet:")
        for line in text.split("\n"):
            line = line.strip()
            if line:
                print(" ->", line)
        await browser.close()

asyncio.run(inspect())
