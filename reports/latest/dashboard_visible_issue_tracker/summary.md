# Dashboard Visible Issue Tracker
Generated: 2026-08-06T03:44:25.750Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `81`
Info line count: `87`
Screenshot missing count: `0`
Unsettled tab count: `16`
UI exception count: `0`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 5019ms markers=CHECKING...
- [ ] Fix visible UI blocker on Truth Control: BLOCKED
- [ ] Fix visible UI blocker on Truth Control: MONEY_READY_BLOCKED
- [ ] Fix visible UI blocker on Truth Control: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- [ ] Fix visible UI blocker on Truth Control: Backend/API route health	BLOCKED	YES	health=0, state=0
- [ ] Fix visible UI blocker on Truth Control: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- [ ] Fix visible UI blocker on Truth Control: Funds / margin truth	BLOCKED	YES	available=-, used=-, source=-
- [ ] Fix visible UI blocker on Truth Control: Holdings and live positions read path	BLOCKED	YES	holdings=0, positions=0
- [ ] Fix visible UI blocker on Truth Control: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- [ ] Fix visible UI blocker on Truth Control: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- [ ] Fix visible UI blocker on Truth Control: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- [ ] Fix visible UI blocker on Truth Control: Paper/analyzer lifecycle	BLOCKED	NO	today_trade_rows=0, endpoint=0
- [ ] Fix visible UI blocker on Truth Control: Risk gates and automation status	BLOCKED	YES	auto_gates_http=0, status=-
- [ ] Fix visible UI blocker on Truth Control: Dashboard operator truth	BLOCKED	YES	health_ok=false, broker_ok=false, gates_ok=false, enabled_chains_ready=0/4 (runtime API probes; not hard-coded)
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: last scanner snapshot and staleness
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on E2E Proof: DHAN DEGRADED
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
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Overview: DHAN DEGRADED
- [ ] Fix visible UI blocker on Overview: API status: NETWORK_ERROR - Network/DNS could not reach Cloud Run backend for /api/batch/market-data. Keeping last good data where available. Retrying slowly; last good truth remains visible where available.
- [ ] Fix visible UI blocker on Overview: ERROR
- [ ] Fix visible UI blocker on Overview: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Overview: NETWORK_ERROR
- [ ] Fix visible UI blocker on Sim Live: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Sim Live: DHAN DEGRADED
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Option Chain: DHAN DEGRADED
- [ ] Fix visible UI blocker on Option Chain: Market: CLOSED · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Option Chain: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Signals: DHAN DEGRADED
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Trade: DHAN DEGRADED
- [ ] Fix visible UI blocker on Trade: Market: CLOSED · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Trade: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Paper Trades: DHAN DEGRADED
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Positions: DHAN DEGRADED
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Performance: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 5011ms markers=CHECKING MODEL ARTIFACTS...
- [ ] Fix visible UI blocker on ML Model: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: 0 proven / 0 blocked
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: Training proof missing.
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Broker: DHAN DEGRADED
- [ ] Fix visible UI blocker on Broker: ERROR/BLOCKED
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Broker: Failed to load funds: unknown error
- [ ] Fix visible UI blocker on Broker: Failed to load holdings: unknown error
- [ ] Fix visible UI blocker on Broker: Failed to load positions: unknown error
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on Alerts: DHAN DEGRADED
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on System: DHAN DEGRADED
- [ ] Fix visible UI blocker on System: NETWORK_ERROR
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 5013ms markers=CHECKING...
- [ ] Fix visible UI blocker on Live Gate: DHAN DEGRADED
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 5019 | 14 | 4 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 5013 | 4 | 6 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 5014 | 19 | 4 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 5012 | 7 | 10 | 0 | overview.txt |
| Sim Live | BLOCKED | OK | NO | 5012 | 2 | 7 | 0 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 5011 | 4 | 5 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 5010 | 2 | 4 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 5011 | 4 | 6 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 5012 | 2 | 6 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 5011 | 2 | 6 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 5012 | 2 | 6 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 5011 | 5 | 4 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 5014 | 7 | 6 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 5015 | 2 | 4 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 5015 | 3 | 5 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 5013 | 2 | 4 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 5019ms markers=CHECKING...
- **Truth Control**: BLOCKED
- **Truth Control**: MONEY_READY_BLOCKED
- **Truth Control**: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- **Truth Control**: Backend/API route health	BLOCKED	YES	health=0, state=0
- **Truth Control**: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- **Truth Control**: Funds / margin truth	BLOCKED	YES	available=-, used=-, source=-
- **Truth Control**: Holdings and live positions read path	BLOCKED	YES	holdings=0, positions=0
- **Truth Control**: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- **Truth Control**: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- **Truth Control**: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- **Truth Control**: Paper/analyzer lifecycle	BLOCKED	NO	today_trade_rows=0, endpoint=0
- **Truth Control**: Risk gates and automation status	BLOCKED	YES	auto_gates_http=0, status=-
- **Truth Control**: Dashboard operator truth	BLOCKED	YES	health_ok=false, broker_ok=false, gates_ok=false, enabled_chains_ready=0/4 (runtime API probes; not hard-coded)
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: last scanner snapshot and staleness
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **E2E Proof**: DHAN DEGRADED
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
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Overview**: DHAN DEGRADED
- **Overview**: API status: NETWORK_ERROR - Network/DNS could not reach Cloud Run backend for /api/batch/market-data. Keeping last good data where available. Retrying slowly; last good truth remains visible where available.
- **Overview**: ERROR
- **Overview**: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Overview**: PEND
- **Overview**: NETWORK_ERROR
- **Sim Live**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Sim Live**: DHAN DEGRADED
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Option Chain**: DHAN DEGRADED
- **Option Chain**: Market: CLOSED · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Option Chain**: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Signals**: DHAN DEGRADED
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Trade**: DHAN DEGRADED
- **Trade**: Market: CLOSED · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Trade**: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Paper Trades**: DHAN DEGRADED
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Positions**: DHAN DEGRADED
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Performance**: DHAN DEGRADED
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 5011ms markers=CHECKING MODEL ARTIFACTS...
- **ML Model**: DHAN DEGRADED
- **ML Model**: 0 proven / 0 blocked
- **ML Model**: BLOCKED
- **ML Model**: Training proof missing.
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Broker**: DHAN DEGRADED
- **Broker**: ERROR/BLOCKED
- **Broker**: BLOCKED BY BACKEND FLAG
- **Broker**: Failed to load funds: unknown error
- **Broker**: Failed to load holdings: unknown error
- **Broker**: Failed to load positions: unknown error
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **Alerts**: DHAN DEGRADED
- **System**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **System**: DHAN DEGRADED
- **System**: NETWORK_ERROR
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 5013ms markers=CHECKING...
- **Live Gate**: DHAN DEGRADED
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
- **Overview**: Paper / Analyzer Mode
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
- **Option Chain**: No chain rows yet (market closed — last snapshot not loaded).
- **Signals**: MARKET CLOSED / DATA POLLING
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: Paper Trades
- **Trade**: MARKET CLOSED / DATA POLLING
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: Paper Trades
- **Trade**: Loading… · 0 rows · Dhan live · trading truth for paper MTM
- **Trade**: No chain rows yet (market closed — last snapshot not loaded).
- **Paper Trades**: MARKET CLOSED / DATA POLLING
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
- **Paper Trades**: Loading paper positions + Dhan mark-to-market…
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
