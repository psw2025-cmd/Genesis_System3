# Codex Deep Investigation Proposal — Architecture + Data Pipeline
**Date:** 2026-06-13
**Author:** Codex
**Status:** PROPOSED — requesting Gemini verification

## Executive Diagnosis

The original diagnosis is directionally correct, but the current worktree has already started bridging the old ML stack into the new ranking path. `src/ranking/ml_signal_aggregator.py` now exists, `scripts/daily_gain_rank_and_validate.py` imports `load_ml_confidence()`, and `src/ranking/gain_rank_engine.py` has an `ml_confidence` factor at 20% weight.

The serious remaining problem is that the bridge is not end-to-end operational. There is no scheduled pre-ranking step that creates a fresh `storage/live/dhan_index_ai_signals.csv`; `storage/` is empty in this workspace; both `dhan_live_ai_signals.py` and the daily rank runner currently fail before runtime because `pandas` cannot import missing `dateutil`; and Phase 82 lists scheduled jobs but does not enforce wall-clock execution. So the system is still fragmented operationally even though the bridge code exists.

Evidence:
- `scripts/daily_gain_rank_and_validate.py:33` imports the ML aggregator and `:142-150` loads `ml_confidence` before ranking.
- `src/ranking/gain_rank_engine.py:71-78` accepts `ml_confidence`; `:164-199` applies the ML score and returns `ml_confidence_score`.
- `src/ranking/ml_signal_aggregator.py:27-40` depends on `storage/live/dhan_index_ai_signals.csv`, but `find storage -maxdepth 5 -type f` returned 0 files.
- `python scripts/daily_gain_rank_and_validate.py --mode rank --top-n 3` failed because `pandas` could not import `dateutil`.
- `python core/engine/dhan_live_ai_signals.py` failed for the same `dateutil` dependency.
- `python core/engine/system3_phase82_job_scheduler.py --list` lists four jobs, all `NEVER_RUN`.
- `core/engine/system3_phase82_job_scheduler.py:88-128` runs a job when called; it does not evaluate `schedule_time`, `timezone`, `weekdays_only`, or loop as a daemon.

## Architecture Diagnosis

### What the old system produces

`core/engine/dhan_live_ai_signals.py` reads `storage/live/dhan_index_options_watch.csv`, takes the last 30 rows, runs the enhanced `system3_signal_engine` first, and falls back to per-underlying trained models if needed. Its output is per-option signal data with columns such as `pred_label`, `pred_confidence`, `prob_BUY_CE`, `prob_BUY_PE`, `prob_HOLD`, and `expected_move_score`; fallback output is appended to `storage/live/dhan_index_ai_signals.csv`.

This is the right source for a ranking bridge, but it is not self-feeding. It requires `storage/live/dhan_index_options_watch.csv`, and that file is not present in this workspace.

### What the new ranking system consumes

`GainRankEngine` ranks underlyings, not strikes. It consumes:
- option chain DataFrames by underlying,
- spot prices,
- optional previous/current OI history,
- optional volume history,
- optional ML confidence by underlying.

The ML bridge now exists at code level, but it reads only a CSV artifact. If the signal generator has not run within four hours, the aggregator returns `{}` and the ML factor becomes zero.

### How serious the disconnect is

Severity is still high. The code-level bridge is a partial fix, but production behavior is still disconnected unless the daily sequence runs:

1. fetch/build live option chain snapshot,
2. run `system3_signal_engine` / `dhan_live_ai_signals.py`,
3. write fresh `storage/live/dhan_index_ai_signals.csv`,
4. aggregate ML confidence,
5. run `GainRankEngine`,
6. validate and save OI cache,
7. consume retrain signal if fired.

Today only steps 4 and 5 are partially wired. Steps 1-3 and 7 are not in the configured daily automation.

## Master Orchestrator Plan

Create one production daily orchestrator, preferably `scripts/genesis_daily_orchestrator.py`, and make Phase 82 or cron invoke only that orchestrator. Phase 82 should remain a job registry/executor, not the business workflow.

