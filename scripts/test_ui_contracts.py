import urllib.request
import json

with urllib.request.urlopen("http://localhost:8008/api/options/gainers") as r:
    res = json.loads(r.read().decode())

data = res.get("data", {})
ce = data.get("ce_gainers", [])
pe = data.get("pe_gainers", [])

all_contracts = list({f"{c.get('contract')}:{c.get('option_type')}": c for c in (ce + pe)}.values())
print(f"Total combined rows rendered in UI: {len(all_contracts)}")

indices = set(c.get("symbol") for c in all_contracts if c.get("symbol") in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"])
equities = set(c.get("symbol") for c in all_contracts if c.get("symbol") not in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"])

print(f"Indices in table: {indices}")
print(f"Equities in table: {equities}")

print("\nSample Index rows:")
for c in [x for x in all_contracts if x.get("symbol") in indices][:5]:
    print(f"  [INDEX] {c.get('contract')} | LTP: {c.get('ltp')} | Chg: {c.get('change_pct')}% | Prov: {c.get('data_provenance')}")

print("\nSample Equity F&O rows:")
for c in [x for x in all_contracts if x.get("symbol") in equities][:5]:
    print(f"  [EQUITY FO] {c.get('contract')} | LTP: {c.get('ltp')} | Chg: {c.get('change_pct')}% | Prov: {c.get('data_provenance')}")
