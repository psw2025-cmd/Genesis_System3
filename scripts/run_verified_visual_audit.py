import base64
import json
import os
import subprocess
import time
import urllib.request
import websocket
from pathlib import Path

CDP_PORT = 9226
BASE_URL = "http://127.0.0.1:8000/ui"
ARTIFACT_DIR = Path(r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\3957d29d-e75a-4a9f-86fb-5d267e6799ee\screenshots")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = Path(r"C:\Genesis_System3_clean\reports\latest\ui_analysis")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TABS = [
  'decision-intel', 'truth', 'genesis', 'e2e-proof', 'overview', 'sim-live',
  'options-intel', 'chain', 'signals', 'trade', 'paper', 'positions',
  'risk-scenarios', 'multibagger', 'prediction-audit', 'performance',
  'ml', 'data-integrity', 'broker', 'alerts', 'system', 'system-readiness', 'gates'
]

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\tmp\cdp_audit_profile"
cmd = [
    chrome_path,
    "--headless=new",
    f"--remote-debugging-port={CDP_PORT}",
    "--disable-gpu",
    "--no-sandbox",
    f"--user-data-dir={user_data}",
    "--window-size=1920,1080"
]
print("Launching Headless Chrome on CDP port 9226...")
chrome_proc = subprocess.Popen(cmd)
time.sleep(3)

try:
    req = urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new", method="PUT")
    with urllib.request.urlopen(req, timeout=10) as resp:
        tab_info = json.loads(resp.read().decode("utf-8"))
    ws_url = tab_info.get("webSocketDebuggerUrl")
    ws = websocket.create_connection(ws_url, timeout=20)

    def cdp_eval(expr, req_id):
        ws.send(json.dumps({
            "id": req_id,
            "method": "Runtime.evaluate",
            "params": {"expression": expr, "returnByValue": True}
        }))
        start = time.time()
        while time.time() - start < 10:
            try:
                msg = json.loads(ws.recv())
                if msg.get("id") == req_id:
                    return msg.get("result", {}).get("result", {}).get("value")
            except Exception:
                pass
        return None

    def cdp_shot(req_id):
        ws.send(json.dumps({"id": req_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        start = time.time()
        while time.time() - start < 10:
            try:
                msg = json.loads(ws.recv())
                if msg.get("id") == req_id:
                    data = msg.get("result", {}).get("data", "")
                    if data:
                        return base64.b64decode(data)
            except Exception:
                pass
        return None

    ws.send(json.dumps({"id": 1, "method": "Page.enable", "params": {}}))
    time.sleep(0.5)
    ws.send(json.dumps({"id": 2, "method": "Runtime.enable", "params": {}}))
    time.sleep(0.5)

    results = []

    for idx, tab in enumerate(TABS):
        tab_url = f"{BASE_URL}/?tab={tab}"
        ws.send(json.dumps({"id": 100 + idx, "method": "Page.navigate", "params": {"url": tab_url}}))
        # Wait 4 seconds for all React hooks and background REST calls to settle
        time.sleep(4.0)

        eval_expr = """(() => {
            const pending = [];
            const partial = [];
            for (let el of document.querySelectorAll('*')) {
                if (el.children.length === 0) {
                    const txt = (el.innerText || el.textContent || '').trim();
                    if (/PENDING/i.test(txt)) {
                        pending.push(txt);
                    }
                    if (/PARTIAL/i.test(txt)) {
                        partial.push(txt);
                    }
                }
            }
            const body = document.body.innerText || '';
            return {
                title: document.title,
                tab: window.location.search,
                pending: pending,
                partial: partial,
                hasError: body.includes('Something went wrong') || body.includes('crash'),
                bodyPreview: body.slice(0, 150).replace(/\\s+/g, ' ')
            };
        })()"""

        data = cdp_eval(eval_expr, 200 + idx) or {}
        shot_bytes = cdp_shot(300 + idx)

        shot_file = f"{idx+1:02d}_{tab}.png"
        if shot_bytes:
            (ARTIFACT_DIR / shot_file).write_bytes(shot_bytes)
            (REPORTS_DIR / shot_file).write_bytes(shot_bytes)

        tab_result = {
            "index": idx + 1,
            "tab": tab,
            "url": tab_url,
            "pendingCount": len(data.get("pending", [])),
            "pendingItems": data.get("pending", []),
            "partialCount": len(data.get("partial", [])),
            "partialItems": data.get("partial", []),
            "hasError": data.get("hasError", False),
            "bodyPreview": data.get("bodyPreview", ""),
            "screenshot": shot_file,
            "screenshotBytes": len(shot_bytes) if shot_bytes else 0
        }
        results.append(tab_result)
        print(f"[{idx+1:02d}/23] {tab:18} | Pending: {tab_result['pendingCount']:2} | Partial: {tab_result['partialCount']:2} | Error: {tab_result['hasError']} | Shot: {tab_result['screenshotBytes']}B")

    ws.close()

    report_path = REPORTS_DIR / "visual_verification_report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\n[DONE] Saved visual verification report with {len(results)} tabs to {report_path}")

finally:
    chrome_proc.terminate()
    print("Chrome headless process terminated.")
