# System3 TRACKING CHECKLIST (live — overwrite only)

**Updated UTC:** `2026-08-25T13:30:03.383223+00:00`  
**Base:** `https://genesis-system3-web-doq2wplepa-el.a.run.app`  
**Serving SHA:** `719566d23fd9aeb783a72fcec9493557f783781f`  
**Broker:** connected=True auth=AUTH_OK secret_v=319  
**Gates:** 2/7 trade_ready=False  
**Scheduler healthy:** False  
**LIVE trading:** False  

**Counts:** OPEN=24 IN_PROGRESS=6 WATCH=2 DONE=0 · **P0 active=19**

> This file is **replaced** on every tracker run. Do not create dated duplicate tracking logs.
> Catalog/solutions: `docs/handoffs/SESSION_ISSUES_MASTER.md` · Runbook §0A/§10/§11

## Checklist

| ID | Pri | Status | Title | Live proof | Need from user | Recommendation |
|---|---|---|---|---|---|---|
| PEND-001 | P0 | **OPEN** | Serving SHA lag behind GitHub main | serving=719566d (compare origin/main in session) | None | MRI Auto Deploy |
| PEND-002 | P0 | **OPEN** | Scheduler health UNHEALTHY | healthy=False http=200 | None | MRI Scheduler IAM |
| PEND-003 | P1 | **WATCH** | Broker AUTH_OK keep fresh | connected=True auth=AUTH_OK v=319 | None | Watch rotate |
| PEND-004 | P0 | **IN_PROGRESS** | Stale chain badge false-green | UI fix landed locally; DONE only after serving SHA re-snap | None | Deploy OptionChain fix |
| PEND-005 | P0 | **IN_PROGRESS** | Default chain not ATM-centered | UI fix landed locally; DONE only after serving SHA re-snap | None | Deploy OptionChain fix |
| PEND-006 | P0 | **IN_PROGRESS** | Missing LTP Chg % | UI fix landed locally; DONE only after serving SHA re-snap | None | Deploy OptionChain fix |
| PEND-007 | P0 | **IN_PROGRESS** | Missing Buildup | UI fix landed locally; DONE only after serving SHA re-snap | None | Deploy OptionChain fix |
| PEND-008 | P0 | **IN_PROGRESS** | Missing OI%/Vol% | UI fix landed locally; DONE only after serving SHA re-snap | None | Deploy OptionChain fix |
| PEND-009 | P0 | **IN_PROGRESS** | Missing Greeks columns | UI fix landed locally; DONE only after serving SHA re-snap | None | Deploy OptionChain fix |
| PEND-010 | P1 | **OPEN** | Equity options security_id map | awaiting implementation/proof | Priority underlyings optional | Scrip master map |
| PEND-011 | P1 | **OPEN** | /api/holdings /api/funds 404 | holdings=404 funds=404 | None | Deploy alias routes |
| PEND-012 | P1 | **OPEN** | /api/charts 404 | charts=404 | None | Implement or mark MISSING |
| PEND-013 | P1 | **OPEN** | multibagger/predictions/backtest 404 | predictions=404 multibagger=404 | None | Wire or honest MISSING |
| PEND-014 | P0 | **OPEN** | Paper positions file missing | Positions file not found | LIVE stays OFF | Cloud persistence |
| PEND-015 | P0 | **OPEN** | Paper P&L synthetic/stale | awaiting implementation/proof | None | Paper lifecycle |
| PEND-016 | P0 | **OPEN** | /api/paper/* subroutes 404 | paper/trades=404 | None | Implement or document |
| PEND-017 | P0 | **OPEN** | Paper lifecycle gate FAIL | pass=False | None | Market-hours proof |
| PEND-018 | P0 | **OPEN** | Expectancy negative | pass=False | Do not weaken gate | Better signals |
| PEND-019 | P0 | **OPEN** | Spearman rho below 0.70 | pass=False | Do not lower threshold | Retrain/validate |
| PEND-020 | P0 | **OPEN** | ML predictions = 0 | total_predictions=0 | None | Prediction writer |
| PEND-021 | P0 | **OPEN** | Signal file missing / 429 | action=NO_TRADE http=200 | None | Persist + rate limit |
| PEND-022 | P1 | **OPEN** | /api/positions empty file | awaiting implementation/proof | None | Align paths |
| PEND-023 | P0 | **OPEN** | Tick health gate FAIL | pass=False | None | Refresh/WS proof |
| PEND-024 | P0 | **OPEN** | Option visibility gate FAIL | pass=False | None | ATM audit |
| PEND-025 | P1 | **WATCH** | API key public_readonly | public_readonly until user decides | Enforce or document | User decision |
| PEND-026 | P1 | **OPEN** | No RUHI board on UI | awaiting implementation/proof | Confirm want board | UI board |
| PEND-027 | P2 | **OPEN** | Claude memory stale | user action required | Update Claude memory | User |
| PEND-028 | P1 | **OPEN** | Gates not 7/7 | gates=2/7 trade_ready=False | LIVE OFF until 7/7 | Close blockers |
| PEND-029 | P1 | **OPEN** | Full Dhan parity FAIL | awaiting implementation/proof | Keep Dhan open | Close chain gaps |
| PEND-030 | P2 | **OPEN** | Wrong Cursor path | user action required | Open primary path | User |
| PEND-031 | P0 | **OPEN** | Multibagger 0 candidates | awaiting implementation/proof | None | Research pipeline |
| PEND-032 | P1 | **OPEN** | Manual Dhan book vs paper separate | awaiting implementation/proof | None | Keep separate truth |

## Endpoint proof snapshot

- holdings=404 funds=404 charts=404 predictions=404 multibagger=404
- paper=200 paper/trades=404 open_count=0 total_trades=9
- chain/NIFTY=200 spot=24334.55 contracts=488
- signals action=NO_TRADE ml_predictions=0

## Agent next

1. Read this file first every session
2. Work highest P0 OPEN/IN_PROGRESS
3. After deploy: re-run `python scripts/system3_pending_tracker_refresh.py`
4. Re-snap UI; mark DONE only with serving proof
