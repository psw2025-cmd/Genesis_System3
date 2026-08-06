# Dashboard Visible Issue Tracker
Generated: 2026-08-06T06:50:55.366Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `56`
Info line count: `93`
Screenshot missing count: `0`
Unsettled tab count: `16`
UI exception count: `0`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- [ ] Fix visible UI blocker on Truth Control: BLOCKED
- [ ] Fix visible UI blocker on Truth Control: MONEY_READY_BLOCKED
- [ ] Fix visible UI blocker on Truth Control: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- [ ] Fix visible UI blocker on Truth Control: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- [ ] Fix visible UI blocker on Truth Control: Dashboard operator truth	BLOCKED	YES	health_ok=true, broker_ok=true, gates_ok=true, enabled_chains_ready=0/4 (runtime API probes; not hard-coded)
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on E2E Proof: Real broker/data truth only. Live money remains blocked until every row below passes.
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · FULL E2E
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · API
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · DHAN CHAIN
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · TRADER READY
- [ ] Fix visible UI blocker on E2E Proof: Dhan broker connection	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Dhan access token/session	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker funds/margin	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker holdings response	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker positions response	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback markers in chain	PASS	clean
- [ ] Fix visible UI blocker on E2E Proof: Paper/analyzer P&L endpoint	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Today paper lifecycle endpoint	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Gate/risk endpoint visible	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Live-money switch blocked until separate proof	PASS	blocked
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Sim Live: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 5007ms
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Signals: What Blocked Trading?
- [ ] Fix visible UI blocker on Signals: Candidate evidence exists, but broker order remains blocked until risk/paper lifecycle gates pass.
- [ ] Fix visible UI blocker on Signals: What Blocked Trading? Candidate only: paper/risk/live gates still decide whether trade is allowed
- [ ] Fix visible UI blocker on Signals: What Blocked Trading? Scanner Segments 3/4
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Paper Trades: LIVE Order Safety: BLOCKED · AUTO_EXECUTE_TRADES=0
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- [ ] Fix visible UI blocker on ML Model: MODEL_PROOF_LOADED_BUT_BLOCKED
- [ ] Fix visible UI blocker on ML Model: Loaded 1 blocked accuracy artifact(s). Model not proven — missing matured prediction history / post-market validation. Blocker: model_accuracy_report:NO_PREDICTION_SOURCE_FOUND
- [ ] Fix visible UI blocker on ML Model: 0 proven / 1 blocked
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: MODEL	STATUS	PREDICTIONS	AVG ACCURACY	PROOF PASS / BLOCKED	BLOCKER	GENERATED
- [ ] Fix visible UI blocker on ML Model: model_accuracy_report	BLOCKED	0	N/A	0 / 1	NO_PREDICTION_SOURCE_FOUND	2026-08-06T06:45:45.123467+00:00
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on System: ERROR
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- [ ] Fix visible UI blocker on Live Gate: LIVE_TRADING_BLOCKED
- [ ] Fix visible UI blocker on Live Gate: Live trading blocked — see failed gates above
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 5016 | 6 | 4 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 5013 | 3 | 5 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 5011 | 18 | 3 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 5010 | 2 | 10 | 0 | overview.txt |
| Sim Live | BLOCKED | OK | NO | 5013 | 1 | 8 | 0 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 5007 | 1 | 3 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 5011 | 5 | 5 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 5013 | 1 | 4 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 5011 | 2 | 24 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 5010 | 1 | 4 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 5009 | 1 | 5 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 5009 | 7 | 3 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 5010 | 2 | 3 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 5009 | 1 | 3 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 5013 | 2 | 4 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 5009 | 3 | 5 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- **Truth Control**: BLOCKED
- **Truth Control**: MONEY_READY_BLOCKED
- **Truth Control**: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- **Truth Control**: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- **Truth Control**: Dashboard operator truth	BLOCKED	YES	health_ok=true, broker_ok=true, gates_ok=true, enabled_chains_ready=0/4 (runtime API probes; not hard-coded)
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **E2E Proof**: Real broker/data truth only. Live money remains blocked until every row below passes.
- **E2E Proof**: BLOCKED · FULL E2E
- **E2E Proof**: BLOCKED · API
- **E2E Proof**: BLOCKED · DHAN CHAIN
- **E2E Proof**: No non-Dhan/stale/fallback
- **E2E Proof**: BLOCKED · TRADER READY
- **E2E Proof**: Dhan broker connection	BLOCKED	-
- **E2E Proof**: Dhan access token/session	BLOCKED	-
- **E2E Proof**: Real broker funds/margin	BLOCKED	-
- **E2E Proof**: Real broker holdings response	BLOCKED	-
- **E2E Proof**: Real broker positions response	BLOCKED	-
- **E2E Proof**: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- **E2E Proof**: No non-Dhan/stale/fallback markers in chain	PASS	clean
- **E2E Proof**: Paper/analyzer P&L endpoint	BLOCKED	-
- **E2E Proof**: Today paper lifecycle endpoint	BLOCKED	-
- **E2E Proof**: Gate/risk endpoint visible	BLOCKED	-
- **E2E Proof**: Live-money switch blocked until separate proof	PASS	blocked
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Overview**: PEND
- **Sim Live**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 5007ms
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Signals**: What Blocked Trading?
- **Signals**: Candidate evidence exists, but broker order remains blocked until risk/paper lifecycle gates pass.
- **Signals**: What Blocked Trading? Candidate only: paper/risk/live gates still decide whether trade is allowed
- **Signals**: What Blocked Trading? Scanner Segments 3/4
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Paper Trades**: LIVE Order Safety: BLOCKED · AUTO_EXECUTE_TRADES=0
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- **ML Model**: MODEL_PROOF_LOADED_BUT_BLOCKED
- **ML Model**: Loaded 1 blocked accuracy artifact(s). Model not proven — missing matured prediction history / post-market validation. Blocker: model_accuracy_report:NO_PREDICTION_SOURCE_FOUND
- **ML Model**: 0 proven / 1 blocked
- **ML Model**: BLOCKED
- **ML Model**: MODEL	STATUS	PREDICTIONS	AVG ACCURACY	PROOF PASS / BLOCKED	BLOCKER	GENERATED
- **ML Model**: model_accuracy_report	BLOCKED	0	N/A	0 / 1	NO_PREDICTION_SOURCE_FOUND	2026-08-06T06:45:45.123467+00:00
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Broker**: BLOCKED BY BACKEND FLAG
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- **System**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **System**: ERROR
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- **Live Gate**: LIVE_TRADING_BLOCKED
- **Live Gate**: Live trading blocked — see failed gates above
## Informational lines
- **Truth Control**: PAPER
- **Truth Control**: LIVE OFF
- **Truth Control**: Paper Trades
- **Truth Control**: Paper/analyzer lifecycle	PASS	NO	today_trade_rows=2, endpoint=200
- **Genesis Brain**: PAPER
- **Genesis Brain**: LIVE OFF
- **Genesis Brain**: Paper Trades
- **Genesis Brain**: Next: enforce position sizing in paper lifecycle
- **Genesis Brain**: "message": "I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS."
- **E2E Proof**: PAPER
- **E2E Proof**: LIVE OFF
- **E2E Proof**: Paper Trades
- **Overview**: PAPER
- **Overview**: LIVE OFF
- **Overview**: Paper Trades
- **Overview**: ANALYZER / PAPER COMMAND CENTER
- **Overview**: Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
- **Overview**: PAPER P&L
- **Overview**: Paper only
- **Overview**: market closed must not hide read-only data
- **Overview**: Paper Lifecycle
- **Overview**: Wire is_tradeable_fo_symbol() in ranking/paper trade path
- **Sim Live**: PAPER
- **Sim Live**: LIVE OFF
- **Sim Live**: Paper Trades
- **Sim Live**: ✓ LIVE OFF
- **Sim Live**: Backend virtual paper order tape
- **Sim Live**: POS_0001	NIFTY	CE	24800		81.95	₹-70.59	OPEN	paper_simulation
- **Sim Live**: POS_0002	BANKNIFTY	CE	59200		243.5	₹0.00	OPEN	paper_simulation
- **Sim Live**: REAL PAPER LIFECYCLE MARKET DAY PROOF
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: Paper Trades
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: Paper Trades
- **Signals**: Candidate only: paper/risk/live gates still decide whether trade is allowed
- **Signals**: Refreshed 2026-08-06 12:21:23 · ok · 25 rows · Dhan live · trading truth for paper MTM
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: Paper Trades
- **Trade**: Refreshed 2026-08-06 12:21:23 · ok · 25 rows · Dhan live · trading truth for paper MTM
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
- **Paper Trades**: Aligned to DhanHQ v2 Positions fields · Source: PAPER_CLOUD_SIM · Refresh: 8/6/2026, 6:51:48 AM
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
- **Paper Trades**: Open Paper Positions (2)
- **Paper Trades**: Columns map to DhanHQ v2 Positions: tradingSymbol, positionType, productType, buyAvg, netQty, unrealizedProfit, drvOptionType, drvStrikePrice, drvExpiryDate + paper SL/Target.
- **Paper Trades**: NSE_FNO	PAPER_CLOUD_SIM
- **Paper Trades**: Paper Exposure
- **Paper Trades**: Order Book (Paper)
- **Paper Trades**: Broker order book stays empty in paper mode.
- **Paper Trades**: GET /v2/orders → N/A (paper ledger only)
- **Paper Trades**: Paper fills → PAPER_CLOUD_SIM + Dhan LTP MTM
- **Paper Trades**: Today Paper Trade Proof
- **Positions**: PAPER
- **Positions**: LIVE OFF
- **Positions**: Paper Trades
- **Positions**: PAPER ONLY — NO REAL MONEY
- **Performance**: PAPER
- **Performance**: LIVE OFF
- **Performance**: Paper Trades
- **Performance**: OPEN PAPER
- **Performance**: Cloud paper engine
- **ML Model**: PAPER
- **ML Model**: LIVE OFF
- **ML Model**: Paper Trades
- **Broker**: PAPER
- **Broker**: LIVE OFF
- **Broker**: Paper Trades
- **Alerts**: PAPER
- **Alerts**: LIVE OFF
- **Alerts**: Paper Trades
- **System**: PAPER
- **System**: LIVE OFF
- **System**: Paper Trades
- **System**: Paper Mode
- **Live Gate**: PAPER
- **Live Gate**: LIVE OFF
- **Live Gate**: Paper Trades
- **Live Gate**: LIVE_TRADING_ENABLED=0 (must be 0 for paper, 1 for live)
- **Live Gate**: All technical gates must pass before the approval section appears. Continue running in PAPER mode to accumulate proof data.
