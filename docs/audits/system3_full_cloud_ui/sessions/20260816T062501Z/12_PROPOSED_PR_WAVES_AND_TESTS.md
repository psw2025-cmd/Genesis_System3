# Proposed PR Waves (DO NOT EXECUTE IN THIS PHASE)

## Wave 0 — Truth / deploy lock
- Goal: serving-SHA convergence + honest weekend empty states
- Files: deploy contract, Truth/E2E empty-state copy, proof harness selectors
- Tests: exact serving SHA gate; 22-tab smoke on serving SHA

## Wave 1 — Dhan request architecture
- Goal: single-flight OC, eliminate stampede timeouts
- Files: datasource_manager.py, app.py chain cache, useData pollers
- Tests: concurrent /api/chain stress; no NO_DHAN_DATA under 4 parallel

## Wave 2 — Issue #188 universe parity
- Goal: broker-master vs API vs UI counts
- Files: equity_fo_universe, underlyings, coverage APIs, Data Integrity UI
- Tests: universe diff CI; index+equity sample OC

## Wave 3 — UI/backend wiring
- Goal: PCR fields, Prediction Audit, accuracy_trend consumer
- Files: OptionsIntelligence.tsx, PredictionAudit.tsx, MLPerformance.tsx, DTOs
- Tests: contract tests for chain schema; tab API map

## Wave 4 — Durable OC / lineage lake
- Goal: GCS/Parquet snapshots; survive Cloud Run recycle
- GCP: buckets, retention
- Tests: restart durability proof

## Wave 5 — Prediction / model registry
- Goal: label heuristic vs model; MLflow or signed manifest; promotion gates
- Files: ensemble_predictor, auto_retrain, dashboard ML tab
- Tests: model version visible in UI

## Wave 6 — Backtest / replay
- Goal: costed walk-forward gate
- Tests: leakage suite

## Wave 7 — Charts
- Goal: only charts with authoritative data (OI heatmap, ρ trend, paper equity)
- Tests: visual smoke

## Wave 8 — Observability
- Goal: alerts for disconnect, rotation fail, chain incomplete, SHA drift
- GCP: monitoring policies

## Wave 9 — IAM / secret hygiene
- Goal: disable old secret versions; close temporary run.developer debt
- Tests: deny proofs

## Wave 10 — Market-hours production proof
- Goal: Mon–Fri 09:30–15:30 IST 60-minute window, Issue #188 matrix
