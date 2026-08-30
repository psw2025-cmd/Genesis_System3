import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path(r"C:\Users\ADMIN\Genesis_System3\Genesis_System3\live-production-ui-proof\multi-validation")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"

VIEWPORTS = [
    {"name": "Mobile_Portrait", "width": 375, "height": 667},
    {"name": "Tablet_Portrait", "width": 768, "height": 1024},
    {"name": "Laptop_Standard", "width": 1280, "height": 800},
    {"name": "Desktop_FHD", "width": 1920, "height": 1080},
]

TABS_TO_AUDIT = [
    "decision-intel",
    "overview",
    "paper",
    "chain",
    "signals",
    "trade",
    "positions",
    "risk-scenarios",
    "ml",
    "broker",
    "truth",
    "gates"
]

ZOOM_LEVELS = [1.0, 1.25, 1.5]

async def run_multi_validation_matrix():
    summary_results = []
    print("================================================================")
    print("GENESIS SYSTEM3 ADVANCED UI/UX MULTI-VALIDATION MATRIX")
    print(f"Target URL: {BASE_URL}")
    print(f"Viewports: {len(VIEWPORTS)} | Tabs: {len(TABS_TO_AUDIT)} | Zooms: {len(ZOOM_LEVELS)}")
    print("================================================================\n")

    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            print(f"\n>>> TESTING VIEWPORT: {vp['name']} ({vp['width']}x{vp['height']})")
            context = await browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = await context.new_page()

            console_errors = []
            page_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            for tab in TABS_TO_AUDIT:
                target_url = f"{BASE_URL}/ui/?tab={tab}"
                try:
                    await page.goto(target_url, wait_until="networkidle", timeout=25000)
                    await page.wait_for_timeout(1500)

                    body_text = await page.inner_text("body")
                    error_present = "Something went wrong" in body_text or "ReferenceError" in body_text

                    # Test zoom simulation
                    for zoom in ZOOM_LEVELS:
                        await page.evaluate(f"document.body.style.zoom = '{zoom}'")
                        await page.wait_for_timeout(500)

                    # Reset zoom
                    await page.evaluate("document.body.style.zoom = '1.0'")

                    # Save proof screenshot for sample key tabs
                    shot_name = f"{vp['name']}_{tab}.png"
                    shot_path = OUT_DIR / shot_name
                    await page.screenshot(path=str(shot_path))

                    status = "PASS" if not error_present and len(page_errors) == 0 else "FAIL"
                    print(f"  [{status}] Tab: {tab:<15} | Crash: {error_present} | PageErrors: {len(page_errors)}")

                    summary_results.append({
                        "viewport": vp["name"],
                        "tab": tab,
                        "status": status,
                        "crash": error_present,
                        "page_errors": list(page_errors),
                        "console_errors_count": len(console_errors),
                        "screenshot": str(shot_path)
                    })

                except Exception as e:
                    print(f"  [FAIL] Tab: {tab:<15} | Error: {e}")
                    summary_results.append({
                        "viewport": vp["name"],
                        "tab": tab,
                        "status": "FAIL",
                        "error": str(e)
                    })

            await context.close()

        await browser.close()

    elapsed = time.time() - start_time
    total_tests = len(summary_results)
    passed_tests = sum(1 for r in summary_results if r.get("status") == "PASS")

    print("\n================================================================")
    print(f"MULTI-VALIDATION SUMMARY: {passed_tests}/{total_tests} PASSED ({passed_tests/total_tests*100:.1f}%) in {elapsed:.1f}s")
    print(f"Artifacts Directory: {OUT_DIR}")
    print("================================================================")

    out_json = OUT_DIR / "multi_validation_summary.json"
    with open(out_json, "w", encoding="utf-8") as fp:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "base_url": BASE_URL,
            "total": total_tests,
            "passed": passed_tests,
            "pass_rate_pct": round(passed_tests/total_tests*100, 2),
            "results": summary_results
        }, fp, indent=2)

if __name__ == "__main__":
    asyncio.run(run_multi_validation_matrix())
