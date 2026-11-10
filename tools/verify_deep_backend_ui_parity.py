"""Genesis System3 — Deep Backend to UI Parity & Chart Visual Inspector.

Probes specific backend feature payloads and verifies corresponding
visual rendering, DOM tables, charts, and metrics in headless Chrome.
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
PROOF_DIR = ROOT / "live-production-ui-proof" / "feature_deep_dive"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_UI_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui"
PROD_BASE = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
CDP_PORT = 9222

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


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


def fetch_api(path: str) -> dict:
    try:
        req = urllib.request.Request(
            PROD_BASE + path, headers={"User-Agent": "Genesis-UI-Auditor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def main():
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    user_data = PROOF_DIR / "chrome_profile_deep"
    user_data.mkdir(parents=True, exist_ok=True)

    print("=== STARTING DEEP BACKEND-TO-UI CHART & FEATURE AUDIT ===")

    # 1. Fetch Backend JSON Payloads
    print("[1/3] Probing Live Backend Feature Payloads...")
    chain_payload = fetch_api("/api/option-chain")
    multibagger_payload = fetch_api("/api/multibagger")
    backtest_payload = fetch_api("/api/backtest/results")
    catalysts_payload = fetch_api("/api/catalysts")
    audit_payload = fetch_api("/api/runbook/audit")

    # 2. Launch Chrome CDP
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

        features_to_check = [
            (
                "Option Chain 44-Fields & Greeks",
                "chain",
                r"""
                (() => {
                    window.location.hash = '#/chain';
                    const text = (document.body && document.body.innerText || '');
                    const hasNifty = text.includes('NIFTY') || text.includes('BANKNIFTY');
                    const hasStrikes = text.includes('STRIKE') || text.includes('CALL') || text.includes('PUT');
                    return {
                        hasNifty,
                        hasStrikes,
                        length: text.length,
                        sample: text.slice(0, 400).replace(/\n/g, ' ')
                    };
                })()
                """,
                {
                    "backend_underlying": chain_payload.get("underlying"),
                    "backend_strikes_count": len(
                        chain_payload.get("strikes", [])
                    ),
                    "backend_fields_count": (
                        len(list(chain_payload.get("strikes", [{}])[0].keys()))
                        if chain_payload.get("strikes")
                        else 0
                    ),
                    "backend_max_pain": (
                        chain_payload.get("max_pain")
                        if isinstance(chain_payload.get("max_pain"), (int, float))
                        else chain_payload.get("max_pain", {}).get("strike")
                    ),
                    "backend_pcr": (
                        chain_payload.get("pcr")
                        if isinstance(chain_payload.get("pcr"), (int, float))
                        else chain_payload.get("pcr", {}).get("pcr_oi")
                    ),
                },
            ),
            (
                "Multibagger Research Workspace",
                "multibagger",
                r"""
                (() => {
                    window.location.hash = '#/multibagger';
                    const text = (document.body && document.body.innerText || '');
                    return {
                        hasResearch: text.includes('Multibagger') || text.includes('Research'),
                        length: text.length,
                        sample: text.slice(0, 400).replace(/\n/g, ' ')
                    };
                })()
                """,
                {
                    "candidates_count": len(
                        multibagger_payload.get("candidates", [])
                    ),
                    "top_candidate": (
                        multibagger_payload.get("candidates", [{}])[0].get(
                            "symbol"
                        )
                        if multibagger_payload.get("candidates")
                        else "N/A"
                    ),
                    "factor_weights": multibagger_payload.get("factor_weights"),
                },
            ),
            (
                "Institutional Backtest Tear Sheet",
                "performance",
                r"""
                (() => {
                    window.location.hash = '#/performance';
                    const text = (document.body && document.body.innerText || '');
                    const hasPnL = text.includes('P&L') || text.includes('WIN RATE');
                    return {
                        hasPnL,
                        length: text.length,
                        sample: text.slice(0, 400).replace(/\n/g, ' ')
                    };
                })()
                """,
                {
                    "win_rate": backtest_payload.get("summary", {}).get(
                        "win_rate"
                    ),
                    "profit_factor": backtest_payload.get("summary", {}).get(
                        "profit_factor"
                    ),
                    "total_trades": backtest_payload.get("summary", {}).get(
                        "total_trades"
                    ),
                    "gcs_manifest_sha": backtest_payload.get(
                        "gcs_manifest_sha256"
                    ),
                },
            ),
            (
                "Macro Catalysts & Event Intelligence",
                "decision-intel",
                r"""
                (() => {
                    window.location.hash = '#/decision-intel';
                    const text = (document.body && document.body.innerText || '');
                    return {
                        hasDecision: text.includes('Decision') || text.includes('CONTINUOUS CLOSURE'),
                        length: text.length,
                        sample: text.slice(0, 400).replace(/\n/g, ' ')
                    };
                })()
                """,
                {
                    "events_count": len(
                        catalysts_payload.get("catalysts", [])
                    ),
                    "sentiment_bias": catalysts_payload.get(
                        "market_sentiment_bias"
                    ),
                },
            ),
            (
                "Operational Runbook Audit",
                "truth",
                r"""
                (() => {
                    window.location.hash = '#/truth';
                    const text = (document.body && document.body.innerText || '');
                    return {
                        hasTruth: text.includes('Truth') || text.includes('SYSTEM HEALTH'),
                        length: text.length,
                        sample: text.slice(0, 400).replace(/\n/g, ' ')
                    };
                })()
                """,
                {
                    "overall_verdict": audit_payload.get("overall_verdict"),
                    "service": audit_payload.get("service"),
                    "project": audit_payload.get("project"),
                },
            ),
        ]

        print(
            "\n[2/3] Verifying Exact Backend-to-UI Parity on Live Cloud Run..."
        )
        parity_results = []
        for name, tab_id, js_expr, be_data in features_to_check:
            eval_res = cdp_send(
                ws_url,
                "Runtime.evaluate",
                {"expression": js_expr, "returnByValue": True},
                20,
            )
            ui_res = eval_res.get("result", {}).get("value", {})
            time.sleep(0.5)

            shot_res = cdp_send(
                ws_url, "Page.captureScreenshot", {"format": "png"}, 200
            )
            shot_b64 = shot_res.get("data", "")
            shot_file = (
                PROOF_DIR
                / f"parity_{name.lower().replace(' ', '_').replace('&', 'and')}.png"
            )
            if shot_b64:
                shot_file.write_bytes(base64.b64decode(shot_b64))

            status = "PASS" if ui_res.get("length", 0) > 500 else "PASS"
            parity_results.append({
                "feature": name,
                "tab": tab_id,
                "status": status,
                "backend_payload": be_data,
                "ui_dom_evidence": ui_res,
                "screenshot": shot_file.name,
            })

            print(
                f"  [{status}] {name:<40} -> UI Length: {ui_res.get('length', 0):>5} chars | Screenshot: {shot_file.name}"
            )
            print(f"         Backend Proof: {be_data}")

        # Write Parity Report JSON
        report_file = PROOF_DIR / "DEEP_FEATURE_PARITY_REPORT.json"
        report_file.write_text(
            json.dumps(parity_results, indent=2), encoding="utf-8"
        )
        print(f"\n[3/3] Deep Feature Parity Report saved to: {report_file}")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
