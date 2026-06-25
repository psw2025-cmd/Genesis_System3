# Render OOM Agent Prompt

Paste this to Cursor/Claude if deeper local/cloud runtime work is needed.

```text
You are working only inside repo psw2025-cmd/Genesis_System3.

Goal:
Resolve Render memory/OOM risk for genesis-system3-backend and genesis-system3-worker.

Safety:
- Analyzer/Paper only.
- Do not enable live trading.
- Do not touch .env or credentials.
- Do not place real orders.
- Do not create paid cloud resources.
- Do not fake PASS.

Tasks:
1. Inspect render.yaml and confirm web/worker services.
2. Inspect scripts/cloud_worker.py and all active runtime while True loops.
3. Identify unbounded lists, dicts, caches, DataFrames, open handles, repeated model loads, or retained snapshots.
4. Add safe memory diagnostics to active worker loop:
   - RSS MB log every 5 minutes.
   - active thread status.
   - no secrets in logs.
5. Add cleanup only where safe:
   - del large temporary DataFrames/lists.
   - close file/network resources with context managers.
   - bounded queues/TTL caches for histories.
   - gc.collect only after heavy batch jobs, not every small operation.
6. Do not run browser/Playwright proof inside Render web runtime.
7. Generate reports/latest/render_memory_audit/summary.md and summary.json.
8. Run safe tests only.
9. Return Action/Result/Evidence/Blocker table.

Do not ask for secrets.
```
