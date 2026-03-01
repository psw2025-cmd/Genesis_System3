# Data Source State Machine – Full Pass Proof

**System:** System3 Ultra Dashboard  
**Date:** 2026-02-28  
**Objective:** Dashboard always shows data (cached when market closed, live when open); `live_allowed` only when market open and `data_source == "live"`.

---

## 4.1 Configuration & Persistence Setup

### Cache Location and Format

| File | Location | Purpose |
|------|----------|---------|
| `last_known.json` | `outputs/last_known.json` | Canonical timestamp of most recent data fetch |
| `chain_raw_live.csv` | `outputs/chain_raw_live.csv` | Option chain data (preserved when market closes) |
| `health.json` | `outputs/health.json` | Health metrics including `last_data_fetch` |

### last_known.json Format (Redacted)

```json
{
  "timestamp": "2026-02-28T09:15:05+05:30",
  "chain_file": "chain_raw_live.csv",
  "health_file": "health.json",
  "updated_at": "2026-02-28T09:15:05+05:30"
}
```

### When Cache Is Updated

- **option_chain_automation_master.py** `_save_chain_data()`: After successful chain save, calls `write_last_known(outputs_dir)`.
- **generate_market_closed_outputs()**: Does NOT overwrite `chain_raw_live.csv`; last known data is preserved for dashboard.

---

## 4.2 State Machine Logic

| State | Condition |
|-------|-----------|
| `not_ready` | No data ever fetched (no last_known, health, or chain file) |
| `cached` | Market closed AND last data &lt; 24h old; OR market open but data &gt; 5s old |
| `live` | Market open AND data younger than 5 seconds |

### Thresholds (dashboard/backend/data_source_state.py)

- `LIVE_THRESHOLD_SEC = 5`
- `CACHE_MAX_AGE_SEC = 86400` (24h)

---

## 4.3 API Responses

### Market Closed, Cached Data Exists

```json
{
  "status": "ok",
  "data_source": "cached",
  "last_data_time": "2026-02-28T15:29:58+05:30",
  "data_age_seconds": 123.5,
  "live_allowed": false,
  "live_blockers": ["data_source is cached", "market is closed"]
}
```

### Market Open, Live Streaming

```json
{
  "status": "ok",
  "data_source": "live",
  "last_data_time": "2026-02-28T09:15:05+05:30",
  "data_age_seconds": 2.1,
  "live_allowed": true,
  "live_blockers": []
}
```

### First Run (No Data)

```json
{
  "status": "ok",
  "data_source": "not_ready",
  "last_data_time": null,
  "data_age_seconds": null,
  "live_allowed": false,
  "live_blockers": ["data_source is not_ready", "market is closed"]
}
```

---

## 4.4 UI Behavior

| data_source | Badge | Banner |
|-------------|-------|--------|
| `live` | 🟢 LIVE | Green: "LIVE DATA – PAPER TRADING MODE" |
| `cached` | 📦 CACHED | Amber: "CACHED DATA (Market Closed)" + Last updated time |
| `not_ready` | ⚠️ NOT READY | Blue/Yellow: "No data yet" or "BROKER NOT READY" |

---

## 4.5 Files Modified

| File | Change |
|------|--------|
| `dashboard/backend/data_source_state.py` | **New** – State machine, `last_known.json`, `compute_data_source()` |
| `dashboard/backend/state_sync_service.py` | Use `compute_data_source`; set `last_data_time`, `data_age_seconds` |
| `dashboard/backend/app.py` | `live_allowed` only when `data_source == "live"`; add `last_data_time`, `data_age_seconds` to health |
| `option_chain_automation_master.py` | `write_last_known` after chain save; preserve `chain_raw_live.csv` when market closed |
| `dashboard/frontend/src/components/DataSourceWarning.tsx` | Handle live/cached/not_ready; show last updated |
| `dashboard/frontend/src/components/Overview.tsx` | Pass `lastDataTime`, `dataAgeSeconds`; update status badge |

---

## 4.6 Runbook: Data Source Issues

1. **data_source stuck at not_ready**
   - Ensure trading system has run at least once (or `chain_raw_live.csv` / `health.json` exists).
   - Check `outputs/last_known.json` exists after a fetch.
   - Verify `utils.market_hours.is_market_open()` for market status.

2. **Cached data not showing**
   - Confirm `chain_raw_live.csv` was not overwritten (market-closed path no longer overwrites it).
   - Check `last_known.json` or `health.json` `last_data_fetch` is &lt; 24h.

3. **live_allowed false when market open**
   - `live_allowed` requires `data_source == "live"` (data &lt; 5s old).
   - Ensure trading system is fetching; if not, data will age and become `cached`.
