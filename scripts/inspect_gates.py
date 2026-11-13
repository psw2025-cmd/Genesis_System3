import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    'https://genesis-system3-web-802404398783.asia-south1.run.app/api/auto_gates',
    headers={'User-Agent': 'Mozilla/5.0'}
)

with urllib.request.urlopen(req, context=ctx) as r:
    data = json.loads(r.read())
    print("STATUS:", data.get("status"))
    print("RUNTIME_DRIVEN:", data.get("runtime_driven"))
    print("SOURCE:", data.get("source"))
    gates = data.get("gates", {})
    passing = 0
    total = len(gates)
    for k, v in gates.items():
        is_pass = v.get("pass")
        if is_pass:
            passing += 1
        print(f"[{'PASS' if is_pass else 'BLOCKED'}] {k} -> blocker={v.get('blocker_id')} metric={v.get('metric')}")
    print(f"\nTOTAL: {passing}/{total} PASSING")
