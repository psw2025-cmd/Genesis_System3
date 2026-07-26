#!/usr/bin/env python3
"""Capture all System3 dashboard tabs with browser/network proof.

Read-only browser actions. No control buttons are clicked; only navigation tabs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

TABS = [
    "truth", "genesis", "e2e-proof", "overview", "sim-live", "chain", "signals",
    "trade", "paper", "positions", "performance", "ml", "broker", "alerts", "system", "gates",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_url(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}{parts.path}" + (f"?{parts.query}" if parts.query else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:3000")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()
    output = args.output.resolve()
    shots = output / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)

    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[dict[str, str]] = []
    responses: list[dict[str, object]] = []
    tab_results: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page = context.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("requestfailed", lambda request: failed_requests.append({
            "url": normalized_url(request.url),
            "failure": str(request.failure),
            "method": request.method,
        }))
        page.on("response", lambda response: responses.append({
            "url": normalized_url(response.url),
            "status": response.status,
            "method": response.request.method,
            "resource_type": response.request.resource_type,
        }))

        navigation = page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        page.wait_for_selector('[data-dashboard-navigation="sidebar"]', timeout=args.timeout_ms)
        page.wait_for_timeout(3000)
        initial_status = navigation.status if navigation else None
        title = page.title()

        for tab in TABS:
            started_errors = len(console_errors) + len(page_errors)
            started_responses = len(responses)
            selector = f'[data-dashboard-tab="{tab}"]'
            result: dict[str, object] = {"tab": tab, "selector": selector}
            try:
                page.locator(selector).click(timeout=10000)
                page.wait_for_timeout(1500)
                path = shots / f"{tab}.png"
                page.screenshot(path=str(path), full_page=False)
                tab_responses = responses[started_responses:]
                result.update({
                    "status": "PASS",
                    "screenshot": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "new_browser_errors": len(console_errors) + len(page_errors) - started_errors,
                    "new_http_responses": len(tab_responses),
                    "new_non_2xx_responses": sum(not 200 <= int(item["status"]) < 300 for item in tab_responses),
                    "non_2xx_responses": [item for item in tab_responses if not 200 <= int(item["status"]) < 300][:100],
                })
            except Exception as error:
                result.update({"status": "FAIL", "error": f"{type(error).__name__}: {error}"})
            tab_results.append(result)

        html_path = output / "dashboard_final.html"
        html_path.write_text(page.content(), encoding="utf-8")
        browser.close()

    passed = sum(result["status"] == "PASS" for result in tab_results)
    non_2xx = [item for item in responses if not 200 <= int(item["status"]) < 300]
    status_counts = {
        str(status): sum(int(item["status"]) == status for item in responses)
        for status in sorted({int(item["status"]) for item in responses})
    }
    non_2xx_url_counts: dict[str, int] = {}
    for item in non_2xx:
        key = f"{item['method']} {item['status']} {item['url']}"
        non_2xx_url_counts[key] = non_2xx_url_counts.get(key, 0) + 1
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "url": args.url,
        "initial_http_status": initial_status,
        "page_title": title,
        "tabs_expected": len(TABS),
        "tabs_captured": passed,
        "tabs_failed": len(TABS) - passed,
        "screenshot_bytes": sum(int(result.get("bytes", 0)) for result in tab_results),
        "console_error_count": len(console_errors),
        "page_error_count": len(page_errors),
        "failed_request_count": len(failed_requests),
        "http_response_count": len(responses),
        "http_non_2xx_count": len(non_2xx),
        "http_status_counts": status_counts,
        "non_2xx_url_counts": dict(sorted(non_2xx_url_counts.items())),
        "non_2xx_responses": non_2xx[:300],
        "tab_results": tab_results,
        "console_errors": console_errors[:300],
        "page_errors": page_errors[:300],
        "failed_requests": failed_requests[:300],
        "final_html": str(html_path),
        "final_html_sha256": sha256(html_path),
        "live_trading_enabled": False,
        "order_controls_clicked": 0,
        "order_placement_allowed": False,
    }
    summary_path = output / "dashboard_ui_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if passed == len(TABS) else 2


if __name__ == "__main__":
    raise SystemExit(main())
