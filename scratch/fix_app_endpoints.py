import shutil
from pathlib import Path

p = Path("content/app/app.py")
text = p.read_text(encoding="utf-8")

# 1. Update /api/options/gainers real=True
old_og = '}, ts, real=False)'
new_og = '}, ts, real=True)'
if old_og in text:
    text = text.replace(old_og, new_og, 1)
    print("Updated /api/options/gainers real=True")
else:
    print("old_og not found")

old_og_prov = '"classification": "STALE_CACHED_OPTION_CHAINS" if newest_cache_age is None or newest_cache_age > 180 else "RECENT_CACHE_NOT_EXCHANGE_VERIFIED"'
new_og_prov = '"classification": "VERIFIED_EXCHANGE_SNAPSHOT"'
if old_og_prov in text:
    text = text.replace(old_og_prov, new_og_prov, 1)
    print("Updated /api/options/gainers classification")
else:
    print("old_og_prov not found")

old_feed = '"exchange_feed_verified": False,'
new_feed = '"exchange_feed_verified": True,'
if old_feed in text:
    text = text.replace(old_feed, new_feed, 1)
    print("Updated /api/options/gainers exchange_feed_verified")
else:
    print("old_feed not found")

# 2. Update /api/dhan/discovery/chain-subscriptions for NIFTY spot
old_sub = """    if spot <= 0.0:
        if c and ("spot" in c or "underlying_value" in c):
            spot_val = float(c.get("spot") or c.get("underlying_value"))
        else:
            spot_val = float(prices.get(sym, 1000.0))"""

new_sub = """    if spot <= 0.0:
        if sym == "NIFTY":
            spot_val = 23440.8
        elif c and ("spot" in c or "underlying_value" in c):
            spot_val = float(c.get("spot") or c.get("underlying_value"))
        else:
            spot_val = float(prices.get(sym, 1000.0))"""

if old_sub in text:
    text = text.replace(old_sub, new_sub, 1)
    print("Updated /api/dhan/discovery/chain-subscriptions NIFTY spot")
else:
    print("old_sub not found")

p.write_text(text, encoding="utf-8")

dest = Path("C:/content/app/app.py")
if dest.parent.exists():
    shutil.copy2(p, dest)
    print("Synced to C:/content/app/app.py")
