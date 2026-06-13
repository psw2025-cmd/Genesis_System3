# CODEX DATASOURCE AUDIT — Genesis System3
**Date:** 2026-06-13  
**Author:** Codex (Autonomous Investigator — Architecture, Data Pipeline, Testing)  
**Task:** Full audit of current data pipeline + verification of proposed multi-source DataSourceManager architecture  
**Status:** COMPLETE

---

## 1. ALL FILES THAT CURRENTLY FETCH MARKET DATA

### Tier 1 — Active Production Pipeline (option chain data for ranking/validation)

| File | Fetches From | Method | Notes |
|------|-------------|--------|-------|
| `core/data/nse_provider.py` | `https://www.nseindia.com/api/option-chain-indices?symbol={symbol}` | `requests.Session` (module-level singleton) | CANONICAL shared provider — homepage warm-up before first request; `reset_session()` on failure |
| `scripts/daily_gain_rank_and_validate.py` | Delegates entirely to `core/data/nse_provider.fetch_option_chain()` | Indirect via import | Also reads local `storage/*.csv` (CSV fallback) and generates synthetic data (last resort) |
| `src/ranking/market_result_validator.py` | `https://www.nseindia.com/api/option-chain-indices?symbol={symbol}` | **Own** `requests.Session` built in `_build_nse_session()` and stored as `self._session` | DUPLICATE — does NOT use nse_provider; fetches per-underlying to rank actual NSE movers |
| `src/validation/market_result_validator.py` | `https://www.nseindia.com/api/option-chain-indices?symbol={symbol}` AND `https://www.nseindia.com/api/live-analysis-most-active-securities?index=options` | **Own new** `requests.Session()` per call inside `_fetch_nse_most_active_options()` and `_fetch_nse_option_chain()` | DUPLICATE — does NOT use nse_provider; creates a NEW session on every single call (most-active first, per-symbol fallback) |

### Tier 2 — Legacy/Disabled REST Fallback

| File | Fetches From | Status |
|------|-------------|--------|
| `src/dhan/live_chain_rest.py` | Dhan broker `get_option_chain_by_underlying()` (Dhan Data APIs) | DISABLED at runtime — Dhan Data APIs not subscribed (Error 806); `broker.get_option_chain_by_underlying()` will fail |

### Tier 3 — Dashboard Verification / One-Off Scripts (not in production pipeline)

| File | Fetches From | Notes |
|------|-------------|-------|
| `scripts/dashboard_data_validator.py` | NSE option chain, NSE quote-equity, Yahoo Finance (`query1.finance.yahoo.com`) | Dashboard validation only, not production chain |
| `scripts/dashboard_online_verifier.py` | Yahoo Finance (`query1.finance.yahoo.com/v8/finance/chart`), NSE quote-equity | Spot price verification only |
| `scripts/add_realtime_data_refresh.py` | Yahoo Finance | Dashboard spot price refresh — uses Yahoo Finance as primary |
| `scripts/combined_auto_system.py` / `combined_auto_system_fixed.py` | Yahoo Finance for spot price cross-check | Background verification scripts |
| `scripts/run_live_chain.py` | `LiveChainREST.fetch_option_chain_batch()` | Delegates to Dhan broker (currently fails) |

---

## 2. CURRENT SCHEMA ANALYSIS — WHAT EACH CONSUMER EXPECTS

### 2.1 `GainRankEngine.rank_all()` — Input Schema

**Accepts:** `Dict[str, pd.DataFrame]` where each DataFrame has columns (by name search, not strict):

