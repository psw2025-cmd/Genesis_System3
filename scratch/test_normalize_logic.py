import json

with open('state/chain_cache/NIFTY.json', 'r', encoding='utf-8') as f:
    snap = json.load(f)

def _optional_float(value):
    if value is None: return None
    try: return float(value)
    except: return None

def normalize_index_chain_exchange(chain, underlying):
    if not isinstance(chain, dict):
        return {
            "underlying": underlying.upper(),
            "spot": 0.0,
            "spot_price": 0.0,
            "contracts": [],
            "total_contracts": 0,
            "iv_percentile": 50.0,
            "oi_change": "+0",
            "total_oi_change": 0,
            "pcr": 1.0,
            "data_source": "dhan",
            "status": "EMPTY",
        }

    out = dict(chain)
    out["underlying"] = underlying.upper()
    spot = _optional_float(out.get("spot") or out.get("spot_price") or out.get("underlying_spot")) or 0.0
    out["spot"] = spot
    out["spot_price"] = spot

    contracts = out.get("contracts") or []
    out["total_contracts"] = len(contracts)

    if out.get("total_oi_change") is None:
        total_oi_change = sum(int(c.get("oi_change") or 0) for c in contracts if isinstance(c, dict))
        out["total_oi_change"] = total_oi_change
    else:
        total_oi_change = int(out.get("total_oi_change") or 0)

    if not out.get("oi_change"):
        out["oi_change"] = f"{total_oi_change:+d}" if total_oi_change != 0 else "+0"

    if out.get("iv_percentile") is None:
        valid_ivs = [float(c.get("iv") or 0) for c in contracts if isinstance(c, dict) and float(c.get("iv") or 0) > 0]
        if valid_ivs:
            atm_ivs = [
                float(c["iv"])
                for c in contracts
                if isinstance(c, dict)
                and abs(float(c.get("strike") or 0) - spot) <= (spot * 0.015)
                and float(c.get("iv") or 0) > 0
            ]
            ref_iv = (sum(atm_ivs) / len(atm_ivs)) if atm_ivs else (sum(valid_ivs) / len(valid_ivs))
            out["iv_percentile"] = round((sum(1 for iv in valid_ivs if iv <= ref_iv) / len(valid_ivs)) * 100, 1)
        else:
            out["iv_percentile"] = 50.0

    out["data_source"] = "dhan"
    if not out.get("status"):
        out["status"] = "OK"

    return out

norm = normalize_index_chain_exchange(snap, 'NIFTY')
print('Normalized NIFTY:')
print('spot:', norm['spot'], 'spot_price:', norm['spot_price'])
print('contracts:', len(norm['contracts']))
print('total_oi_change:', norm['total_oi_change'])
print('oi_change:', norm['oi_change'])
print('iv_percentile:', norm['iv_percentile'])
print('data_source:', norm['data_source'])
