# Broker and Chain Semantic Gate

- Generated UTC: `2026-07-15T11:13:46.889703Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (HTTP_502)
- Funds semantic proof: `False`
- Mandatory chains ready: `3/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False
- BANKNIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False
- FINNIFTY: BLOCKED http=502 source=None status=None contracts=0 stale=False
- MIDCPNIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False

## Blockers
- BROKER:HTTP_502
- FUNDS:HTTP_502
- CHAIN:FINNIFTY:HTTP_502
