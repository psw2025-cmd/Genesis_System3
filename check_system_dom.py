import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab=system", wait_until="networkidle")
        await asyncio.sleep(2)
        text = await page.locator("body").inner_text()
        print("System tab body text snippet:")
        for line in text.split("\n"):
            line = line.strip()
            if any(w in line for w in ["Cycle Count", "Cycle Duration", "SLA Result", "QC Status", "Runtime Performance", "Deploy SHA"]):
                print(" ->", line)
        await browser.close()

asyncio.run(inspect())
