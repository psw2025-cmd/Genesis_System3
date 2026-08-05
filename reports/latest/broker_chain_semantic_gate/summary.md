# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-05T05:37:51.961466Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `True` (CONNECTED)
- Funds semantic proof: `True`
- Mandatory chains ready: `3/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: BLOCKED http=0 source=None status=None contracts=0 stale=False
- BANKNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- FINNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- MIDCPNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False

## Blockers
- CHAIN:NIFTY:TIMEOUTERROR
