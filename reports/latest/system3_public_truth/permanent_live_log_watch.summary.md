# Permanent Live Log Watch

Generated: 2026-07-10T09:05:47.619Z
Base: https://genesis-system3-backend.onrender.com
Final verdict: **BLOCKED_NOT_TRADE_READY**
Truth control visible: **true**

## Runtime Log Sources Captured
- Browser console entries: 1
- Page errors: 0
- Request failures: 0
- Network responses: 80

## Dhan Chain Truth
- BLOCKED /api/chain/NIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/BANKNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/FINNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/MIDCPNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/SENSEX source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS

## API Endpoints
- PASS 200 /api/auth/status
- PASS 200 /api/deploy/info
- PASS 200 /api/health
- PASS 200 /api/state
- PASS 200 /api/broker/dhan/status
- PASS 200 /api/broker/funds
- PASS 200 /api/broker/holdings
- PASS 200 /api/broker/positions/live
- PASS 200 /api/chain/NIFTY
- PASS 200 /api/chain/BANKNIFTY
- PASS 200 /api/chain/FINNIFTY
- PASS 200 /api/chain/MIDCPNIFTY
- PASS 200 /api/chain/SENSEX
- PASS 200 /api/gain_rank
- PASS 200 /api/pnl
- PASS 200 /api/auto_gates

## Screenshots
- PASS Truth Control size=132224
- PASS Genesis Brain size=213429
- PASS E2E Proof size=116207
- PASS Overview size=99100
- PASS Option Chain size=58481
- PASS Signals size=70245
- PASS Paper Trades size=97107
- PASS Positions size=53409
- PASS Broker size=89305
- PASS Performance size=53084
- PASS ML Model size=62926
- PASS Live Gate size=88686

## Infrastructure Blockers
- none

## Trading Readiness Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS