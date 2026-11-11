import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
url = 'https://genesis-system3-web-802404398783.asia-south1.run.app/api/auto_gates'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('HTTP', resp.status)
        gates = data.get('gates', {})
        for k, v in gates.items():
            print(f"  {k}: pass={v.get('pass')} blocker={v.get('blocker_code') or v.get('blocker_id')}")
except Exception as e:
    print('Error:', e)
