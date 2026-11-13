import urllib.request
import json

base_url = "https://genesis-system3-web-802404398783.asia-south1.run.app"

for path in ["/api/charting/iv-surface/NIFTY", "/api/charting/greeks/NIFTY?greek=delta"]:
    req = urllib.request.Request(f"{base_url}{path}", headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"\n=== {path} ===")
        print("Top keys:", list(data.keys()))
        for k, v in data.items():
            if isinstance(v, dict):
                print(f"  Subkeys of {k}:", list(v.keys()))
                for sk, sv in v.items():
                    if isinstance(sv, list):
                        print(f"    {sk} list len:", len(sv), "sample:", sv[:3] if sv else [])
                    else:
                        print(f"    {sk}:", sv)
            elif isinstance(v, list):
                print(f"  {k} list len:", len(v), "sample:", v[:3] if v else [])
            else:
                print(f"  {k}:", v)
