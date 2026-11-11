import urllib.request
import json

endpoints = [
    "http://127.0.0.1:8008/api/market",
    "http://127.0.0.1:8008/api/verified-market",
    "http://127.0.0.1:8008/api/dhan/summary",
    "http://127.0.0.1:8008/api/ml/prediction-audit",
    "http://127.0.0.1:8008/api/paper/ledger",
    "http://127.0.0.1:8008/api/depth?symbol=RELIANCE",
    "http://127.0.0.1:8008/api/chain?symbol=RELIANCE",
]

for url in endpoints:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode('utf-8')
            parsed = json.loads(data)
            print(f"=== {url} === STATUS: {resp.status}")
            if "verified-market" in url:
                print("Quotes:", json.dumps(parsed.get("quotes", {}), indent=2))
            elif "market" in url:
                print("Prices:", parsed.get("prices", {}))
                print("Change Pct:", parsed.get("change_pct", {}))
            elif "dhan/summary" in url:
                print("Connected:", parsed.get("connected"))
                print("Profile:", parsed.get("profile"))
                print("Holdings count:", len(parsed.get("holdings", [])))
            elif "ml/prediction-audit" in url:
                print("Batches logged:", parsed.get("batches_logged"))
                print("Walk forward:", parsed.get("walk_forward"))
            elif "paper/ledger" in url:
                print("Total trades:", parsed.get("total_trades"))
                print("Net PnL:", parsed.get("net_pnl"))
            else:
                print(str(parsed)[:200])
    except Exception as e:
        print(f"=== {url} === ERROR: {e}")
