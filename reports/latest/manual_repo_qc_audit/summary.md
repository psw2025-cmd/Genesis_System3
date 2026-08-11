# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 08:51 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `b7bca87904aaae36af7a09b85021ea10ce179f8d`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..b7bca87904aaae36af7a09b85021ea10ce179f8d` is **13 commits ahead** and changes only `reports/latest/manual_repo_qc_audit/summary.md`; latest application/source HEAD therefore remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- PR #97 remains OPEN at head `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`. Its synthetic-P&L suppression still substitutes zero for unavailable/rejected P&L, so it does not close null/provenance concerns.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- Exact application-HEAD workflow/runtime proof remains **NOT PROVEN**. Workflow/configuration presence is not deployment evidence.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH** via `StateTruth` + domain-CAS |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH** via `OptionChainTruth` |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| AI prediction ledger | **MISSING / P0-P1** | **READY TO PATCH/DESIGN** via `PredictionTruth` |
| Model provenance / leakage control | **INCOMPLETE / P0-P1** | **READY TO PATCH** |
| Probability calibration / drift | **NOT PROVEN / P1** | **READY TO PATCH/DESIGN** |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH** via `DeploymentTruth` |
| Observability/runtime error truth | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, calibrated confidence, model-ready, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

- `AUTH-001..004` OPEN: login contract mismatch, pre-auth polling, raw browser API-key storage, incomplete session expiry/revocation proof.
- `UI-001..019` OPEN: false-valid defaults, source inference, empty/error ambiguity, missing authoritative mode/provenance, weak responsive/accessibility and deployment/build truth.
- `CHAIN-001..014` OPEN: warming PCR false-data, weak Dhan proof, incomplete Greeks, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented source, generic expiry fallback and parser-error collapse.
- `READY-001..009` OPEN: missing safety evidence default-safe paths, semantic lifecycle/risk/economic gates incomplete, weak account-success semantics, Render-era Live Gate copy and evidence-poor human approval.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN: default safety/data values, unproven mutation route, direct executor bypass, process-local lifecycle, stale-price handling, incomplete costs/reconciliation and legacy mutation UI residue.
- `RISK-001..009` OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrail conditions, unproven canonical wiring and proxy gate semantics.
- `WS-001..011` OPEN/UNPROVEN: socket-open≠healthy stream, weak heartbeat truth, REST/WS ordering, stale-value re-stamping, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped age and route-owner uncertainty.
- `GCP-001..011` OPEN: exact-revision proof missing, immutable digest absent, weak frontend SHA, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, weak typed safety/incident proof and incomplete Render retirement.
- `STATE-001..012` OPEN: file backend default, optional Firestore fallback, stale whole-snapshot overwrite, missing domain revisions/CAS, startup local-file promotion, plausible green defaults, duplicate SSOT methods, position error→empty collapse, weak identity, mixed-generation file sync and missing multi-writer tests.

## 4. New deep slice — AI/ML, prediction ledger, model provenance and calibration

### ML-001 / P0-P1 — Prediction Audit is a static contract, not a wired prediction ledger

**Exact proof:** `dashboard/frontend/src/components/workspaces/PredictionAudit.tsx` explicitly states that no production prediction ledger is wired and renders only `PENDING — DATA SERVICE PENDING`.

**Symptom/root cause:** the product has a first-class Prediction Audit tab but no immutable backend ledger/API connecting prediction issuance to later paper outcomes.

**Real-money impact:** a displayed AI decision cannot be forensically tied to the exact model, data cutoff, feature values, evidence, subsequent fills or realized outcome. Calibration and model accountability therefore cannot be proven.

**Exact files/routes:** `dashboard/frontend/src/components/workspaces/PredictionAudit.tsx`; new backend `prediction_ledger` service/router required; paper lifecycle and scanner/ranker contracts must supply IDs.

**Target behavior:** each prediction gets an immutable `prediction_id` at issuance and is never rewritten. Outcome/calibration records append later using correlation IDs.

