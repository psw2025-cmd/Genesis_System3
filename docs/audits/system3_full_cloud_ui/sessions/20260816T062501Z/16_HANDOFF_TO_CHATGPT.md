# HANDOFF TO CHATGPT — System3 Full Cloud UI Forensic

**Read this first, then deeper matrices in the same session folder.**

## 1. Exact GitHub main

`c763ecf048478842688373cf674eb56a7dc04aa9` — `Fix false non-Dhan chain classification in live UI proof (#237)` (2026-08-16T05:29:18Z)

## 2. Exact serving runtime SHA

`a48e7b3c7c086a21352f718355d1c12d4a48955b`  
Revision `genesis-system3-web-00384-tuw`  
Image `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:a48e7b3c7c08-1786830179`

**Drift:** main ≠ serving. Treat serving SHA as runtime authority until deploy converges.

## 3. Fresh evidence window

- Start: 2026-08-16T06:25:01Z / 2026-08-16 11:55:01 IST
- End: 2026-08-16T06:35:47Z / 2026-08-16 12:05:47 IST
- Market: Weekend closed (Sunday)

## 4. Executive verdict

Broker **connected**, Paper/Live **off**, NIFTY chain **462** contracts with visible `source=dhan`. System is **not** Issue #188 complete, **not** institutional-ML complete, and has **material UI/backend + durability gaps**. See `01_EXECUTIVE_VERDICT.md`.

## 5–7. Findings

P0: F-001 serving drift; F-002 Issue #188 incomplete; F-014 safety correct (keep).  
P1: F-003..F-008, F-015 (broker now connected — historical handoff obsolete).  
P2/P3: F-009..F-013.

Full table: `00_MASTER_FINDING_TABLE.md` + `11_P0_P3_REMEDIATION_BACKLOG.md`.

## 8. 22-tab readiness

All 22 tabs loaded in Playwright with 0 console errors in capture.  
WAITING: truth, genesis, e2e-proof, overview, multibagger, system (weekend).  
Provenance visible: chain, trade, truth/e2e (source= marker).  
CSV: `02_LIVE_UI_22_TAB_SCORECARD.csv`.

## 9–10. Option universe / CE-PE

| Symbol | Contracts | CE | PE | Status |
|--------|-----------|----|----|--------|
| NIFTY | 462 | 231 | 231 | MARKET_CLOSED_DHAN_SNAPSHOT |
| BANKNIFTY | 0* | 0 | 0 | intermittent NO_DHAN_DATA / CHAIN_FETCH_TIMEOUT under concurrent fetch (*earlier probe had large body) |
| FINNIFTY | 0* | 0 | 0 | same |
| MIDCPNIFTY | 0* | 0 | 0 | same |

Full equity/BSE universe counts: **NOT_PROVEN** this session. CSV: `06_OPTION_UNIVERSE_CE_PE_COVERAGE.csv`.

## 11. Chart/graph gaps

See `09_CHART_GRAPH_VISUAL_GAP_MATRIX.md` (~22 tab rows; highest priority: ρ trend, pred-vs-actual, PCR fix, OI heatmap, paper equity).

## 12. FE/BE miswirings

See `03_UI_BACKEND_TRACE_MATRIX.csv` + supporting `lane_b_wiring__miswirings.csv`.

## 13. GCP runtime issues

Serving lag; capacity 429s on optional genesis routes; 257 enabled token secret versions; Firestore used for state; OC lake missing.

## 14. Rate-limit

Paced OC 3.4s; stampede timeouts; Cloud Run capacity 429 ≠ Dhan 429 (latter NOT_PROVEN this window).

## 15–17. Data / history / backtest

Lineage file-path oriented; OC EPHEMERAL; backtest institutional gates MISSING. Docs 05, 08.

## 18–20. Prediction / training / observability

Heuristic GainRank primary; registry MISSING; predict APIs underused; observability gaps in 10.

## 21. IAM debt

Not closed this audit; compare later to `deploy/gcp/system3_iam_baseline.json` without mutating.

## 22. Remediation waves

See `12_PROPOSED_PR_WAVES_AND_TESTS.md` (Waves 0–10).

## 23–24. Files / tests (expected)

Wave 0–3 touch primarily: `dashboard/frontend/src/components/**`, `dashboard/backend/app.py`, `chain_adapter.py`, `core/data/datasource_manager.py`, proof harnesses, coverage APIs.  
Tests: serving-SHA gate, concurrent chain, schema contracts, universe diff, 22-tab smoke.

## 25. Market-hours validation

**Required** — `13_MARKET_HOURS_REPRO_PLAN.md`.

## 26. Post-fix production proof

New browser lifecycle on converged serving SHA; four-index + equity samples; broker connected; live off; Issue #188 matrix categories.

## 27. Do NOT change (until authorized)

- LIVE_TRADING_ENABLED / AUTO_EXECUTE_TRADES / order APIs
- Secret payloads / PIN / TOTP in chat
- Unsolicited token mint storms
- This audit’s evidence-only scope (no silent functional merge)

## 28. NOT_PROVEN / uncertainties

- Full NSE/BSE equity+option counts vs broker master
- Live-session LTP/OI freshness SLO
- Dhan HTTP 429 rate in this window
- Whether main commits after a48e7b3 are runtime-affecting or proof-only
- Continuous paper lifecycle over market days

---

**PR purpose:** durable evidence handoff only.  
**Next actor:** ChatGPT designs remediation; human authorizes execution.

## Amendment A1 (Lane C closeout) — 2026-08-16T06:37Z

**P1 — Token rotate job latest execution FAILED on DESTROYED TOTP secret version**

- Execution: `genesis-system3-dhan-token-rotate-25szr`
- Error: `dhan-totp-secret/versions/latest` resolves to **versions/8 DESTROYED**
- Prior four rotate executions succeeded; access-token still at enabled **v257** and broker was **connected** during UI audit
- Blast: next scheduled/manual mint may fail until `dhan-totp-secret` latest points at a valid ENABLED version (user/Secret Manager ops — do not paste secrets in chat)
- Evidence: `supporting_lane_extracts/lane_c_gcp__03_jobs_summary.json`, `lane_c_gcp__FORENSIC_SUMMARY.md`
- Status: CONFIRMED_DEFECT (ops/runtime), remediation **not** executed in audit phase

Also recorded by Lane C: HTTP 429 count=8 in ~2h were mostly Cloud Run capacity aborts; ERROR=0; timeout text=0.
