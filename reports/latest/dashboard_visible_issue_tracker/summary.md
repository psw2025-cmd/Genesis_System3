# Dashboard Visible Issue Tracker
Generated: 2026-07-24T15:10:54.296Z
Base: http://127.0.0.1:8000
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `0`
Visible blocker count: `0`
Info line count: `0`
Screenshot missing count: `0`
Unsettled tab count: `0`
UI exception count: `0`
Auth OK: `false`
Production-grade claim allowed: `false`
Global exception: `Error: page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:8000/ui/
Call log:
  - navigating to "http://127.0.0.1:8000/ui/", waiting until "domcontentloaded"
`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Live dashboard UI scan failed before tab scan: Error: page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:8000/ui/
Call log:
  - navigating to "http://127.0.0.1:8000/ui/", waiting until "domcontentloaded"

## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
## Visible blockers
- none
## Informational lines
- none