**Minimal safe implementation:** introduce `PredictionTruth` + append-only prediction ledger; expose read-only `/api/predictions`, `/api/predictions/{id}`, `/api/predictions/calibration`.

**Schema:** prediction ID, issued time, target horizon, instrument/contract key, model artifact ID/hash, feature-schema hash, frozen data cutoff, raw score, calibrated probability, uncertainty, evidence/counter-evidence references, input-source IDs, source/runtime revision, maturity rule and state.

**Closure tests:** restart-safe append, duplicate-ID rejection, immutability test, exact model/data hash round-trip, scanner→prediction→paper correlation, matured outcome append without mutating original prediction.

**Fail-safe:** missing ledger/provenance => AI decision remains advisory and execution-ineligible.

**Status:** `READY TO PATCH/DESIGN`.

### ML-002 / P0-P1 — historical training PASS is promoted to `model_proof_ready=true`

**Exact proof:** `dashboard/backend/routers/ml.py::_options_model_record()` sets `model_proof_ready=True` solely when `reports/latest/options_ml_training/summary.json` has `status == PASS`, while the same record sets `validation_days=0`, `ready_for_live=False` and says forward paper validation is still required. `get_ml_performance()` then uses `any(model_proof_ready)` to set global model proof, and `MLPerformance.tsx` renders the page `ready` when that API flag is true.

**Root cause:** one boolean is overloaded across `TRAINED`, `HISTORICAL_VALIDATED`, `FORWARD_VALIDATED`, `CALIBRATED`, and `MONEY_READY` concepts.

**Impact:** the UI can show `MODEL_PROOF_READY` for a model that is only historically trained/evaluated, even with zero forward validation days.

**Canonical solution:** replace boolean readiness with a typed maturity state:
`NOT_TRAINED | TRAINED | HISTORICAL_VALIDATED | FORWARD_VALIDATING | FORWARD_VALIDATED | CALIBRATED | DRIFTED | RETIRED`.
Money/readiness gates consume explicit required states and never infer from `status=PASS`.

**Exact files:** `dashboard/backend/routers/ml.py`, `dashboard/frontend/src/components/MLPerformance.tsx`, auto-gate/readiness consumers.

**Tests/PASS:** historical training PASS with zero forward records must render `TRAINED / FORWARD VALIDATION PENDING`, never green model-proof-ready.

**Status:** `READY TO PATCH`.

### ML-003 / P1 — “Best Model” comparison selects first proven record, not best metric

**Proof:** `/api/ml/compare` builds `proven` then uses `next(iter(proven.keys()))` as `best_name`.

**Impact:** model ranking shown to operator can be dictionary-order dependent rather than evidence/metric driven.

**Solution:** require a versioned selection policy with primary metric, tie breakers, minimum sample/maturity, calibration constraint and untouched holdout. Return `selection_policy_id` and per-model comparable metrics. If models are not comparable, `best_model=null`.

**Tests:** reorder input dictionary; selected model must remain identical under deterministic policy.

**Status:** `READY TO PATCH`.

### ML-004 / P0-P1 — gain-rank score is converted into fake “confidence”

**Proof:** `/api/signal/top` returns `confidence = min(abs(gain_score)/100, 1.0)` and direction from score sign. Option-visibility audit similarly derives `conf` from gain score.

**Root cause:** rank/score is treated as though it were a calibrated probability.

**Impact:** operator/AI decision surfaces can present a mathematically uncalibrated ranking score as confidence, which is unsafe for sizing, ranking or readiness logic.

**Solution:** `rank`, `raw_score`, `forecast`, `probability`, `calibrated_probability`, `uncertainty` are separate nullable fields. No confidence field exists unless produced by a named calibration model with evidence.

**Tests:** a gain score of 80 must not produce 0.8 probability/confidence unless an explicit calibrator generated it.

**Status:** `READY TO PATCH`.

### ML-005 / P1 — percentage units are inferred heuristically in the UI

**Proof:** `MLPerformance.tsx::fmtPct()` assumes values `<=1` are fractions and values `>1` are already percentages.

