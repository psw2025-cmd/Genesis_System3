# Dashboard Live UI Proof

Generated: 2026-07-14T10:11:53.503Z
Base: https://genesis-system3-backend.onrender.com
Required symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
Optional symbols: SENSEX
Final verdict: **PASS**
Owner badge visible: **true**
Safety labels visible: **true**
ML proof visible: **true**
Paper truth visible: **true**
Trader readiness panel visible: **true**
Truth control visible: **true**

## Visual Requirements
- PASS OWNER_BADGE_VISIBLE
- PASS SAFETY_LABELS_VISIBLE
- PASS ML_PROOF_VISIBLE
- PASS PAPER_TRUTH_VISIBLE
- PASS MOBILE_SCREENSHOT_PRESENT
- PASS MOBILE_OWNER_OR_RESPONSIVE_UI

## Chain Truth
- PASS (required) /api/chain/NIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=24068.65 contracts=160 blocker=-
- PASS (required) /api/chain/BANKNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=57447.3 contracts=160 blocker=-
- PASS (required) /api/chain/FINNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=26515.25 contracts=160 blocker=-
- PASS (required) /api/chain/MIDCPNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=14729.7 contracts=160 blocker=-
- PASS (optional) /api/chain/SENSEX source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=77155.48 contracts=160 blocker=-

## API
- PASS 200  /api/auth/status
- PASS 200  /api/deploy/info
- PASS 200  /api/health
- PASS 200  /api/state
- PASS 200  /api/broker/dhan/status
- PASS 200  /api/broker/funds
- PASS 200  /api/broker/holdings
- PASS 200  /api/broker/positions/live
- PASS 200  /api/chain/NIFTY
- PASS 200  /api/chain/BANKNIFTY
- PASS 200  /api/chain/FINNIFTY
- PASS 200  /api/chain/MIDCPNIFTY
- PASS 200 (optional) /api/chain/SENSEX
- PASS 200  /api/gain_rank
- PASS 200  /api/scanner/top_contract_gainers?top_n=5
- PASS 200  /api/pnl
- PASS 200  /api/trades/today
- PASS 200  /api/auto_gates
- PASS 200  /api/ml/performance
- PASS 200  /api/ml/compare
- PASS 200  /api/paper

## UI Screenshots
- PASS Truth Control owner=true safety=true ml=true paper=true
- PASS Genesis Brain owner=true safety=true ml=true paper=true
- PASS E2E Proof owner=true safety=true ml=true paper=true
- PASS Overview owner=true safety=true ml=true paper=true
- PASS Option Chain owner=true safety=true ml=true paper=true
- PASS Signals owner=true safety=true ml=true paper=true
- PASS Paper Trades owner=true safety=true ml=true paper=true
- PASS Positions owner=true safety=true ml=true paper=true
- PASS Broker owner=true safety=true ml=true paper=true
- PASS Performance owner=true safety=true ml=true paper=true
- PASS ML Model owner=true safety=true ml=true paper=true
- PASS Live Gate owner=true safety=true ml=true paper=true

## Infrastructure Blockers
- none

## Visual Blockers
- none

## Trading Readiness Blockers
- none

## Optional Data Blockers
- none

## Required Solutions
- none