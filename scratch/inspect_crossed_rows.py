import urllib.request
import json

for sym in ['BANKNIFTY', 'FINNIFTY']:
    url = f'https://genesis-system3-web-802404398783.asia-south1.run.app/api/chain/{sym}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        contracts = data.get('contracts', [])
        print(f"=== {sym} (Total: {len(contracts)}) ===")
        for idx, c in enumerate(contracts):
            bid = c.get('bidPrice', c.get('top_bid_price', c.get('bid')))
            ask = c.get('offerPrice', c.get('top_ask_price', c.get('ask')))
            try:
                if bid is not None and ask is not None and float(ask) < float(bid):
                    print(f"Row {idx}: strike={c.get('strike')} opt={c.get('option_type')} bid={bid} ask={ask} ltp={c.get('ltp')}")
            except Exception as e:
                pass
    except Exception as e:
        print(f"Error fetching {sym}: {e}")