**Impact:** ambiguous API units can silently turn 1.2 into `1.20%` when it may mean 120%, or otherwise hide contract drift.

**Solution:** API carries explicit metric unit/domain (`fraction_0_1`, `percent_0_100`, correlation `-1_1`). Frontend formatting is schema-driven only.

**Status:** `READY TO PATCH`.

### ML-006 / P1 — missing model counts become plausible zeros

**Proof:** ML table renders `total_predictions ?? 0`, `proof_pass_count ?? 0`, `validation_pending_count ?? 0`.

**Impact:** unavailable/malformed evidence can look like a genuine measured zero instead of unknown.

**Solution:** nullable metrics + quality state. Render `— / UNKNOWN` unless backend proves zero.

**Status:** `READY TO PATCH`.

### ML-007 / P0-P1 — `MLPerformanceTracker.record_prediction()` corrupts its own in-memory type contract

**Proof:** a newly created model stores `underlyings` as a `set`; after the first record the method converts it to a `list` for JSON. The next prediction for that same model calls `model_stats["underlyings"].add(underlying)`, which a list does not support.

**Symptom:** second prediction for an existing model can raise `AttributeError`, preventing reliable ledger/performance accumulation.

**Solution:** keep canonical internal structure type-stable (`set` only in memory) and serialize through a copy, or use list + explicit deduplicating append consistently. Add typed dataclass/Pydantic model.

**Tests/PASS:** 100 sequential predictions for same model, restart/load, multiple underlyings and concurrent append; zero exceptions/data loss.

**Status:** `READY TO PATCH`.

### ML-008 / P0-P1 — tracker accuracy math can produce false accuracy and biased averages

**Proof:** when `actual_result == 0`, accuracy is forced to `1.0` regardless of prediction error. `avg_accuracy` divides accumulated accuracy by **total predictions**, including predictions whose actual result/accuracy is still `None`.

**Impact:** accuracy can be materially wrong in both directions and is unsuitable as readiness evidence.

**Solution:** define target-specific metrics. For regression: MAE/RMSE/MAPE only where mathematically valid. For classification: accuracy/precision/recall/F1/AUC plus calibration. Matured sample count is separate from issued count; no immature prediction enters denominator.

**Tests:** actual zero with wrong prediction, immature predictions, class imbalance, all-zero outcome edge case.

**Status:** `READY TO PATCH`.

### ML-009 / P1 — ML tracker corruption silently becomes empty history and writes are non-atomic

**Proof:** `_load_data()` catches all parse/read exceptions and resets to `{models:{}, predictions:[]}`; `_save_data()` writes directly to the JSON file without temp+replace, locking or checksum.

**Impact:** corruption/partial write can erase apparent model history and be mistaken for no predictions; concurrent writers can lose records.

**Solution:** prediction ledger moves to authoritative append-only shared persistence. Until migration: atomic temp+replace, schema/checksum, file lock, corruption quarantine and explicit `LEDGER_ERROR` rather than empty.

**Status:** `READY TO PATCH`.

### ML-010 / P0-P1 — option-model holdout is not a proven market-time/purged split

**Proof:** dataset rows are sorted only **within each contract group**, then groups are appended. Training uses `train_test_split(..., shuffle=False)` on the concatenated dataset. Therefore the final 25% is not guaranteed to be a global chronological holdout across all contracts. Overlapping forward-step labels are also not purged around the split boundary.

**Impact:** train/test leakage or contract-order bias can inflate historical accuracy/AUC and invalidate model-selection evidence.

**Solution:** globally parse/sort timestamps, define immutable data cutoff, use purged walk-forward splits with embargo at least equal to label horizon, group-aware checks for contract/expiry leakage and a final untouched holdout period.

**Tests/PASS:** assert `max(train_event_time) < min(validation_event_time)` after purge for every fold; no overlapping label windows across boundaries; duplicate timestamp/contract leakage report = zero violations.

**Status:** `READY TO PATCH`.

