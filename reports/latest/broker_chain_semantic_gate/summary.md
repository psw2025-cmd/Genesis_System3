# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-04T07:35:54.053519Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (TIMEOUTERROR)
- Funds semantic proof: `True`
- Mandatory chains ready: `2/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- BANKNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- FINNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- MIDCPNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False

## Blockers
- BROKER:TIMEOUTERROR
- CHAIN:FINNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:MIDCPNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
