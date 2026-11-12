"""Read-only cloud/browser observations; never certify readiness from HTTP success."""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import requests

ROOT = Path(__file__).resolve().parents[1]
URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"


def main():
    now = datetime.now(timezone.utc)
    out = ROOT / "reports/market_truth" / (now.strftime("%Y%m%dT%H%M%SZ") + "_cloud")
    out.mkdir(parents=True, exist_ok=False)
    result = {"utc": now.isoformat(), "url": URL, "verdict": "UNVERIFIED"}
    for route in ("/api/health", "/api/state"):
        try:
            response = requests.get(URL + route, timeout=20)
            item = {"http": response.status_code}
            if response.status_code == 200:
                body = response.json()
                # Only public operational fields; exclude account/credentials/identity.
                item["observed"] = {k: body.get(k) for k in ("timestamp_utc", "timestamp_ist", "mode", "market", "qc", "data_source")}
            result[route] = item
        except Exception as exc:
            result[route] = {"error_type": type(exc).__name__}
    total, used, free = shutil.disk_usage(ROOT)
    result["disk_used_pct"] = round(used / total * 100, 2)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for label, viewport in (("desktop", {"width": 1440, "height": 1000}),
                                    ("mobile", {"width": 390, "height": 844})):
                page = browser.new_page(viewport=viewport)
                errors = []
                page.on("pageerror", lambda e: errors.append(type(e).__name__))
                response = page.goto(URL + "/ui", wait_until="commit", timeout=30000)
                page.wait_for_selector("body", timeout=15000)
                page.wait_for_timeout(1500)
                # Add acquisition URL/time banner in browser; screenshot is unedited.
                stamp = datetime.now(timezone.utc).isoformat()
                page.evaluate("""text => { const banner=document.createElement('div');
                  banner.textContent=text; banner.style='position:fixed;top:0;left:0;z-index:2147483647;background:#fff;color:#000;font:12px monospace;padding:8px;max-width:100%;overflow-wrap:anywhere';
                  document.body.appendChild(banner); }""", URL + "/ui | " + stamp + " UTC | READ-ONLY OBSERVATION; PARITY UNVERIFIED")
                page.screenshot(path=str(out / (label + ".png")), full_page=False)
                result[label] = {"http": response.status if response else None, "screenshot": label + ".png",
                                 "js_error_count": len(errors), "parity": "UNVERIFIED", "utc": stamp}
                page.close()
            browser.close()
    except Exception as exc:
        result["browser"] = {"error_type": type(exc).__name__, "verified": False}
    (out / "observation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"artifact": str(out), "result": result}))


if __name__ == "__main__":
    main()
