# GCP Cloud Run Deploy Readiness

## Purpose

Prepare a safe manual Google Cloud Run deployment path for the System3 backend.

## Decision

Preferred deployment target: GCP Cloud Run.

The current Azure workflow exists, but Azure readiness is not proven. GCP Cloud Run will be used only through a manual gated workflow until backend health, identity, image build, and runtime mode are proven.

## Repository proof

- Proven backend source path: `dashboard/backend/`.
- Proven backend Dockerfile path: `dashboard/backend/Dockerfile`.
- Backend app candidate: `dashboard/backend/app.py`.
- Current backend Dockerfile is build-proof oriented and uses `python -m http.server`.
- Production uvicorn backend runtime is still not proven in this PR.
- Dashboard Cloud Run deployment is out of scope because `dashboard/Dockerfile` is not proven on main.

## Required manual GCP values before real deployment

- GCP project ID
- Cloud Run region, recommended: `asia-south1`
- Artifact Registry repository name
- Workload Identity Provider
- Service Account for GitHub Actions
- Cloud Run backend service name

## Safety

This PR does not modify trading logic, broker configuration, database files, model artifacts, or live runtime mode files.

## Status

| Gate | Result |
|---|---|
| Latest main used | PASS |
| Backend path proof | PASS |
| Manual workflow only | PASS |
| Real deployment enabled by default | NO |
| Live trading enabled | NO |
| Dashboard deploy enabled | NO |
| Production backend Dockerfile proven | WARN |
| GCP project and identity proven | MANUAL ACTION REQUIRED |

## Next proof target

Run the manual workflow in dry-run mode first. Real deployment should be enabled only after dry-run passes and required GCP values are configured.
