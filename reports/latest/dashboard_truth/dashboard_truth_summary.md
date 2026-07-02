# Dashboard Truth Proof — Phase 11 (Updated)

**Generated:** 2026-07-02 21:08 IST (originally 17:38 IST)
**Status:** PARTIAL_UPGRADED — 2 real, API-cross-checked screenshots now captured; 4 panels still not captured

## Update: real Playwright screenshot captured this session

Found `npx playwright screenshot` CLI already available in this environment (avoided `npm install` given tight disk space) and self-captured a fresh screenshot at 21:05 IST: `reports/latest/dashboard_truth/screenshots/ui_overview_20260702_2105ist.png`.

Shows: live clock (21:05:12 IST), `MARKET CLOSED` badge, `DHAN ✗` (disconnected), `PAPER`/`LIVE OFF` badges, green LIVE websocket indicator, Option Chain panel locked with "Market Closed" message.

**Cross-checked**: `/api/broker/status` in the same minute showed `connected:false, error:TOKEN_EXPIRED_OR_INVALID` — exactly matching the screenshot's DHAN-X badge. (Broker had been connected at the 20:52 IST check earlier — its web-side token also expired in the intervening ~13 minutes, consistent with the web/worker token divergence finding.)

**Real discrepancy found and disclosed**: the backend now serves real 200-contract EOD chain data (see Phase 8), but the UI's Option Chain panel shows a hard client-side "Market Closed" lock regardless — never querying for after-hours EOD availability. A genuine frontend/backend truth gap, not fixed this session.

## Original 17:38 IST evidence (preserved)

User-shared screenshot showing `PAPER TRADING MODE`, `PAPER`/`LIVE OFF` badges, 0 open positions, ₹0.00 P&L — cross-checked against `/api/health` at the time, matched.

## Not captured this session

Broker panel, scheduler panel, analyzer/signal log, paper order/tradebook/lifecycle panel — real, disclosed gap, not faked.