Recommended daily sequence:

1. `preflight`: validate Python dependencies, token health, writable state paths, and Dhan/NSE data availability.
2. `09:00 IST data_snapshot`: fetch option chain through `core/data/nse_provider.py` now, Dhan Data APIs later when subscribed; persist a normalized snapshot to `storage/live/dhan_index_options_watch.csv` or a new canonical `state/live_chain_snapshot.json`.
3. `09:05 IST ml_signals`: run `core.engine.system3_signal_engine` directly on the normalized snapshot, not through stale CSV-only assumptions; write `storage/live/dhan_index_ai_signals.csv`.
4. `09:15 IST rank`: call `scripts/daily_gain_rank_and_validate.py --mode rank`, which now uses OI cache and ML confidence.
5. `15:35 IST validate`: run market validation and save post-market OI cache only from real NSE/Dhan data.
6. `15:40 IST trend`: compute rolling Spearman rho and hit-rate trend.
7. `15:45 IST retrain`: run a retrain consumer if `state/retrain_signal.json` exists and is unprocessed.

Phase 82 should either:
- enforce `schedule_time`, `timezone`, `weekdays_only`, and `last_run_date` itself in a daemon mode, or
- be replaced by OS cron/systemd that invokes the orchestrator at fixed times.

I recommend OS cron/systemd for actual production scheduling and Phase 82 for manual/status execution, because wall-clock scheduling inside a short-lived CLI is fragile.

## Data Pipeline Completeness

### Existing data flows

- `core/data/nse_provider.py` is now the shared NSE option chain and OI-cache layer.
- `scripts/daily_gain_rank_and_validate.py` loads NSE first, CSV second, synthetic fallback last.
- `state/market_cache.json` exists, but currently contains zero OI values, so no real previous-session OI baseline is established yet.
- `src/ranking/ml_signal_aggregator.py` can aggregate model output from `storage/live/dhan_index_ai_signals.csv`.
- `core/engine/build_dhan_training_dataset.py` builds training rows only from `storage/live/dhan_index_options_watch.csv`.

### Remaining data gaps

- `storage/` contains no live watch CSV, no AI signal CSV, no historical option chain files, and no training CSV in this workspace.
- The daily NSE chain DataFrame lacks Greeks fields such as delta/gamma/theta/vega. The ensemble predictors can fill missing features with zero, but that degrades model quality.
- Dhan option chain, quotes, OHLC, historical, and WebSocket data remain unavailable until Data APIs are subscribed.
- There is no IV history store, so `iv_percentile` is closer to a current median-IV score than a true percentile.
- There is no volume baseline store, so volume surge mostly uses absolute volume fallback.
- There are two active validators with different schemas and fetch logic: `src/validation/market_result_validator.py` and `src/ranking/market_result_validator.py`.

## Automation Completeness

Currently automatic:
- Token daemon/watchdog according to state files and prior logs.
- Phase 82 can run configured jobs manually.

Not actually automatic end-to-end:
- No persistent scheduler loop or external cron was found for the four Phase 82 jobs.
- No step creates fresh ML signal CSV before `daily_gain_rank`.
- No retrain signal consumer exists.
- No dashboard widget surfaces Spearman rho, gain rank, token expiry, OI freshness, or retrain status.

`core/engine/dhan_report_scheduler.py` is not a conflict for execution because it explicitly disables auto-scheduling. It is a naming/UX risk because `system3_ultra.py` still exposes it as a menu item, but it does not run jobs by itself.

## Retrain Signal Consumer

`src/validation/market_result_validator.py:304-315` can emit `state/retrain_signal.json`, but repository search found no consumer. A production-grade consumer should be explicit and idempotent:

- New script: `scripts/auto_retrain.py`.
- Reads `state/retrain_signal.json`.
- Validates signal freshness, reason, and whether it was already processed.
- Runs the approved trainer, likely `core/engine/dhan_blended_model_trainer_v2.py` first, then later a dedicated gain-regression trainer.
- Writes `state/retrain_status.json` with start/end time, command, exit code, logs, model paths, and previous/new validation metrics.
- Archives processed signals to `state/retrain_signals/YYYY-MM-DDTHHMMSS.json`.
- Never silently overwrites production models; stage into a candidate directory, run validation, then promote through an explicit model selector or approved promotion manager.

