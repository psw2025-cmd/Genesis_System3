import urllib.request
import json

base = "https://genesis-system3-web-802404398783.asia-south1.run.app"

print("=" * 60)
print("1. VERIFY /api/deploy/info")
print("=" * 60)
req = urllib.request.Request(f"{base}/api/deploy/info", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print("git_sha:", data.get("git_sha"))
    print("revision:", data.get("revision"))
    print("cloud_run_revision:", data.get("cloud_run_revision"))
    print("deploy_target:", data.get("deploy_target"))

print("\n" + "=" * 60)
print("2. VERIFY /api/chain/NIFTY")
print("=" * 60)
req = urllib.request.Request(f"{base}/api/chain/NIFTY", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print("underlying:", data.get("underlying"))
    print("spot:", data.get("spot"))
    print("atm_strike:", data.get("atm_strike"))
    print("change:", data.get("change"))
    print("change_pct:", data.get("change_pct"))
    print("pcr:", data.get("pcr"))
    print("contracts count:", len(data.get("contracts", [])))
    print("status:", data.get("status"))

print("\n" + "=" * 60)
print("3. VERIFY /api/market/live_board")
print("=" * 60)
req = urllib.request.Request(f"{base}/api/market/live_board", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    indices = data.get("indices", [])
    print(f"Total indices returned: {len(indices)}")
    for item in indices:
        sym = item.get("symbol")
        ltp = item.get("ltp")
        chg = item.get("change")
        chg_pct = item.get("change_pct")
        source = item.get("source")
        print(f"  {sym}: ltp={ltp}, chg={chg} ({chg_pct}%), source={source}")

print("\n" + "=" * 60)
print("4. VERIFY /api/auto_gates")
print("=" * 60)
req = urllib.request.Request(f"{base}/api/auto_gates", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print(f"Gates passing: {data.get('gates_passing')}/{data.get('gates_total')} PASS")
    print(f"Status: {data.get('status')}")
    for g in data.get("proof_gates", []):
        print(f"  [{g.get('status')}] {g.get('name')}: {g.get('note')}")

print("\n" + "=" * 60)
print("5. VERIFY /api/ml/performance")
print("=" * 60)
req = urllib.request.Request(f"{base}/api/ml/performance", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print(f"proof_status: {data.get('proof_status')}")
    print(f"ready_for_live: {data.get('ready_for_live')}")
    print(f"rho: {data.get('rho')}")
    print(f"hit_rate: {data.get('hit_rate')}")
    print(f"proof_pass_count: {data.get('proof_pass_count')}")
