# Render Memory OOM Runbook — Genesis System3

## Purpose

This runbook is for diagnosing and resolving Render Out-of-Memory restarts for `genesis-system3-backend` and `genesis-system3-worker`.

## Safety rules

- Analyzer/Paper mode only.
- Do not enable live trading.
- Do not place broker orders.
- Do not commit `.env`, tokens, OTP, PIN, passwords, broker credentials, or private logs.
- Do not upgrade paid Render plan before code/resource leak review.

## Current Render blueprint facts

`render.yaml` defines two Docker services:

- `genesis-system3-backend` web service using `./dashboard/backend/Dockerfile`.
- `genesis-system3-worker` worker service using the same Dockerfile and `python scripts/cloud_worker.py`.
- Both services are on `starter` plan.
- Live trading is hard-disabled using `LIVE_TRADING_ENABLED=0` and `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- Dhan credentials are `sync: false`, so secrets must remain in Render dashboard, not repo.

## Immediate diagnostic order

1. Open Render service logs for both:
   - `genesis-system3-backend`
   - `genesis-system3-worker`
2. Look at the final 3–5 minutes before restart.
3. Search logs for:
   - `Out of memory`
   - `Killed`
   - `MemoryError`
   - `OOM`
   - restart loop
   - worker repeating same heavy job
4. Compare memory spike timing against:
   - dashboard traffic
   - option-chain fetches
   - model/backtest jobs
   - infinite loops
   - scheduled worker tasks
5. Do not scale plan until memory growth pattern is identified.

## Most likely memory-risk areas

1. Long-running `while True` loops.
2. DataFrames or large dict/list objects retained across iterations.
3. Option-chain snapshots cached without size/TTL limits.
4. Repeated model loads without singleton/cache control.
5. Browser/Playwright usage inside the web service instead of a separate proof runner.
6. Logs or accuracy records accumulated in memory before writing to disk.
7. Background worker jobs running in the same constrained Docker image as the web service.

## Required code controls

For every long-running loop:

- Use bounded queues or TTL caches.
- Use `try/finally` cleanup.
- `del` large DataFrames/lists after use.
- Call `gc.collect()` after heavy batch jobs only.
- Sleep between iterations.
- Write logs incrementally to disk, not to in-memory arrays.
- Do not keep full history in process memory.
- Store proof under `reports/latest/...` and archive old heavy files outside runtime memory.

## Recommended memory instrumentation

Use `tools/render_memory_probe.py` locally or in a one-off worker run to capture:

- RSS memory MB.
- Python allocated memory using `tracemalloc`.
- top allocation lines.
- loop iteration count.
- timestamp.

Do not run memory probe with broker secrets printed.

## Render configuration checklist

- Keep web and worker separated.
- Do not run heavy proof/browser tests inside the web process.
- Keep Playwright dashboard proof on laptop/cloud runner, not Render web runtime.
- Keep persistent disk disabled unless intentionally paid and approved.
- Keep `LIVE_TRADING_ENABLED=0`.
- Add memory logging endpoint/report before upgrading RAM.

## Upgrade decision rule

Upgrade Render plan only if all are true:

1. No steady memory leak is found.
2. Memory usage is stable under normal loop execution.
3. Spikes are caused by legitimate workload volume.
4. Heavy tasks cannot be moved to a separate worker/runner.
5. A budget is approved.

## Evidence output expected

Generate/update:

- `reports/latest/render_memory_audit/summary.md`
- `reports/latest/render_memory_audit/summary.json`

Statuses:

- `PASS`: no leak risks found and memory proof exists.
- `PASS_WITH_WARNINGS`: risks exist but controls/runbook are present.
- `NOT_PROVEN`: runtime logs/metrics were not available.
- `FAIL`: clear unbounded growth or unsafe memory behavior found.
