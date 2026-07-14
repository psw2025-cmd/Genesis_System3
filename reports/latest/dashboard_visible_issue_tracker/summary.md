# Dashboard Visible Issue Tracker
Generated: 2026-07-14T14:04:42.838Z
Base: https://genesis-system3-backend.onrender.com
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
Global exception: `Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/chromium_headless_shell-1148/chrome-linux/headless_shell
╔═════════════════════════════════════════════════════════════════════════╗
║ Looks like Playwright Test or Playwright was just installed or updated. ║
║ Please run the following command to download new browsers:              ║
║                                                                         ║
║     npx playwright install                                              ║
║                                                                         ║
║ <3 Playwright Team                                                      ║
╚═════════════════════════════════════════════════════════════════════════╝`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Playwright/browser launch failed: Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/chromium_headless_shell-1148/chrome-linux/headless_shell
╔═════════════════════════════════════════════════════════════════════════╗
║ Looks like Playwright Test or Playwright was just installed or updated. ║
║ Please run the following command to download new browsers:              ║
║                                                                         ║
║     npx playwright install                                              ║
║                                                                         ║
║ <3 Playwright Team                                                      ║
╚═════════════════════════════════════════════════════════════════════════╝
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
## Visible blockers
- none
## Informational lines
- none
