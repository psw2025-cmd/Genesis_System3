import json
import subprocess
import time
import urllib.request
import websocket
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9227
USER_DATA = Path(r"C:\Genesis_System3_clean\reports\latest\chrome_audit_profile")
USER_DATA.mkdir(parents=True, exist_ok=True)

cmd = [
    CHROME_PATH,
    "--headless=new",
    f"--remote-debugging-port={CDP_PORT}",
    "--remote-allow-origins=*",
    f"--user-data-dir={USER_DATA}",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1920,1080",
]
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2.5)

req_id = 0

def cdp_send(ws, method, params=None):
    global req_id
    req_id += 1
    ws.send(json.dumps({"id": req_id, "method": method, "params": params or {}}))
    start = time.time()
    while time.time() - start < 10:
        try:
            raw = ws.recv()
            if not raw:
                continue
            msg = json.loads(raw)
            if msg.get("id") == req_id:
                return msg
        except Exception:
            pass
    return None

try:
    with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json") as r:
        tabs = json.loads(r.read().decode())
    target_tab = tabs[0]
    ws_url = target_tab["webSocketDebuggerUrl"]

    ws = websocket.create_connection(ws_url, timeout=10)

    # Enable console and network tracking
    cdp_send(ws, "Console.enable")
    cdp_send(ws, "Runtime.enable")
    cdp_send(ws, "Page.enable")

    # Navigate to http://127.0.0.1:8008/ui
    cdp_send(ws, "Page.navigate", {"url": "http://127.0.0.1:8008/ui"})
    time.sleep(3.0)

    eval_script = """
    (() => {
        const report = {
            title: document.title,
            brokenUnicode: [],
            tabsFound: [],
            allButtons: [],
            inputsFound: [],
            brokenHandlers: [],
            tickers: {},
            consoleErrors: []
        };

        // 1. Check Unicode
        const allTextNodes = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            const val = walker.currentNode.nodeValue;
            if (val && val.includes('?')) {
                const parent = walker.currentNode.parentElement;
                if (parent && (parent.className || parent.tagName)) {
                    report.brokenUnicode.push({
                        text: val.trim(),
                        parentTag: parent.tagName,
                        parentClass: parent.className
                    });
                }
            }
        }

        // 2. Check Tabs
        const tabBtns = document.querySelectorAll('[onclick*="switchInstTab"]');
        tabBtns.forEach((b, idx) => {
            report.tabsFound.push({
                text: b.innerText.trim(),
                onclick: b.getAttribute('onclick'),
                visible: b.offsetParent !== null
            });
        });

        // 3. Check All Buttons
        const buttons = document.querySelectorAll('button, .btn, [role="button"]');
        buttons.forEach(b => {
            report.allButtons.push({
                text: b.innerText.trim(),
                hasOnclick: b.hasAttribute('onclick'),
                onclick: b.getAttribute('onclick') || 'NONE',
                id: b.id,
                className: b.className
            });
        });

        // 4. Check Inputs
        const inputs = document.querySelectorAll('input');
        inputs.forEach(i => {
            report.inputsFound.push({
                id: i.id,
                placeholder: i.placeholder,
                hasOninput: i.hasAttribute('oninput')
            });
        });

        // 5. Check Tickers
        report.tickers = {
            topBarNifty: document.getElementById('vm-nifty')?.innerText || document.querySelector('.ticker-item')?.innerText,
            instTickerNifty: document.getElementById('inst-ticker-nifty')?.innerText,
            instTickerBank: document.getElementById('inst-ticker-bank')?.innerText,
            instTickerSensex: document.getElementById('inst-ticker-sensex')?.innerText,
            instTickerReliance: document.getElementById('inst-ticker-reliance')?.innerText
        };

        // 6. Test calling switchInstTab
        report.switchInstTabDefined = typeof window.switchInstTab === 'function';
        if (typeof window.switchInstTab === 'function') {
            [1, 2, 3, 4].forEach(i => {
                try {
                    window.switchInstTab(i);
                    const tabPane = document.getElementById('inst-tab-' + i);
                    report.tabsFound.push({
                        testTabId: i,
                        displayAfterSwitch: tabPane ? tabPane.style.display : 'MISSING'
                    });
                } catch(e) {
                    report.brokenHandlers.push({ fn: 'switchInstTab(' + i + ')', error: e.message });
                }
            });
        }

        return report;
    })()
    """

    res = cdp_send(ws, "Runtime.evaluate", {"expression": eval_script, "returnByValue": True})
    report = res.get("result", {}).get("value", {})
    print(json.dumps(report, indent=2))

    with open(r"C:\Genesis_System3_clean\reports\latest\ui_interactivity_audit.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

finally:
    proc.terminate()
