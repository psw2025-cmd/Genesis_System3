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
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)

        print("Navigating to http://127.0.0.1:8008/ui ...")
        await page.goto("http://127.0.0.1:8008/ui", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # 1. Capture Tab 1 (Candlestick Canvas with Volume, EMA 20, VWAP)
        tab1_snap = dest_dir / "proof_ui_tab1_candlestick_ema_vwap.png"
        await page.screenshot(path=str(tab1_snap), full_page=True)
        (art_dir / "proof_ui_tab1_candlestick_ema_vwap.png").write_bytes(tab1_snap.read_bytes())
        print(f"Captured Tab 1: {tab1_snap}")

        # 2. Capture Options Intelligence card
        opt_card = page.locator("#options-intel-card-title").locator("..").locator("..").first
        if await opt_card.count() > 0:
            opt_snap = dest_dir / "proof_ui_options_greeks.png"
            await opt_card.screenshot(path=str(opt_snap))
            (art_dir / "proof_ui_options_greeks.png").write_bytes(opt_snap.read_bytes())
            print(f"Captured Options Greeks Card: {opt_snap}")

        # 3. Click Tab 3 (Quantitative Prediction & Micro-Reasoning)
        print("Clicking Tab 3 ...")
        tab3_btn = page.locator("#inst-tab-btn-3")
        await tab3_btn.click()
        await asyncio.sleep(2)
        
        # Select NIFTY to test dynamic feature weights update
        sel = page.locator("#reasoning-symbol-select")
        if await sel.count() > 0:
            await sel.select_option("NIFTY")
            await asyncio.sleep(1)

        tab3_snap = dest_dir / "proof_ui_tab3_quant_feature_chart.png"
        await page.screenshot(path=str(tab3_snap), full_page=True)
        (art_dir / "proof_ui_tab3_quant_feature_chart.png").write_bytes(tab3_snap.read_bytes())
        print(f"Captured Tab 3: {tab3_snap}")

        # 4. Click Tab 4 (Autonomous Agent Sandbox Logs)
        print("Clicking Tab 4 ...")
        tab4_btn = page.locator("#inst-tab-btn-4")
        await tab4_btn.click()
        await asyncio.sleep(2)

        tab4_snap = dest_dir / "proof_ui_tab4_agent_logs.png"
        await page.screenshot(path=str(tab4_snap), full_page=True)
        (art_dir / "proof_ui_tab4_agent_logs.png").write_bytes(tab4_snap.read_bytes())
        print(f"Captured Tab 4: {tab4_snap}")

        print("Total Console Errors encountered:", len(console_errors))
        for err in console_errors:
            print("  ", err)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
