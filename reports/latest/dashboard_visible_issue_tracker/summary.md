# Dashboard Visible Issue Tracker
Generated: 2026-08-03T23:41:51.114Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `83`
Info line count: `84`
Screenshot missing count: `0`
Unsettled tab count: `16`
UI exception count: `0`
Auth OK: `false`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Dashboard auth session failed status=401
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 5023ms
- [ ] Fix visible UI blocker on Truth Control: BLOCKED
- [ ] Fix visible UI blocker on Truth Control: MONEY_READY_BLOCKED
- [ ] Fix visible UI blocker on Truth Control: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- [ ] Fix visible UI blocker on Truth Control: Backend/API route health	BLOCKED	YES	health=200, state=401
- [ ] Fix visible UI blocker on Truth Control: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- [ ] Fix visible UI blocker on Truth Control: Funds / margin truth	BLOCKED	YES	available=-, used=-, source=-
- [ ] Fix visible UI blocker on Truth Control: Holdings and live positions read path	BLOCKED	YES	holdings=0, positions=0
- [ ] Fix visible UI blocker on Truth Control: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- [ ] Fix visible UI blocker on Truth Control: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- [ ] Fix visible UI blocker on Truth Control: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- [ ] Fix visible UI blocker on Truth Control: Paper/analyzer lifecycle	BLOCKED	NO	today_trade_rows=0, endpoint=401
- [ ] Fix visible UI blocker on Truth Control: Risk gates and automation status	BLOCKED	YES	auto_gates_http=401, status=-
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: last scanner snapshot and staleness
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on E2E Proof: Real broker/data truth only. Live money remains blocked until every row below passes.
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · FULL E2E
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · API
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · DHAN CHAIN
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · TRADER READY
- [ ] Fix visible UI blocker on E2E Proof: Dhan broker connection	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Dhan access token/session	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker funds/margin	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Real broker holdings response	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Real broker positions response	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback markers in chain	PASS	clean
- [ ] Fix visible UI blocker on E2E Proof: Paper/analyzer P&L endpoint	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Today paper lifecycle endpoint	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Gate/risk endpoint visible	BLOCKED	401
- [ ] Fix visible UI blocker on E2E Proof: Live-money switch blocked until separate proof	PASS	blocked
- [ ] Fix visible UI blocker on E2E Proof: NIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: BANKNIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: FINNIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: MIDCPNIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: SENSEX	BLOCKED	-	-	401	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: /api/state	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/dhan/status	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/funds	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/holdings	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/positions/live	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/gain_rank	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/pnl	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/trades/today	401	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/auto_gates	401	BLOCKED	-
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Overview: API status: API_AUTH_REQUIRED - Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds. Retrying slowly; last good truth remains visible where available.
- [ ] Fix visible UI blocker on Overview: ERROR
- [ ] Fix visible UI blocker on Overview: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- [ ] Fix visible UI blocker on Overview: FAIL
- [ ] Fix visible UI blocker on Sim Live: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Sim Live: Backend simulation API not available yet: backend simulation API failed: 401. After Render deploy, this should come from /api/simulation/live/state.
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Paper Trades: Error Loading Data
- [ ] Fix visible UI blocker on Paper Trades: Error: Request failed with status code 401
- [ ] Fix visible UI blocker on Paper Trades: ❌ Error Loading Data Endpoint: /api/state Error: Request failed with status code 401 Retry
- [ ] Fix visible UI blocker on Paper Trades: Endpoint: /api/state Error: Request failed with status code 401
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Performance: Failed to load performance data: 401
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on ML Model: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- [ ] Fix visible UI blocker on ML Model: 0 proven / 0 blocked
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: Training proof missing.
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Broker: ERROR/BLOCKED
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Broker: Failed to load funds: 401 - API_AUTH_REQUIRED - Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- [ ] Fix visible UI blocker on Broker: Failed to load holdings: Holdings: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- [ ] Fix visible UI blocker on Broker: Failed to load positions: Positions: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Alerts: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds. Retrying slowly; last good truth remains visible where available.
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on System: AUTH REQUIRED
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 5012ms
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 5023 | 13 | 4 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 5014 | 4 | 6 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 5015 | 32 | 4 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 5012 | 5 | 10 | 0 | overview.txt |
| Sim Live | BLOCKED | OK | NO | 5013 | 2 | 6 | 0 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 5016 | 1 | 5 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 5013 | 1 | 5 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 5016 | 1 | 5 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 5013 | 5 | 5 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 5015 | 1 | 6 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 5010 | 2 | 4 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 5010 | 5 | 4 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 5010 | 6 | 6 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 5010 | 2 | 4 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 5011 | 2 | 5 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 5012 | 1 | 5 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 5023ms
- **Truth Control**: BLOCKED
- **Truth Control**: MONEY_READY_BLOCKED
- **Truth Control**: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- **Truth Control**: Backend/API route health	BLOCKED	YES	health=200, state=401
- **Truth Control**: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- **Truth Control**: Funds / margin truth	BLOCKED	YES	available=-, used=-, source=-
- **Truth Control**: Holdings and live positions read path	BLOCKED	YES	holdings=0, positions=0
- **Truth Control**: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- **Truth Control**: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- **Truth Control**: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- **Truth Control**: Paper/analyzer lifecycle	BLOCKED	NO	today_trade_rows=0, endpoint=401
- **Truth Control**: Risk gates and automation status	BLOCKED	YES	auto_gates_http=401, status=-
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: last scanner snapshot and staleness
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **E2E Proof**: Real broker/data truth only. Live money remains blocked until every row below passes.
- **E2E Proof**: BLOCKED · FULL E2E
- **E2E Proof**: BLOCKED · API
- **E2E Proof**: BLOCKED · DHAN CHAIN
- **E2E Proof**: No non-Dhan/stale/fallback
- **E2E Proof**: BLOCKED · TRADER READY
- **E2E Proof**: Dhan broker connection	BLOCKED	401
- **E2E Proof**: Dhan access token/session	BLOCKED	-
- **E2E Proof**: Real broker funds/margin	BLOCKED	401
- **E2E Proof**: Real broker holdings response	BLOCKED	401
- **E2E Proof**: Real broker positions response	BLOCKED	401
- **E2E Proof**: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- **E2E Proof**: No non-Dhan/stale/fallback markers in chain	PASS	clean
- **E2E Proof**: Paper/analyzer P&L endpoint	BLOCKED	401
- **E2E Proof**: Today paper lifecycle endpoint	BLOCKED	401
- **E2E Proof**: Gate/risk endpoint visible	BLOCKED	401
- **E2E Proof**: Live-money switch blocked until separate proof	PASS	blocked
- **E2E Proof**: NIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- **E2E Proof**: BANKNIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- **E2E Proof**: FINNIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- **E2E Proof**: MIDCPNIFTY	BLOCKED	-	-	401	-	-	UNKNOWN
- **E2E Proof**: SENSEX	BLOCKED	-	-	401	-	-	UNKNOWN
- **E2E Proof**: /api/state	401	BLOCKED	-
- **E2E Proof**: /api/broker/dhan/status	401	BLOCKED	-
- **E2E Proof**: /api/broker/funds	401	BLOCKED	-
- **E2E Proof**: /api/broker/holdings	401	BLOCKED	-
- **E2E Proof**: /api/broker/positions/live	401	BLOCKED	-
- **E2E Proof**: /api/gain_rank	401	BLOCKED	-
- **E2E Proof**: /api/pnl	401	BLOCKED	-
- **E2E Proof**: /api/trades/today	401	BLOCKED	-
- **E2E Proof**: /api/auto_gates	401	BLOCKED	-
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Overview**: API status: API_AUTH_REQUIRED - Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds. Retrying slowly; last good truth remains visible where available.
- **Overview**: ERROR
- **Overview**: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- **Overview**: FAIL
- **Sim Live**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Sim Live**: Backend simulation API not available yet: backend simulation API failed: 401. After Render deploy, this should come from /api/simulation/live/state.
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Paper Trades**: Error Loading Data
- **Paper Trades**: Error: Request failed with status code 401
- **Paper Trades**: ❌ Error Loading Data Endpoint: /api/state Error: Request failed with status code 401 Retry
- **Paper Trades**: Endpoint: /api/state Error: Request failed with status code 401
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Performance**: Failed to load performance data: 401
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **ML Model**: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- **ML Model**: 0 proven / 0 blocked
- **ML Model**: BLOCKED
- **ML Model**: Training proof missing.
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Broker**: ERROR/BLOCKED
- **Broker**: BLOCKED BY BACKEND FLAG
- **Broker**: Failed to load funds: 401 - API_AUTH_REQUIRED - Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- **Broker**: Failed to load holdings: Holdings: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- **Broker**: Failed to load positions: Positions: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Alerts**: Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds. Retrying slowly; last good truth remains visible where available.
- **System**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **System**: AUTH REQUIRED
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
## Informational lines
- **Truth Control**: MARKET CLOSED / DATA POLLING
- **Truth Control**: PAPER
- **Truth Control**: LIVE OFF
- **Truth Control**: Paper Trades
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
- **Overview**: MARKET CLOSED / DATA POLLING
- **Overview**: PAPER
- **Overview**: LIVE OFF
- **Overview**: Paper Trades
- **Overview**: ANALYZER / PAPER COMMAND CENTER
- **Overview**: Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
- **Overview**: PAPER P&L
- **Overview**: Paper only
- **Overview**: market closed must not hide read-only data
- **Overview**: Market closed — last verified Dhan option-chain snapshot (2026-08-04 05:10 IST)
- **Sim Live**: MARKET CLOSED / DATA POLLING
- **Sim Live**: PAPER
- **Sim Live**: LIVE OFF
- **Sim Live**: Paper Trades
- **Sim Live**: ✓ LIVE OFF
- **Sim Live**: Backend virtual paper order tape
- **Option Chain**: MARKET CLOSED / DATA POLLING
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: Paper Trades
- **Option Chain**: AFTER HOURS SNAPSHOT - NIFTY source=dhan priority=dhan_last_verified_snapshot age=9.3s fetched=2026-08-03T23:40:23.531846+00:00 - Market closed — last verified Dhan snapshot (2026-08-04 05:10 IST)
- **Signals**: MARKET CLOSED / DATA POLLING
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: Paper Trades
- **Signals**: Enter the Dashboard API key to unlock read-only signal, broker, paper, scanner and gate data.
- **Trade**: MARKET CLOSED / DATA POLLING
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: Paper Trades
- **Trade**: AFTER HOURS SNAPSHOT - NIFTY source=dhan priority=dhan_last_verified_snapshot age=24.4s fetched=2026-08-03T23:40:23.531846+00:00 - Market closed — last verified Dhan snapshot (2026-08-04 05:10 IST)
- **Paper Trades**: MARKET CLOSED / DATA POLLING
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
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
- **Live Gate**: All technical gates must pass before the approval section appears. Continue running in PAPER mode to accumulate proof data.
