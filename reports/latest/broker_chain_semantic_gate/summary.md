# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-04T11:30:51.011162Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (BROKER_NOT_CONNECTED)
- Funds semantic proof: `False`
- Mandatory chains ready: `4/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False
- BANKNIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False
- FINNIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False
- MIDCPNIFTY: PASS http=200 source=dhan status=MARKET_CLOSED_DHAN_SNAPSHOT contracts=160 stale=False

## Blockers
- BROKER:BROKER_NOT_CONNECTED
- FUNDS:TOKEN_EXPIRED_OR_INVALID
