import requests
import json
import time

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"

print(f"--- PROBING LIVE CLOUD RUN AT {BASE_URL} ---")

endpoints = [
    ("/api/health", "Health"),
    ("/api/broker/status", "Broker Status"),
    ("/api/opportunity-gap", "Gap Up Runners Engine"),
    ("/api/t1-pre-ignition", "T1 Pre-Ignition Engine"),
    ("/api/multibagger/predictions", "Multibagger Predictions"),
    ("/api/paper/account", "Paper Account Margin/Balance"),
    ("/api/trades/today", "Trades Today (Rolling Dynamic Session)"),
    ("/api/trades/history", "Trades History"),
    ("/api/state", "System3 State"),
    ("/api/qc", "Quality Control"),
    ("/ui/", "Dashboard UI HTML"),
]

results = {}

for ep, name in endpoints:
    url = f"{BASE_URL}{ep}"
    try:
        t0 = time.time()
        res = requests.get(url, timeout=15)
        elapsed = round(time.time() - t0, 3)
        status = res.status_code
        content_type = res.headers.get("Content-Type", "")
        
        preview = ""
        data = None
        if "json" in content_type:
            try:
                data = res.json()
                preview = json.dumps(data)[:300]
            except Exception as e:
                preview = f"JSON decode error: {e}"
        else:
            preview = res.text[:200]
            
        print(f"[{status}] {name} ({ep}) in {elapsed}s | Content-Type: {content_type}")
        print(f"    Preview: {preview}\n")
        
        results[ep] = {
            "name": name,
            "status": status,
            "elapsed": elapsed,
            "data": data,
            "preview": preview
        }
    except Exception as e:
        print(f"[FAIL] {name} ({ep}) error: {e}\n")
        results[ep] = {"name": name, "status": "ERROR", "error": str(e)}

# Detailed evaluations:
print("--- DETAILED METRICS VERIFICATION ---")

# 1. Paper Account Check
paper_acc = results.get("/api/paper/account", {}).get("data", {})
init_cap = paper_acc.get("initial_capital")
avail_margin = paper_acc.get("available_margin")
used_margin = paper_acc.get("used_margin")
cap_proven = paper_acc.get("capital_proven")
print(f"Paper Account: initial_capital={init_cap}, available_margin={avail_margin}, used_margin={used_margin}, capital_proven={cap_proven}")

# 2. Trades Today Check
trades_today = results.get("/api/trades/today", {}).get("data", {})
entries_count = len(trades_today.get("entries", [])) if isinstance(trades_today, dict) else 0
exits_count = len(trades_today.get("exits", [])) if isinstance(trades_today, dict) else 0
print(f"Trades Today: entries={entries_count}, exits={exits_count}, total_today={entries_count + exits_count}")

# 3. Opportunity Gap Check
opp_gap = results.get("/api/opportunity-gap", {}).get("data", {})
opp_status = opp_gap.get("status") if isinstance(opp_gap, dict) else None
runners = opp_gap.get("runners", []) if isinstance(opp_gap, dict) else []
print(f"Opportunity Gap: status={opp_status}, runners_count={len(runners)}")
if runners:
    first_runner = runners[0]
    print(f"   First Runner: {first_runner.get('symbol')} | Gap%: {first_runner.get('gap_pct')}% | Rec Strike: {first_runner.get('recommended_strike')} | Target: {first_runner.get('target')}")

# 4. T1 Pre-Ignition Check
t1_data = results.get("/api/t1-pre-ignition", {}).get("data", {})
t1_signals = t1_data.get("signals", []) if isinstance(t1_data, dict) else []
print(f"T1 Pre-Ignition: signals_count={len(t1_signals)}")
if t1_signals:
    print(f"   First Signal: {t1_signals[0].get('symbol')} | Contract: {t1_signals[0].get('contract')} | Score: {t1_signals[0].get('pre_ignition_score')}")

# 5. Multibagger Predictions Check
mb_data = results.get("/api/multibagger/predictions", {}).get("data", {})
mb_preds = mb_data.get("predictions", []) if isinstance(mb_data, dict) else []
print(f"Multibagger Predictions: predictions_count={len(mb_preds)}")

# 6. Safety check: Zero live broker orders
broker_status = results.get("/api/broker/status", {}).get("data", {})
live_enabled = broker_status.get("live_trading_enabled", True)
order_allowed = broker_status.get("order_placement_allowed", True)
mode = broker_status.get("mode")
print(f"Safety Gate: live_trading_enabled={live_enabled} (MUST be False), order_placement_allowed={order_allowed} (MUST be False), mode={mode}")

with open("scratch/live_cloud_run_verification_receipt.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved receipt to scratch/live_cloud_run_verification_receipt.json")