### ML-011 / P1 — trained model artifact lacks full reproducibility identity

**Proof:** saved joblib contains `model`, `best_model`, `results`, `trained_at`; summary records row counts/results but no dataset SHA256, source-file manifest, feature schema hash, cutoff, label horizon, sklearn/python versions, dependency lock hash, git SHA or model artifact hash.

**Impact:** a dashboard metric cannot be proven to correspond to an exact dataset/code/model build.

**Solution:** `ModelArtifactManifest` with `model_id`, model SHA256, source Git SHA/tree, dataset manifest/hash, feature/label schema hash, train cutoff, fold definitions, library/container digest, hyperparameters, selection policy, generated time and evidence ID.

**Status:** `READY TO PATCH`.

### ML-012 / P1 — same test partition is used for model selection and reported performance

**Proof:** both candidate models are evaluated on one `X_test`; the higher AUC/accuracy chooses `best_model`, and the same scores are written as final results.

**Impact:** reported selected-model performance is optimistically biased because the evaluation set participates in model selection.

**Solution:** train → tuning/walk-forward validation → model selection → untouched final holdout. Holdout is evaluated once after policy/model freeze.

**Status:** `READY TO PATCH`.

### ML-013 / P1 — no calibration evidence exists for probability-like output

**Proof:** training reports accuracy and ROC AUC only; no Brier score, log loss, ECE, reliability bins, calibration slope/intercept or calibrated estimator is persisted. Yet product concepts use confidence/probability language.

**Solution:** if probabilistic decisions are needed, fit calibration on a dedicated calibration window or nested fold; persist Brier/ECE/reliability data and calibration-model hash. Calibration drift is monitored separately from discrimination metrics.

**Status:** `READY TO PATCH/DESIGN`.

### ML-014 / P0-P1 — no immutable prediction→after-cost outcome linkage

**Proof:** Prediction Audit admits no production ledger. Existing ML router uses gain-rank history and market-validation files; the inspected contracts do not require paper order/fill IDs, charges, slippage, taxes or reconciled net outcome per prediction.

**Impact:** even a statistically correct model cannot be proven economically useful, and profitability claims cannot be reproduced.

**Solution:** outcome append record references `prediction_id`, paper `correlation_id`, entry/exit fill IDs, maturity time, gross return, fees/slippage/taxes, net after-cost return, MAE/MFE and reconciliation evidence. Calibration metrics use matured outcomes; profitability/readiness uses reconciled net outcomes only.

**Status:** `READY TO PATCH/DESIGN`.

## 5. Canonical truth contracts

### 5.1 `SafetyTruth`
Mode, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 5.2 `DataTruthEnvelope` / `StreamTruth`
Source/session/instrument, source/backend/frontend timestamps, uncapped age/TTL, schema/normalizer versions, transport vs heartbeat vs stream state, sequence/rejected-old events, quality and evidence.

### 5.3 `OptionChainTruth`
Underlying/security ID/segment, requested+resolved expiry authority, provider/session, times/age/TTL, expiry-aware cache identity, schema/normalizer versions, nullable quote/Greek fields + field quality, completeness, source/runtime revision and evidence ID.

### 5.4 `DeploymentTruth`
Exact source/tree SHA, Cloud Build ID, immutable image digest, final Cloud Run revision/traffic, frontend/backend SHA, runtime app/service account, policy/config hash, secret/scheduler provenance, verified time and evidence ID.

### 5.5 `StateTruth`
Required shared backend, collection/document, shared-state health, runtime/instance ID, last shared read/write, per-domain revision/writer/event/time/schema/quality/evidence. Global version is diagnostic only.

### 5.6 `PredictionTruth` — NEW
`prediction_id`, immutable issue time, target/horizon, instrument key, model artifact ID/hash, dataset/feature schema hash, frozen data cutoff, raw score, calibrated probability, uncertainty, evidence/counter-evidence, input truth IDs, runtime/source revision, maturity rule/state, later append-only outcome/calibration links.

