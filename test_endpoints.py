import urllib.request
import json

endpoints = [
    '/health',
    '/api/verified-market',
    '/api/dhan/profile',
    '/api/dhan/funds',
    '/api/dhan/holdings',
    '/api/dhan/summary'
]

for endpoint in endpoints:
    url = f"http://127.0.0.1:8008{endpoint}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== {endpoint} (HTTP {resp.status}) ===")
            if "quotes" in data:
                print("Quotes:", list(data["quotes"].keys()))
                for k, v in data["quotes"].items():
                    print(f"  {k}: price={v.get('price')}, time={v.get('last_trade_ist')}, status={v.get('status')}")
            elif "holdings" in data:
                print(f"Holdings count: {data.get('count')}, total_current_val: {data.get('total_current_value')}")
                for h in data["holdings"][:2]:
                    print(" ", h.get("trading_symbol"), "qty:", h.get("total_qty"), "ltp:", h.get("last_traded_price"))
            elif "profile" in data:
                print("Profile summary:", data.get("profile"))
            elif "funds" in data:
                print("Funds summary:", data.get("funds"))
            else:
                print("Keys:", list(data.keys())[:5])
    except Exception as e:
        print(f"=== {endpoint} FAILED: {e} ===")
