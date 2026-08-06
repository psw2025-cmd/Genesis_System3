# Upstream request timeout — root cause and fix

**Symptom:** Cloud UI `/ui` showed plain text `upstream request timeout`.

**Date:** 2026-08-06

## Root causes (proven)

1. **Event-loop starvation (primary)**  
   Open-market path in `_get_chain_uncached` called sync `fetch_chain_for_api()` **on the asyncio event loop**. With `index_chain_micro_loop` + paper seed fan-out, `/ui` and `/api/health` queued behind multi-second Dhan OC HTTP and Cloud Run returned `upstream request timeout`.

2. **Broken MemGuard env (revision 00072)**  
   Manual `gcloud --update-env-vars` mangled values into one string:  
   `MEM_LIMIT_MB='960 MEM_WARN_MB=700 MEM_GC_MB=850'` → `ValueError` on `int(...)` → container never listened on PORT.

3. **Paper seed bug**  
   `_cache_get("scanner_gainers:5:25:1")` called without required `ttl_s`.

## Fixes shipped

| Change | File |
|---|---|
| Open-market Dhan OC via `_run_blocking` / `asyncio.to_thread` | `dashboard/backend/app.py` |
| Safer `MEM_*` int parse (first token only) | `dashboard/backend/middleware/memory_guard.py` |
| Paper seeds: cache/push only (no live OC fan-out) + fix `_cache_get` ttl | `dashboard/backend/app.py` |
| Index micro sleep 0.4s → 2.0s when open | `dashboard/backend/app.py` |
| Warm instance + 1Gi + MEM defaults in auto-deploy | `scripts/gcp_cloud_run_auto_deploy.py` |

## Success criteria

- `GET /ui` → HTTP 200 HTML in **&lt; 3s** under market-open load
- `GET /api/health` → HTTP 200 in **&lt; 5s**
- No `ValueError` / startup crash on `MEM_LIMIT_MB`
- Serving revision Ready; live trading flags remain OFF

## Live proof (2026-08-06)

| Check | Result |
|---|---|
| Serving revision | `genesis-system3-web-00075-rqp` (image `ui-fix-1785994037`) |
| `/ui` x4 | **62–139 ms**, HTTP 200 HTML |
| `/api/health` x4 | **82–323 ms**, HTTP 200 |
| Dhan secret BOM | stripped (`dhan-access-token` v12, `system3-dhan-access-token` v9) |
| Live trading | remains OFF |

Probe log: `reports/latest/upstream_timeout_fix/proof_probes.txt`
