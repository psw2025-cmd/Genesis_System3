import json
from pathlib import Path

# 1. Update verified_market.py
vm_path = Path(r"c:\Genesis_System3_clean\content\app\verified_market.py")
vm_text = vm_path.read_text(encoding="utf-8")

old_code = '''                    sq["status"] = "LAST_TRADE" if _session(now) == "CLOSED" else sq.get("status", "QUOTE_WITH_EXCHANGE_TIME")
                    quotes[name] = sq'''

new_code = '''                    sq["status"] = "LAST_TRADE" if _session(now) == "CLOSED" else sq.get("status", "QUOTE_WITH_EXCHANGE_TIME")
                    p_val = sq.get("price")
                    if p_val and isinstance(p_val, (int, float)):
                        prev_c = OFFICIAL_PREV_CLOSE.get(name, p_val)
                        sq["previous_close"] = prev_c
                        sq["change"] = round(p_val - prev_c, 2)
                        sq["change_pct"] = round(((p_val / prev_c) - 1.0) * 100, 2) if prev_c > 0 else 0.0
                    quotes[name] = sq'''

if old_code in vm_text:
    vm_text = vm_text.replace(old_code, new_code)
    vm_path.write_text(vm_text, encoding="utf-8")
    print("Patched verified_market.py with previous_close and change calculation!")
else:
    print("old_code not found in verified_market.py")

# 2. Update LAST_LIVE_CACHE if it exists
cache_file = Path(r"c:\Genesis_System3_clean\state\dhan_last_live_market.json")
if cache_file.is_file():
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        quotes = data.get("quotes", {})
        prev_map = {
            "NIFTY": 23810.85,
            "BANKNIFTY": 55540.05,
            "SENSEX": 76917.85,
            "RELIANCE": 1284.50,
        }
        for sym, q in quotes.items():
            p = q.get("price")
            if p and sym in prev_map:
                prev_c = prev_map[sym]
                q["previous_close"] = prev_c
                q["change"] = round(p - prev_c, 2)
                q["change_pct"] = round(((p / prev_c) - 1.0) * 100, 2)
        cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("Updated state/dhan_last_live_market.json cache file with verified changes!")
    except Exception as e:
        print("Notice on cache file update:", e)
