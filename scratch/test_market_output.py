import urllib.request
import json

print('=== 1. /api/verified-market ===')
with urllib.request.urlopen('http://127.0.0.1:8008/api/verified-market') as r:
    vm = json.loads(r.read().decode())
    quotes = vm.get('quotes', {})
    for sym in ['NIFTY', 'BANKNIFTY', 'SENSEX']:
        q = quotes.get(sym, {})
        print(f"{sym}: Price={q.get('price')} PrevClose={q.get('previous_close')} Change={q.get('change')} ChangePct={q.get('change_pct')}%")

print('\n=== 2. /api/market ===')
with urllib.request.urlopen('http://127.0.0.1:8008/api/market') as r:
    mkt = json.loads(r.read().decode())
    for q in mkt.get('data', {}).get('quotes', []):
        if q.get('symbol') in ['NIFTY', 'BANKNIFTY', 'SENSEX', 'RELIANCE']:
            print(f"{q.get('symbol')}: Price={q.get('price')} PrevClose={q.get('previous_close')} Change={q.get('change')} ChangePct={q.get('change_pct')}%")