### 5.7 `ModelArtifactManifest` — NEW
Model/dataset/code/container hashes, feature+label schema, train cutoff, purged walk-forward folds, calibration/holdout windows, hyperparameters, environment fingerprint, selection policy, metrics/sample counts and evidence ID.

### 5.8 `PaperLifecycleTruth`, `GateTruth`, `RiskPolicy`, `PreTradeRiskTruth`
Retain immutable lifecycle, semantic evidence gates, server-owned policy and fail-closed pre-trade decision contracts.

## 6. Canonical remediation roadmap

- `SOL-01 Auth/session — READY TO PATCH`: correct login body; cookie-only auth; remove raw API key; auth-gate polling/WS; TTL/revocation tests.
- `SOL-02 SafetyTruth — READY TO PATCH`: one backend authority; missing/stale => UNKNOWN.
- `SOL-03 DataTruthEnvelope — READY TO PATCH`: remove production zero/plausible defaults.
- `SOL-04 Semantic readiness — READY TO PATCH`: HTTP/object presence never PASS; lifecycle/reconciliation/risk/economics mandatory.
- `SOL-05 OptionChainTruth + Greeks — READY TO PATCH`: nullable parser, expiry-aware cache, explicit provenance/IV units/full Greeks.
- `SOL-06 Immutable paper lifecycle — READY TO PATCH`: durable event ledger, IDs/idempotency, restart replay/reconciliation, costed P&L.
- `SOL-07 Scanner contract — READY TO PATCH`: rank/score/probability/forecast/realized distinct and nullable.
- `SOL-08 DeploymentTruth + GCP least privilege — READY TO PATCH`: immutable digest/final revision/source SHA, one service mutation, dedicated identities, WIF-only auth.
- `SOL-09 PreTradeRiskService — READY TO PATCH`: server-owned policy; fresh PASS required; UNKNOWN/ERROR denies.
- `SOL-10 Legacy UI quarantine — READY TO PATCH`: production entrypoint guard; no legacy mutation surface.
- `SOL-11 StreamTruth — READY TO PATCH`: transport != healthy stream; heartbeat schema; ordered REST/WS merge; uncapped age; true WS proof.
- `SOL-12 RuntimeEventEnvelope — READY TO PATCH/DESIGN`: incidents/logs bound to source SHA + digest + Cloud Run revision.
- `SOL-13 StateTruth + domain-CAS — READY TO PATCH`: Firestore required in GCP; sparse domain writes; no local authority fallback; restart/multi-writer proof.
- `SOL-14 PredictionTruth + ModelArtifactManifest — READY TO PATCH/DESIGN`: immutable prediction ledger, exact model/data identity, purged walk-forward, untouched holdout, calibrated probability, drift monitoring and after-cost outcome linkage.

### SOL-14 ordered implementation

1. Define `PredictionTruth`, `PredictionOutcome`, `ModelArtifactManifest`, `CalibrationReport` schemas.
2. Split existing model state from one boolean into typed maturity stages.
3. Remove gain-score→confidence derivation; preserve rank/raw score only.
4. Fix `MLPerformanceTracker` type instability and metric denominators, then deprecate file JSON as authority.
5. Move prediction issuance to append-only shared persistence with immutable IDs/idempotency.
6. Produce dataset/source manifests with SHA256 and exact frozen data cutoff.
7. Rebuild CE/PE evaluation using globally ordered purged walk-forward folds + embargo and an untouched final holdout.
8. Add model-selection policy ID; do not pick dictionary-first model.
9. Add probability calibration with Brier/ECE/reliability evidence when probability is exposed.
10. Add feature/prediction/calibration drift monitoring and explicit `DRIFTED` maturity state.
11. Wire scanner/candidate → prediction ID → paper lifecycle correlation ID → reconciled after-cost outcome.
12. Update `PredictionAudit.tsx` and `MLPerformance.tsx` to show provenance, maturity, sample counts, calibration, drift and outcome linkage; unknown remains unknown.
13. Add replay/restart/concurrency tests and exact-revision runtime evidence.

