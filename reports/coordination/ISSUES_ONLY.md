# ISSUES ONLY (overwrite)

**UTC:** `2026-08-29T11:10:58.823255+00:00`  
**Serving:** `01a4592f4c68c120a26b4fd955d1aff655b82e33`  
**Gates:** 3/7  
**Broker:** AUTH_OK v323  
**Scheduler healthy:** True  
**last_run_id:** `local-20260829T111055Z`  

## Access requests (credentials / human approval)

| resource | reason | ttl_requested | approver | owner | ticket | ack_utc |
|---|---|---|---|---|---|---|
| vault:SYSTEM3_CC_SIGNER_KEY + SYSTEM3_CC_SMOKE_TOKEN | signature_status UNSIGNED_PENDING_VAULT — mint denied | 1h | warghade2012@gmail.com | cursor-composer | issue:#188 | 2026-08-29T11:11:00.430967+00:00 |

## Acknowledged P0 board (agent-owned; ack refreshed each command_center run)

| ID | Pri | Status | Title | Live proof | Next | owner | ack_utc |
|---|---|---|---|---|---|---|---|
| PEND-001 | P0 | OPEN | Serving SHA lag behind GitHub main | serving=01a4592 (compare origin/main in session) | MRI Auto Deploy | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-004 | P0 | IN_PROGRESS | Stale chain badge false-green | UI fix landed locally; DONE only after serving SHA re-snap | Deploy OptionChain fix | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-005 | P0 | IN_PROGRESS | Default chain not ATM-centered | UI fix landed locally; DONE only after serving SHA re-snap | Deploy OptionChain fix | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-006 | P0 | IN_PROGRESS | Missing LTP Chg % | UI fix landed locally; DONE only after serving SHA re-snap | Deploy OptionChain fix | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-007 | P0 | IN_PROGRESS | Missing Buildup | UI fix landed locally; DONE only after serving SHA re-snap | Deploy OptionChain fix | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-008 | P0 | IN_PROGRESS | Missing OI%/Vol% | UI fix landed locally; DONE only after serving SHA re-snap | Deploy OptionChain fix | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-009 | P0 | IN_PROGRESS | Missing Greeks columns | UI fix landed locally; DONE only after serving SHA re-snap | Deploy OptionChain fix | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-014 | P0 | OPEN | Paper positions file missing | Positions file not found | Cloud persistence | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-015 | P0 | OPEN | Paper P&L synthetic/stale | awaiting implementation/proof | Paper lifecycle | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-016 | P0 | OPEN | /api/paper/* subroutes 404 | paper/trades=404 | Implement or document | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-017 | P0 | OPEN | Paper lifecycle gate FAIL | pass=False | Market-hours proof | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-018 | P0 | OPEN | Expectancy negative | pass=False | Better signals | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-020 | P0 | OPEN | ML predictions = 0 | total_predictions=0 | Prediction writer | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-021 | P0 | OPEN | Signal file missing / 429 | action=NO_TRADE http=200 | Persist + rate limit | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-023 | P0 | OPEN | Tick health gate FAIL | pass=False | Refresh/WS proof | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-024 | P0 | OPEN | Option visibility gate FAIL | pass=False | ATM audit | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-031 | P0 | OPEN | Multibagger 0 candidates | awaiting implementation/proof | Research pipeline | cursor-composer | 2026-08-29T11:11:00.430967+00:00 |
| PEND-003 | P1 | WATCH | Broker AUTH_OK keep fresh | connected=True auth=AUTH_OK v=323 | Watch rotate | shared |  |
| PEND-010 | P1 | OPEN | Equity options security_id map | awaiting implementation/proof | Scrip master map | shared |  |
| PEND-012 | P1 | OPEN | /api/charts 404 | charts=404 | Implement or mark MISSING | shared |  |
| PEND-013 | P1 | OPEN | multibagger/predictions/backtest 404 | predictions=404 multibagger=404 | Wire or honest MISSING | shared |  |
| PEND-022 | P1 | OPEN | /api/positions empty file | awaiting implementation/proof | Align paths | shared |  |
| PEND-025 | P1 | WATCH | API key public_readonly | public_readonly until user decides | User decision | shared |  |
| PEND-026 | P1 | OPEN | No RUHI board on UI | awaiting implementation/proof | UI board | shared |  |
| PEND-028 | P1 | OPEN | Gates not 7/7 | gates=3/7 trade_ready=False | Close blockers | shared |  |
| PEND-029 | P1 | OPEN | Full Dhan parity FAIL | awaiting implementation/proof | Close chain gaps | shared |  |
| PEND-032 | P1 | OPEN | Manual Dhan book vs paper separate | awaiting implementation/proof | Keep separate truth | shared |  |
| PEND-027 | P2 | OPEN | Claude memory stale | user action required | User | shared |  |
| PEND-030 | P2 | OPEN | Wrong Cursor path | user action required | User | shared |  |

Full options Excel: `reports/coordination/AGENT_OPERATING_OPTIONS.xlsx`
Open sheet `2_Options_Priority` — prefer rank 1 OPT-A1.

If vault mint is required, PR comment exactly: "Requesting approval: resource=vault:SYSTEM3_CC_SIGNER_KEY, reason=verify ACCESS_POLICY signature for ephemeral CC smoke token, ttl=1h, approver=warghade2012@gmail.com"
