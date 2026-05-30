# PR13A Backend Docker Build Proof

## Finding

Root `backend/` does not exist. Therefore any workflow using `backend/Dockerfile` will fail.

## Correct current path

- Backend source path: `dashboard/backend/`
- Dockerfile path: `dashboard/backend/Dockerfile`

## Safety

- No trading logic changed.
- No broker config changed.
- No `.env` changed.
- No database changed.
- No model artifacts changed.
- No Azure deploy enabled.
- Workflow is manual-only with `workflow_dispatch`.

## Purpose

This PR only proves that the backend Docker image can build and push to GHCR from the correct path.
