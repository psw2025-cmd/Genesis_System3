#!/usr/bin/env python3
"""
Genesis System3 — Cloud Verify + Issue Finder
Runs in GitHub Actions (can reach Render).
Fetches every API, detects every issue, writes full report.
Claude reads report → fixes code → CI runs again → repeat.
"""
import json, sys, os, urllib.request, urllib.error, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

IST  = timezone(timedelta(hours=5, minutes=30))
BASE = os.environ.get("DASHBOARD_URL", "https://genesis-system3-backend.onrender.com")
OUT  = Path("reports/latest/dashboard_ui_proof")
OUT.mkdir(parents=True, exist_ok=True)

def fetch(path, timeout=25):
    try:
        req = urllib.request.Request(f"{BASE}{path}",
            headers={"User-Agent":"Genesis-CI/2.0","Accept":"application/json"})
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
    "issues": [],
    "fixes_needed": [],
    "summary": {},
}

print(f"=== Genesis System3 Cloud Verify ===")
print(f"Time: {report['timestamp_ist']}")
print(f"URL:  {BASE}")
print()

# ── Fetch all APIs ────────────────────────────────────────────────────────
APIS = [
    ("/health",                     "health",           5),
    ("/api/health",                 "api_health",       10),
    ("/api/state",                  "state",            10),
    ("/api/broker/status",          "broker_status",    10),
    ("/api/broker/dhan/status",     "dhan_status",      10),
    ("/api/broker/diagnose",        "broker_diagnose",  15),
    ("/api/broker/funds",           "broker_funds",     15),
    ("/api/broker/holdings",        "broker_holdings",  15),
    ("/api/broker/positions/live",  "broker_positions", 15),
    ("/api/paper",                  "paper",            10),
    ("/api/gain_rank",              "gain_rank",        10),
    ("/api/qc",                     "qc",               10),
    ("/api/auto_gates",             "auto_gates",       10),
    ("/api/approval/status",        "approval",         10),
    ("/api/chain/NIFTY",            "chain_nifty",      20),
    ("/api/chain/BANKNIFTY",        "chain_banknifty",  20),
    ("/api/alerts/recent?limit=5",  "alerts",           10),
    ("/api/accuracy_trend",         "accuracy_trend",   10),
    ("/api/learning/status",        "learning",         10),
    ("/api/system_health",          "system_health",    10),
    ("/api/perf",                   "perf",             10),
    ("/api/scanner/top_contract_gainers", "scanner_gainers", 30),
    ("/api/portfolio/unified",      "portfolio",        15),
]

