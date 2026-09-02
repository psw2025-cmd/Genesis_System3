"""Genesis System3 — 22 Canonical Tabs Local Audit & Telemetry Parity."""

import datetime
import json
from pathlib import Path
import urllib.request
import urllib.error

CANONICAL_TABS = [
    "decision-intel", "truth", "genesis", "e2e-proof", "overview",
    "sim-live", "options-intel", "chain", "signals", "trade",
    "paper", "positions", "risk-scenarios", "multibagger", "prediction-audit",
    "performance", "ml", "data-integrity", "broker", "alerts",
    "system", "gates"
]

TAB_API_MAP = {
    "decision-intel": "/api/state",
    "truth": "/api/broker/status",
    "genesis": "/api/health",
    "e2e-proof": "/api/deploy/info",
    "overview": "/api/state",
    "sim-live": "/api/chain/NIFTY",
    "options-intel": "/api/chain/BANKNIFTY",
    "chain": "/api/chain/NIFTY",
    "signals": "/api/state",
    "trade": "/api/state",
    "paper": "/api/paper/account",
    "positions": "/api/state",
    "risk-scenarios": "/api/state",
    "multibagger": "/api/state",
    "prediction-audit": "/api/state",
    "performance": "/api/health",
    "ml": "/api/state",
    "data-integrity": "/api/health",
    "broker": "/api/broker/status",
    "alerts": "/api/state",
    "system": "/api/agent-status",
    "gates": "/api/auto_gates",
}

def audit_22_tabs():
    base_url = "http://127.0.0.1:8000"
    now_ist = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    now_utc = datetime.datetime.utcnow().isoformat() + "Z"

    print("=" * 80)
    print("   GENESIS SYSTEM3 — 22 CANONICAL TABS LOCAL AUDIT & API PARITY")
    print(f"   Time: {now_ist} | URL: {base_url}/ui")
    print("=" * 80)

    results = {}
    passed = 0

    for tab in CANONICAL_TABS:
        api_path = TAB_API_MAP.get(tab, "/api/state")
        url = f"{base_url}{api_path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Genesis22TabAudit/1.0"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                status = resp.status
                ok = status == 200
                if ok:
                    passed += 1
                results[tab] = {
                    "tab": tab,
                    "ui_path": f"/ui/{tab}",
                    "bound_api": api_path,
                    "http_status": status,
                    "verdict": "PASS" if ok else "FAIL",
                }
                print(f"   [{'PASS' if ok else 'FAIL'}] Tab: {tab:<18} -> API: {api_path:<24} (HTTP {status})")
        except Exception as e:
            results[tab] = {
                "tab": tab,
                "ui_path": f"/ui/{tab}",
                "bound_api": api_path,
                "http_status": 0,
                "verdict": "FAIL",
                "error": str(e),
            }
            print(f"   [FAIL] Tab: {tab:<18} -> API: {api_path:<24} (Error: {e})")

    report = {
        "timestamp_ist": now_ist,
        "timestamp_utc": now_utc,
        "total_tabs": len(CANONICAL_TABS),
        "passed_tabs": passed,
        "verdict": "ALL_22_TABS_PASS" if passed == len(CANONICAL_TABS) else "DEGRADED",
        "tab_audit": results,
    }

    out_file = Path(r"C:\Genesis_System3_Runtime\state\22_tabs_audit_report.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print(f"   RESULT: {passed}/{len(CANONICAL_TABS)} Canonical Tabs Passed Local API Parity")
    print(f"   Saved Report : {out_file}")
    print("=" * 80)

if __name__ == "__main__":
    audit_22_tabs()
