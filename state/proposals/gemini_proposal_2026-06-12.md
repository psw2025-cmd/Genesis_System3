# Gemini Proposal — OI Persistence Cache & Real Data Integration
> Agent: Gemini | Date: 2026-06-12 | Domain: Market Data + Highest Gain Ranking
> Status: IMPLEMENTED by Claude 2026-06-13 — all 4 files created/updated

---

## Problem

**The system's most critical predictive factor (OI Change %, 30% weight) is currently driven by random noise.**

1. **Synthetic Data Fallback:** In `scripts/daily_gain_rank_and_validate.py`, the `load_live_chain_data()` function generates random OI values (`np.random.randint(50000, 500000, 20)`) when storage CSVs are missing. Since Dhan Data APIs are unsubscribed (Error 806), these CSVs are never populated with real data.
2. **Missing Persistence:** `GainRankEngine` is designed to use `oi_history` (prev vs curr OI) for its 30% weight scoring. However, the daily runner never passes this history, and there is no file-based cache to store OI totals between market sessions.
3. **Accuracy Impact:** The "synthetic" OI change is effectively a random number, which caps the Spearman ρ accuracy at ~0.35-0.45. Real OI change is the single best predictor of institutional positioning and subsequent price gain.

---

## Your Recommended Solution

**Implement a lightweight persistence layer and integrate NSE fallback data directly into the ranking pipeline.**

### 1. Data Persistence Layer
Create `state/market_cache.json` to store the last known total Open Interest for each tracked underlying.
```json
{
  "last_updated": "2026-06-12T15:35:00",
  "oi_data": {
    "NIFTY": 12450000,
    "BANKNIFTY": 3890000,
    "FINNIFTY": 1200000
  }
}
```

### 2. NSE Data Provider
Extract the NSE fetching logic from `MarketResultValidator` into a shared utility `core/data/nse_provider.py` so that it can be used for both **ranking** (morning) and **validation** (evening).

### 3. Integration into Daily Runner
Modify `scripts/daily_gain_rank_and_validate.py`:
- **Morning (rank):**
    1. Load `prev_oi` from `state/market_cache.json`.
    2. Fetch `curr_oi` from NSE (fallback).
    3. Construct `oi_history` dict and pass to `engine.rank_all()`.
- **Evening (validate/save):**
    1. After fetching fresh NSE data for validation, update `state/market_cache.json` with the latest total OI.

---

## Alternatives Rejected

1. **Relying on NSE's `changeinOpenInterest` field:**
    - *Rejected* because it's a "change from yesterday's close" which is useful, but having our own `prev_oi` allows us to verify data integrity and handle multi-day gaps (e.g., long weekends) more robustly using timestamped snapshots.
2. **Implementing a Database (SQLite/Redis):**
    - *Rejected* as overkill. A simple JSON file at `state/market_cache.json` is sufficient for the <50 symbols we track, is human-readable, and survives system restarts without extra service dependencies.
3. **Waiting for Dhan Data API Subscription:**
    - *Rejected* because the user hasn't acted on it yet. We can achieve 80% of the accuracy gains using the NSE public API fallback today with zero extra cost.

---

## Success Metric

- **Primary:** Spearman ρ (rank correlation) improves from <0.45 to >0.60 within 3 trading days of real OI data flowing.
- **Secondary:** `state/market_cache.json` exists and correctly records total OI after each session.
- **Verification:** `state/gain_rank_history.json` shows non-random, meaningful `oi_change_score` values.

---

## Files to Change

1. `src/ranking/gain_rank_engine.py` — minor: ensure `oi_history` handling is robust.
2. `scripts/daily_gain_rank_and_validate.py` — major: replace synthetic data with NSE fallback + load/save cache.
3. `core/data/nse_provider.py` — new: shared NSE fetching logic.
4. `state/market_cache.json` — new: persistence store.

---

**I request Codex to cross-verify this proposal, specifically checking if `core/data/nse_provider.py` is the right architectural choice for the shared fetching logic.**
