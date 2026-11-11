import asyncio
import os
import sys
import pytest
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPORTS_DIR = os.path.abspath("reports")
SCREENSHOT_PATH = os.path.join(REPORTS_DIR, "ui_e2e_verified.png")
LATEST_SNAP_PATH = os.path.join(REPORTS_DIR, "latest", "ui_verified_snap.png")


@pytest.mark.asyncio
async def test_ui_production_flow():
    os.makedirs(REPORTS_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # Step 1: Navigate to http://127.0.0.1:8008/ui
        print("\n[Step 1] Navigating to http://127.0.0.1:8008/ui...")
        response = await page.goto("http://127.0.0.1:8008/ui", wait_until="domcontentloaded", timeout=30000)

        # Step 2: Assert page loads with HTTP 200
        print("[Step 2] Asserting HTTP 200 OK...")
        assert response is not None, "Response was None"
        assert response.status == 200, f"Expected 200 OK, got {response.status}"
        print(f" -> Confirmed HTTP {response.status} OK")

        # Step 3: Assert Top Ticker Bar exists and displays numerical values
        print("[Step 3] Asserting Top Ticker Bar and numerical prices...")
        await page.wait_for_selector(".ticker-overview-bar", timeout=10000)
        nifty_elem = await page.wait_for_selector("#t-nifty-val", timeout=10000)

        for _ in range(20):
            nifty_text = (await nifty_elem.inner_text()).strip()
            if nifty_text and nifty_text != "—":
                break
            await asyncio.sleep(0.5)

        safe_nifty = nifty_text.encode("ascii", "replace").decode("ascii")
        print(f" -> Ticker NIFTY 50 Value: {safe_nifty}")
        assert nifty_text != "—", "Ticker NIFTY value is still placeholder '—'"

        # Step 4: Assert Trading Operations Console container exists
        print("[Step 4] Asserting Trading Operations Console container exists...")
        console_elem = await page.wait_for_selector("#trading-operations-console", timeout=10000)
        assert console_elem is not None, "Trading Operations Console element #trading-operations-console not found"
        print(" -> Found #trading-operations-console")

        # Step 5: Assert route list shows [POST] and [GET] tags
        print("[Step 5] Asserting Route List shows [POST] and [GET] tags...")
        await page.wait_for_selector("#routes-container a.route-item", timeout=15000)

        route_text = await page.inner_text("#routes-container")
        assert "[GET]" in route_text, "Expected [GET] tags in routes list"
        assert "[POST]" in route_text, "Expected [POST] tags in routes list"
        print(" -> Confirmed both [GET] and [POST] route tags are rendered in UI")

        # Step 6: Open Live Order Modal, submit, assert Safety Gate toast
        print("[Step 6] Testing Live Order Modal & Safety Gate Enforcement...")
        btn_open = await page.wait_for_selector("#btn-open-live-order", timeout=5000)
        await btn_open.click()

        modal = await page.wait_for_selector("#live-order-modal", timeout=5000)
        is_visible = await modal.is_visible()
        assert is_visible, "Live order modal did not open on button click"
        print(" -> Live Order Modal opened successfully")

        # Fill order form
        await page.fill("#order-symbol", "NIFTY")
        await page.fill("#order-qty", "50")
        await page.select_option("#order-side", "BUY")
        await page.select_option("#order-pricetype", "MARKET")
        await page.select_option("#order-product", "MIS")

        # Click submit
        btn_submit = await page.wait_for_selector("#btn-submit-order", timeout=5000)
        await btn_submit.click()
        print(" -> Clicked SUBMIT ORDER button")

        # Assert toast appears with Safety Gate message
        toast = await page.wait_for_selector("#order-toast", timeout=10000)
        toast_text = (await toast.inner_text()).strip()
        safe_toast = toast_text.encode("ascii", "replace").decode("ascii")
        print(f" -> Toast observed: '{safe_toast}'")
        assert "Order Blocked by Backend Safety Gate" in toast_text or "Live trading is locked" in toast_text, \
            f"Expected safety block message, got: {toast_text}"
        print(" -> Backend Safety Gate assertion PASSED!")

        # Step 7: Take full-page screenshot
        print(f"[Step 7] Capturing full-page screenshot to {SCREENSHOT_PATH} and {LATEST_SNAP_PATH}...")
        os.makedirs(os.path.dirname(LATEST_SNAP_PATH), exist_ok=True)
        await page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        await page.screenshot(path=LATEST_SNAP_PATH, full_page=True)
        assert os.path.exists(SCREENSHOT_PATH), f"Screenshot was not saved at {SCREENSHOT_PATH}"
        assert os.path.exists(LATEST_SNAP_PATH), f"Screenshot was not saved at {LATEST_SNAP_PATH}"
        print(f" -> Screenshots saved ({os.path.getsize(SCREENSHOT_PATH)} bytes)")

        # Step 8: Verify GET /api/v1/placeorder returns HTTP 200 (not 405 Method Not Allowed)
        print("[Step 8] Verifying GET /api/v1/placeorder returns HTTP 200 OK...")
        resp_po = await page.goto("http://127.0.0.1:8008/api/v1/placeorder", wait_until="domcontentloaded")
        assert resp_po is not None and resp_po.status == 200, f"Expected 200 on GET /api/v1/placeorder, got {resp_po.status if resp_po else None}"
        po_text = await page.inner_text("body")
        assert "Method Not Allowed" not in po_text, "GET /api/v1/placeorder still returned Method Not Allowed"
        assert "ONLINE_SAFETY_LOCKED" in po_text, "Expected ONLINE_SAFETY_LOCKED in GET /api/v1/placeorder response"
        print(" -> Confirmed GET /api/v1/placeorder returns HTTP 200 OK with ONLINE_SAFETY_LOCKED")

        await browser.close()
        print("\n=== ALL PLAYWRIGHT E2E ASSERTIONS 100% PASSED ===")


if __name__ == "__main__":
    asyncio.run(test_ui_production_flow())
