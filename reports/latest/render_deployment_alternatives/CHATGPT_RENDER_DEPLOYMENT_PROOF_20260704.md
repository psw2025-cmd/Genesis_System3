# ChatGPT Render Deployment Proof — 2026-07-04

## Verdict

Do **not** create a third Render service named `genesis-system3-scheduler` unless the existing worker service is intentionally being replaced or split.

The current repository design already runs the scheduler inside `genesis-system3-worker` through:

```text
python scripts/cloud_worker.py
```

## Proof summary

### 1. `render.yaml` defines only two active services

File: `render.yaml`

The header says the active Render blueprint has two services:

- `web` — FastAPI backend
- `worker` — background daemons: token refresh + watchdog + job scheduler

The active worker service is:

```yaml
- type: worker
  name: genesis-system3-worker
  runtime: docker
  dockerfilePath: ./dashboard/backend/Dockerfile
  dockerContext: .
  dockerCommand: python scripts/cloud_worker.py
```

Therefore the correct Render worker command is:

```text
python scripts/cloud_worker.py
```

### 2. `scripts/cloud_worker.py` is the actual cloud entrypoint

File: `scripts/cloud_worker.py`

The file says it is the single-process entrypoint for the Render worker service and starts five daemon threads:

1. token daemon
2. token watchdog
3. job scheduler
4. scheduler health push
5. option-chain push

The job scheduler thread runs:

```python
from core.engine.system3_phase82_job_scheduler import run_daemon
run_daemon()
```

So scheduler is already embedded in the worker process.

### 3. `core.engine.system3_phase82_job_scheduler` is a valid alternate direct scheduler entrypoint

File: `core/engine/system3_phase82_job_scheduler.py`

The scheduler supports:

```text
python core/engine/system3_phase82_job_scheduler.py --daemon
python -m core.engine.system3_phase82_job_scheduler --daemon
```

But this direct daemon should only be used if the architecture is intentionally split into a separate scheduler worker.

### 4. `python -m core.scheduler` is not supported by current repo evidence

No verified file/module named `core.scheduler` was found in repo search.

Do not use:

```text
python -m core.scheduler
```

This can cause Render deploy failure or a service that does nothing.

## Alternatives ranked by safety

### Option A — Safe current design: keep only existing worker

Use current Render setup:

```text
Service: genesis-system3-worker
Type: Background Worker
Runtime: Docker
Command: python scripts/cloud_worker.py
```

This is the recommended path.

Why:

- Matches `render.yaml`
- Starts token refresh
- Starts watchdog
- Starts scheduler
- Starts health push to backend
- Starts option-chain push
- Avoids duplicate scheduler runs

### Option B — Direct scheduler-only split

Only use this if the existing worker is too heavy or crashing due to token/chain push workload.

Render service:

```text
Service: genesis-system3-scheduler
Type: Background Worker
Runtime: Docker
Command: python -m core.engine.system3_phase82_job_scheduler --daemon
```

Required env vars:

```text
SYSTEM3_DEPLOY_TARGET=render
RENDER=true
SYSTEM3_MODE=analyzer
ANALYZE_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
WEB_SERVICE_URL=https://genesis-system3-backend.onrender.com
```

Risk:

- This does not run token daemon, watchdog, health push, or chain push.
- Backend may still show no scheduler health unless a separate health-push process exists.
- Do not run this together with `cloud_worker.py` scheduler thread unless duplicate firing protection is proven.

### Option C — Render Blueprint repair

Use Render Blueprint from `render.yaml` instead of manual service setup.

Expected services:

```text
genesis-system3-backend
genesis-system3-worker
```

This is useful if manual Render settings drifted from repo.

## Correct health-push verification

The worker code sends this header:

```text
X-Worker-Token: <token>
```

Use this PowerShell command from laptop:

```powershell
$TOKEN="PASTE_NEW_WORKER_PUSH_TOKEN_HERE"

curl.exe -i -X POST "https://genesis-system3-backend.onrender.com/api/scheduler/health/push" `
  -H "Content-Type: application/json" `
  -H "X-Worker-Token: $TOKEN" `
  --data "{""daemon_heartbeat"":""manual-test"",""daemon_pid"":0,""jobs"":{},""jobs_status_today"":{},""fired_keys_today"":[]}"
```

Expected:

```text
HTTP/1.1 200 OK
```

Do not use this header for this repo:

```text
Authorization: Bearer <token>
```

## Token safety

A token was pasted in chat. Treat it as exposed and rotate it.

Generate a new token locally:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Set the same value in:

```text
genesis-system3-backend → WORKER_PUSH_TOKEN
genesis-system3-worker  → WORKER_PUSH_TOKEN
```

Or set it once in Render environment group:

```text
dhan-shared-credentials → WORKER_PUSH_TOKEN
```

## Final action

Use Option A now.

Do not create `genesis-system3-scheduler` today unless the worker is intentionally split and duplicate scheduler execution is handled.
