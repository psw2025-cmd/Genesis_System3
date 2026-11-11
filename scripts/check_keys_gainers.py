import json

with open('state/market_top_ce_pe.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Keys in json:', list(data.keys()))
if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, list):
            print(f'Key: {k}, length: {len(v)}')
            if v and isinstance(v[0], dict):
                print(f'First item of {k}:', v[0].get('symbol'), v[0].get('strike'), v[0].get('change_pct'))
