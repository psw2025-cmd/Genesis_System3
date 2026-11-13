import json

with open('state/market_top_ce_pe.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ce_gainers = data.get('ce_gainers', [])
print(f'Total CE gainers in state/market_top_ce_pe.json: {len(ce_gainers)}')
for g in ce_gainers[:15]:
    print(f"  {g.get('symbol')} {g.get('strike')} {g.get('option_type')}: ltp={g.get('ltp')} chg={g.get('change_pct')}%")
