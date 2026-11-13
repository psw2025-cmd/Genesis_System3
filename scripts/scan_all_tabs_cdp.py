import base64
import json
import os
import subprocess
import time
import urllib.request
import websocket
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9226
USER_DATA = Path(r"C:\Genesis_System3_clean\reports\latest\chrome_profile_clean")
USER_DATA.mkdir(parents=True, exist_ok=True)
OUT_DIR = Path(r"C:\Genesis_System3_clean\reports\latest\ui_analysis")
SCREENSHOT_DIR = OUT_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

cmd = [
    CHROME_PATH,
    "--headless=new",
    f"--remote-debugging-port={CDP_PORT}",
    "--remote-allow-origins=*",
    f"--user-data-dir={USER_DATA}",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1920,1080",
    "--disable-background-networking",
]
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2.5)

def send_and_recv_id(ws, method, params, req_id):
    ws.send(json.dumps({"id": req_id, "method": method, "params": params or {}}))
    start = time.time()
    while time.time() - start < 15:
        try:
            raw = ws.recv()
            if not raw:
                continue
            msg = json.loads(raw)
            if msg.get("id") == req_id:
                return msg.get("result", {})
        except Exception:
            pass
    return {}

TABS = [
  'decision-intel', 'truth', 'genesis', 'e2e-proof', 'overview', 'sim-live',
  'options-intel', 'chain', 'signals', 'trade', 'paper', 'positions',
  'risk-scenarios', 'multibagger', 'prediction-audit', 'performance',
  'ml', 'data-integrity', 'broker', 'alerts', 'system', 'system-readiness', 'gates'
]

results = {}

try:
    req = urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new", method="PUT")
    with urllib.request.urlopen(req, timeout=10) as resp:
        tab_info = json.loads(resp.read().decode("utf-8"))
    ws_url = tab_info.get("webSocketDebuggerUrl")
    ws = websocket.create_connection(ws_url, timeout=15)

    send_and_recv_id(ws, "Page.enable", {}, 1)
    send_and_recv_id(ws, "Runtime.enable", {}, 2)
    send_and_recv_id(ws, "Network.enable", {}, 3)
    send_and_recv_id(ws, "Network.setCacheDisabled", {"cacheDisabled": True}, 4)

    for idx, tab in enumerate(TABS):
        print(f"[{idx+1}/{len(TABS)}] Checking tab: {tab}...")
        url = f"http://127.0.0.1:8000/ui/?tab={tab}"
        
        # Navigate
        send_and_recv_id(ws, "Page.navigate", {"url": url}, 10 + idx * 10)
        time.sleep(2.5)

        # Inspect DOM
        eval_res = send_and_recv_id(ws, "Runtime.evaluate", {
            "expression": """(() => {
                const pending = [];
                const partial = [];
                for (let el of document.querySelectorAll('*')) {
                    if (el.children.length === 0) {
                        const txt = (el.innerText || el.textContent || '').trim();
                        if (/PENDING/i.test(txt)) {
                            pending.push({ text: txt, tag: el.tagName, class: el.className, testId: el.getAttribute('data-testid') });
                        }
                        if (/PARTIAL/i.test(txt)) {
                            partial.push({ text: txt, tag: el.tagName, class: el.className, testId: el.getAttribute('data-testid') });
                        }
                    }
                }
                const bodyTxt = document.body.innerText || '';
                return {
                    pending: pending,
                    partial: partial,
                    hasError: bodyTxt.includes('Something went wrong') || bodyTxt.includes('Component Crash'),
                    snippet: bodyTxt.slice(0, 200)
                };
            })()""",
            "returnByValue": True
        }, 11 + idx * 10)

        info = eval_res.get("result", {}).get("value") or {}
        p_list = info.get("pending", [])
        part_list = info.get("partial", [])
        err = info.get("hasError", False)

        # Screenshot
        shot_res = send_and_recv_id(ws, "Page.captureScreenshot", {"format": "png"}, 12 + idx * 10)
        img_bytes = base64.b64decode(shot_res.get("data", ""))
        shot_path = SCREENSHOT_DIR / f"{idx+1:02d}_{tab}.png"
        if img_bytes:
            shot_path.write_bytes(img_bytes)

        results[tab] = {
            "pendingCount": len(p_list),
            "partialCount": len(part_list),
            "pending": p_list,
            "partial": part_list,
            "hasError": err,
            "screenshot": str(shot_path.name),
            "screenshotBytes": len(img_bytes)
        }
        print(f"    Pending: {len(p_list)}, Partial: {len(part_list)}, HasError: {err}, Shot: {len(img_bytes)}B")

    (OUT_DIR / "all_tabs_scan.json").write_text(json.dumps(results, indent=2))
    print("\n[SUCCESS] Wrote all_tabs_scan.json successfully for all 23 tabs.")
    ws.close()
finally:
    proc.terminate()
    proc.wait()
