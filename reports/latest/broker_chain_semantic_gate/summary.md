# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-05T07:34:15.119928Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (TOKEN_EXPIRED_OR_INVALID)
- Funds semantic proof: `False`
- Mandatory chains ready: `4/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- BANKNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- FINNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False
- MIDCPNIFTY: PASS http=200 source=dhan status=MARKET_OPEN contracts=160 stale=False

## Blockers
- BROKER:TOKEN_EXPIRED_OR_INVALID
- FUNDS:TOKEN_EXPIRED_OR_INVALID
