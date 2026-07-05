# Patch Pack 3 — Deploy Plan

## What changed

| File | Change |
|---|---|
| `dashboard/backend/app.py` | Added `DEFER_INSTRUMENT_WARMUP` env guard around startup instrument warm-up |
| `dashboard/backend/Dockerfile` | Added `--limit-max-requests 200` to uvicorn CMD |
| `render.yaml` | Added `DEFER_INSTRUMENT_WARMUP=1`, `CLOUD_PAPER_ENGINE=0`; fixed `healthCheckPath` to `/api/health` |

## Memory impact (estimated)

| Component | Before | After |
|---|---|---|
| Instruments JSON at startup | ~150–200 MB | 0 MB (deferred) |
| Cloud paper trading loop | running | disabled via env |
| Uvicorn process recycle | never | every 200 requests |
| Estimated peak RAM | ~450–530 MB → OOM | ~280–350 MB → stable |

## Safety unchanged

- `LIVE_TRADING_ENABLED=0` kept
- `SYSTEM3_LIVE_TRADING_ALLOWED=0` kept
- Dhan credentials remain `sync: false` (Render dashboard only)
- No broker write APIs called
- Analyzer/Paper mode unchanged

## Deploy sequence

1. Merge `chatgpt/qc-dashboard-forensic-md` → `main`
2. Render auto-deploys (autoDeploy: true, branch: main)
3. New instance starts with `DEFER_INSTRUMENT_WARMUP=1` from render.yaml
4. Instruments warm-up skipped at startup → reduced peak RAM
5. First call to `/api/instruments/health` triggers lazy-load
6. Process recycles after 200 requests, preventing slow memory creep

## Rollback

Set `DEFER_INSTRUMENT_WARMUP=0` in Render dashboard env vars → redeploy.
No code rollback needed — the guard is additive.
