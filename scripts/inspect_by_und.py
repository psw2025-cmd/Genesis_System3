import json

with open('state/market_top_ce_pe.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

by_und = d.get('by_underlying', {})
print('Underlyings in by_underlying:', list(by_und.keys()))

for sym in ['WIPRO', 'RELIANCE', 'NIFTY', 'BANKNIFTY']:
    if sym in by_und:
        print(f'=== {sym} ===')
        ce = by_und[sym].get('top_ce_list', [])
        pe = by_und[sym].get('top_pe_list', [])
        print(f'  CE count: {len(ce)}, PE count: {len(pe)}')
        if ce:
            print('  First CE:', ce[0])
