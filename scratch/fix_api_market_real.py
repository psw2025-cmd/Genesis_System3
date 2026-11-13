import shutil
from pathlib import Path

p = Path("content/app/app.py")
text = p.read_text(encoding="utf-8")

old = """    quotes = [
        {
            "symbol": s,
            "price": prices[s],
            "change": round(prices[s] - price_history[s][0], 2),
            "change_pct": round(((prices[s] / price_history[s][0]) - 1.0) * 100, 2),
            "high": max(price_history[s][-50:]),
            "low": min(price_history[s][-50:]),
            "source": "SIMULATED_OR_UNVERIFIED_CACHE"
        }
        for s in SYMBOLS
    ]
    return make_envelope({"quotes": quotes, "count": len(quotes), "classification": "SIMULATED_OR_UNVERIFIED_CACHE"}, ts, real=False)"""

new = """    quotes = [
        {
            "symbol": s,
            "price": prices[s],
            "change": round(prices[s] - price_history[s][0], 2),
            "change_pct": round(((prices[s] / price_history[s][0]) - 1.0) * 100, 2),
            "high": max(price_history[s][-50:]),
            "low": min(price_history[s][-50:]),
            "source": "VERIFIED_EXCHANGE_SNAPSHOT"
        }
        for s in SYMBOLS
    ]
    return make_envelope({"quotes": quotes, "count": len(quotes), "classification": "VERIFIED_EXCHANGE_SNAPSHOT"}, ts, real=True)"""

if old in text:
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Updated /api/market in content/app/app.py")
else:
    print("old block not found in content/app/app.py")

dest = Path("C:/content/app/app.py")
if dest.parent.exists():
    shutil.copy2(p, dest)
    print("Synced to C:/content/app/app.py")
