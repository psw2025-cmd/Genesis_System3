# Backend Docker Deploy Proof

## Purpose

Fix backend container deployment path for Genesis_System3.

## Verified structure

- Root `backend/` is not present.
- Real backend application is under `dashboard/backend/`.
- `dashboard/backend/app.py` imports root/core/src modules, so Docker build context must remain repository root.
- Backend image name remains `ghcr.io/psw2025-cmd/genesis_system3/genesis-backend:latest`.

## Protected areas

This change must not modify:

- trading logic
- broker config
- `.env`
- databases
- model artifacts

## Files changed

- `dashboard/backend/Dockerfile`
- `.dockerignore`
- `.github/workflows/cd.yml`
- `docs/deploy/BACKEND_DOCKER_DEPLOY_PROOF.md`
