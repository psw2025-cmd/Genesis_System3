# System3 Dhan Token Update Note

Status note from owner: **Dhan token has been updated**.

## Historical context (Render.com — retired)

Older worker screenshots from the retired Render.com host showed Dhan authentication failures such as:

- `Dhan expiry-list HTTP 401`
- `Authentication Failed - Client ID or Token invalid`
- `DHAN_EMPTY_OPTION_CHAIN_ROWS`
- backend web service `502 Bad Gateway`
- `WORKER_PUSH_TOKEN` mismatch between web and worker
- Render deploy/build blocked because the workspace had run out of pipeline minutes

Those Render.com services are **not** current authority. Production is GCP Cloud Run only.

## Current interpretation

The token update is noted, but it is **not yet proven resolved** until the latest Cloud Run revision and worker Job reload the updated environment and proof reports show Dhan read-only endpoints passing.

## Required verification after token update

- Cloud Run service `genesis-system3-web` serving the exact expected SHA.
- Worker Job using the same Dhan credentials from Secret Manager (never paste tokens).
- `/api/broker/dhan/status` no longer reports auth failure.
- `/api/broker/funds` responds without 401/auth error.
- Dhan expiry list returns without HTTP 401.
- Option-chain proof no longer shows `DHAN_EMPTY_OPTION_CHAIN_ROWS` caused by auth.
- Dashboard Broker tab shows token valid / funds responded / holdings responded.
- Dashboard visible issue tracker passes after latest deploy.

## Worker preflight

Canonical current worker/token proof is Cloud Run + the dedicated Dhan rotation Job. Leftover `tools/system3_render_worker_preflight.py` is a retired stub and must not be treated as a Render deploy step.

## GitHub failure storm containment

`tools/system3_github_render_failure_tracker.py` is retired. It writes a Cloud Run-only retired report and no longer probes Render public hostnames.
