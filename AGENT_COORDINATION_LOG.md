# Multi-Agent Coordination Log — Portfolio + Real Trading Readiness

## Last updated: 2026-06-24 by Claude (web)

## What Claude just completed (this session)

### Portfolio Tab (NEW)
- Added `/api/broker/funds` endpoint in app.py (Dhan read-only available balance)
- Added Portfolio tab to dashboard (index.html + app.js)
- Wired 3 real broker APIs into dashboard poll:
  - `/api/broker/holdings` — real Dhan equity holdings
  - `/api/broker/positions/live` — real Dhan open positions
  - `/api/broker/funds` — real Dhan account balance
- Portfolio tab shows: account funds, real holdings table, real positions table, paper trade detail table
- All read-only, transparency banner shows MIXED_PAPER_AND_BROKER_READONLY

### Option Chain Fix (this session)
- Chain now tries Dhan P0 (live) FIRST via DataSourceManager + chain_adapter
- CSV (chain_raw_live.csv) is now TRUE last resort (was being served stale from Feb 1)
- This fixes ChgOI=0 issue — live previous_oi now flows for oi_change calc

## Field mapping reference (CONFIRMED from official Dhan docs 2026-06-24)
Dhan option_chain() leg fields:
- oi, previous_oi → change_in_oi = oi - previous_oi (NO direct field)
- greeks.{delta,gamma,theta,vega} (nested!)
- top_bid_price, top_ask_price (NOT bid/ask)
- implied_volatility (divide by 100 for decimal)
- last_price, volume, average_price, security_id

## For Cursor/Codex — DO NOT
- Do NOT revert chain to CSV-first (must be Dhan P0 first)
- Do NOT add bid/ask field names (Dhan uses top_bid_price/top_ask_price)
- Do NOT enable live trading (LIVE_TRADING_ENABLED stays 0)
- Do NOT remove the dhan_option_chain_parser.py (it's correct)

## Still pending (needs laptop/runtime — agents cannot do from repo)
- P0: Real market-day paper lifecycle proof (run during 09:15-15:30 IST)
- P0: 5+ Spearman rho validation days (currently 1/5)
- P1: Truth bridge live report (tools/run_truth_bridge_powershell.bat)
- P1: Production viability bridge run

## Real trading readiness gate (unchanged)
trade_ready = false
blocker = live_market_analyzer_paper_trade_not_proven
verdict = ANALYZER_READY_PROOF_INCOMPLETE


## ════════════════════════════════════════════
## 2026-06-24 UPDATE — RESILIENCE + CONFLICT FIXES (Claude)
## ════════════════════════════════════════════

### Multi-agent conflicts found & resolved
Multiple agents declared the SAME Vue refs → JS SyntaxError → blank dashboard.
- `portfolioData` declared twice (Claude + Cursor) → removed Claude's simpler one, kept Cursor's richer
- `brokerHoldings` declared twice (Claude ref + Cursor computed) → Cursor's renamed to `unifiedHoldings`
- `brokerPositions` declared twice → Cursor's renamed to `unifiedPositions`

### CRITICAL RULE FOR ALL AGENTS — before pushing app.js:
1. Run `node --check dashboard/app.js` — MUST pass before commit
2. Do NOT re-declare an existing `const` ref — search the file first
3. Setup-scope refs (4-space indent `    const x = ref(...)`) must be UNIQUE
4. If you need portfolio/unified data, use `unifiedHoldings`/`unifiedPositions` (already declared)
5. If you need raw broker API data, use `brokerHoldings`/`brokerPositions`/`brokerFunds` refs (already declared) or the `holdingRows`/`positionRows`/`fundsInfo` computed

### Resilience guards added (do NOT remove)
- `app.config.errorHandler` — render errors logged, app keeps running (no freeze)
- `window.addEventListener('error'/'unhandledrejection')` — global safety net
- `_polling` flag — non-overlapping polls (won't stack if backend slow)
- poll try/finally — survives any API/render error, auto-retries next cycle
- `connHealth` ref — LIVE/RECONNECTING/CONNECTING indicator in topbar
- `_NO_CACHE_HEADERS` in app.py — browser always gets freshest files after redeploy

### Why this matters
With 5+ agents editing the same dashboard files, one bad edit used to blank the
whole UI. Now: a syntax error in ONE section won't kill the rest, poll auto-recovers,
and the connection indicator shows when backend is redeploying.

### Verification protocol (run after ANY dashboard edit)
```
node --check dashboard/app.js   # syntax
grep -c "const portfolioData = ref(" dashboard/app.js   # must be 1
```