t0 = time.time()
for path, key, timeout in APIS:
    ts = time.time()
    data, status, err = fetch(path, timeout)
    elapsed = round(time.time()-ts, 2)
    ok = (status == 200)
    report["apis"][key] = {
        "path": path, "status": status,
        "ok": ok, "error": err,
        "elapsed_s": elapsed, "size": len(json.dumps(data))
    }
    icon = "✅" if ok else "❌"
    speed = f" [{elapsed}s]" if elapsed > 2 else ""
    extra = ""

    # Per-API checks
    if key == "api_health" and ok:
        broker_conn = data.get("broker",{}).get("connected", False)
        live_ok     = data.get("live_allowed") is False
        market_open = data.get("market",{}).get("is_open", False)
        extra = f" broker={'✅' if broker_conn else '🔴DISCONNECTED'} market={'OPEN' if market_open else 'CLOSED'} live={'BLOCKED✅' if live_ok else '🔴ENABLED!'}"
        if not broker_conn:
            report["issues"].append({
                "severity": "CRITICAL",
                "api": path,
                "label": "Broker disconnected",
                "detail": data.get("message",""),
                "fix": "Update DHAN_ACCESS_TOKEN in Render env vars → check /api/broker/diagnose"
            })
        if data.get("live_allowed") is True:
            report["issues"].append({
                "severity": "CRITICAL",
                "api": path,
                "label": "live_allowed=True! Safety gate broken!",
                "fix": "Restore live_allowed=False hardcode in get_health()"
            })

    if key == "broker_diagnose" and ok:
        issues_found = data.get("issues", [])
        env = data.get("env_vars", {})
        extra = f" token={'PRESENT' if env.get('DHAN_ACCESS_TOKEN_present') else '🔴MISSING'} len={env.get('DHAN_ACCESS_TOKEN_length',0)}"
        for iss in issues_found:
            report["issues"].append({"severity":"HIGH","api":path,"label":iss,
                "fix": data.get("fix_action","Check Render env vars")})

    if key == "chain_nifty" and ok:
        contracts = data.get("contracts", [])
        spot = data.get("spot", 0)
        extra = f" spot={spot} contracts={len(contracts)}"
        if spot == 0 or len(contracts) == 0:
            report["issues"].append({
                "severity": "HIGH",
                "api": path,
                "label": f"NIFTY chain empty: spot={spot}, contracts={len(contracts)}",
                "fix": "Broker must be connected for Dhan P0 chain fetch"
            })
        # Phantom price check
        for c in contracts[:20]:
            ltp = float(c.get("ltp",0) or 0)
            strike = float(c.get("strike",0) or 0)
            ot = str(c.get("option_type",""))
            if ltp > 0 and spot > 0 and strike > 0:
                intrinsic = max(0,spot-strike) if ot=="CE" else max(0,strike-spot)
                extrinsic = ltp - intrinsic
                mny = abs(spot-strike)/spot*100
                cap = 0.03*spot if (intrinsic==0 and mny>2) else 0.05*spot
                if extrinsic > cap:
                    report["issues"].append({
                        "severity":"HIGH","api":path,
                        "label":f"Phantom price {strike:.0f}{ot} ltp={ltp:.1f} extrinsic={extrinsic:.1f}>{cap:.1f}",
                        "fix":"B1 phantom guard should catch this — check datasource_manager"
                    })

    if key == "paper" and ok:
        history = data.get("pnl",{}).get("history",[])
        summary = data.get("pnl",{}).get("summary",{})
        stale = any("2026-02-01" in str(t.get("time_ist","")) for t in history[:3])
        if stale:
            report["issues"].append({
                "severity":"HIGH","api":path,
                "label":f"Fake Feb-1 data in paper history ({len(history)} trades)",
                "fix":"Remove paper_closed_trades_feb2026.json fallback in get_pnl()"
            })
        mismatch = len(history) > 0 and summary.get("total_trades",0) == 0
        if mismatch:
            report["issues"].append({
                "severity":"MEDIUM","api":path,
                "label":f"Paper mismatch: history={len(history)} trades but summary.total_trades=0",
                "fix":"get_pnl summary and history must come from same source"
            })
        extra = f" history={len(history)} summary_trades={summary.get('total_trades','?')}"

    if key == "scanner_gainers":
        extra = f" [{elapsed}s] {'🔴SLOW' if elapsed > 10 else '✅fast'}"
        if elapsed > 15:
            report["issues"].append({
                "severity":"HIGH","api":path,
                "label":f"Scanner took {elapsed}s — blocks dashboard poll",
                "fix":"TTL cache should be working — check _cache_get('scanner_gainers')"
            })

    print(f"  {icon} {key:30} HTTP {status}{speed}{extra}")

total_time = round(time.time()-t0, 1)
ok_count   = sum(1 for v in report["apis"].values() if v["ok"])
slow_apis  = [(k,v["elapsed_s"]) for k,v in report["apis"].items() if v["elapsed_s"] > 5]

# ── Summary ────────────────────────────────────────────────────────────────
critical = [i for i in report["issues"] if i["severity"]=="CRITICAL"]
high     = [i for i in report["issues"] if i["severity"]=="HIGH"]
medium   = [i for i in report["issues"] if i["severity"]=="MEDIUM"]

report["summary"] = {
    "total_apis": len(APIS),
    "apis_ok": ok_count,
    "apis_fail": len(APIS)-ok_count,
    "total_issues": len(report["issues"]),
    "critical": len(critical),
    "high": len(high),
    "medium": len(medium),
    "slow_apis": slow_apis,
    "total_fetch_time_s": total_time,
    "verdict": "HEALTHY" if len(critical)==0 and len(high)==0 else "NEEDS_FIX",
}

print(f"\n=== ISSUES ({len(report['issues'])}) ===")
for iss in report["issues"]:
    print(f"  [{iss['severity']}] {iss['label']}")
    print(f"    FIX: {iss['fix']}")

print(f"\n=== SUMMARY ===")
print(json.dumps(report["summary"], indent=2))

# Write report
out_path = OUT / "latest.json"
out_path.write_text(json.dumps(report, indent=2))
print(f"\nReport written: {out_path}")

# Exit non-zero if critical/high issues (makes CI fail visibly)
sys.exit(1 if (critical or high) else 0)
