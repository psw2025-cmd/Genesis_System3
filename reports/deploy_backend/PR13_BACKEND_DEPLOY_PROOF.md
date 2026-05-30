# PR13 Backend Docker Build Path Proof

## Finding

Root `backend/` does not exist. Therefore any workflow using `backend/Dockerfile` can fail.

## Correct current path

- Backend source path: `dashboard/backend/`
- Dockerfile path: `dashboard/backend/Dockerfile`

## Current PR scope

This PR only proves backend Docker image build/push path.

## Safety

- No trading logic changed.
- No broker config changed.
- No `.env` changed.
- No database changed.
- No model artifacts changed.
- No Azure deploy enabled.
- Workflow is manual-only with `workflow_dispatch`.

## Why not production Dockerfile yet

A production Dockerfile needs the real app entrypoint, dependency file, and health endpoint. Those are not proven yet, so this PR avoids guessing and uses a build-proof container first.
