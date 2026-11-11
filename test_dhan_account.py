import urllib.request
import json
from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\.secrets\dhan.env")
creds = {}
for line in p.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")

headers = {
    "access-token": creds["DHAN_ACCESS_TOKEN"],
    "client-id": creds["DHAN_CLIENT_ID"],
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("1. Testing Dhan Profile...")
try:
    req = urllib.request.Request("https://api.dhan.co/v2/profile", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        profile = json.loads(resp.read().decode())
        print("Profile:", json.dumps(profile, indent=2))
except Exception as e:
    print("Profile Error:", e)

print("\n2. Testing Dhan Funds...")
try:
    req = urllib.request.Request("https://api.dhan.co/v2/fundlimit", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        funds = json.loads(resp.read().decode())
        print("Funds:", json.dumps(funds, indent=2))
except Exception as e:
    print("Funds Error:", e)

print("\n3. Testing Dhan Holdings...")
try:
    req = urllib.request.Request("https://api.dhan.co/v2/holdings", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        holdings = json.loads(resp.read().decode())
        print(f"Total Holdings: {len(holdings)}")
        for h in holdings[:3]:
            print("Holding:", h.get("tradingSymbol"), "Qty:", h.get("totalQty"), "AvgPrice:", h.get("avgCostPrice"), "LTP:", h.get("lastTradedPrice"))
except Exception as e:
    print("Holdings Error:", e)
