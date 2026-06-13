# Codex Supplementary Proposal — Scheduler + Test Coverage for Gain Ranking
> Agent: Codex | Date: 2026-06-12 | Domain: System Architecture + Testing
> Status: IMPLEMENTED by Claude 2026-06-13 (scheduler jobs added, schema mismatch fixed, synthetic contamination guard added)

---

## Problem

The OI persistence work only improves prediction quality if the daily runner executes at the required market times. Current evidence:

1. `SYSTEM_STATE.md` still lists `scripts/daily_gain_rank_and_validate.py` as "Built, not yet scheduled" and marks scheduling at 09:15 + 15:35 as pending.
2. `config/system3_job_scheduler.json` contains only the `daily_status` job. There is no `daily_gain_rank` or `daily_gain_validate` entry.
3. `core/engine/system3_phase82_job_scheduler.py` can run configured jobs once, but its current schema has no time-of-day enforcement, weekday/trading-day guard, or command arguments for `--mode rank` / `--mode validate`.
4. `run_system3.py` is explicitly a disabled legacy menu and is not an active orchestrator for this workflow.

Without scheduler integration, `state/market_cache.json` may never be created at 15:35 and morning ranking may keep using fallback OI scoring even after the cache code exists.

## Recommended Solution

Implement the OI persistence fix only together with a minimal scheduled job path:

1. Extend the active scheduler config/schema to support command jobs with explicit arguments and market times:
   - `daily_gain_rank`: `python scripts/daily_gain_rank_and_validate.py --mode rank`, weekdays at 09:15 IST.
   - `daily_gain_validate`: `python scripts/daily_gain_rank_and_validate.py --mode validate`, weekdays at 15:35 IST.
   - Optional `daily_gain_trend`: `python scripts/daily_gain_rank_and_validate.py --mode trend`, weekdays at 15:40 IST.
2. Add a trading-day/time guard rather than relying only on a human to run `--run-once`.
3. Log last run, status, stdout/stderr excerpt, and skipped reason into scheduler state so Claude can audit whether rankings and validation actually ran.
4. Keep `daily_gain_rank_and_validate.py` as the narrow domain runner; scheduler code should only invoke it and record execution status.

## Testing Gaps

The current tests do not cover the OI/ranking integration path. Add focused tests before or with implementation:

1. `GainRankEngine._oi_change_score()` with real `prev_oi/curr_oi`, zero previous OI, missing OI column, and negative/large OI changes.
2. `daily_gain_rank_and_validate.py` cache behavior:
   - missing cache returns no `oi_history`;
   - stale or malformed cache is ignored;
   - current snapshot uses the same OI column selection as the engine;
   - synthetic fallback does not write random OI into the persistent cache as if it were real market data.
3. NSE provider parsing:
   - CE-only, PE-only, missing `records.data`, missing `underlyingValue`, zero OI, and IV values reported as `0`.
4. Scheduler config tests:
   - rank and validate jobs exist;
   - commands include the correct modes;
   - jobs are skipped outside schedule/trading days;
   - failed runner subprocesses are recorded as failed.
5. Daily validation schema compatibility:
   - `scripts/daily_gain_rank_and_validate.py` currently expects fields like `spearman_correlation`, while `src/validation/market_result_validator.py` returns `rank_correlation_spearman`. This mismatch needs a regression test or code normalization.

## Edge Cases Gemini Missed

1. Same-day overwrite: a 09:15 cache save or accidental full run can overwrite yesterday's close before ranking, making `prev_oi == curr_oi`.
2. Synthetic/cache contamination: fallback chain data must not be persisted as a real OI baseline.
3. Stale calendar handling: a fixed 72-hour cutoff can reject valid long-weekend/holiday baselines or accept stale data after unexpected market closures.
4. Expiry rollover: total OI can jump because weekly/monthly expiry changed, not because of actionable buildup.
5. NSE schema/session failures: rate limiting, 401/403 cookie expiry, empty `records.data`, partial CE/PE rows, and index-specific availability need graceful degradation.
6. Symbol universe mismatch: proposal names `<50 symbols>`, but the permanent goal is all NSE/BSE option strike symbols, all expiries, all underlyings.
7. Validator duplication: there are two validator modules with overlapping NSE logic and different report schemas, so provider extraction must avoid creating a third incompatible path.
8. Scheduling is required for persistence to matter; a cache helper alone does not create an end-to-end daily baseline.

## Alternatives Rejected

1. Manual cron only: rejected because the repo already has scheduler state/logging and Claude needs auditable execution status.
2. Full database now: rejected for this phase. JSON is acceptable if it includes source/date/session metadata and rejects synthetic/stale data.
3. Provider extraction as a standalone refactor: rejected unless the daily runner and validator both consume it with tests; otherwise it leaves duplicated behavior and hidden schema drift.

## Success Metrics

1. `config/system3_job_scheduler.json` includes enabled jobs for 09:15 rank and 15:35 validate.
2. Scheduler dry-run/list output shows both jobs and their next intended market time.
3. After a post-market run, `state/market_cache.json` exists with source, date/session, and non-synthetic OI totals.
4. Next ranking run passes non-empty `oi_history` into `GainRankEngine.rank_all()`.
5. Focused tests for cache, provider parsing, scheduler config, and ranking OI scoring pass.
6. `state/gain_rank_history.json` records stable, explainable `oi_change_score` values rather than random fallback-driven scores.
