# Google Cloud Run deployment (guarded)

Target project: `system3-openalgo-safe`
Target region: `asia-south1` (Mumbai)

This directory contains configuration only. Nothing here deploys automatically.
Both deployment scripts refuse to run unless `ALLOW_GCP_DEPLOY=YES` is supplied
after explicit approval.

## Safety invariants

- Analyzer/paper mode only.
- Both live-trading flags are fixed to `0`.
- The web service starts with zero minimum instances and one maximum instance.
- The smoke job has one task, one-way parallelism, no retries, and a 10-minute timeout.
- No broker secrets are embedded in files or image metadata.
- The web service is private by default.
- Runtime state is shared through the free-tier Firestore database.

## Build (Stage 3 only)

```bash
gcloud builds submit --project=system3-openalgo-safe \
  --config=deploy/gcp/cloudbuild.yaml .
```

Use the immutable commit-SHA image printed by Cloud Build. Never deploy `latest`.

## Deploy health-only web service (Stage 3 only)

```bash
ALLOW_GCP_DEPLOY=YES deploy/gcp/deploy_web.sh \
  asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:<commit-sha>
```

## Deploy bounded no-trade smoke job (Stage 3 only)

```bash
ALLOW_GCP_DEPLOY=YES deploy/gcp/deploy_smoke_job.sh \
  asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:<commit-sha>
```

Deployment and job execution require separate approval. Dhan secrets are not
added until the later read-only integration stage.
