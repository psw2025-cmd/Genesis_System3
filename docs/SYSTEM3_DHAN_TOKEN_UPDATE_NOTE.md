# System3 Dhan Token Update Note

Status note from owner: **Dhan token has been updated**.

## Evidence context from Render screenshot

The Render worker logs before this note showed Dhan authentication failures such as:

- `Dhan expiry-list HTTP 401`
- `Authentication Failed - Client ID or Token invalid`
- `DHAN_EMPTY_OPTION_CHAIN_ROWS`
- backend web service `502 Bad Gateway`
- `WORKER_PUSH_TOKEN missing or different between Render web and worker`
- Render deploy/build blocked because the workspace had run out of pipeline minutes

## Current interpretation

The token update is noted, but it is **not yet proven resolved** until the latest backend and worker processes reload the updated environment and proof reports show Dhan read-only endpoints passing.

## Required verification after token update

- Render backend redeployed or restarted with updated environment.
- Render worker redeployed or restarted with the same updated Dhan credentials.
- `/api/broker/dhan/status` no longer reports auth failure.
- `/api/broker/funds` responds without 401/auth error.
- Dhan expiry list returns without HTTP 401.
- Option-chain proof no longer shows `DHAN_EMPTY_OPTION_CHAIN_ROWS` caused by auth.
- Dashboard Broker tab shows token valid / funds responded / holdings responded.
- Dashboard visible issue tracker passes after latest deploy.

## Still separate blockers

This token update does not automatically resolve:

- Render pipeline minutes exhausted.
- Backend `502 Bad Gateway`.
- Worker push token mismatch.
- ML validation/profit/paper lifecycle gates.
- Real live trading readiness.

Live trading remains OFF until all real proof gates pass.
