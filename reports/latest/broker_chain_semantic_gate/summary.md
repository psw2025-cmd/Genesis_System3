# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-04T09:37:54.493551Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (TIMEOUTERROR)
- Funds semantic proof: `True`
- Mandatory chains ready: `1/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- BANKNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- FINNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- MIDCPNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False

## Blockers
- BROKER:TIMEOUTERROR
- CHAIN:NIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:BANKNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:FINNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
