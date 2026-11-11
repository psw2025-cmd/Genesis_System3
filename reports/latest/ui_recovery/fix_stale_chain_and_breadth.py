from pathlib import Path
import ast
p=Path(r'C:\Genesis_System3_clean\content\app\app.py')
s=p.read_text(encoding='utf-8')
old='''        "newest_mtime_ist": newest_ist,
        "master_rows": master_rows,'''
new='''        "newest_mtime_ist": newest_ist,
        "newest_age_seconds": round(max(0.0, time.time() - max(mtimes)), 1) if mtimes else None,
        "oldest_age_seconds": round(max(0.0, time.time() - min(mtimes)), 1) if mtimes else None,
        "fresh_snapshots_count": sum(1 for t in mtimes if 0 <= time.time() - t <= 180),
        "master_rows": master_rows,'''
assert s.count(old)==1
s=s.replace(old,new,1)
old='''        "chain_cache_newest_mtime_ist": cm["newest_mtime_ist"],'''
new='''        "chain_cache_newest_mtime_ist": cm["newest_mtime_ist"],
        "chain_cache_newest_age_seconds": cm["newest_age_seconds"],
        "chain_cache_oldest_age_seconds": cm["oldest_age_seconds"],
        "chain_cache_fresh_snapshots_count": cm["fresh_snapshots_count"],
        "chain_cache_status": "FRESH_CACHE" if cm["fresh_snapshots_count"] == cm["readable_files"] and cm["readable_files"] > 0 else "STALE_OR_INCOMPLETE_CACHE",'''
assert s.count(old)==1
s=s.replace(old,new,1)
old='''    data = {
        "advances": 1382,
        "declines": 1182,
        "unchanged": 175,
        "ad_ratio": 1.17,
        "total_traded": 2739,
        "market_sentiment": "MODERATELY_BULLISH"
    }
    return make_envelope(data, ts)'''
new='''    # Do not manufacture NSE-wide breadth from static demonstration figures.
    data = {
        "advances": None,
        "declines": None,
        "unchanged": None,
        "ad_ratio": None,
        "total_traded": None,
        "market_sentiment": None,
        "status": "NO_AUTHENTICATED_MARKET_BREADTH_FEED",
        "next_action": "Connect timestamped licensed NSE market breadth provider"
    }
    return make_envelope(data, ts, real=False)'''
assert s.count(old)==1
s=s.replace(old,new,1)
ast.parse(s)
p.write_text(s,encoding='utf-8')
print('STALE_CACHE_AND_FAKE_BREADTH_PATCH_OK')
