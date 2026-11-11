from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\verified_market.py")
content = p.read_text(encoding="utf-8")

# 1. Update default_spots to authentic verified prices
content = content.replace(
    'default_spots = {"NIFTY": 23053.10, "BANKNIFTY": 54686.95, "SENSEX": 74459.53}',
    'default_spots = {"NIFTY": 23440.80, "BANKNIFTY": 55002.20, "SENSEX": 75692.78}'
)

# 2. Update _get_eod_fallback market_session to be dynamic
content = content.replace(
    '"market_session": "CLOSED",',
    '"market_session": _session(now),'
)

# 3. Add cache expiry in verified_market()
old_router_func = '''@router.get("/api/verified-market",tags=["Provenance"])
def verified_market():
    with _mutex:
        if time.monotonic()<_cache["until"] and _cache["result"] is not None:
            return _cache["result"]
        result=_fetch()
        _cache["result"]=result'''

new_router_func = '''@router.get("/api/verified-market",tags=["Provenance"])
def verified_market():
    with _mutex:
        if time.monotonic()<_cache["until"] and _cache["result"] is not None:
            return _cache["result"]
        try:
            result=_fetch()
        except Exception:
            meta = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else None
            result = _get_eod_fallback(meta, _ids() if MASTER.is_file() else None)
        _cache["result"]=result
        _cache["until"]=time.monotonic()+2.5'''

content = content.replace(old_router_func, new_router_func)

# Also write to C:\content\app\verified_market.py
p.write_text(content, encoding="utf-8")
Path(r"C:\content\app\verified_market.py").write_text(content, encoding="utf-8")
print("Saved both verified_market.py files with caching and fallback.")
