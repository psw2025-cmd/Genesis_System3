# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-04T08:32:51.839817Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (BROKER_NOT_CONNECTED)
- Funds semantic proof: `False`
- Mandatory chains ready: `0/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- BANKNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- FINNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False
- MIDCPNIFTY: BLOCKED http=200 source=dhan status=NO_DHAN_DATA contracts=0 stale=False

## Blockers
- BROKER:BROKER_NOT_CONNECTED
- FUNDS:TOKEN_EXPIRED_OR_INVALID
- CHAIN:NIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:BANKNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:FINNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
- CHAIN:MIDCPNIFTY:NO_CURRENT_VERIFIED_DHAN_CHAIN
