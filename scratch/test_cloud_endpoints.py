import urllib.request
import json

base_url = "https://genesis-system3-web-802404398783.asia-south1.run.app"
endpoints = [
    "/api/broker/status",
    "/api/health",
    "/api/ml/performance",
    "/api/state",
    "/api/charting/heatmap/NIFTY?metric=oi",
    "/api/charting/iv-surface/NIFTY",
    "/api/charting/greeks/NIFTY?greek=delta",
    "/api/charting/pcr/NIFTY",
]

results = {}
for ep in endpoints:
    url = f"{base_url}{ep}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results[ep] = {"status": resp.status, "keys": list(data.keys()) if isinstance(data, dict) else type(data).__name__, "sample": str(data)[:200]}
    except Exception as e:
        results[ep] = {"error": f"{type(e).__name__}: {e}"}

print(json.dumps(results, indent=2))
