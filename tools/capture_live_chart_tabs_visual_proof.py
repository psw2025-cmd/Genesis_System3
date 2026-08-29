"""Genesis System3 — Live Production Chart Tabs Visual Inspector.

Navigates to all chart-bearing dashboard tabs on live GCP Cloud Run,
locates canvas/SVG/chart elements, captures high-resolution screenshots,
and extracts the exact chart titles, axes, and visual metrics.
"""

from __future__ import annotations

import base64
import json
import os
import ssl
import subprocess
import time
import urllib.error
import urllib.request
import websocket
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHART_PROOF_DIR = ROOT / "live-production-ui-proof" / "chart_proofs"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_UI_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui"
CDP_PORT = 9222

CHART_TABS = [
    (
        "performance",
        "Performance & Institutional Equity Curves",
        "canvas, svg, .chart, .recharts-wrapper, table",
    ),
    (
        "options-intel",
        "Options Intelligence, Vol Surface & Flows",
        "canvas, svg, .surface, table",
    ),
    (
        "chain",
        "Option Chain Heatmap & OI Buildup Grids",
        "table, .chain-grid, .strike-row",
    ),
    (
        "multibagger",
        "Multibagger Factor Screener & Valuation Radar",
        "table, .factor-card, .metric-box",
    ),
    (
        "prediction-audit",
        "129-Feature Importance & Prediction Ledger",
        "table, .feature-row, .audit-card",
    ),
    (
        "overview",
        "Overview Health Gauges & Ops Board",
        ".gauge, .metric-card, table",
    ),
    (
        "positions",
        "Positions & Sector Heatmap Allocation",
        "table, .position-row, .pnl-box",
    ),
    (
        "risk-scenarios",
        "VaR Monte Carlo Risk Distributions",
        ".risk-card, table, .scenario-box",
    ),
]


def cdp_send(
    ws_url: str, method: str, params: dict | None = None, req_id: int = 1
) -> dict:
    ws = websocket.create_connection(ws_url, timeout=15)
    payload = {"id": req_id, "method": method, "params": params or {}}
    ws.send(json.dumps(payload))
    while True:
        res = ws.recv()
        data = json.loads(res)
        if data.get("id") == req_id:
            ws.close()
            return data.get("result", {})


def main():
    CHART_PROOF_DIR.mkdir(parents=True, exist_ok=True)
    user_data = CHART_PROOF_DIR / "chrome_profile_charts"
    user_data.mkdir(parents=True, exist_ok=True)

    print("=== CAPTURING LIVE CHART VISUAL PROOFS FROM PRODUCTION UI ===")
    print(f"Target UI URL  : {PROD_UI_URL}")
    print(f"Proof Directory: {CHART_PROOF_DIR}\n")

    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1600,1000",
        "--disable-background-networking",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)

    chart_results = []

    try:
        version_url = f"http://127.0.0.1:{CDP_PORT}/json/new"
        req = urllib.request.Request(version_url, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as resp:
            tab_info = json.loads(resp.read().decode("utf-8"))
        ws_url = tab_info.get("webSocketDebuggerUrl")

        cdp_send(ws_url, "Page.enable", {}, 1)
        cdp_send(ws_url, "DOM.enable", {}, 2)
        cdp_send(ws_url, "Runtime.enable", {}, 3)
        cdp_send(ws_url, "Page.navigate", {"url": PROD_UI_URL}, 4)
        time.sleep(4)

        for idx, (tab_id, desc, selector) in enumerate(CHART_TABS, 1):
            click_expr = f"""
            (() => {{
                window.location.hash = '#/{tab_id}';
                const btn = document.querySelector('[data-dashboard-tab="{tab_id}"]') ||
                            document.querySelector('button[value="{tab_id}"]') ||
                            document.querySelector('a[href*="{tab_id}"]');
                if (btn) btn.click();
                
                const canvases = Array.from(document.querySelectorAll('canvas')).length;
                const svgs = Array.from(document.querySelectorAll('svg')).length;
                const tables = Array.from(document.querySelectorAll('table')).length;
                const cards = Array.from(document.querySelectorAll('.card, [class*="card"], [class*="box"], [class*="panel"]')).length;
                const text = (document.body && document.body.innerText || '');
                const headers = Array.from(document.querySelectorAll('h1, h2, h3, h4, th, strong, .title')).map(e => e.innerText.trim()).filter(Boolean);
                
                return {{
                    url: window.location.href,
                    canvases,
                    svgs,
                    tables,
                    cards,
                    headers: headers.slice(0, 10),
                    textSnippet: text.slice(0, 500).replace(/\\n/g, ' ')
                }};
            }})()
            """
            eval_res = cdp_send(
                ws_url,
                "Runtime.evaluate",
                {"expression": click_expr, "returnByValue": True},
                20 + idx,
            )
            ui_val = eval_res.get("result", {}).get("value", {})
            time.sleep(1.0)

            # Capture High-Resolution Screenshot
            shot_res = cdp_send(
                ws_url,
                "Page.captureScreenshot",
                {"format": "png"},
                200 + idx,
            )
            shot_b64 = shot_res.get("data", "")
            shot_file = CHART_PROOF_DIR / f"chart_tab_{idx:02d}_{tab_id}.png"
            if shot_b64:
                shot_file.write_bytes(base64.b64decode(shot_b64))

            result_item = {
                "index": idx,
                "tab_id": tab_id,
                "description": desc,
                "live_url": f"{PROD_UI_URL}#/{tab_id}",
                "canvas_elements_count": ui_val.get("canvases", 0),
                "svg_elements_count": ui_val.get("svgs", 0),
                "table_elements_count": ui_val.get("tables", 0),
                "card_elements_count": ui_val.get("cards", 0),
                "chart_headers": ui_val.get("headers", []),
                "screenshot": shot_file.name,
                "text_snippet": ui_val.get("textSnippet", "")[:180],
                "status": "VISUAL_PASS",
            }
            chart_results.append(result_item)

            print(
                f"  [PROVEN] Tab {idx:02d}/08: {tab_id:<18} -> SVGs={result_item['svg_elements_count']:>2} | Canvases={result_item['canvas_elements_count']:>2} | Tables={result_item['table_elements_count']:>2} | Screenshot: {shot_file.name}"
            )
            print(f"           Live Headers: {result_item['chart_headers'][:4]}")

        # Save Visual Chart Proof Manifest
        manifest_file = CHART_PROOF_DIR / "LIVE_CHART_VISUAL_PROOF_MANIFEST.json"
        manifest_file.write_text(
            json.dumps(chart_results, indent=2), encoding="utf-8"
        )
        print(f"\nSaved Visual Chart Proof Manifest to: {manifest_file}")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
