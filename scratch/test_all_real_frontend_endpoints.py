import requests
import json
import time

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"

endpoints = [
    "/api/accuracy_trend",
    "/api/agent/status",
    "/api/alerts/recent",
    "/api/approval/status",
    "/api/auto_gates",
    "/api/backtest/results",
    "/api/batch/chains",
    "/api/batch/market-data",
    "/api/batch/positions-holdings",
    "/api/broker/positions/live",
    "/api/broker/status",
    "/api/chain/NIFTY",
    "/api/deploy/info",
    "/api/expiries/NIFTY",
    "/api/forensic/report",
    "/api/health",
    "/api/instruments/health",
    "/api/learning/status",
    "/api/market/live_board",
    "/api/ml/performance",
    "/api/multibagger",
    "/api/multibagger/predictions",
    "/api/opportunity-gap",
    "/api/t1-pre-ignition",
    "/api/paper/account",
    "/api/trades/today",
    "/api/trades/history",
    "/api/pnl",
    "/api/positions",
    "/api/research/multibagger",
    "/api/scanner/moneycontrol_gainers",
    "/api/scanner/top_contract_gainers",
    "/api/signal/top",
    "/api/simulation/live/state",
    "/api/simulation/replay/lifecycle",
    "/api/simulation/replay/state",
    "/api/state",
    "/api/system/readiness",
    "/api/system_health",
    "/api/underlyings",
    "/api/validation/status"
]

results = {}
failing = []
ok_count = 0

print(f"=== TESTING {len(endpoints)} FRONTEND ENDPOINTS ON LIVE CLOUD RUN ===\n")

for ep in endpoints:
    url = f"{BASE_URL}{ep}"
    try:
        t0 = time.time()
        res = requests.get(url, timeout=12)
        elapsed = round(time.time() - t0, 3)
        code = res.status_code
        try:
            data = res.json()
            is_json = True
            keys = len(data) if isinstance(data, (dict, list)) else 1
            has_error = isinstance(data, dict) and data.get("status") == "error"
            err_msg = data.get("error", "") if has_error else ""
        except:
            is_json = False
            keys = len(res.text)
            has_error = code >= 400
            err_msg = f"Non-JSON response ({code})"

        status_tag = "OK" if code == 200 and not has_error else f"FAIL ({code})"
        if status_tag == "OK":
            ok_count += 1
        else:
            failing.append({"endpoint": ep, "code": code, "error": err_msg})
            
        print(f"[{status_tag}] {ep} -> HTTP {code} in {elapsed}s | {keys} keys/items {f'| Error: {err_msg}' if has_error else ''}")
        results[ep] = {"code": code, "elapsed": elapsed, "has_error": has_error, "error_msg": err_msg}
    except Exception as e:
        print(f"[CONN_ERR] {ep} -> {e}")
        failing.append({"endpoint": ep, "code": "ERR", "error": str(e)})

print(f"\nSummary: {ok_count}/{len(endpoints)} OK, {len(failing)} failing.")
if failing:
    print("\nFailing Endpoints:")
    for f in failing:
        print(f"  - {f['endpoint']}: {f['code']} - {f['error']}")

with open("scratch/frontend_endpoints_probe_report.json", "w") as fp:
    json.dump({"results": results, "failing": failing, "ok_count": ok_count, "total": len(endpoints)}, fp, indent=2)
