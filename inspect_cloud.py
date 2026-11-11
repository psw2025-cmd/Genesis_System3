import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = 'https://genesis-system3-web-802404398783.asia-south1.run.app'
endpoints = [
    '/api/system/readiness',
    '/api/proof_ledger',
    '/api/market/validation',
    '/api/backtest/results',
    '/api/system/status',
    '/api/alerts',
    '/api/accuracy_trend',
    '/api/pnl'
]

results = {}
for ep in endpoints:
    url = base + ep
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            results[ep] = {'status': resp.status, 'data': data}
    except Exception as e:
        results[ep] = {'error': str(e)}

with open('inspect_cloud.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Fetched successfully. Keys:", list(results.keys()))
for k, v in results.items():
    if 'error' in v:
        print(f"{k}: ERROR {v['error']}")
    else:
        print(f"{k}: HTTP {v['status']}")
