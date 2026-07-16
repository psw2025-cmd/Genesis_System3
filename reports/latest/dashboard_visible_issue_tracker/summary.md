# Dashboard Visible Issue Tracker
Generated: 2026-07-16T22:56:18.042Z
Base: https://genesis-system3-backend.onrender.com
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `0`
Info line count: `0`
Screenshot missing count: `16`
Unsettled tab count: `16`
UI exception count: `16`
Auth OK: `false`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Dashboard auth session failed status=502
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | truth.txt |
| Genesis Brain | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | genesis.txt |
| E2E Proof | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | e2e_proof.txt |
| Overview | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | overview.txt |
| Sim Live | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | sim_live.txt |
| Option Chain | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | chain.txt |
| Signals | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | signals.txt |
| Trade | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | trade.txt |
| Paper Trades | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | paper.txt |
| Positions | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | positions.txt |
| Performance | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | performance.txt |
| ML Model | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | ml.txt |
| Broker | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | broker.txt |
| Alerts | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | alerts.txt |
| System | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | system.txt |
| Live Gate | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | gates.txt |
## Visible blockers
- none
## Informational lines
- none
