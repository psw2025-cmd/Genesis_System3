# System3 Master Goal Lock

Repository: `psw2025-cmd/Genesis_System3`
Production authority: GCP project `system3-openalgo-safe`, region `asia-south1`, Cloud Run service `genesis-system3-web`

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

## Master objective

Build Genesis System3 as a world-class AI-assisted automated trading intelligence system for Indian option markets, with production-grade data integrity, prediction validation, paper-trade lifecycle truth, autonomous operations, and user-visible proof.

The system must continuously discover, predict, validate, and improve high-probability CE/PE opportunities while preserving strict evidence, safety, and reproducibility standards.

## Current operating safety lock

Until separately and explicitly proven/authorized:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `ANALYZE_MODE=1`
- `SYSTEM3_MODE=analyze`
- `AUTO_EXECUTE_TRADES=0`
- PAPER/analyzer only
- no real broker order placement/modification/cancellation/square-off

Broker authority is Dhan. Render.com hosting is forbidden (retired host). Never recreate `render.yaml`. Angel-era operating instructions are historical/non-authoritative.

## Result-oriented execution rule

Every phase, PR, script, workflow, agent run, and patch must define:

1. exact goal;
2. expected measurable result;
3. affected files/services;
4. test/verification path;
5. evidence generated;
6. PASS/PARTIAL/BLOCKED/FAIL/NOT_PROVEN status;
7. remaining blocker;
8. next action;
9. safety state;
10. evidence observation time and evidence class when the result is time-sensitive.

Code written is not completion. CI green is not completion. Deployment green is not completion. HTTP 200 is not semantic UI completion.

## Temporal truth lock

`latest` is not `live`.

A stored artifact, `reports/latest/`, `SYSTEM_STATE.md`, `CHANGE_LOG.md`, prior screenshot, proof pack, prior API response, PR narrative, or previous workflow result is historical after observation. It may explain what happened but cannot answer a later question about what is happening now.

For every current/live/present/now claim:

1. start a new observation after the current investigation/request begins;
2. query the authoritative production boundary;
3. include observation UTC time;
4. compare relevant independent sources;
5. after a fix/deploy/recovery, observe again.

For UI-facing truth, use a new Chrome/WebDriver session against the actual GCP production URL and capture fresh production screenshots + visible text + same-session read-only API state.

Use `scripts/gcp_live_ui_snapshot.py` and `scripts/system3_temporal_truth_guard.py`.

A phase may be frozen historically in a report, but that freeze does not automatically prove the same runtime condition is still true later.

## Full UI truth lock

The production dashboard has 22 canonical tabs:

`decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

A current UI PASS requires fresh production-browser evidence for the relevant scope. A full UI PASS requires all 22 tabs captured from the actual production URL.

For data-bearing tabs, rendering alone is insufficient. Validate visible data/state, freshness, loading/degraded/empty conditions, and relevant backend/API truth.

## Phase framework

### Phase A — Authority and safety

Goal: repository/GCP/broker/safety authority is unambiguous and enforced.

PASS requires current proof of:
- authoritative repo and production service;
- keyless WIF control path;
- LIVE/order execution disabled;
- broker secret isolation;
- declared IAM authority and remaining debt clearly classified.

### Phase B — Runtime and deployment integrity

Goal: current `main` and serving GCP production are intentionally aligned.

PASS requires fresh deployment metadata showing the exact serving revision/SHA/traffic plus runtime safety evidence.

### Phase C — Broker and market-data integrity

Goal: Dhan/authentication and required market-data surfaces are operational and fresh.

PASS requires fresh broker/API evidence. Token metadata alone cannot prove broker connectivity. HTTP 200 alone cannot prove market-data completeness.

### Phase D — Production UI truth

Goal: actual user-facing GCP UI matches backend truth.

PASS requires request-scoped production browser capture, semantic UI checks, and contradiction-free UI/API state.

### Phase E — Prediction-vs-actual validation

Goal: every prediction is compared with actual market outcomes using reproducible real-data evidence.

PASS requires measured, non-fabricated benchmark data with timestamps and source provenance.

### Phase F — Paper trade lifecycle and PnL reconciliation

Goal: signal -> plan -> paper entry -> management -> exit -> PnL is durably and consistently reconciled.

PASS requires end-to-end records and matching UI/API/storage truth.

### Phase G — Continuous learning

Goal: evidence-backed model/threshold improvements without unsafe auto-promotion.

PASS requires before/after out-of-sample or walk-forward evidence and rollback capability.

### Phase H — Multi-day production-grade proof

Goal: demonstrate stable behavior across relevant market sessions and failure/recovery conditions.

PASS requires repeated fresh proof, not one historical success.

## Agent drift prevention

Every agent must read the temporal truth policy before current-state reasoning.

If an old file contains statements such as `current`, `working`, `production ready`, `broker connected`, or `data complete`, treat those as statements about the file's observation time only unless live revalidated.

When agents disagree on live state, generate a new request-scoped observation. Agent consensus never overrides fresher authoritative evidence.

## Completion law

A task is complete only when the user's requested end state is proven at the authoritative boundary where it matters.

For user-visible features, that boundary is the fresh production UI plus correlated backend/runtime truth.
