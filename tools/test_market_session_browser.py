"""SIMULATION: verify compiled UI under source failure; no real broker/API traffic."""
import json
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    url = "http://127.0.0.1:4178"
    out = ROOT / "reports/market_truth" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_simulation")
    out.mkdir(parents=True, exist_ok=False)
    service = subprocess.Popen(["node", "node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", "4178", "--strictPort"],
                               cwd=ROOT / "dashboard/frontend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        time.sleep(2)
        assert service.poll() is None, "isolated preview did not start"
        print("SIMULATION preview started", flush=True)
        with sync_playwright() as p:
            print("SIMULATION browser launch", flush=True)
            browser = p.chromium.launch(headless=True, timeout=15000)
            for label, size in (("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})):
                page = browser.new_page(viewport=size)
                page.set_default_timeout(15000)
                print("SIMULATION page", label, flush=True)
                # HTTP route interception does not block WebSockets. Isolate both.
                page.route_web_socket("**/*", lambda socket: socket.close())
                # Static preview only. Fulfil every API request locally, including external hosts.
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(url) and "/api/" not in route.request.url
                           else route.fulfill(status=503, content_type="application/json", body='{"detail":"SIMULATION_SOURCE_DOWN"}'))
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.get_by_text("MARKET SESSION UNKNOWN", exact=True).first.wait_for(timeout=15000)
                text = page.locator("body").inner_text()
                (out / (label + "_body.txt")).write_text(text, encoding="utf-8")
                page.screenshot(path=str(out / (label + "_before_assert.png")))
                assert "MARKET SESSION OPEN" not in text
                assert "MARKET CLOSED" not in text
                page.evaluate("""() => {const b=document.createElement('div');b.textContent='SIMULATION · SOURCE DOWN · NOT CLOUD PROOF';b.style='position:fixed;top:0;z-index:999999;background:white;color:black';document.body.appendChild(b)}""")
                page.screenshot(path=str(out / (label + ".png")))
                page.close()
            browser.close()
        (out / "result.json").write_text(json.dumps({"label": "SIMULATION", "utc": datetime.now(timezone.utc).isoformat(),
            "desktop_unknown": True, "mobile_unknown": True, "production_acceptance": "UNVERIFIED"}, indent=2))
        print("SIMULATION desktop/mobile UNKNOWN assertions passed; artifacts:", out)
    finally:
        service.terminate()
        service.wait(timeout=10)


if __name__ == "__main__":
    main()
