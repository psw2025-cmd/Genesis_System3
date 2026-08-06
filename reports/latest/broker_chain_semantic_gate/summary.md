# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-06T10:33:57.782358Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `True` (CONNECTED)
- Funds semantic proof: `True`
- Mandatory chains ready: `1/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False
- BANKNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- FINNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- MIDCPNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False

## Blockers
- CHAIN:BANKNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:FINNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:MIDCPNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
