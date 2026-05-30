# PR13 Backend Docker Deploy Path Proof

## Finding

Root `backend/` does not exist, so any workflow using `backend/Dockerfile` will fail with `lstat backend: no such file or directory`.

## Correct path

- Use `dashboard/backend/` as backend source path.
- Add `dashboard/backend/Dockerfile`.
- Do not copy root `requirements.txt`.
- Install dependencies only if `dashboard/backend/requirements.txt` exists.

## Safety

- No trading logic changed.
- No broker config changed.
- No `.env` changed.
- No database changed.
- No model artifacts changed.
- Workflow is manual-only using `workflow_dispatch`.
- Azure deploy is not enabled in this PR until GHCR image proof passes.