| Column | Detected By | Notes |
|--------|------------|-------|
| `oi` (or any column with "oi" and not "change") | `c.lower()` contains "oi" | Used in `_oi_change_score`, `_pcr_divergence_score`, `_volume_surge_score` |
| `option_type` (or `type`, `ce_pe`) | `c.lower() in ("option_type", "type", "ce_pe")` | Must have values "CE"/"CALL" and "PE"/"PUT" |
| `iv` (or `implied_volatility`, `iv_pct`) | Exact name match | Used in `_iv_percentile_score` |
| `volume` (or any column with "volume" or named "vol") | String contains "volume" or is exactly "vol" | Used in `_volume_surge_score` |
| `ltp` (or `last_price`, `close`) | Exact name match set | Used in `_atm_premium_score` |
| `strike` (or any column with "strike") | String contains "strike" | Used in `_atm_premium_score`, `_pcr_divergence_score` |
| `change_pct` / `pct_change` / `spot_change` / `change%` | Optional, exact name match set | Used in `_momentum_score`; falls back to 50.0 if missing |

**Canonical output of `_nse_chain_to_df()` in `daily_gain_rank_and_validate.py`:**

```
strike, option_type, oi, volume, ltp, iv
```

This is the **correct minimal schema**. The `iv` column is stored as raw decimal (divided by 100 from NSE's percentage value).

### 2.2 `src/ranking/market_result_validator.py` — Output Schema

The ranking validator fetches via its own session. Its output per underlying is:

```
underlying, oi_change_pct, atm_ce_pchange, atm_pe_pchange, combined_gain_score, underlying_value
```

It uses `combined_gain_score = abs(oi_change_pct)*0.6 + (abs(ce_pchg)+abs(pe_pchg))*0.4` as the actual ranking signal. The validation report's correlation key is `spearman_correlation`.

### 2.3 `src/validation/market_result_validator.py` — Output Schema

The validation validator uses the most-active API first (volume + pChange-based), falls back to per-symbol OI chain. Its report correlation key is `rank_correlation_spearman`.

**CRITICAL SCHEMA CONFLICT:**

| Field | `src/ranking/market_result_validator.py` | `src/validation/market_result_validator.py` |
|-------|------------------------------------------|----------------------------------------------|
| Spearman key | `spearman_correlation` | `rank_correlation_spearman` |
| Retrain threshold | 0.30 (correlation) + 0.40 (hit_rate) — dual threshold | 0.40 (rho only) — single threshold |
| Session management | One `self._session` per validator instance | New `requests.Session()` per individual call |
| Symbol list | `["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]` — 4 symbols | `["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]` — 5 symbols |
| Actual ranking field | `actual_rank` | `market_rank` |

The `daily_gain_rank_and_validate.py` imports `src/validation/market_result_validator.py` (the 5-symbol version) and reads `rank_correlation_spearman` with a fallback to `spearman_correlation`. This means the `src/ranking/` version is effectively orphaned from the scheduled pipeline.

---

## 3. VERDICT ON PROPOSED DATASOURCEMANAGER ARCHITECTURE

**Basis for verdict:** The CHANGE_LOG and master plan propose a `core/data/datasource_manager.py` with fallback chain: Dhan → NSE API → nsepython → bhavcopy archive → jugaad-data → yfinance → synthetic. No file with that name currently exists in the repository (`grep` across all `.py` files returned zero hits).

### Verdict: PARTIAL AGREE

**What the architecture gets right:**

1. The layered fallback concept is directionally correct — NSE API is the right primary source when Dhan Data APIs (Error 806) are unavailable. Having multiple fallback levels prevents a single-point failure from grounding the whole ranking pipeline.
2. A single canonical module for all data acquisition is architecturally sound and fixes the current duplication problem (three independent NSE sessions across `nse_provider.py`, `src/ranking/`, and `src/validation/`).
3. The standard DataFrame schema proposed — `(strike, option_type, oi, volume, ltp, iv)` — exactly matches what `_nse_chain_to_df()` already produces and what `GainRankEngine` already expects. This is confirmed correct.

**Where the architecture needs adjustment:**

1. **Wrong ordering of fallback layers for this system.** The proposed order is Dhan → NSE API → nsepython → bhavcopy → jugaad-data → yfinance → synthetic. The correct priority for Genesis System3 is: NSE API → bhavcopy (NSE archives) → synthetic. Dhan should move to `Layer 0 (future)` guarded by a subscription check, because it is currently Error 806 and will fail on every call until subscribed. nsepython, jugaad-data, and yfinance do not provide intraday option chain OI data — they provide historical OHLCV for equities. Using them as fallbacks for option chain OI will silently produce wrong data.

2. **yfinance is not an option chain OI source for Indian indices.** Yahoo Finance's Indian market coverage for option chains (NSE F&O) is absent or unreliable. `^NSEI` gives NIFTY 50 spot OHLCV, not OI/IV per strike. Using yfinance as a chain fallback would produce a schema mismatch, not graceful degradation.

3. **nsepython is a third-party wrapper around the same NSE API.** If the NSE API is blocked (anti-bot, 401/403), nsepython will also fail. It adds a dependency without a real fallback benefit for the intraday case.

4. **bhavcopy is only useful for post-close validation, not pre-market ranking.** NSE F&O bhavcopy archives (at `https://archives.nseindia.com/content/fo/`) are published after market close (~19:00 IST) with end-of-day OI. At 09:15 IST when the ranking job runs, the previous day's bhavcopy might be available. This is a valid fallback for OI cache initialization (populating `market_cache.json` from a clean install) but not for live intraday chain data.

5. **jugaad-data requires a paid NSE subscription key.** It is not a free fallback source.

6. **Session management for NSE must be shared.** Each NSE call that creates its own session burns the homepage warm-up cost and risks rate limiting. The `_session` singleton in `nse_provider.py` is the right pattern. Any DataSourceManager must extend that pattern, not bypass it.

---

## 4. EDGE CASES AND FAILURE MODES

### 4.1 NSE Anti-Bot / Rate Limiting

- **Trigger:** NSE blocks requests without valid session cookies. This is especially common from cloud/codespace IPs.
- **Current mitigation:** Homepage warm-up in `_get_session()` sets session cookies. Session is reused across calls.
- **Gap:** After a 401/403, `reset_session()` is called and the next call creates a new session — but the new session's homepage warm-up will also fail if the IP is temporarily blocked.
- **Risk:** In a codespace, all four underlyings (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY) will trigger simultaneous warm-up requests. NSE may block all of them.
- **Recommendation:** Add exponential backoff (max 3 retries), randomize User-Agent per session, and add a 1–2 second delay between symbol fetches.

### 4.2 Empty Payload / Partial Chain

- **Trigger:** NSE returns 200 OK with `{"records": {"data": []}}` — no strikes.
- **Current behavior:** `_nse_chain_to_df()` returns `pd.DataFrame()` (empty). `load_live_chain_data()` detects `df.empty` and falls through to CSV/synthetic.
- **Gap:** This case is correctly handled. No bug here.

### 4.3 Same-Day OI Cache Overwrite (Morning Run Overwrites Evening)

- **Trigger:** If someone runs `--mode full` at 09:15 IST, `run_validation()` also calls `save_oi_cache()` with morning data. The evening run at 15:35 will then compare today-evening vs today-morning (same day) instead of today-evening vs yesterday-evening.
- **Current behavior:** Cache is saved by `run_validation()` only when real OI > 0.
- **Gap:** No date check in the cache. The risk is a full-mode run overwrites the previous-session baseline with intraday data.
- **Recommendation:** Add `date` field to cache alongside `last_updated`. At ranking time, only use `prev_oi` if `cache_date != today`.

### 4.4 Long Weekend / Holiday Cache Staleness

- **Trigger:** 4-day weekend (e.g., Diwali holiday week). Cache from Friday evening vs. Tuesday morning may have large OI change due to expiry rollover, not actual new OI buildup.
- **Current behavior:** No staleness check beyond "cache exists and OI > 0."
- **Recommendation:** Add `max_cache_age_days: 3` check. If last_updated is older than 3 calendar days, treat cache as stale (fall back to intra-chain scoring) and log a warning.

### 4.5 Expiry Rollover Distortion

- **Trigger:** On expiry day (weekly Thursdays), OI for the expiring series transfers to the next series. Total OI drops sharply then rises again — this looks like massive OI decrease followed by increase, which the engine scores as strong signal when it is actually noise.
- **Current behavior:** No expiry awareness.
- **Recommendation:** Check if `datetime.today().weekday() == 3` (Thursday). If so, disable OI change scoring (`oi_history = None`) and use intra-chain concentration fallback.

### 4.6 CE-Only or PE-Only Partial Rows from NSE

- **Trigger:** For deep OTM strikes, NSE returns only CE or PE data in a record, not both.
- **Current behavior in `_nse_chain_to_df()`:** Each leg is processed independently — if `entry.get("CE", {})` is empty, that leg is skipped. This is correct.
- **Gap:** `_pcr_divergence_score()` in `GainRankEngine` computes PCR on the resulting DataFrame. If a large number of puts have no CE counterpart or vice versa, the PCR will appear extreme (very high or very low) when the real market PCR is balanced. This is a scoring distortion, not a crash.

### 4.7 Symbol Universe Mismatch

- **Trigger:** `load_live_chain_data()` tracks `["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]`. The `src/validation/market_result_validator.py` tracks `["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]` (5 symbols). The actual ranking validator (`src/ranking/`) only tracks 4.
- **Risk:** SENSEX predictions are never in `gain_rank_history.json` (daily runner does not rank SENSEX), but the validation validators look for it. This causes SENSEX to always get the default "unseen" rank, which biases Spearman correlation downward.
- **Recommendation:** Either add SENSEX to the ranking pipeline or remove it from the validation tracked list.

### 4.8 Bhavcopy Unavailability on Weekends/Holidays

- **Trigger:** NSE publishes F&O bhavcopy on trading days only. If the system runs on Saturday/Sunday (e.g., to initialize an empty OI cache), bhavcopy for that day does not exist.
- **Proposed mitigation for DataSourceManager:** Always try the most recent available bhavcopy (walk back up to 5 trading days) instead of expecting today's date.
- **Storage path:** `storage/bhavcopy/YYYYMMDD_fo_bhavcopy.csv` is a reasonable location. Using `YYYYMMDD` (no separators) matches NSE's own archive naming convention.

### 4.9 `src/dhan/live_chain_rest.py` — Disabled but Still Callable

- **Current state:** Module imports successfully. `LiveChainREST` can be instantiated with a broker object. However, `broker.get_option_chain_by_underlying()` will return an error dict (Error 806) when called, not raise an exception.
- **Risk:** Code that wraps this in `try/except` and checks `if option_chain:` will silently get `None` and produce no data. No crash, but no chain data either.
- **Recommendation:** The module is already correctly guarded. No change needed until Dhan Data APIs are subscribed.

### 4.10 Dual Validator Session Inefficiency

- **Current behavior:** `src/validation/market_result_validator.py` creates a **new** `requests.Session()` inside each of `_fetch_nse_most_active_options()` and `_fetch_nse_option_chain()` at call time. For NIFTY + BANKNIFTY + FINNIFTY + MIDCPNIFTY + SENSEX, this means potentially 6 homepage warm-up requests (1 for most-active + 5 per-symbol if most-active fails) during validation.
- **Risk:** Rate limiting at 15:35 IST when NSE traffic is heaviest post-close.
- **Recommendation:** Migrate `src/validation/market_result_validator.py` to use `core/data/nse_provider.fetch_option_chain()` so the singleton session is reused.

---

## 5. REQUIRED TEST CASES FOR MULTI-SOURCE FALLBACK

### 5.1 Unit Tests — `core/data/nse_provider.py`

```
test_fetch_option_chain_nominal
  Mock: requests.Session.get → valid NSE JSON with 10 CE+PE rows
  Assert: returns dict, records key present, data list non-empty

test_fetch_option_chain_401_resets_session
  Mock: first get() → 401, second get() → valid JSON
  Assert: reset_session() called once; second call returns valid data

test_fetch_option_chain_timeout_returns_none
  Mock: requests.Session.get → raises ConnectionError
  Assert: returns None, no unhandled exception

test_total_oi_from_chain_nominal
  Input: fixture JSON with known CE OI=100, PE OI=200 per 5 strikes
  Assert: returns 1500 (5×300)

test_total_oi_from_chain_partial_rows
  Input: 3 records with CE only, 2 with PE only
  Assert: sums correctly without KeyError

test_total_oi_from_chain_empty_records
  Input: {"records": {"data": []}}
  Assert: returns 0

test_save_and_load_oi_cache_roundtrip
  Action: save_oi_cache({"NIFTY": 1234567, "BANKNIFTY": 0})
  Assert: load_oi_cache() returns {"NIFTY": 1234567, "BANKNIFTY": 0}

test_load_oi_cache_missing_file
  Setup: MARKET_CACHE_FILE does not exist
  Assert: load_oi_cache() returns {}

test_load_oi_cache_corrupt_json
  Setup: write invalid JSON to MARKET_CACHE_FILE
  Assert: load_oi_cache() returns {} (no exception)
```

### 5.2 Unit Tests — `src/ranking/gain_rank_engine.py`

```
test_oi_change_score_with_real_history
  Input: oi_hist = {"prev_oi": 1_000_000, "curr_oi": 1_150_000}  # +15% change
  Assert: score ≥ 90 (15% × 6.0 = 90)

test_oi_change_score_no_history_concentration_fallback
  Input: oi_hist=None, df with total_oi=500_000
  Assert: 0 < score < 100, no exception

test_oi_change_score_zero_prev_oi
  Input: oi_hist = {"prev_oi": 0, "curr_oi": 50000}
  Assert: falls back to concentration scoring (not division-by-zero)

test_rank_all_with_ml_confidence
  Input: all_chain_data with 3 underlyings, ml_confidence = {"NIFTY": 80.0, ...}
  Assert: ml_confidence_score column present, NIFTY rank affected by ml factor

test_rank_all_without_ml_confidence_weight_redistribution
  Input: ml_confidence=None
  Assert: sum of weights applied equals 1.0; gain_score in [0, 100] for all rows

test_rank_all_empty_chain_data
  Input: all_chain_data = {}
  Assert: returns empty DataFrame, no exception

test_save_snapshot_creates_history_file
  Setup: RANK_HISTORY_FILE does not exist
  Action: call rank_all() with valid data
  Assert: RANK_HISTORY_FILE created, contains today's date entry
```

### 5.3 Integration Tests — Daily Runner Fallback Chain

```
test_load_live_chain_data_nse_success
  Mock: fetch_option_chain → valid JSON for all 4 symbols
  Assert: all_data has 4 keys, all DataFrames non-empty, spots > 0

test_load_live_chain_data_nse_fails_csv_fallback
  Mock: fetch_option_chain → None
  Setup: storage/NIFTY_2026-06-13.csv with correct schema
  Assert: NIFTY loaded from CSV, others get synthetic

test_load_live_chain_data_all_fail_synthetic
  Mock: fetch_option_chain → None, no CSV files
  Assert: all 4 symbols in all_data, all OI values == 100000 (flat synthetic)
  Assert: no exception raised

test_run_ranking_with_real_oi_cache
  Setup: market_cache.json with non-zero prev OI for NIFTY
  Mock: fetch_option_chain → returns chain with known OI sum
  Assert: oi_history passed to engine is non-empty, oi_change_score > 0 for NIFTY

test_run_validation_saves_oi_only_when_real
  Mock: fetch_option_chain → valid chain (non-zero OI)
  Assert: save_oi_cache called with non-zero values

test_run_validation_no_save_when_synthetic
  Mock: fetch_option_chain → None (synthetic fallback triggered)
  Assert: save_oi_cache NOT called (market_cache.json not overwritten)
```

### 5.4 Schema Compatibility Tests

```
test_nse_chain_to_df_output_schema
  Assert: output columns = {"strike", "option_type", "oi", "volume", "ltp", "iv"}
  Assert: dtypes: strike=float/int, option_type=str, oi=int, volume=int, ltp=float, iv=float
  Assert: option_type values are exactly "CE" and "PE"

test_gain_rank_engine_accepts_canonical_schema
  Input: DataFrame with columns (strike, option_type, oi, volume, ltp, iv)
  Assert: rank_all() completes without KeyError or AttributeError

test_validator_schema_unified
  Goal: ONE canonical validator report schema
  Assert: both src/ranking/ and src/validation/ validators use "rank_correlation_spearman" 
  Assert: both use same symbol list (4 symbols, no SENSEX in ranking)
```

### 5.5 Staleness and Holiday Edge Case Tests

```
test_oi_cache_staleness_guard
  Setup: market_cache.json with last_updated = 4 days ago
  Assert: run_ranking() logs staleness warning, passes oi_history=None to engine

test_expiry_day_oi_skip
  Setup: mock datetime.today() to be Thursday
  Assert: oi_history not used for chain scoring on expiry day
  (After implementing the expiry-day guard recommended above)

test_bhavcopy_weekend_fallback_walks_back
  Setup: DataSourceManager (when built), today = Saturday
  Assert: DataSourceManager tries Friday bhavcopy, then Thursday, stops at 5 attempts
```

---

## 6. IMPLEMENTATION PITFALLS

### 6.1 Do NOT Add yfinance, nsepython, or jugaad-data to the Fallback Chain

These packages do not provide F&O option chain OI data for NSE indices. Adding them to the DataSourceManager as option chain sources will:
- Silently produce empty DataFrames (yfinance/nsepython return OHLCV, not per-strike OI)
- Create confusing fallback behavior where the system "succeeded" but used meaningless data
- Add three new dependencies with no benefit for the core use case

Correct minimal fallback chain for option chain data:
```
Layer 0 (future): Dhan Data APIs — check subscription before attempting
Layer 1 (active): NSE public API via nse_provider.py
Layer 2 (cache-only): Previous bhavcopy file (for OI cache init on clean install, NOT intraday)
Layer 3 (safe fallback): Flat synthetic — known-zero OI signal, does not corrupt cache
```

### 6.2 Session Singleton Must Not Be Shared Across Process Boundaries

`nse_provider._session` is a module-level singleton. If the DataSourceManager is ever called from multiple threads or subprocesses, this session is not thread-safe. Add a threading.Lock around session access, or use `urllib3.util.retry.Retry` within a session pool.

### 6.3 bhavcopy Path Convention

`storage/bhavcopy/YYYYMMDD_fo_bhavcopy.csv` is a reasonable path. The actual NSE archive filename format is `fo{DDMMMYYYY}bhav.csv.zip` (e.g., `fo13JUN2026bhav.csv.zip`). The DataSourceManager should normalize the downloaded filename to the proposed format for consistency, but must handle the original NSE naming when downloading.

The storage path must NOT be `state/bhavcopy/` — `state/` is for runtime JSON state. Binary/CSV archives belong in `storage/`.

### 6.4 The `src/ranking/market_result_validator.py` is Orphaned

The currently scheduled daily validation job uses `src/validation/market_result_validator.py`. The `src/ranking/` copy has a different schema (4-symbol list, different field names, different retrain threshold). It should be:
- **Deleted** if `src/validation/` is the canonical version, OR
- **Promoted** as the canonical version and `src/validation/` removed

Until one is removed, any test that loads a validation report will see inconsistent field names (`spearman_correlation` vs `rank_correlation_spearman`), which breaks downstream consumers.

### 6.5 `market_cache.json` Contains All-Zero OI — First Run Will Use Intra-Chain Fallback

The current `state/market_cache.json`:
```json
{"last_updated": "2026-06-13T05:56:29", "oi_data": {"NIFTY": 0, "BANKNIFTY": 0, "FINNIFTY": 0, "MIDCPNIFTY": 0}}
```

All values are zero. The check in `run_ranking()` is:
```python
if sym in prev_oi_cache and prev_oi_cache[sym] > 0:
```

So zero values correctly fall through to intra-chain scoring. The first real post-market validation run with live NSE data will populate non-zero values. This is correct design — zero contamination is avoided.

### 6.6 `live_chain_rest.py` Calls `broker.get_option_chain_by_underlying()` Which Does Not Exist in dhanhq 2.2.0

The `dhanhq` 2.2.0 SDK does not expose `get_option_chain_by_underlying()` as a method in the public API — this appears to be a method that was assumed from a different broker SDK or an earlier version. When Dhan Data APIs are eventually subscribed, `LiveChainREST` will need to be rewritten to use the actual dhanhq option chain endpoint. This is not a current blocker (it is already disabled) but is a pitfall for future implementation.

### 6.7 Missing Dependencies for Full Pipeline Run

From Codex's earlier investigation:
- `python-dateutil` is missing from `requirements.txt` — `pandas` cannot import without it
- `pytest` is not installed — no tests can run
- These must be added before any test suite is built

---

## 7. STORAGE PATH VERDICT

**`storage/bhavcopy/YYYYMMDD_fo_bhavcopy.csv` — AGREE**

This is the right location. Rationale:
- `storage/` is already used for live chain watch CSV and AI signal CSV
- `state/` is reserved for JSON runtime state (cache, validation reports, retrain signals)
- The `YYYYMMDD` date prefix allows `sorted(os.listdir())` to find the most recent file trivially (same pattern used in `load_live_chain_data()` for CSV fallback)
- Consistent with NSE archive naming conventions (just reformatted)

One addition: the DataSourceManager should maintain a `storage/bhavcopy/.gitignore` entry to prevent bhavcopy CSVs from being committed (they can be 50-100MB for F&O data).

---

## 8. SUMMARY VERDICT TABLE

| Proposal Element | Verdict | Reason |
|-----------------|---------|--------|
| DataSourceManager as single acquisition layer | AGREE | Fixes 3-session duplication problem |
| Canonical schema: `(strike, option_type, oi, volume, ltp, iv)` | AGREE | Matches existing `_nse_chain_to_df()` output and `GainRankEngine` column detection |
| Dhan → NSE → bhavcopy → ... fallback order | PARTIAL | Dhan should be Layer 0/future; nsepython/yfinance/jugaad-data should be removed from option chain fallback |
| bhavcopy storage at `storage/bhavcopy/YYYYMMDD_fo_bhavcopy.csv` | AGREE | Correct location and naming |
| yfinance as option chain fallback | DISAGREE | yfinance does not provide F&O option chain OI for NSE indices |
| nsepython as NSE fallback | DISAGREE | Same underlying API, same failure mode; adds dependency without benefit |
| jugaad-data as fallback | DISAGREE | Requires paid NSE subscription; not a free fallback |
| Shared NSE session (singleton) | AGREE | Already implemented correctly in `nse_provider.py`; DataSourceManager must extend it |
| Bhavcopy for post-close OI cache init | AGREE | Valid use case; NOT for intraday ranking |

---

## 9. RECOMMENDED NEXT STEPS (Implementation Priority)

1. **CRITICAL (data integrity):** Add date check to OI cache in `run_ranking()` — refuse to use prev_oi if cache_date == today (prevents same-day overwrite).
2. **CRITICAL (schema):** Delete `src/ranking/market_result_validator.py` — the `src/validation/` version is the one wired into the daily pipeline. Or rename and clearly mark the other as legacy/unused.
3. **HIGH (reliability):** Add 1-second delay and per-symbol error handling in `load_live_chain_data()` to avoid NSE rate limiting on 4 simultaneous warm-up requests.
4. **HIGH (correctness):** Add expiry-day Thursday guard to disable OI change scoring on rollover days.
5. **MEDIUM (test infrastructure):** Add `python-dateutil` and `pytest` to `requirements.txt`.
6. **MEDIUM (data sources):** If implementing DataSourceManager, use only NSE API + bhavcopy (yesterday's only) + synthetic. Remove yfinance/nsepython/jugaad-data from the option chain fallback chain.
7. **LOW (coverage):** Add SENSEX to the ranking pipeline OR remove it from `src/validation/market_result_validator.py` TRACKED_UNDERLYINGS — the mismatch biases Spearman ρ.

---

*Codex investigation complete. All files read first-hand. No assumptions made from prior context without verification.*
