"""Public NSE quote fallback, NOT a Moneycontrol scrape or next-open forecast.

Usage: python -m scripts.nse_option_gainers --symbol NIFTY --expiry 29-Sep-2026
Ranks only the requested symbol/expiry. No all-market coverage claim.
"""
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from math import isfinite
from urllib.parse import urlencode
from urllib.request import Request, urlopen

IST = timezone(timedelta(hours=5, minutes=30))


def number(value):
    if isinstance(value, bool):
        raise ValueError('boolean quote')
    value = float(value)
    if not isfinite(value):
        raise ValueError('nonfinite quote')
    return value


def rank(raw, symbol, expiry, observed_at, min_volume=100, min_previous=1):
    if observed_at.tzinfo is None:
        raise ValueError('observation timezone required')
    if min_volume < 0 or min_previous <= 0:
        raise ValueError('invalid filters')
    expected = datetime.strptime(expiry, '%d-%b-%Y').date()
    records = json.loads(raw)['records']
    source_time = datetime.strptime(records['timestamp'], '%d-%b-%Y %H:%M:%S').replace(tzinfo=IST)
    age = (observed_at - source_time).total_seconds()
    if age < -60 or age > 900:
        raise ValueError('stale or future source timestamp')
    if expected < source_time.date():
        raise ValueError('expired contract')
    rows, seen, rejected = [], set(), 0
    for pair in records['data']:
        for side in ('CE', 'PE'):
            quote = pair.get(side)
            if not quote:
                continue
            try:
                if quote['underlying'] != symbol:
                    raise ValueError('symbol mismatch')
                if datetime.strptime(quote['expiryDate'], '%d-%m-%Y').date() != expected:
                    raise ValueError('expiry mismatch')
                strike = number(quote['strikePrice'])
                last = number(quote['lastPrice'])
                change = number(quote['change'])
                previous = last - change
                volume = number(quote['totalTradedVolume'])
                bid, ask = number(quote['buyPrice1']), number(quote['sellPrice1'])
                if strike <= 0 or last <= 0 or previous < min_previous or volume < min_volume:
                    raise ValueError('price or volume filter')
                if bid <= 0 or ask < bid:
                    raise ValueError('invalid two-sided quote')
                pct = 100 * change / previous
                if abs(pct - number(quote['pChange'])) > 0.1:
                    raise ValueError('inconsistent percent change')
                key = (symbol, expiry, strike, side)
                if key in seen:
                    raise ValueError('duplicate contract')
                seen.add(key)
                rows.append(dict(symbol=symbol, expiry=expiry, strike=strike, side=side,
                                 last_price=last, previous_close_derived=round(previous, 6),
                                 gain_pct=round(pct, 4), volume=volume,
                                 bid=bid, ask=ask))
            except (KeyError, TypeError, ValueError):
                rejected += 1
    if not rows:
        raise ValueError('no usable quotes')
    rows.sort(key=lambda r: (-r['gain_pct'], r['strike'], r['side']))
    return dict(source='NSE_PUBLIC_OPTION_CHAIN', source_timestamp=source_time.isoformat(),
                first_observed_at=observed_at.isoformat(), source_sha256=sha256(raw).hexdigest(),
                scope=dict(symbol=symbol, expiry=expiry), coverage='REQUESTED_SYMBOL_EXPIRY_ONLY',
                minimum_volume=min_volume, minimum_previous_close=min_previous,
                accepted_count=len(rows), rejected_count=rejected,
                gainers=[r for r in rows if r['gain_pct'] > 0],
                non_gainer_count=sum(r['gain_pct'] <= 0 for r in rows),
                forecast_status='NOT_A_FORECAST', expected_next_open=None, orders_allowed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--expiry', required=True)
    parser.add_argument('--kind', choices=['Indices', 'Equity'], default='Indices')
    args = parser.parse_args()
    url = 'https://www.nseindia.com/api/option-chain-v3?' + urlencode(
        dict(type=args.kind, symbol=args.symbol, expiry=args.expiry))
    request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'System3-Research/1.0'})
    with urlopen(request, timeout=25) as response:
        if 'application/json' not in response.headers.get('Content-Type', ''):
            raise ValueError('non-JSON response; no bypass or fake fallback')
        raw = response.read(10000001)
    if len(raw) > 10000000:
        raise ValueError('response too large')
    result = rank(raw, args.symbol, args.expiry, datetime.now(timezone.utc))
    result['source_url'] = url
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
