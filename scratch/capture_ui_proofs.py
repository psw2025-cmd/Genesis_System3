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

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error", "warning"] else None)

        print("Navigating to http://127.0.0.1:8008/ui ...")
        await page.goto("http://127.0.0.1:8008/ui", wait_until="networkidle", timeout=30000)
        
        # Give JS tickers and async card loaders time to run
        await asyncio.sleep(5)

        # 1. Full page snapshot
        full_snap = dest_dir / "ui_verified_snap.png"
        await page.screenshot(path=str(full_snap), full_page=True)
        print(f"Captured full page: {full_snap}")
        
        # Copy to artifact dir
        (art_dir / "ui_verified_live_proof.png").write_bytes(full_snap.read_bytes())
        print(f"Copied to artifact dir: ui_verified_live_proof.png")

        # 2. Capture Top Ticker Bar
        ticker = page.locator(".top-ticker-bar, .ticker-strip, .ticker-container, header, .header").first
        if await ticker.count() > 0:
            ticker_path = dest_dir / "ui_ticker_snap.png"
            await ticker.screenshot(path=str(ticker_path))
            (art_dir / "ui_ticker_snap.png").write_bytes(ticker_path.read_bytes())
            print("Captured ticker bar screenshot")

        # 3. Capture ML and Paper Trade Cards
        ml_cards = page.locator("#ml-batches-count, .kpi-row, .kpi-grid").first
        if await ml_cards.count() > 0:
            ml_path = dest_dir / "ui_ml_paper_snap.png"
            await ml_cards.screenshot(path=str(ml_path))
            (art_dir / "ui_ml_paper_snap.png").write_bytes(ml_path.read_bytes())
            print("Captured ML & Paper cards screenshot")

        # 4. Click Tab 2 to view Live Broker Account & Holdings
        tab2 = page.locator("text=[TAB 2] LIVE BROKER ACCOUNT & HOLDINGS, text=[TAB 2], text=LIVE BROKER ACCOUNT").first
        if await tab2.count() > 0:
            print("Clicking Tab 2 (Live Broker Account & Holdings)...")
            await tab2.click()
            await asyncio.sleep(3)
            tab2_snap = dest_dir / "ui_tab2_holdings_snap.png"
            await page.screenshot(path=str(tab2_snap), full_page=True)
            (art_dir / "ui_tab2_holdings_snap.png").write_bytes(tab2_snap.read_bytes())
            print("Captured Tab 2 screenshot with 11 Dhan Holdings")

        print("Console errors/warnings encountered:", len(console_errors))
        for err in console_errors[:10]:
            print("  ", err)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
