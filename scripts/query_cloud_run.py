import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://genesis-system3-web-802404398783.asia-south1.run.app/api/auto_gates",
    "https://genesis-system3-web-802404398783.asia-south1.run.app/api/health",
    "https://genesis-system3-web-802404398783.asia-south1.run.app/api/ml/overview",
    "https://genesis-system3-web-802404398783.asia-south1.run.app/api/system/readiness"
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = resp.read().decode("utf-8")
            print(f"=== {u} (HTTP {resp.status}) ===")
            try:
                js = json.loads(data)
                print(json.dumps(js, indent=2)[:400])
            except Exception:
                print(data[:300])
    except Exception as e:
        print(f"=== {u} ERROR: {e} ===")
