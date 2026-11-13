import json

with open('state/chain_cache/NIFTY.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Keys:', list(data.keys()))
print('spot_price:', data.get('spot_price'), 'spot:', data.get('spot'))
print('data_source:', data.get('data_source'), 'source:', data.get('source'))
print('contracts count:', len(data.get('contracts', [])))
if data.get('contracts'):
    print('First contract keys:', list(data['contracts'][0].keys()))
