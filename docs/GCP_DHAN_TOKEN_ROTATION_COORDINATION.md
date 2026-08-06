# GCP Dhan Token Rotation — Agent Coordination Lock

**Authoritative implementation:** PR #85  
**Target runtime:** Google Cloud Run, Google Secret Manager and Google Cloud Scheduler only  
**Safety mode:** analyzer/read-only; live trading and order routing remain disabled

## Reserved scope

Until PR #85 is resolved, other agents must not modify:

- `.github/workflows/cloud-run-auto-deploy.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/gcp-dhan-token-rotation.yml`
- `core/brokers/dhan/cloud_token_provider.py`
- `core/brokers/dhan/cloud_runtime_patch.py`
- `core/utils/env_loader.py`
- `dashboard/backend/Dockerfile`
- `dashboard/backend/requirements.txt`
- `dashboard/frontend/src/App.tsx`
- `dashboard/frontend/src/components/BrokerProofPanel.tsx`
- `scripts/start_cloud_run.py`
- `scripts/gcp_dhan_token_rotation_job.py`
- `tests/test_gcp_dhan_token_rotation_contract.py`

## Reconciliation decision

Claude commits `fd21dd3` and `e330c1d` modified the duplicate `.github/workflows/deploy.yml`.
Those changes are not copied because:

1. `DHAN_TOKEN_REFRESH_ENABLED` is not consumed by the current token implementation.
2. Calling `/health` does not start a token-refresh daemon.
3. The workflow disables dashboard API authentication.
4. A second deploy workflow can overwrite the guarded Cloud Run service configuration.

PR #85 removes that duplicate workflow and uses one guarded deployment path.

## Final ownership split

- **Google Cloud Scheduler:** authoritative daily trigger at 07:30 Asia/Kolkata.
- **Cloud Run Job:** single task, single parallel execution, no retries that could mint competing tokens.
- **Secret Manager:** durable token source and version proof.
- **Cloud Run web service:** scale-to-zero allowed, maximum one active instance, dynamic latest-version reads.
- **GitHub Actions:** code deployment, validation and manual recovery only; not the daily clock.
- **UI Broker tab:** non-secret evidence for token source, version, expiry, reload, broker reads, required option chains and live-money safety.

## Completion gates

- Python compile and focused unit contracts pass.
- Frontend production build contains the token proof panel.
- Architecture and trading-safety gates pass.
- Cloud Run Job rotates or safely skips a healthy token.
- A real rotation advances Secret Manager version and validates the replacement token.
- Cloud Scheduler configuration is proven at 07:30 IST.
- `/api/broker/status` proves dynamic Secret Manager source and `connected=true`.
- UI shows funds, holdings, positions, required Dhan chains and live-money safety OFF.
