from pathlib import Path
import ast
p=Path(r'C:\Genesis_System3_clean\content\app\app.py')
s=p.read_text(encoding='utf-8')
start=s.index('@app.get("/api/options/gainers"')
end=s.index('@app.get("/api/options/oi-buildup"',start)
chunk=s[start:end]
chunk=chunk.replace('    equity_fo = {"COLPAL", "RELIANCE"}','    equity_fo = {c.get("symbol") for c in ce_movers + pe_movers if c.get("symbol") and c.get("symbol") not in indices}')
chunk=chunk.replace('    top_ce = (ce_idx[:20] + ce_eq[:10]) if ce_eq else ce_movers[:30]','    top_ce = ce_movers[:30]')
chunk=chunk.replace('    top_pe = (pe_idx[:20] + pe_eq[:10]) if pe_eq else pe_movers[:30]','    top_pe = pe_movers[:30]')
chunk=chunk.replace('    if chain_dir.is_dir():','    newest_cache_age = None\n    if chain_dir.is_dir():\n        newest_cache_age = min((max(0.0, time.time() - f.stat().st_mtime) for f in chain_dir.glob("*.json")), default=None)')
chunk=chunk.replace('                contracts = chain_data.get("contracts", [])','                contracts = chain_data.get("contracts", [])\n                file_age_sec = max(0.0, time.time() - chain_file.stat().st_mtime)')
chunk=chunk.replace('                        "data_provenance": "VERIFIED_DHAN_CLOSE_SNAPSHOT"','                        "data_provenance": "LOCAL_CACHED_CHAIN",\n                        "cache_age_sec": round(file_age_sec, 1),\n                        "expiry": c.get("expiry") or c.get("expiry_date"),\n                        "security_id": c.get("security_id") or c.get("securityId"),\n                        "trading_symbol": c.get("trading_symbol") or c.get("symbol")')
chunk=chunk.replace('        "source": "DHAN_VERIFIED_F_AND_O_CHAINS",','        "source": "LOCAL_CACHED_OPTION_CHAINS",\n        "fresh_contracts_count": sum(1 for c in ce_movers + pe_movers if c["cache_age_sec"] <= 180),\n        "cache_newest_age_seconds": round(newest_cache_age, 1) if newest_cache_age is not None else None,')
chunk=chunk.replace('"snapshot_type": "LIVE_INTRADAY_EXCHANGE_FEED" if is_open else "LAST_VERIFIED_EXCHANGE_SNAPSHOT"','"snapshot_type": "LOCAL_CACHE_NOT_LIVE_VERIFIED"')
chunk=chunk.replace('}, ts, real=True)','}, ts, real=False)')
chunk=chunk.replace('"source": "DHAN_VERIFIED_F_AND_O_CHAINS"','"source": "LOCAL_CACHED_OPTION_CHAINS"')
chunk=chunk.replace('"freshness_sec": 0','"freshness_sec": round(newest_cache_age, 1) if newest_cache_age is not None else None')
chunk=chunk.replace('"exchange_feed_verified": True','"exchange_feed_verified": False')
chunk=chunk.replace('"classification": "VERIFIED_EXCHANGE_SNAPSHOT"','"classification": "STALE_CACHED_OPTION_CHAINS" if newest_cache_age is None or newest_cache_age > 180 else "RECENT_CACHE_NOT_EXCHANGE_VERIFIED"')
assert 'equity_fo = {"COLPAL", "RELIANCE"}' not in chunk
s=s[:start]+chunk+s[end:]
start=s.index('@app.get("/api/chain/{symbol}"')
end=s.index('@app.get("/api/market/top-gainers"',start)
chunk=s[start:end]
chunk=chunk.replace('    if cdata:\n','    cache_file = APP_DIR.parent.parent / "state" / "chain_cache" / f"{sym}.json"\n    cache_age_sec = max(0.0, time.time() - cache_file.stat().st_mtime) if cache_file.is_file() else None\n    if cdata:\n',1)
chunk=chunk.replace('"status": "LIVE_CHAIN" if is_open else "VERIFIED_CLOSE_SNAPSHOT"','"status": "RECENT_LOCAL_CACHE" if cache_age_sec is not None and cache_age_sec <= 180 else "STALE_LOCAL_CACHE",\n            "cache_age_seconds": round(cache_age_sec, 1) if cache_age_sec is not None else None')
chunk=chunk.replace('"source": "DHAN_VERIFIED_OPTION_CHAIN"','"source": "LOCAL_OPTION_CHAIN_CACHE"')
chunk=chunk.replace('real=True','real=False').replace('"freshness_sec": 0','"freshness_sec": round(cache_age_sec, 1) if cache_age_sec is not None else None').replace('"exchange_feed_verified": True','"exchange_feed_verified": False').replace('"classification": "VERIFIED_EXCHANGE_SNAPSHOT"','"classification": "LOCAL_CACHE_NOT_EXCHANGE_VERIFIED"')
fallback=chunk.index('    # Fallback to SCANNER proximity strikes')
chunk=chunk[:fallback]+'''    return make_envelope({
        "underlying": sym, "symbol": sym, "contracts": [],
        "contracts_count": 0, "status": "NO_AUTHENTICATED_CHAIN_SNAPSHOT",
        "source": "NO_CHAIN_AVAILABLE", "next_action": "Fetch this security ID and expiry from Dhan option chain"
    }, ts, real=False)

'''
s=s[:start]+chunk+s[end:]
start=s.index('@app.get("/api/market/top-gainers"')
chunk=s[start:]
chunk=chunk.replace('}, ts, real=True)','}, ts, real=False)',1)
chunk=chunk.replace('"source": "DHAN_VERIFIED_F_AND_O_CHAINS"','"source": "LOCAL_CACHED_OPTION_CHAINS"')
chunk=chunk.replace('"freshness_sec": 0','"freshness_sec": gdata.get("cache_newest_age_seconds")')
chunk=chunk.replace('"exchange_feed_verified": True','"exchange_feed_verified": False')
chunk=chunk.replace('"classification": "VERIFIED_EXCHANGE_SNAPSHOT"','"classification": "CACHED_GAINS_NOT_EXCHANGE_VERIFIED"')
s=s[:start]+chunk
ast.parse(s)
p.write_text(s,encoding='utf-8')
print('OPTION_CONTRACT_PROVENANCE_AND_EQUITY_UNIVERSE_PATCH_OK')
