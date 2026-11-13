import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    dest_dir = Path(r"C:\Genesis_System3_clean\reports\latest")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    art_dir = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\4e630206-710d-4a9e-ba31-a652f67afb7e")
    art_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Navigating to http://127.0.0.1:8008/ui ...")
        await page.goto("http://127.0.0.1:8008/ui", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Click Tab 2
        print("Clicking #inst-tab-btn-2 ...")
        btn = page.locator("#inst-tab-btn-2")
        await btn.click()
        
        # Wait for holdings to load
        await asyncio.sleep(4)

        tab2_snap = dest_dir / "ui_tab2_holdings_snap.png"
        await page.screenshot(path=str(tab2_snap), full_page=True)
        (art_dir / "ui_tab2_holdings_snap.png").write_bytes(tab2_snap.read_bytes())
        print(f"Captured Tab 2 screenshot: {tab2_snap}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
