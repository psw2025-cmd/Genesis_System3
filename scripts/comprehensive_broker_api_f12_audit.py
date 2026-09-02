"""Genesis System3 — Complete All-API & Broker F12 DevTools Diagnostic Engine."""

import datetime
import json
import os
import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient
import urllib.request
import urllib.error

from pathlib import Path
import sys
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Set local laptop environment
os.environ["INDEX_CHAIN_MICRO_STREAM"] = "0"
os.environ["MARKET_TOP_MICRO_STREAM"] = "0"

from dashboard.backend.app import app
from core.brokers.dhan.dhan_readonly import DhanReadOnly
from core.utils.env_loader import get_dhan_credentials

client = TestClient(app)
base_url = "http://127.0.0.1:8000"

def audit_broker_deep():
    print("\n" + "=" * 90)
    print("   GENESIS SYSTEM3 — SECTION 1: DEEP BROKER & VAULT DIAGNOSTIC")
    print("=" * 90)

    broker_routes = [
        "/api/broker/status",
        "/api/broker/truth",
        "/api/broker/positions",
        "/api/broker/holdings",
        "/api/broker/margins",
        "/api/broker/funds",
        "/api/broker/orders",
        "/api/broker/trades",
        "/api/batch/positions-holdings",
        "/api/market/live_board",
    ]

    broker_results = {}
    for r in broker_routes:
        start = time.time()
        res = client.get(r)
        latency = round((time.time() - start) * 1000, 2)
        status_code = res.status_code
        try:
            data = res.json()
        except Exception:
            data = res.text[:200]

        # Security check: verify no secrets or tokens in plain text
        secret_leak = False
        data_str = json.dumps(data) if isinstance(data, dict) else str(data)
        if "access_token" in data_str and len(str(data.get("access_token", ""))) > 50:
            secret_leak = True

        broker_results[r] = {
            "status_code": status_code,
            "latency_ms": latency,
            "secret_leak": secret_leak,
            "headers": dict(res.headers),
            "payload_preview": data if isinstance(data, dict) else str(data)[:200],
        }

        verdict = "PASS" if status_code == 200 and not secret_leak else "FAIL"
        print(f"   [{verdict}] Route: {r:<30} | HTTP {status_code:<3} | Latency: {latency:>6.2f}ms | Leak: {secret_leak}")

    # Direct Dhan Client Inspection
    print("\n   [*] Direct Broker SDK Client Status:")
    dhan = DhanReadOnly()
    creds = get_dhan_credentials()
    b_status = dhan.get_status()
    print(f"       Broker Name       : {b_status.get('broker')}")
    print(f"       Connected         : {b_status.get('connected')}")
    print(f"       Client ID Present : {b_status.get('client_id_present')}")
    print(f"       Token Present     : {b_status.get('access_token_present')}")
    print(f"       Vault Type        : {b_status.get('vault_type')}")
    print(f"       Vault Provenance  : {b_status.get('vault_provenance')}")
    print(f"       Rotation Authority: {b_status.get('rotation_authority')}")
    print(f"       Read-Only Mode    : {b_status.get('mode')} (Order Placement Allowed: {b_status.get('order_placement_allowed')})")

    return broker_results, b_status

def audit_all_api_routes():
    print("\n" + "=" * 90)
    print("   GENESIS SYSTEM3 — SECTION 2: COMPLETE FASTAPI ROUTES F12 AUDIT")
    print("=" * 90)

    # Discover all registered GET endpoints
    all_routes = []
    for route in app.routes:
        if hasattr(route, "methods") and "GET" in route.methods:
            path = route.path
            # Exclude websocket and path parameter wildcard routes
            if not path.startswith("/ws") and "{" not in path:
                all_routes.append(path)

    all_routes = sorted(list(set(all_routes)))
    print(f"   Total Distinct Static GET Routes Discovered: {len(all_routes)}")

    api_results = {}
    passed = 0
    failed = 0

    for path in all_routes:
        start = time.time()
        res = client.get(path)
        latency = round((time.time() - start) * 1000, 2)
        status_code = res.status_code
        content_type = res.headers.get("content-type", "")

        ok = status_code in (200, 204)
        if ok:
            passed += 1
        else:
            failed += 1

        try:
            preview = res.json()
        except Exception:
            preview = res.text[:100]

        api_results[path] = {
            "path": path,
            "status_code": status_code,
            "content_type": content_type,
            "latency_ms": latency,
            "verdict": "PASS" if ok else "FAIL",
            "content_length": len(res.content),
        }

        verdict_str = "PASS" if ok else "FAIL"
        print(f"   [{verdict_str}] {path:<40} | HTTP {status_code:<3} | {latency:>6.2f}ms | {content_type.split(';')[0]}")

    print("\n" + "=" * 90)
    print(f"   ALL-API F12 AUDIT SUMMARY: {passed} PASSED | {failed} FAILED (Total: {len(all_routes)})")
    print("=" * 90)

    return api_results, passed, failed

def main():
    now_ist = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    now_utc = datetime.datetime.utcnow().isoformat() + "Z"

    broker_results, b_status = audit_broker_deep()
    api_results, passed, failed = audit_all_api_routes()

    full_report = {
        "timestamp_ist": now_ist,
        "timestamp_utc": now_utc,
        "runtime_authority": "LOCAL_LAPTOP",
        "backend_url": base_url,
        "broker_audit": {
            "status": b_status,
            "endpoints": broker_results,
        },
        "all_api_audit": {
            "total_endpoints": len(api_results),
            "passed": passed,
            "failed": failed,
            "routes": api_results,
        }
    }

    # Save reports
    out1 = Path(r"C:\Genesis_System3_Runtime\state\broker_and_all_api_f12_audit.json")
    out1.parent.mkdir(parents=True, exist_ok=True)
    out1.write_text(json.dumps(full_report, indent=2), encoding="utf-8")

    out2 = Path(r"C:\Temp\broker_and_all_api_f12_audit.json")
    out2.write_text(json.dumps(full_report, indent=2), encoding="utf-8")

    print(f"\n   [OK] Reports saved to:")
    print(f"        -> {out1}")
    print(f"        -> {out2}\n")

if __name__ == "__main__":
    main()
