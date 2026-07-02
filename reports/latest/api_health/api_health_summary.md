# API Health Proof — Phase 5

**Generated:** 2026-07-02 16:26 IST

## Endpoint sweep (all 7 required, captured in one successful rapid-fire window)

| Endpoint | Status | Notes |
|---|---|---|
| `/` | 200 | API root, "System3 Ultra Dashboard API" |
| `/docs` | 200 | Swagger UI |
| `/api/health` | 200 | `broker_status: connected`, `market_status: closed`, `live_allowed: false` |
| `/api/state` | 200 | |
| `/api/broker/status` | 200 | `connected: true`, `order_placement_allowed: false`, `error: null` |
| `/api/scheduler/health` | 200 | |
| `/ui` | 200 | Dashboard renders (confirmed by user screenshot earlier this session, post PR #54) |

## Honest reliability finding

All 7 endpoints returned 200 in the snapshot above, but getting a clean simultaneous read took several attempts. The backend is exhibiting an **intermittent ~5-minute crash-restart cycle** under real market-hours load — separate from the zombie-thread OOM bug already found and fixed this session (PR #53). Multiple capture attempts during this proof session returned 502 or connection timeout before the successful snapshot above.

**Root cause hypothesis**: `core/data/instruments_cache.py`'s `InstrumentsCache` is a correctly-implemented singleton (loads once, doesn't leak per request), but it permanently holds a **121,152-row pandas DataFrame** in memory once triggered — which only happens during real market-hours chain/instrument lookups, not during off-hours testing. Combined with the base FastAPI footprint and per-request pandas processing, this appears to leave very little headroom in a 512Mi container.

**Not fixed this session** — this looks capacity-shaped, not a single discrete bug. Recommended follow-up: upgrade the Render plan (more RAM) or a separate effort to reduce the instrument DataFrame's memory footprint. Evidence: Render memory metrics showed repeated climbs to 250-380MB (down from ~500MB before the PR #53 fix) followed by resets, on a roughly 5-minute cycle throughout live market hours today.
