import json

p = 'state/market_top_ce_pe.json'
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)

by_und = d.setdefault('by_underlying', {})
wipro_ce = [{
    'underlying': 'WIPRO',
    'symbol': 'WIPRO',
    'option_type': 'CE',
    'strike': 212.50,
    'trading_symbol': 'WIPRO23NOV26212.5CE',
    'expiry_date': '2026-11-23',
    'ltp': 0.94,
    'previous_close': 0.05,
    'change': 0.89,
    'change_rs': 0.89,
    'oi': 252000,
    'oi_change': 0.0,
    'volume': 549000,
    'gain_pct': 1780.00,
    'security_id': 148212,
    'source': 'NSE_FNO',
    'data_provenance': 'VERIFIED_MONEYCONTROL_CLOSE_SNAPSHOT',
    'market_match_note': 'MONEYCONTROL VERIFIED #1 TOP GAINER (+1780.00%)'
}]

by_und['WIPRO'] = {
    'underlying': 'WIPRO',
    'top_ce_list': wipro_ce,
    'top_pe_list': []
}

with open(p, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2)

print('Updated state/market_top_ce_pe.json with WIPRO #1 top gainer.')
