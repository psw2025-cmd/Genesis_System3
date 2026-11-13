from pathlib import Path
import ast
p=Path(r'C:\Genesis_System3_clean\content\app\app.py')
s=p.read_text(encoding='utf-8')
old='return make_envelope({"quotes": quotes, "count": len(quotes)}, ts, real=True)'
assert s.count(old)==1
s=s.replace(old,'return make_envelope({"quotes": quotes, "count": len(quotes), "classification": "SIMULATED_OR_UNVERIFIED_CACHE"}, ts, real=False)',1)
old='''    routes_status = [
        {"feed": "NSE Market Feed", "status": "ONLINE_RECONCILED_SNAPSHOT", "latency_ms": 0.8, "freshness_sec": 0},
        {"feed": "Broker (Paper/Dhan)", "status": "CONNECTED_DHANHQ_READONLY", "latency_ms": 32.0, "freshness_sec": 0},
        {"feed": "Order API Gateway", "status": "ONLINE_SAFETY_LOCKED_PAPER_ONLY", "latency_ms": 0.4, "freshness_sec": 0},
        {"feed": "Evidence Store Chain", "status": "CRYPTOGRAPHIC_SHA256_PASS", "latency_ms": 0.2, "freshness_sec": 0}
    ]
    env = make_envelope({"routes": routes_status, "overall_health": "VERIFIED_HEALTHY"}, ts, real=True)
    env["provenance"] = {
        "source": "VERIFIED_LOCAL_AND_DHAN_TELEMETRY",
        "safety_mode": "PAPER_MODE",
        "freshness_sec": 0,
        "exchange_feed_verified": True,
        "classification": "VERIFIED_TELEMETRY"
    }'''
new='''    # This route does not measure live upstream latency or freshness.
    routes_status = [
        {"feed": "NSE Market Feed", "status": "NOT_VERIFIED", "latency_ms": None, "freshness_sec": None},
        {"feed": "Broker (Paper/Dhan)", "status": "NOT_VERIFIED_BY_THIS_ROUTE", "latency_ms": None, "freshness_sec": None},
        {"feed": "Order API Gateway", "status": "PAPER_ONLY_CONFIGURED_NOT_PROBED", "latency_ms": None, "freshness_sec": None},
        {"feed": "Evidence Store Chain", "status": "NOT_VERIFIED_BY_THIS_ROUTE", "latency_ms": None, "freshness_sec": None}
    ]
    env = make_envelope({"routes": routes_status, "overall_health": "NOT_VERIFIED"}, ts, real=False)
    env["provenance"] = {
        "source": "LOCAL_ROUTE_CONFIGURATION_ONLY",
        "safety_mode": "PAPER_MODE",
        "freshness_sec": None,
        "exchange_feed_verified": False,
        "classification": "UPSTREAM_TELEMETRY_NOT_MEASURED"
    }'''
assert s.count(old)==1
s=s.replace(old,new,1)
old='"token_hours_remaining": round(hours, 2) if hours else 23.5,'
assert s.count(old)==1
s=s.replace(old,'"token_hours_remaining": round(hours, 2) if hours is not None else None,',1)
ast.parse(s)
p.write_text(s,encoding='utf-8')
print('MARKET_TRUTH_LABELS_PATCH_OK')
