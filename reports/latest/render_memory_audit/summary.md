# Render Memory OOM Audit Summary

## Verdict

`PASS_WITH_WARNINGS`

This is not a full runtime proof because Render private service logs and memory charts are not available from the GitHub repo alone.

## What was verified from the repo

- `render.yaml` defines two Docker services:
  - `genesis-system3-backend` web service.
  - `genesis-system3-worker` worker service.
- Both services use the `starter` plan.
- The worker command is `python scripts/cloud_worker.py`.
- Live trading remains disabled in the Render blueprint.
- `scripts/cloud_worker.py` runs three long-running daemon threads and has a main keep-alive loop.
- The repo contains multiple `while True` style long-running scripts that need active-runtime classification.

## High probability memory risks

| Priority | Area | Risk | Action |
|---|---|---|---|
| P0 | Render worker | One process runs multiple long-running daemons. If any daemon leaks memory, the whole worker can restart. | Add memory snapshot logs and isolate heavy jobs. |
| P0 | Long-running loops | Multiple runtime-like scripts contain `while True` loops. | Classify active vs old/backup scripts; add bounded cache/cleanup to active loops. |
| P1 | Option-chain/dataframe jobs | Option-chain and market-data parsing can create large temporary objects. | Delete/clear temporary objects after each batch. |
| P1 | Render logs unavailable | GitHub repo cannot prove exact OOM root cause. | Collect last 3–5 minutes of Render logs before restart. |
| P1 | Heavy proof/browser tasks | Browser proof should not run inside Render web runtime. | Run Playwright on laptop/cloud runner, not production web service. |

## Correct remediation order

1. Collect Render logs before the restart.
2. Add safe memory snapshot logging to the worker loop.
3. Run active-runtime loop audit.
4. Patch only active runtime files.
5. Keep browser proof outside the Render web service.
6. Upgrade Render plan only if memory is stable but legitimate workload needs more RAM.

## Files added

- `docs/render/RENDER_MEMORY_OOM_RUNBOOK.md`
- `reports/latest/render_memory_audit/summary.json`
- `reports/latest/render_memory_audit/summary.md`

## Current blocker

Runtime logs and memory charts are still required to prove whether this is:

- steady memory leak,
- sudden spike from scheduled job,
- traffic burst,
- worker crash loop,
- or insufficient RAM for legitimate workload.

## Final recommendation

Do **not** upgrade Render RAM first. First collect logs and add memory diagnostics. Keep System3 in Analyzer/Paper mode.
