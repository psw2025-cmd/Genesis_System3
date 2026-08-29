# System3 TRACKING CHECKLIST (live — overwrite only)

**Updated UTC:** `2026-08-26T19:35:00Z`  
**Base:** `https://genesis-system3-web-doq2wplepa-el.a.run.app`  
**Serving SHA:** `fb4772f9d52b67a31b55ee85aab8604e525bbad6`  
**GitHub main:** `0d6955987115f88b710aca0f0f0dec68d23fa6bc`  
**Lag class:** DOCS/TEST/CI_ONLY_LAG  
**Broker:** connected=True auth=AUTH_OK secret_v=320  
**Gates:** 2/7 trade_ready=False  
**Scheduler healthy:** True (business PARTIAL wrong-date)  
**LIVE trading:** False  
**Ruleset:** 21581518 · 6 required contexts  

**Counts:** see `TODO_CHECKLIST_FULL_VERIFY.md` · **P0 #188 still OPEN**

> This file is **replaced** on every tracker run. Do not create dated duplicate tracking logs.
> Catalog/solutions: `docs/handoffs/SESSION_ISSUES_MASTER.md` · Runbook §0A/§10/§11

## Checklist

| ID | Pri | Status | Title | Live proof | Need from user | Recommendation |
|---|---|---|---|---|---|---|
| PEND-001 | P0 | **CLASSIFIED_OK** | Serving SHA lag behind GitHub main | main tip docs/test; serving #367 | None | Do not redeploy |
| PEND-002 | P0 | **DONE** | Scheduler health UNHEALTHY | healthy=True http=200 | None | Watch business PARTIAL |
| PEND-003 | P1 | **WATCH** | Broker AUTH_OK keep fresh | connected=True auth=AUTH_OK v=320 | None | Watch rotate |
| PEND-004 | P0 | **IN_PROGRESS** | Stale chain badge false-green | UI fix local only; not on serving | None | Runtime PR+deploy |
| PEND-005 | P0 | **IN_PROGRESS** | Default chain not ATM-centered | UI fix local only | None | Runtime PR+deploy |
| PEND-006 | P0 | **IN_PROGRESS** | Missing LTP Chg % | UI fix local only | None | Runtime PR+deploy |
| PEND-007 | P0 | **IN_PROGRESS** | Missing Buildup | UI fix local only | None | Runtime PR+deploy |
| PEND-008 | P0 | **IN_PROGRESS** | Missing OI%/Vol% | UI fix local only | None | Runtime PR+deploy |
| PEND-009 | P0 | **IN_PROGRESS** | Missing Greeks columns | UI fix local only | None | Runtime PR+deploy |
| PEND-010 | P1 | **OPEN** | Equity options security_id map | awaiting | Optional | Scrip master map |
| PEND-011 | P1 | **DONE** | /api/holdings /api/funds 404 | holdings=200 funds=200 | None | Keep |
| PEND-012 | P1 | **OPEN** | /api/charts 404 | charts=404 | None | Implement or MISSING |
| PEND-013 | P1 | **OPEN** | multibagger/predictions/backtest 404 | 404 | None | Wire or MISSING |
| PEND-014 | P0 | **OPEN** | Paper positions file missing | Positions file not found | LIVE OFF | Cloud persistence |
| PEND-015 | P0 | **OPEN** | Paper P&L synthetic/stale | awaiting | None | Paper lifecycle |
| PEND-016 | P0 | **OPEN** | /api/paper/* subroutes 404 | paper/trades=404 | None | Implement/document |
| PEND-017 | P0 | **OPEN** | Paper lifecycle gate FAIL | pass=False | None | Market-hours proof |
| PEND-018 | P0 | **OPEN** | Expectancy negative | pass=False | Do not weaken | Better signals |
| PEND-019 | P0 | **OPEN** | Spearman rho below 0.70 | pass=False | Do not lower | Retrain/validate |
| PEND-020 | P0 | **OPEN** | ML predictions = 0 | total_predictions=0 | None | Prediction writer |
| PEND-021 | P0 | **OPEN** | Signal file / closed market | action=NO_TRADE MARKET_CLOSED | None | Persist + rate limit |
| PEND-022 | P1 | **OPEN** | /api/positions empty file | awaiting | None | Align paths |
| PEND-023 | P0 | **OPEN** | Tick health gate FAIL | pass=False | None | Refresh/WS proof |
| PEND-024 | P0 | **OPEN** | Option visibility gate FAIL | pass=False | None | ATM audit |
| PEND-025 | P1 | **WATCH** | API key public_readonly | policy | User decision | Document/enforce |
| PEND-026 | P1 | **OPEN** | No RUHI board on UI | awaiting | Confirm | UI board |
| PEND-027 | P2 | **OPEN** | Claude memory stale | user | Update memory | User |
| PEND-028 | P1 | **OPEN** | Gates not 7/7 | gates=2/7 | LIVE OFF | Close blockers |
| PEND-029 | P1 | **OPEN** | Full Dhan parity FAIL | awaiting | Keep Dhan open | Close gaps |
| PEND-030 | P2 | **DONE** | Wrong Cursor path | primary clone OK this session | None | Keep primary |
| PEND-031 | P0 | **OPEN** | Multibagger 0 candidates | awaiting | None | Research pipeline |
| PEND-032 | P1 | **OPEN** | Manual Dhan book vs paper separate | awaiting | None | Keep separate truth |

## Endpoint proof snapshot (2026-08-27 01:05 IST)

- holdings=200 funds=200 charts=404 predictions=404 multibagger=404
- paper=200 paper/trades=404 signals=200 MARKET_CLOSED
- batch/chains=200 (pre-market)
- auto_gates=2/7

## Agent next

1. Read `TODO_CHECKLIST_FULL_VERIFY.md` + this file
2. Runtime UI parity PR for #188 when ready (not this docs PR)
3. Market-hours semantic + business artifact dates
4. Do not redeploy for docs tip