**SOL-14 PASS criteria:** every displayed AI decision maps to immutable prediction/model/data evidence; no rank is labeled probability; no historical-training PASS yields model-ready; no training/validation leakage across frozen time boundaries; calibrated probability has calibration evidence; final model performance comes from untouched holdout/forward data; matured predictions link to reconciled after-cost outcomes; exact deployed revision is known.

**Rollback/fail-safe:** if model artifact, ledger, calibration, cutoff or outcome evidence is missing/stale, AI remains advisory and all execution/readiness dependencies are inhibited.

## 7. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `16/20` | OPEN — ML missing counts add another unknown→zero reproduction |
| UI-002 | `4/20` | OPEN — score→confidence is another semantic metric mislabel |
| UI-003 | `7/20` | OPEN |
| UI-005 | `14/20` | OPEN — ML proof boolean/default semantics independently reproduce |
| UI-006 | `9/20` | OPEN |
| UI-007 | `8/20` | OPEN |
| UI-009 | `6/20` | OPEN |
| UI-011 | `4/20` | OPEN — prediction/model evidence remains incomplete |
| UI-016 | `8/20` | OPEN |
| UI-018 | `2/20` | OPEN |
| CHAIN-001..014 | retained previous counters | OPEN |
| READY-001 | `5/20` | OPEN |
| READY-003 | `3/20` | OPEN — trained-only model proof can influence readiness semantics |
| READY-008 | `2/20` | OPEN |
| PAPER-001..016 | retained previous counters | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| WS-001..010 | `1/20` each | OPEN |
| WS-011 | `1/20` | UNPROVEN |
| GCP-001..011 | `1/20` each | OPEN |
| STATE-001..012 | `1/20` each | OPEN |
| ML-001..014 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 8. Prioritized implementation order

### P0 Wave 1 — eliminate false-green/fail-open authorities
1. SOL-01 auth contract + auth-gated startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-08 exact `DeploymentTruth` baseline.
4. SOL-13 shared `StateTruth` authority + domain-CAS.
5. SOL-05 OptionChainTruth null/cache/expiry correction.
6. SOL-11 StreamTruth and ordered REST/WS merge.
7. SOL-09 server-owned risk + mandatory pre-trade authority.
8. SOL-06 durable lifecycle/idempotency/reconciliation.
9. **SOL-14 model maturity split + score/confidence correction + immutable PredictionTruth foundation.**
10. SOL-04 semantic readiness.
11. SOL-03 remaining zero/live/default-safe fallbacks.
12. SOL-10 legacy mutation UI quarantine.

### P1 Wave 2 — statistical/economic proof
Purged walk-forward + untouched holdout, calibration, drift, model/data hashes, prediction→paper→after-cost outcome linkage, full Greeks/model provenance, true WebSocket proof, GCP IAM split/WIF-only auth and revision-bound runtime incidents.

### P2 Wave 3 — institutional operator quality
Responsive/mobile, accessibility/keyboard/focus, command palette/search, dense table ergonomics, advanced drilldowns, security/session settings and audit export.

## 9. Product information architecture target

1. Command Center — Overview + Decision Intel + authoritative truth strip.
2. Market / Scanner — watch, scanner, ranker, signals.
3. Options & Greeks — chain, expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. **AI Decision Audit — Genesis Brain + Prediction Audit + model provenance + calibration/drift + evidence/outcome linkage.**
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — state authority, domain revisions, transport/heartbeat/source/freshness/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — deployment identity, incidents, logs, schema/parse errors, latency/reconnects and revision-bound evidence.
10. Security / Settings — sessions, IAM/policies, permissions, audit export and non-authoritative preferences.

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 10. Product UI visual evolution — V12

New concept: **AI Decision & Prediction Audit V12** inside the actual `AI Decision Audit` product workspace.

