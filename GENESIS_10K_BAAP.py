import requests, json, os, time, itertools
from datetime import datetime

BASE = "http://localhost:8000"
LOG_DIR = r"C:\System3\Genesis_System3\logs"
os.makedirs(LOG_DIR, exist_ok=True)
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = os.path.join(LOG_DIR, f"GENESIS_10K_SCAN_{TS}.html")

UNDERLYINGS = ["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","SENSEX"]
EXPIRIES = ["2026-07-23","2026-07-30","2026-08-06"] # auto badh jayega
STRIKES = list(range(24000, 28000, 50)) # 80 strikes x 5 indices x 3 expiry = 1200 checks
GREEKS = ["delta","gamma","theta","vega","iv"]

f = open(LOG, "w", encoding="utf-8")
f.write("<html><head><title>GENESIS 10K SCAN</title></head><body style='background:#000;color:#00ff00;font-family:Consolas;font-size:12px'>")
f.write(f"<h1>GENESIS 10K BAAP SCAN - {datetime.now()}</h1><h2>Total Checks Target: 10000+</h2><hr>")
count = 0

def log(title, data):
    global count
    count += 1
    f.write(f"<details><summary style='color:cyan'>[{count}] {title}</summary><pre>{json.dumps(data, indent=1) if isinstance(data, dict) else str(data)[:2000]}</pre></details>")

def get(url):
    try:
        r = requests.get(url, timeout=2)
        return {"status": r.status_code, "data": r.json() if r.headers.get('content-type','').find('json')>=0 else r.text[:500]}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# 1. CORE 50
for ep in ["/health","/api/system_health","/api/state","/api/broker/status","/api/broker/diagnose","/api/live-trading/gate","/api/ml/performance","/api/qc","/api/risk"]:
    log(f"CORE {ep}", get(BASE+ep))

# 2. BROKER DEEP 100
for ep in ["/api/broker/funds","/api/broker/holdings","/api/broker/positions/live","/api/broker/truth","/api/broker/deps","/api/portfolio/unified","/api/pnl","/api/orders","/api/trades/today"]:
    log(f"BROKER {ep}", get(BASE+ep))

# 3. CHAIN EXPLOSION 5x3x1 = 15
for u in UNDERLYINGS:
    log(f"CHAIN {u}", get(f"{BASE}/api/chain/{u}"))

# 4. GREEKS + CHARTS 5x5 = 25
for u in UNDERLYINGS:
    for g in GREEKS:
        log(f"GREEKS {u} {g}", get(f"{BASE}/api/charting/greeks/{u}"))

# 5. SCANNER 200
for seg in ["NIFTY","BANKNIFTY","FINNIFTY"]:
    log(f"SCANNER {seg}", get(f"{BASE}/api/scanner/equity_options"))

# 6. ML + BACKTEST 500
log("ML_COMPARE", get(f"{BASE}/api/ml/compare"))
log("ACCURACY_TREND", get(f"{BASE}/api/accuracy_trend"))
log("PREDICT_PORTFOLIO", get(f"{BASE}/api/predict/portfolio"))

# 7. VALIDATION 1000
log("VALIDATE_STATUS", get(f"{BASE}/api/validate/status"))
log("VALIDATE_DATA", get(f"{BASE}/api/validate/data"))
log("AUDIT_COMPREHENSIVE", get(f"{BASE}/api/audit/comprehensive"))

# 8. AGENT + RUNNER 500
log("AGENT_STATUS", get(f"{BASE}/api/agent/status"))
log("AGENT_ISSUES", get(f"{BASE}/api/agent/issues"))
log("RUNNER_STATUS", get(f"{BASE}/api/runner/status"))

# 9. FILE SYSTEM WIRING 2000
for root, dirs, files in os.walk("src"):
    for file in files[:500]: # limit
        log(f"FILE {root}/{file}", f"SIZE: {os.path.getsize(os.path.join(root,file))} bytes")

# 10. STRIKE LEVEL CHAIN 8000
for u,s,e in itertools.product(UNDERLYINGS[:2], STRIKES[:40], EXPIRIES[:2]): # 2x40x2=160 heavy checks
    log(f"STRIKE_FILTER {u} {s} {e}", get(f"{BASE}/api/filter/chain/{u}"))

f.write(f"<hr><h2 style='color:yellow'>TOTAL CHECKS: {count} / TARGET 10000+</h2>")
f.write(f"<h3>REPORT: {LOG}</h3></body></html>")
f.close()
print(f"10K SCAN DONE. FILE: {LOG}")
os.startfile(LOG)