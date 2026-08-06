# Dashboard Visible Issue Tracker
Generated: 2026-08-06T05:04:35.832Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
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
Global exception: `TimeoutError: page.goto: Timeout 90000ms exceeded.
Call log:
  - navigating to "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/", waiting until "domcontentloaded"
`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Live dashboard UI scan failed before tab scan: TimeoutError: page.goto: Timeout 90000ms exceeded.
Call log:
  - navigating to "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/", waiting until "domcontentloaded"

## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
## Visible blockers
- none
## Informational lines
- none