Changes driven by this iteration:
- model maturity is separated from real-money readiness;
- model SHA256, dataset hash, feature schema and frozen cutoff are first-class operator evidence;
- rank/raw score is visibly separated from calibrated probability;
- calibration and drift have dedicated panels;
- prediction ledger is immutable and prediction-ID based;
- every prediction can drill into model/data/runtime evidence;
- paper order/fill correlation and reconciled after-cost outcome are explicit;
- `TRAINED ≠ PROVEN`, `HIGH AUC ≠ CALIBRATED`, and `GROSS P&L ≠ AFTER-COST` are product rules;
- missing model/calibration/ledger evidence inhibits execution eligibility;
- live router remains locked.

Visual artifact: `Genesis_System3_AI_Prediction_Audit_Target_V12.png`.

## 11. Positive foundations to preserve

- `PredictionAudit.tsx` correctly refuses to display scanner gain-rank rows as validated forecasts and explicitly states the ledger is not wired.
- ML router keeps `ready_for_live=False` even where analyzer-only training proof exists; this safety intent should be preserved while fixing overloaded `model_proof_ready` semantics.
- CE/PE training uses `shuffle=False`, a better starting point than random shuffling, but it must become a globally chronological purged walk-forward design.
- Historical training pipeline forbids synthetic/fake/mock markers and keeps live trading off.
- Firestore persistence already uses transactions; local state writes use temp+replace; these are useful foundations but not sufficient multi-writer/state proof.
- Dhan option-chain traffic remains serialized/rate paced; WS reconnect has backoff+jitter foundations.
- Live Gate approval does not automatically enable live trading.

These are foundations, not readiness/profitability proof.

## 12. Historical proof/open-gate interpretation

Remain open:
- `EXACT_REVISION_CI_RUNTIME_NOT_PROVEN`
- `DEPLOYMENT_TRUTH_NOT_PROVEN`
- `SHARED_STATE_AUTHORITY_NOT_PROVEN`
- `RESTART_CONSISTENCY_NOT_PROVEN`
- `MULTI_WRITER_LOST_UPDATE_PROTECTION_NOT_PROVEN`
- `PREDICTION_LEDGER_NOT_PROVEN`
- `MODEL_ARTIFACT_IDENTITY_NOT_PROVEN`
- `PURGED_WALKFORWARD_NOT_PROVEN`
- `PROBABILITY_CALIBRATION_NOT_PROVEN`
- `MODEL_DRIFT_MONITORING_NOT_PROVEN`
- `PREDICTION_AFTER_COST_LINKAGE_NOT_PROVEN`
- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`
- `OPTION_CHAIN_RUNTIME_TRUTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture.

## 13. Closure standard

A finding becomes `CLOSED` only on the exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; route/schema reconciliation; model/data hashes and frozen-cutoff proof where applicable; leakage/purged-walk-forward/calibration/drift tests for ML; prediction→paper→after-cost reconciliation; concurrency/CAS/restart/failover tests; expiry/cache/freshness/order/reconnect tests as applicable; immutable image digest + final Cloud Run revision/runtime proof; analyzer/live-off unchanged; and no contradictory independent evidence.

## 14. Next audit/solution slices

1. Responsive/accessibility: desktop/tablet/mobile, keyboard/focus/live regions/dense tables.
2. Scanner/ranker contracts and performance/memory/concurrency under market-open load.
3. Security/session detail: cookie policy, CSRF, session revocation, command/settings permissions and audit export.
4. ML follow-up: exact market-validation file semantics and whether gain-rank post-market validation has frozen prediction IDs/cutoffs or look-ahead paths.
5. DB follow-up: exact paper/event persistence files and any SQLite/JSON/Firestore duplicate authorities not yet mapped.

## 15. Hard safety rule

A green UI, endpoint HTTP 200, socket OPEN, historical parser/training PASS, AUC/accuracy, rank-derived confidence, image tag, UI badge, workflow success description, global state version, Firestore transaction, local atomic write, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, inferred Dhan source, human approval or process-local simulator never substitutes for authoritative source+event time+domain revision+writer+freshness+schema+ordering+immutable prediction/model/data evidence+calibration+forward validation+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact source SHA+immutable image digest+final serving runtime revision proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.
