# Dashboard Visible Issue Tracker
Generated: 2026-08-04T19:47:45.173Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `57`
Info line count: `116`
Screenshot missing count: `0`
Unsettled tab count: `16`
UI exception count: `0`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 5023ms
- [ ] Fix visible UI blocker on Truth Control: BLOCKED
- [ ] Fix visible UI blocker on Truth Control: MONEY_READY_BLOCKED
- [ ] Fix visible UI blocker on Truth Control: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- [ ] Fix visible UI blocker on Truth Control: Dashboard operator truth	BLOCKED	YES	health_ok=true, broker_ok=true, gates_ok=true, enabled_chains_ready=1/4 (runtime API probes; not hard-coded)
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: last scanner snapshot and staleness
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on E2E Proof: Real broker/data truth only. Live money remains blocked until every row below passes.
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · FULL E2E
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · DHAN CHAIN
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · NO BAD SOURCE
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · TRADER READY
- [ ] Fix visible UI blocker on E2E Proof: Real Dhan option chain for all watched symbols	BLOCKED	1/5
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback markers in chain	BLOCKED	blocked marker found
- [ ] Fix visible UI blocker on E2E Proof: Live-money switch blocked until separate proof	PASS	blocked
- [ ] Fix visible UI blocker on E2E Proof: BANKNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: FINNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: MIDCPNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: SENSEX	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Overview: market-session proof pending
- [ ] Fix visible UI blocker on Sim Live: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 5017ms
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Signals: What Blocked Trading?
- [ ] Fix visible UI blocker on Signals: Refreshed 2026-08-05 01:17:06 · SCRAPE_FAILED · 0 rows · Reference board (LIVE_SCRAPED) · not used for live orders
- [ ] Fix visible UI blocker on Signals: HTTP Error 403: Forbidden
- [ ] Fix visible UI blocker on Signals: Candidate evidence exists, but broker order remains blocked until risk/paper lifecycle gates pass.
- [ ] Fix visible UI blocker on Signals: 0/4
- [ ] Fix visible UI blocker on Signals: What Blocked Trading? Candidate only: paper/risk/live gates still decide whether trade is allowed
- [ ] Fix visible UI blocker on Signals: What Blocked Trading? Scanner Segments 0/4
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 5017ms
- [ ] Fix visible UI blocker on Trade: Refreshed 2026-08-05 01:17:06 · SCRAPE_FAILED · 0 rows · Reference board (LIVE_SCRAPED) · not used for live orders
- [ ] Fix visible UI blocker on Trade: HTTP Error 403: Forbidden
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Paper Trades: LIVE Order Safety: BLOCKED · AUTO_EXECUTE_TRADES=0
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on ML Model: MODEL_PROOF_LOADED_BUT_BLOCKED
- [ ] Fix visible UI blocker on ML Model: Loaded 1 blocked accuracy artifact(s). Model not proven — missing matured prediction history / post-market validation. Blocker: model_accuracy_report:NO_PREDICTION_SOURCE_FOUND
- [ ] Fix visible UI blocker on ML Model: 0 proven / 1 blocked
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: MODEL	STATUS	PREDICTIONS	AVG ACCURACY	PROOF PASS / BLOCKED	BLOCKER	GENERATED
- [ ] Fix visible UI blocker on ML Model: model_accuracy_report	BLOCKED	0	N/A	0 / 1	NO_PREDICTION_SOURCE_FOUND	2026-07-24T03:53:31.406031+00:00
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Live Gate: LIVE_TRADING_BLOCKED
- [ ] Fix visible UI blocker on Live Gate: Live trading blocked — see failed gates above
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 5023 | 5 | 5 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 5015 | 4 | 6 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 5012 | 14 | 7 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 5013 | 3 | 13 | 0 | overview.txt |
| Sim Live | BLOCKED | OK | NO | 5013 | 1 | 7 | 0 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 5017 | 1 | 5 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 5013 | 8 | 5 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 5017 | 3 | 5 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 5014 | 2 | 26 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 5014 | 1 | 6 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 5014 | 1 | 6 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 5012 | 7 | 4 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 5011 | 2 | 6 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 5011 | 1 | 4 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 5014 | 1 | 5 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 5010 | 3 | 6 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 5023ms
- **Truth Control**: BLOCKED
- **Truth Control**: MONEY_READY_BLOCKED
- **Truth Control**: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- **Truth Control**: Dashboard operator truth	BLOCKED	YES	health_ok=true, broker_ok=true, gates_ok=true, enabled_chains_ready=1/4 (runtime API probes; not hard-coded)
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: last scanner snapshot and staleness
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **E2E Proof**: Real broker/data truth only. Live money remains blocked until every row below passes.
- **E2E Proof**: BLOCKED · FULL E2E
- **E2E Proof**: BLOCKED · DHAN CHAIN
- **E2E Proof**: BLOCKED · NO BAD SOURCE
- **E2E Proof**: No non-Dhan/stale/fallback
- **E2E Proof**: BLOCKED · TRADER READY
- **E2E Proof**: Real Dhan option chain for all watched symbols	BLOCKED	1/5
- **E2E Proof**: No non-Dhan/stale/fallback markers in chain	BLOCKED	blocked marker found
- **E2E Proof**: Live-money switch blocked until separate proof	PASS	blocked
- **E2E Proof**: BANKNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: FINNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: MIDCPNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: SENSEX	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Overview**: PEND
- **Overview**: market-session proof pending
- **Sim Live**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 5017ms
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Signals**: What Blocked Trading?
- **Signals**: Refreshed 2026-08-05 01:17:06 · SCRAPE_FAILED · 0 rows · Reference board (LIVE_SCRAPED) · not used for live orders
- **Signals**: HTTP Error 403: Forbidden
- **Signals**: Candidate evidence exists, but broker order remains blocked until risk/paper lifecycle gates pass.
- **Signals**: 0/4
- **Signals**: What Blocked Trading? Candidate only: paper/risk/live gates still decide whether trade is allowed
- **Signals**: What Blocked Trading? Scanner Segments 0/4
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 5017ms
- **Trade**: Refreshed 2026-08-05 01:17:06 · SCRAPE_FAILED · 0 rows · Reference board (LIVE_SCRAPED) · not used for live orders
- **Trade**: HTTP Error 403: Forbidden
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Paper Trades**: LIVE Order Safety: BLOCKED · AUTO_EXECUTE_TRADES=0
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **ML Model**: MODEL_PROOF_LOADED_BUT_BLOCKED
- **ML Model**: Loaded 1 blocked accuracy artifact(s). Model not proven — missing matured prediction history / post-market validation. Blocker: model_accuracy_report:NO_PREDICTION_SOURCE_FOUND
- **ML Model**: 0 proven / 1 blocked
- **ML Model**: BLOCKED
- **ML Model**: MODEL	STATUS	PREDICTIONS	AVG ACCURACY	PROOF PASS / BLOCKED	BLOCKER	GENERATED
- **ML Model**: model_accuracy_report	BLOCKED	0	N/A	0 / 1	NO_PREDICTION_SOURCE_FOUND	2026-07-24T03:53:31.406031+00:00
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Broker**: BLOCKED BY BACKEND FLAG
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **System**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Live Gate**: LIVE_TRADING_BLOCKED
- **Live Gate**: Live trading blocked — see failed gates above
## Informational lines
- **Truth Control**: MARKET CLOSED / DATA POLLING
- **Truth Control**: PAPER
- **Truth Control**: LIVE OFF
- **Truth Control**: Paper Trades
- **Truth Control**: Paper/analyzer lifecycle	PARTIAL	NO	today_trade_rows=0, endpoint=200
- **Genesis Brain**: MARKET CLOSED / DATA POLLING
- **Genesis Brain**: PAPER
- **Genesis Brain**: LIVE OFF
- **Genesis Brain**: Paper Trades
- **Genesis Brain**: Next: enforce position sizing in paper lifecycle
- **Genesis Brain**: "message": "I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS."
- **E2E Proof**: MARKET CLOSED / DATA POLLING
- **E2E Proof**: PAPER
- **E2E Proof**: LIVE OFF
- **E2E Proof**: Paper Trades
- **E2E Proof**: Paper/analyzer P&L endpoint	PASS	200
- **E2E Proof**: Today paper lifecycle endpoint	PASS	count=0
- **E2E Proof**: /api/state	200	PASS	PAPER
- **Overview**: MARKET CLOSED / DATA POLLING
- **Overview**: PAPER
- **Overview**: LIVE OFF
- **Overview**: Paper Trades
- **Overview**: ANALYZER / PAPER COMMAND CENTER
- **Overview**: Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
- **Overview**: PAPER P&L
- **Overview**: Paper only
- **Overview**: market closed must not hide read-only data
- **Overview**: Market closed: Before pre-market (opens at 09:15)
- **Overview**: Market closed — last verified Dhan snapshot (2026-08-05 01:08 IST)
- **Overview**: Paper Lifecycle
- **Overview**: Wire is_tradeable_fo_symbol() in ranking/paper trade path
- **Sim Live**: MARKET CLOSED / DATA POLLING
- **Sim Live**: PAPER
- **Sim Live**: LIVE OFF
- **Sim Live**: Paper Trades
- **Sim Live**: ✓ LIVE OFF
- **Sim Live**: Backend virtual paper order tape
- **Sim Live**: REAL PAPER LIFECYCLE MARKET DAY PROOF
- **Option Chain**: MARKET CLOSED / DATA POLLING
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: Paper Trades
- **Option Chain**: AFTER HOURS SNAPSHOT - NIFTY source=dhan priority=dhan_last_verified_snapshot age=53.8s fetched=2026-08-04T19:38:17.748380+00:00 - Market closed — last verified Dhan snapshot (2026-08-05 01:08 IST)
- **Signals**: MARKET CLOSED / DATA POLLING
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: Paper Trades
- **Signals**: Candidate only: paper/risk/live gates still decide whether trade is allowed
- **Trade**: MARKET CLOSED / DATA POLLING
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: Paper Trades
- **Trade**: AFTER HOURS SNAPSHOT - NIFTY source=dhan priority=dhan_last_verified_snapshot age=53.8s fetched=2026-08-04T19:38:17.748380+00:00 - Market closed — last verified Dhan snapshot (2026-08-05 01:08 IST)
- **Paper Trades**: MARKET CLOSED / DATA POLLING
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
- **Paper Trades**: Aligned to DhanHQ v2 Positions fields · Source: PAPER_CLOUD_SIM · Refresh: 8/4/2026, 7:48:39 PM
- **Paper Trades**: Dhan production tokens have no paper sandbox — fills are local sim; LTP/PnL from live Dhan option chain. LIVE orders stay OFF.
- **Paper Trades**: Force Paper Tick
- **Paper Trades**: PAPER SAFE
- **Paper Trades**: Today Paper Entries
- **Paper Trades**: Today Paper Exits
- **Paper Trades**: Paper Truth Provenance
- **Paper Trades**: Correct for paper — broker orders must stay off
- **Paper Trades**: Sources checked: DhanHQ Portfolio/Positions docs · Dhan Sandbox (separate tokens) · OpenAlgo Dhan notes · industry paper dashboards (entry, LTP, unrealized/realized PnL, SL/TP, order book empty in paper).
- **Paper Trades**: PAPER TRADING MODE (NO REAL ORDERS)
- **Paper Trades**: Mode: PAPER | Data Source: DHAN_LIVE_MARK_TO_MARKET | Broker: Connected
- **Paper Trades**: Open Paper Positions (0)
- **Paper Trades**: Columns map to DhanHQ v2 Positions: tradingSymbol, positionType, productType, buyAvg, netQty, unrealizedProfit, drvOptionType, drvStrikePrice, drvExpiryDate + paper SL/Target.
- **Paper Trades**: No open paper positions
- **Paper Trades**: Use Force Paper Tick during market hours to open a Dhan-chain-backed paper fill, or wait for the cloud paper loop.
- **Paper Trades**: Paper Exposure
- **Paper Trades**: Order Book (Paper)
- **Paper Trades**: Broker order book stays empty in paper mode.
- **Paper Trades**: GET /v2/orders → N/A (paper ledger only)
- **Paper Trades**: Paper fills → PAPER_CLOUD_SIM + Dhan LTP MTM
- **Paper Trades**: Today Paper Trade Proof
- **Positions**: MARKET CLOSED / DATA POLLING
- **Positions**: PAPER
- **Positions**: LIVE OFF
- **Positions**: Paper Trades
- **Positions**: PAPER ONLY — NO REAL MONEY
- **Positions**: Paper engine generates positions during market hours
- **Performance**: MARKET CLOSED / DATA POLLING
- **Performance**: PAPER
- **Performance**: LIVE OFF
- **Performance**: Paper Trades
- **Performance**: OPEN PAPER
- **Performance**: Cloud paper engine
- **ML Model**: MARKET CLOSED / DATA POLLING
- **ML Model**: PAPER
- **ML Model**: LIVE OFF
- **ML Model**: Paper Trades
- **Broker**: MARKET CLOSED / DATA POLLING
- **Broker**: PAPER
- **Broker**: LIVE OFF
- **Broker**: Paper Trades
- **Broker**: NONE - MARKET CLOSED IS OK
- **Broker**: MARKET CLOSED / READ-ONLY OK
- **Alerts**: MARKET CLOSED / DATA POLLING
- **Alerts**: PAPER
- **Alerts**: LIVE OFF
- **Alerts**: Paper Trades
- **System**: MARKET CLOSED / DATA POLLING
- **System**: PAPER
- **System**: LIVE OFF
- **System**: Paper Trades
- **System**: Paper Mode
- **Live Gate**: MARKET CLOSED / DATA POLLING
- **Live Gate**: PAPER
- **Live Gate**: LIVE OFF
- **Live Gate**: Paper Trades
- **Live Gate**: LIVE_TRADING_ENABLED=0 (must be 0 for paper, 1 for live)
- **Live Gate**: All technical gates must pass before the approval section appears. Continue running in PAPER mode to accumulate proof data.
