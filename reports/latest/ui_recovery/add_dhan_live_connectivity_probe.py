from pathlib import Path
import ast
p=Path(r'C:\Genesis_System3_clean\content\app\app.py')
s=p.read_text(encoding='utf-8')
marker='@app.get("/api/route-health", name="route_health_telemetry")'
assert s.count(marker)==1
addition='''@app.get("/api/dhan/live-connectivity", name="dhan_live_connectivity")
async def dhan_live_connectivity():
    """Explicit read-only authenticated Dhan profile check; no account data returned."""
    import time as _time
    import requests as _requests
    from core.utils.env_loader import get_dhan_token
    ts = utcnow()
    token, source, provider, hours, expiry, unavailable = get_dhan_token()
    if unavailable or not token:
        return make_envelope({
            "status": "AUTH_TOKEN_MISSING",
            "http_status": None, "latency_ms": None,
            "token_expiry_utc": None, "token_hours_remaining": None,
            "next_action": "Configure valid Dhan read-only credentials"
        }, ts, real=False)
    start = _time.perf_counter()
    try:
        response = _requests.get(
            "https://api.dhan.co/v2/profile",
            headers={"access-token": token, "Content-Type": "application/json"},
            timeout=(3, 7),
        )
        latency_ms = round((_time.perf_counter() - start) * 1000, 1)
        code = response.status_code
        # Profile is sensitive: do not expose response body, name, client ID or token.
        status = "CONNECTED_AUTHENTICATED" if code == 200 else (
            "AUTH_REJECTED" if code in (401, 403) else
            "RATE_LIMITED" if code == 429 else "UPSTREAM_HTTP_ERROR"
        )
        return make_envelope({
            "status": status, "http_status": code,
            "latency_ms": latency_ms,
            "token_expiry_utc": expiry.isoformat() if expiry else None,
            "token_hours_remaining": round(hours, 2) if hours is not None else None,
            "next_action": "NONE" if code == 200 else "Inspect Dhan authentication or HTTP response code",
        }, ts, real=(code == 200))
    except _requests.Timeout:
        status = "DHAN_TIMEOUT"
    except _requests.RequestException:
        status = "DHAN_NETWORK_ERROR"
    return make_envelope({
        "status": status, "http_status": None,
        "latency_ms": round((_time.perf_counter() - start) * 1000, 1),
        "token_expiry_utc": expiry.isoformat() if expiry else None,
        "token_hours_remaining": round(hours, 2) if hours is not None else None,
        "next_action": "Check Dhan API reachability and network",
    }, ts, real=False)


'''
s=s.replace(marker,addition+marker,1)
ast.parse(s)
p.write_text(s,encoding='utf-8')
print('DHAN_LIVE_READONLY_PROBE_ADDED')
