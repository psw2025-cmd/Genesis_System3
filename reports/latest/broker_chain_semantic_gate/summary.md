# Broker and Chain Semantic Gate

- Generated UTC: `2026-08-06T04:20:42.644328Z`
- Final verdict: **BLOCKED_NOT_TRADE_READY**
- Broker connected: `False` (TIMEOUTERROR)
- Funds semantic proof: `False`
- Mandatory chains ready: `0/4`
- Analyzer mode: `ON`
- Live trading: `OFF`
- Order endpoints called: `false`
- Secrets written: `false`

## Mandatory chains
- NIFTY: BLOCKED http=503 source=None status=None contracts=0 stale=False
- BANKNIFTY: BLOCKED http=0 source=None status=None contracts=0 stale=False
- FINNIFTY: BLOCKED http=0 source=None status=None contracts=0 stale=False
- MIDCPNIFTY: BLOCKED http=0 source=None status=None contracts=0 stale=False

## Blockers
- BROKER:TIMEOUTERROR
- FUNDS:TIMEOUTERROR
- CHAIN:NIFTY:HTTP_503
- CHAIN:BANKNIFTY:TIMEOUTERROR
- CHAIN:FINNIFTY:TIMEOUTERROR
- CHAIN:MIDCPNIFTY:TIMEOUTERROR
