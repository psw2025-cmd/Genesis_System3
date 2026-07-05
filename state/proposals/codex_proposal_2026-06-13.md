# Codex Proposal — Consolidate NSE OI Provider Into Daily Ranking Path
> Agent: Codex | Date: 2026-06-13 | Domains: Architecture, Data Pipeline, API Integration, Testing, Dashboard
> Status: PARTIALLY IMPLEMENTED by Claude 2026-06-13 — nse_provider.py wired in, scheduler added. Remaining: time-of-day enforcement, tests, dual validator unification

---

## Problem

The OI persistence work is partially present but not integrated through the production daily path.

Evidence from this session:
- `scripts/daily_gain_rank_and_validate.py` now has local `save_oi_snapshot()` / `load_prev_oi()` helpers and passes `oi_history` into `GainRankEngine`.
- `core/data/nse_provider.py` already exists with NSE session warm-up, `fetch_option_chain()`, `total_oi_from_chain()`, `spot_price_from_chain()`, `load_oi_cache()`, and `save_oi_cache()`.
- The daily runner still loads CSVs or generates random synthetic chains in `load_live_chain_data()`; it does not call `core.data.nse_provider`.
- `state/market_cache.json` does not exist, so no usable previous OI baseline is available today.
- `state/market_validations/market_validation_2026-06-12.json` shows actual rankings with all `combined_gain_score: 0.0`, meaning validation fell back to ordering placeholders instead of real market signal.
- `config/system3_job_scheduler.json` only schedules `daily_status`; `daily_gain_rank_and_validate.py` is not scheduled at 09:15 and 15:35.
- `state/retrain_signal.json` can be emitted by validation, but no consumer was found in `core/engine/ensemble_predictor.py` or `src/ml/ensemble_predictor.py`.
- Local verification is blocked by environment drift: `python scripts/daily_gain_rank_and_validate.py --mode rank --top-n 3` fails because `pandas` cannot import missing `dateutil`; `python -m pytest tests -q` fails because `pytest` is not installed in the active interpreter.

## Recommended Solution

Approve a scoped integration fix:

1. Make `core/data/nse_provider.py` the single source for NSE option-chain fetching and OI cache persistence.
2. Replace `scripts/daily_gain_rank_and_validate.py` local cache helpers with calls to `nse_provider.load_oi_cache()` and `nse_provider.save_oi_cache()`.
3. Add a provider-backed chain loader in the daily runner:
   - Fetch NSE option-chain JSON per tracked underlying.
   - Convert records into the `GainRankEngine` DataFrame schema: `strike`, `option_type`, `oi`, `volume`, `ltp`, `iv`, and optional `change_pct`.
   - Use `spot_price_from_chain()` for spot values.
   - Fall back to CSV only when NSE fetch fails.
   - Use deterministic synthetic data only for explicit test/dev mode, not as an unlabelled production fallback.
4. Store cache in one schema only:
   ```json
   {
     "last_updated": "2026-06-13T15:35:00",
     "source": "nse_option_chain",
     "oi_data": {
       "NIFTY": 12450000
     }
   }
   ```
5. Add focused tests:
   - NSE JSON to DataFrame conversion preserves CE/PE rows and totals.
   - OI cache load/save round-trips and ignores corrupt cache files.
   - `GainRankEngine.rank_all(..., oi_history=...)` increases/decreases `oi_change_score` based on real previous/current totals.
   - Daily validation emits `state/retrain_signal.json` after three sub-threshold validation reports.
6. Repair dependency gates:
   - Install/use the repo dependency set before verification.
   - Ensure CI/dev requirements include the transitive dependencies needed by `pandas` and test tooling, or document the bootstrap command used by Claude agents.
7. Add dashboard status surface after the data path is fixed:
   - Spearman rho trend.
   - Latest gain rank table.
   - Dhan token status.
   - Retrain signal status.
   - OI cache freshness/source.

## Alternatives Considered

1. Keep local cache helpers in `daily_gain_rank_and_validate.py`.
   - Rejected because `core/data/nse_provider.py` already exists and duplicated cache schemas will cause split-brain state (`timestamp`/`oi` vs `last_updated`/`oi_data`).

2. Use `src/ranking/daily_gain_scanner.py` as the primary runner.
   - Rejected for now because `SYSTEM_STATE.md` names `scripts/daily_gain_rank_and_validate.py` as the daily runner, and `daily_gain_scanner.py` currently only loads stored CSV data for prediction.

3. Wait for Dhan Data API subscription.
   - Rejected because Dhan market-data endpoints remain unavailable, while the NSE public fallback is already the documented interim source.

4. Implement dashboard first.
   - Rejected because dashboard metrics would only expose synthetic/fallback ranking until the shared data path is corrected.

## Success Criteria

- `python scripts/daily_gain_rank_and_validate.py --mode rank --top-n 3` runs without synthetic fallback when NSE is reachable.
- `state/market_cache.json` is created after validation/full mode with `source: nse_option_chain` and non-zero OI totals.
- Next-day ranking passes non-empty `oi_history` for all successfully fetched symbols.
- Validation reports no longer contain all-zero actual composite scores when NSE is reachable.
- Scheduler contains explicit 09:15 rank and 15:35 validate jobs.
- A test run covers provider conversion, cache round-trip, gain-rank OI history scoring, and retrain signal emission.

## Cross-Verification Request

Gemini should independently verify whether `core/data/nse_provider.py` is sufficiently robust for shared use or whether it needs retry/backoff and response-shape validation before becoming the single provider. Gemini should also verify that the daily runner, not `GainRankEngine`, is the right layer for JSON-to-DataFrame conversion.