The consumer should not call `src/ml/ensemble_predictor.py` directly. Predictors should load promoted model artifacts; training scripts should own model creation and promotion.

## Testing Gaps

Runtime verification today:
- `python -c "import core; import src"` passed.
- `python scripts/daily_gain_rank_and_validate.py --mode rank --top-n 3` failed: missing `dateutil`.
- `python core/engine/dhan_live_ai_signals.py` failed: missing `dateutil`.
- `python -m pytest tests -q` failed: `pytest` not installed.
- `pip show pytest` returned package not found.

Minimum production-grade test suite:

1. Dependency/import smoke test for `pandas`, `requests`, `dhanhq`, `pyotp`, `pytest`, and model-loading libraries used in enabled paths.
2. `GainRankEngine` unit tests for OI history scoring, ML confidence scoring, zero-ML weight redistribution, and rank persistence.
3. `ml_signal_aggregator` tests for fresh/stale CSVs, missing columns, CE/PE probability aggregation, and empty-file behavior.
4. `nse_provider` parser tests using stored NSE JSON fixtures, including empty records, partial CE/PE rows, and bot/rate-limit errors.
5. Daily runner integration test with mocked NSE payloads and mocked ML signal CSV.
6. Validator schema compatibility test to force one canonical output contract.
7. Scheduler/orchestrator test proving jobs do not run outside scheduled windows and do not run twice on the same date.
8. Retrain consumer idempotency test: one signal triggers one staged retrain and then archives.

## Priority Implementation Order

1. Fix environment/requirements: add `python-dateutil` and `pytest` to `requirements.txt`; verify `python -m pytest` can start and daily scripts can import.
2. Build the missing pre-ranking signal step: use NSE chain data to create a canonical live snapshot and run `system3_signal_engine`/ensemble before ranking.
3. Replace CSV-only bridge assumptions with an in-memory path in the orchestrator while still writing CSV artifacts for auditability.
4. Consolidate validators to one canonical module and one report schema.
5. Implement `scripts/auto_retrain.py` with idempotent signal processing and staged model promotion.
6. Implement production scheduling: cron/systemd invoking one orchestrator, or Phase 82 daemon mode with real schedule enforcement.
7. Add IV and volume history stores so the non-ML ranking factors become real history-based signals.
8. Add dashboard status endpoints/widgets after the data contracts are stable.
9. Add a gain-regression head after the bridged classification system is measurable for several trading days.

## Alternatives Considered

- Treat the ML bridge as complete because `ml_signal_aggregator.py` exists. Rejected because no upstream automation creates its required CSV, and the storage directory is empty.
- Use `src/ranking/daily_gain_scanner.py` as the master workflow. Rejected because it still loads only stored CSV data for prediction and duplicates retrain emission logic.
- Keep Phase 82 as-is and rely on manual `--run-once`. Rejected because the stated goal is zero manual steps.
- Train a regression head before fixing orchestration. Rejected because new models will not improve daily rho if the daily pipeline does not reliably fetch data, create signals, rank, validate, and retrain.

## Success Criteria

- `python scripts/daily_gain_rank_and_validate.py --mode rank --top-n 3` runs successfully in a clean environment.
- A pre-market orchestrator run creates fresh option-chain snapshot and `storage/live/dhan_index_ai_signals.csv` before ranking.
- `state/gain_rank_history.json` entries include non-zero `ml_confidence_score` when model signals are available.
- Post-market validation writes one canonical schema and updates OI cache with non-zero real OI when NSE/Dhan data is reachable.
- A synthetic retrain signal triggers exactly one staged retrain and archives the signal.
- Scheduler status shows actual daily run times without manual `--run-once`.
- Focused tests for ranking, NSE parsing, ML aggregation, validation schema, scheduler, and retrain consumer pass in CI.
