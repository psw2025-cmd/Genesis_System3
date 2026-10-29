import requests
BASE = "http://127.0.0.1:8000"
EPS = [
    ("GET",  "/"),
    ("GET",  "/api/health"),
    ("GET",  "/api/state"),
    ("GET",  "/api/broker/status"),
    ("GET",  "/openapi.json"),
    ("GET",  "/docs"),
    ("GET",  "/ui"),
    ("GET",  "/risk"),
    ("GET",  "/tradebook"),
    ("GET",  "/holdings"),
    ("GET",  "/dhan-health"),
    ("POST", "/emergency-exit"),
    ("GET",  "/auto-research"),
    ("GET",  "/verify-strategy"),
    ("GET",  "/learn-from-loss"),
    ("GET",  "/adapt-market"),
    ("GET",  "/option-intelligence/NIFTY"),
    ("GET",  "/autonomous-brain"),
    ("GET",  "/hidden-secrets-lab"),
    ("GET",  "/never-die-monitor"),
    ("GET",  "/hunger-meter"),
    ("GET",  "/data-truth-score"),
    ("GET",  "/world-comparison"),
    ("GET",  "/roadmap"),
    ("GET",  "/cost-roi"),
]

p = f = 0
for method, path in EPS:
    url = BASE + path
    try:
        if method == "POST":
            # Emergency exit needs a payload; use a safe probe first
            r = requests.post(url, json={"dry_run": True, "reason": "api-verification"}, timeout=10)
        else:
            r = requests.get(url, timeout=10)
        ok = 200 <= r.status_code < 300
        tag = "PASS" if ok else "FAIL"
        print(f"{method:5} {r.status_code} {tag:4} {path}")
        if ok: p += 1
        else:  f += 1
    except Exception as e:
        print(f"{method:5} ERR  FAIL {path}  -> {e}")
        f += 1

print(f"\nTOTAL={len(EPS)} PASS={p} FAIL={f}")
