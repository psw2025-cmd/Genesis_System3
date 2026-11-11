import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    'https://genesis-system3-web-802404398783.asia-south1.run.app/api/ml/performance',
    headers={'User-Agent': 'Mozilla/5.0'}
)

with urllib.request.urlopen(req, context=ctx) as r:
    d = json.loads(r.read())
    print("STATUS:", d.get("status"))
    print("PROOF_STATUS:", d.get("proof_status"))
    print("MODEL_PROOF_READY:", d.get("model_proof_ready"))
    print("RHO:", d.get("rho"))
    print("HIT_RATE:", d.get("hit_rate"))
    print("PROOF_PASS_COUNT:", d.get("proof_pass_count"))
    print("BLOCKER_REASON:", d.get("blocker_reason"))
    print("READY_FOR_LIVE:", d.get("ready_for_live"))
    print("CHECKLIST:")
    for item in d.get("validations_checklist", []):
        print("  *", item.get("label"), "->", item.get("pass"), f"({item.get('detail')})")
    print("MODELS:")
    perf = d.get("performance", {})
    models = perf.get("models", {})
    for mname, mdata in models.items():
        if isinstance(mdata, dict):
            print(f"  * {mname}: status={mdata.get('status')} rows={mdata.get('rows')} pass={mdata.get('proof_pass_count')}")
