import requests
import json

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"

print("=== CHECKING FOR UNINTENDED PENDING OR NULL STATES ACROSS APIS ===\n")

# 1. Broker status & token proof
bs = requests.get(f"{BASE_URL}/api/broker/status").json()
tp = bs.get("token_proof", {})
print("1. Broker Status & Token Proof:")
print(f"   connected: {bs.get('connected')}")
print(f"   hours_remaining: {tp.get('hours_remaining')}")
print(f"   source: {tp.get('source')}")
print(f"   secret_version: {tp.get('secret_version')}")
print(f"   loaded_at_utc: {tp.get('loaded_at_utc')}")
print(f"   expires_at_utc: {tp.get('expires_at_utc')}")
print(f"   live_trading_enabled: {bs.get('live_trading_enabled')}")
print(f"   order_placement_allowed: {bs.get('order_placement_allowed')}\n")

# 2. Paper account & trades today
pa = requests.get(f"{BASE_URL}/api/paper/account").json()
tt = requests.get(f"{BASE_URL}/api/trades/today").json()
print("2. Paper Account & Dynamic Trades Today:")
print(f"   initial_capital: {pa.get('initial_capital')}")
print(f"   available_margin: {pa.get('available_margin')}")
print(f"   used_margin: {pa.get('used_margin')}")
print(f"   capital_proven: {pa.get('capital_proven')}")
print(f"   today_trades_total: {tt.get('total_trades')}")
print(f"   today_entries: {len(tt.get('entries', []))}")
print(f"   today_exits: {len(tt.get('exits', []))}\n")

# 3. Option Chain (NIFTY)
oc = requests.get(f"{BASE_URL}/api/chain/NIFTY").json()
print("3. NIFTY Option Chain:")
print(f"   status: {oc.get('status')}")
print(f"   underlying: {oc.get('underlying')}")
print(f"   spot: {oc.get('spot')}")
print(f"   pcr: {oc.get('pcr')}")
print(f"   iv_percentile: {oc.get('iv_percentile')}")
print(f"   oi_change: {oc.get('oi_change')}")
print(f"   source: {oc.get('source') or oc.get('data_source')}")
print(f"   contracts_count: {len(oc.get('contracts', []))}\n")

# 4. Opportunity Gap & T1 Pre-Ignition
og = requests.get(f"{BASE_URL}/api/opportunity-gap").json()
t1 = requests.get(f"{BASE_URL}/api/t1-pre-ignition").json()
print("4. Opportunity Gap & T1 Pre-Ignition:")
print(f"   opportunity_gap_status: {og.get('status')}")
print(f"   runners_count: {len(og.get('runners', []))}")
print(f"   t1_status: {t1.get('status')}")
print(f"   t1_signals_count: {len(t1.get('signals', []))}\n")

# 5. Multibagger Predictions
mb = requests.get(f"{BASE_URL}/api/multibagger/predictions").json()
print("5. Multibagger Predictions:")
print(f"   status: {mb.get('status')}")
print(f"   predictions_count: {len(mb.get('predictions', []))}\n")

# 6. Advanced Charts endpoints for NIFTY
print("6. Advanced Charts Endpoints:")
for path, name in [
    ("/api/charting/heatmap/NIFTY?metric=oi", "Heatmap (OI)"),
    ("/api/charting/iv-surface/NIFTY", "IV Surface"),
    ("/api/charting/greeks/NIFTY?greek=delta", "Greeks (Delta)"),
    ("/api/charting/pcr/NIFTY", "PCR Chart"),
]:
    res = requests.get(f"{BASE_URL}{path}").json()
    st = res.get("status")
    payload = res.get("heatmap") or res.get("surface") or res.get("greeks") or res.get("pcr") or {}
    print(f"   {name}: status={st}, spot={payload.get('spot')}, strikes_count={len(payload.get('strikes', []))}")
