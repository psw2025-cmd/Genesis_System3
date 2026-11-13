import asyncio
import json
from playwright.async_api import async_playwright

TABS = ["ml", "prediction-audit", "system-readiness", "truth", "genesis"]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        results = {}
        for tab in TABS:
            url = f"https://genesis-system3-web-802404398783.asia-south1.run.app/ui?tab={tab}"
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            # Extract header and status bar
            header_text = await page.locator(".top-bar, header, nav, #header").all_inner_texts() if await page.locator(".top-bar, header, nav, #header").count() > 0 else []
            body_text = await page.evaluate("() => document.body.innerText")
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            
            # Find key phrases
            relevant_lines = [l for l in lines if any(k in l.lower() for k in ["serving:", "sha", "ready_for_live", "gate", "block", "lifecycle", "rho", "pass", "collecting"])]
            results[tab] = {
                "header": header_text,
                "first_few": lines[:10],
                "relevant": relevant_lines[:25]
            }
            print(f"=== TAB: {tab} ===")
            for r in relevant_lines[:15]:
                print(f"  {r}")
                
        await browser.close()
        with open("reports/latest/live_verified/dom_inspection.json", "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
