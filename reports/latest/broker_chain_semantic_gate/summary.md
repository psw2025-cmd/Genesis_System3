# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-05T06:33:49.879912Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `True` (CONNECTED)
- Funds semantic proof: `True`
- Mandatory chains ready: `2/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- BANKNIFTY: BLOCKED http=0 source=None status=None contracts=0 stale=False
- FINNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- MIDCPNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False

## Blockers
- CHAIN:BANKNIFTY:TIMEOUTERROR
- CHAIN:FINNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
