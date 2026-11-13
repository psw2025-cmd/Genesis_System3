import urllib.request
import json
import time

base_url = "https://genesis-system3-web-802404398783.asia-south1.run.app"
equities = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", 
    "SBIN", "TATAMOTORS", "BHARTIARTL", "ITC", "LT", 
    "MARUTI", "SUNPHARMA", "TATASTEEL", "BAJFINANCE", "ADANIENT"
]

results = []
for sym in equities:
    url = f"{base_url}/api/chain/{sym}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            elapsed = time.time() - t0
            data = json.loads(resp.read().decode())
            contracts = data.get("contracts", [])
            spot = data.get("spot", data.get("spot_price", 0))
            pcr = data.get("pcr", None)
            strikes = sorted(list(set(c.get("strike") for c in contracts if c.get("strike"))))
            ce_count = sum(1 for c in contracts if c.get("option_type") == "CE")
            pe_count = sum(1 for c in contracts if c.get("option_type") == "PE")
            
            results.append({
                "symbol": sym,
                "status": "OK",
                "http_status": resp.status,
                "elapsed_ms": round(elapsed * 1000, 1),
                "spot": spot,
                "pcr": pcr,
                "total_contracts": len(contracts),
                "ce_contracts": ce_count,
                "pe_contracts": pe_count,
                "strike_count": len(strikes),
                "strike_range": f"{strikes[0]} - {strikes[-1]}" if strikes else "N/A",
                "data_source": data.get("data_source", data.get("source", "N/A"))
            })
    except Exception as e:
        results.append({
            "symbol": sym,
            "status": "FAIL",
            "error": str(e)
        })

print(json.dumps(results, indent=2))
