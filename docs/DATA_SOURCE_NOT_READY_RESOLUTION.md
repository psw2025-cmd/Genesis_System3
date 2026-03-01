# Data Source "not_ready" Resolution – Evidence & Summary

**System:** System3 Ultra Dashboard  
**Issue:** `data_source: not_ready` blocking `live_allowed`  
**Date:** 2026-02-28

**See also:** [DATA_SOURCE_STATE_MACHINE_FULL_PASS_PROOF.md](DATA_SOURCE_STATE_MACHINE_FULL_PASS_PROOF.md) for the full data_source state machine (live/cached/not_ready).  

---

## 1. Configuration Check (Redacted)

### Environment Variables
| Variable | Set | Redacted Value |
|----------|-----|----------------|
| ANGELONE_API_KEY | ✅ | `r***d` |
| ANGELONE_CLIENT_ID | ✅ | `P*******1` |
| ANGELONE_PIN | ✅ | `****` |
| ANGELONE_TOTP | ✅ | `2***I` |
| SYSTEM3_REAL_ONLY | Default | `1` (real data only) |

### Config Files
- **config/.env.example**: Documents Angel One credentials, SYSTEM3_LIVE_TRADING_ALLOWED
- **config/runtime_config.json**: Chain strike band, fetch settings (no data_source config)
- **config/system3_*.yml**: Broker/risk configs

---

## 2. Root Cause Analysis

1. **live_allowed gate**: `ds in ("real", "live")` excluded `"BROKER"` (set by state_sync when market open).
2. **health.json broker field**: Writers use `is_connected`; state_sync expected `broker_status`.
3. **Missing health.json**: When trading system is not running, no health.json → broker status not synced.
4. **REAL_ONLY + market closed**: state_sync set `SYNTHETIC`; REAL_ONLY mode should use `not_ready`.

---

## 3. Fixes Applied

| File | Change |
|------|--------|
| `dashboard/backend/app.py` | Add `"broker"` to `live_allowed` check; use SSOT market status (not qc_data default) for market open/closed |
| `dashboard/backend/state_sync_service.py` | Use `is_connected` when `broker_status` missing; bootstrap health.json when broker connected + market open; REAL_ONLY → `not_ready` when market closed |
| `option_chain_automation_master.py` | Add `data_source` to health.json (`"real"` when connected + data fetched) |

---

## 4. Service Availability

- **Broker (Angel One)**: Connected (verified via `_check_broker_connectivity`)
- **Market hours**: `utils.market_hours.is_market_open()` – MARKET_DETECTION_AVAILABLE = True
- **health.json**: Created by trading system or bootstrap when broker connected + market open

---

## 5. Verification Steps

1. Restart backend: `cd dashboard/backend && python -m uvicorn app:app --host 127.0.0.1 --port 8000`
2. Wait ~5–10 seconds for state sync (first cycle)
3. Call `GET /api/health` – expect `data_source: "BROKER"` or `"real"`, `live_allowed: true`, `live_blockers: []` when market open and broker connected

---

## 6. Expected Final Status

**When market is OPEN (9:15–15:30 IST) and broker connected:**
```json
{
  "status": "ok",
  "data_source": "BROKER",
  "live_allowed": true,
  "live_blockers": []
}
```

**When market is CLOSED:** `data_source: "not_ready"` and `live_blockers` include "market is closed" – expected behavior (no real data available).

---

## 7. Verification Evidence

**Current state (market closed, 03:52 IST):**
- `runtime_state.json`: `data_source: "not_ready"`, `market.is_open: false` ✓
- Broker: connected ✓
- Fixes will take effect when market opens (9:15–15:30 IST)
