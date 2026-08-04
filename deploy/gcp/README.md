# Google Cloud Run deployment

Target project: `system3-openalgo-safe`
Target region: `asia-south1` (Mumbai)

## Automatic deploy (default)

Push to `main` that touches runtime paths (`dashboard/`, `core/`, etc.) triggers
`.github/workflows/cloud-run-auto-deploy.yml`, which runs
`scripts/gcp_cloud_run_auto_deploy.py`:

1. Cloud Build → immutable image tagged with the full commit SHA
2. Cloud Run image patch (secret mounts preserved; live trading forced OFF)

Manual `gcloud` / `ALLOW_GCP_DEPLOY` scripts below remain for emergency/break-glass
only. Preferred path is the GitHub Action.

Required GitHub secret: `GCP_SA_KEY` (JSON for `github-actions-deploy@…`).

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
MERGED_SHA="$(git rev-parse HEAD)"
[[ "$MERGED_SHA" =~ ^[0-9a-f]{40}$ ]]
gcloud builds submit --project=system3-openalgo-safe \
  --config=deploy/gcp/cloudbuild.yaml \
  --substitutions="_IMAGE_TAG=${MERGED_SHA}" .
```

Build only the exact merged `main` commit. The build rejects short, empty, or
non-SHA tags. Never deploy `latest`.

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
