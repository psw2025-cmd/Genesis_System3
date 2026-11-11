import sys
sys.path.insert(0, '.')
import json
from dashboard.backend.chain_adapter import normalize_index_chain_exchange

with open('state/chain_cache/NIFTY.json', 'r', encoding='utf-8') as f:
    snap = json.load(f)

norm = normalize_index_chain_exchange(snap, 'NIFTY')
print('Keys in norm:', list(norm.keys()))
print('spot_price:', norm.get('spot_price'), 'spot:', norm.get('spot'))
print('iv_percentile:', norm.get('iv_percentile'))
print('oi_change:', norm.get('oi_change'))
print('total_oi_change:', norm.get('total_oi_change'))
print('contracts count:', len(norm.get('contracts', [])))
if norm.get('contracts'):
    print('First contract keys:', list(norm['contracts'][0].keys()))
