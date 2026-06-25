#!/usr/bin/env python3
"""
Dashboard Auto-Verify Script — runs in GitHub Actions CI
Fetches all dashboard APIs, detects bugs, writes report to repo.
Does NOT need a browser — tests the API layer (the real source of truth).
"""
import json, sys, os, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

IST  = timezone(timedelta(hours=5, minutes=30))
BASE = os.environ.get("DASHBOARD_URL", "https://genesis-system3-backend.onrender.com")
OUT  = Path("reports/latest/dashboard_ui_proof")
OUT.mkdir(parents=True, exist_ok=True)

def fetch(path, timeout=20):
    try:
        req = urllib.request.Request(
            f"{BASE}{path}",
            headers={"User-Agent": "Genesis-CI-Verify/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()), r.status, None
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read())
        except: body = {}
        return body, e.code, str(e)
    except Exception as e:
        return {}, 0, str(e)

now = datetime.now(IST)
report = {
    "timestamp": now.isoformat(),
    "timestamp_ist": now.strftime("%Y-%m-%d %H:%M:%S IST"),
    "base": BASE,
    "apis": {},
    "bugs": [],
    "summary": {},
}

# ── API-level checks ──────────────────────────────────────────────────────────
CHECKS = [
    ("/health",                    "health"),
    ("/api/health",                "api_health"),
    ("/api/state",                 "state"),
    ("/api/broker/status",         "broker_status"),
    ("/api/broker/dhan/status",    "dhan_status"),
    ("/api/paper",                 "paper"),
    ("/api/gain_rank",             "gain_rank"),
    ("/api/qc",                    "qc"),
    ("/api/auto_gates",            "auto_gates"),
    ("/api/approval/status",       "approval"),
    ("/api/broker/funds",          "broker_funds"),
    ("/api/broker/holdings",       "broker_holdings"),
    ("/api/broker/positions/live", "broker_positions"),
    ("/api/chain/NIFTY",           "chain_nifty"),
    ("/api/chain/BANKNIFTY",       "chain_banknifty"),
    ("/api/alerts/recent?limit=5", "alerts"),
    ("/api/accuracy_trend",        "accuracy_trend"),
    ("/api/signals",               "signals"),
]

print(f"Verifying {BASE} ...")
for path, key in CHECKS:
    data, status, err = fetch(path)
    ok = status == 200
    report["apis"][key] = {"path": path, "status": status, "ok": ok, "error": err}

    # Specific checks
    if key == "paper":
        pnl = data.get("pnl", {})
        # Check for stale Feb-1 data
        ts  = pnl.get("timestamp_ist", "") or str(pnl.get("timestamp",""))
        if "2026-02-01" in ts or "Feb-01" in ts:
            report["bugs"].append({
                "severity": "HIGH",
                "api": path,
                "label": f"Stale Feb-1 data in paper API: {ts}"
            })
        # Check for "NO TRADE / QC failed" in top_trade_signal
    if key == "health" and ok:
        if data.get("live_allowed") is True:
            report["bugs"].append({
                "severity": "CRITICAL",
                "api": path,
                "label": "live_allowed=True! Live trading gate broken!"
            })
    if key == "chain_nifty" and ok:
        contracts = data.get("contracts", [])
        spot = data.get("spot", 0)
        if spot == 0:
            report["bugs"].append({"severity": "HIGH", "api": path, "label": "NIFTY chain: spot=0"})
        if len(contracts) == 0:
            report["bugs"].append({"severity": "HIGH", "api": path, "label": "NIFTY chain: 0 contracts"})
        # Check for phantom prices
        for c in contracts[:10]:
            ltp    = float(c.get("ltp", 0) or 0)
            strike = float(c.get("strike", 0) or 0)
            ot     = str(c.get("option_type",""))
            if ltp > 0 and spot > 0 and strike > 0:
                intrinsic = max(0, spot-strike) if ot=="CE" else max(0, strike-spot)
                extrinsic = ltp - intrinsic
                mny = abs(spot-strike)/spot*100
                cap = 0.03*spot if (intrinsic==0 and mny>2) else 0.05*spot
                if extrinsic > cap:
                    report["bugs"].append({
                        "severity": "HIGH",
                        "api": path,
                        "label": f"Phantom price: {strike:.0f}{ot} ltp={ltp:.1f} extrinsic={extrinsic:.1f} > cap={cap:.1f}"
                    })

    icon = "✅" if ok else "❌"
    extra = ""
    if key == "paper" and ok:
        pnl = data.get("pnl", {})
        extra = f" | trades={pnl.get('total_trades','?')} pnl=₹{pnl.get('total_pnl','?')}"
    if key == "chain_nifty" and ok:
        extra = f" | spot={data.get('spot','?')} contracts={len(data.get('contracts',[]))}"
    if key == "gain_rank" and ok:
        extra = f" | status={data.get('status','?')} stale={data.get('stale','?')}"
    print(f"  {icon} {key:25} HTTP {status}{extra}")

# Summary
ok_count   = sum(1 for v in report["apis"].values() if v["ok"])
fail_count = len(report["apis"]) - ok_count
high_bugs  = [b for b in report["bugs"] if b["severity"] in ("HIGH","CRITICAL")]
report["summary"] = {
    "total_apis": len(report["apis"]),
    "apis_ok": ok_count,
    "apis_fail": fail_count,
    "total_bugs": len(report["bugs"]),
    "high_bugs": len(high_bugs),
    "verdict": "HEALTHY" if fail_count==0 and len(high_bugs)==0 else "NEEDS_FIX",
}

# Write report
result_path = OUT / "latest.json"
result_path.write_text(json.dumps(report, indent=2))
print(f"\n=== SUMMARY ===")
print(json.dumps(report["summary"], indent=2))
if high_bugs:
    print("\nHigh/Critical bugs:")
    for b in high_bugs:
        print(f"  ❌ [{b['severity']}] {b['label']}")

# Exit code
sys.exit(1 if high_bugs else 0)
