import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def verify_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Navigate to UI
        await page.goto("http://127.0.0.1:8008/ui", wait_until="networkidle")
        await asyncio.sleep(2.5)  # allow initial polling to complete
        
        # Evaluate if 23810.85 (live NIFTY quote) is rendered
        eval_result = await page.evaluate("document.body.innerText.includes('23810.85')")
        print(f"EVAL_RESULT: {eval_result}")
        
        # Capture screenshot
        out_path = Path(r"C:\Genesis_System3_clean\ui_final.png")
        await page.screenshot(path=str(out_path), full_page=True)
        print(f"SCREENSHOT_PATH: {out_path}")
        print(f"FILE_SIZE_BYTES: {out_path.stat().st_size}")
        
        # Also copy to reports/latest/ui_verified_snap.png for contract check
        latest_path = Path(r"C:\Genesis_System3_clean\reports\latest\ui_verified_snap.png")
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(latest_path), full_page=True)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_ui())
