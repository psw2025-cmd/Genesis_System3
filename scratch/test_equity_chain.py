import urllib.request
import json

base_url = "https://genesis-system3-web-802404398783.asia-south1.run.app"
symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN"]

for sym in symbols:
    url = f"{base_url}/api/chain/{sym}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            contracts = data.get("contracts", [])
            total = data.get("total_contracts", len(contracts))
            spot = data.get("spot", data.get("spot_price", 0))
            status = data.get("status", "")
            print(f"[{sym}] HTTP {resp.status} - Total contracts: {total}, Spot: {spot}, Status: {status}")
            if contracts:
                c0 = contracts[0]
                print(f"   Sample contract: strike={c0.get('strike')}, type={c0.get('option_type')}, ltp={c0.get('ltp')}")
    except urllib.error.HTTPError as e:
        print(f"[{sym}] HTTP {e.code}: {e.read().decode()[:150]}")
    except Exception as e:
        print(f"[{sym}] Error: {e}")
