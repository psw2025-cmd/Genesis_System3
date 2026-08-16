# Lane C — GCP Forensic (READ-ONLY)

- **Project:** `system3-openalgo-safe`
- **Region:** `asia-south1`
- **Service:** `genesis-system3-web`
- **Capture UTC:** 2026-08-16T06:27:14Z (summary 2026-08-16T06:32:03Z)
- **gcloud:** AVAILABLE (SDK 578.0.0)
- **Mutations:** NONE

## 1. Cloud Run web

| Field | Value |
|------|-------|
| latestReadyRevision | `genesis-system3-web-00384-tuw` |
| Traffic | 100% → `genesis-system3-web-00384-tuw` |
| Image (tag) | `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:a48e7b3c7c08-1786830179` |
| Serving digest | `sha256:0906924c1ececd24787a7b35ffbaebfe85d786d7cb87bddcc4643262252b83f9` |
| Service Account | `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com` |
| CPU / Memory | 1 / 1Gi |
| Concurrency / Timeout | 50 / 300s |
| Min / Max instances | 1 / 10 |
| Env NAMES | 41 |
| Secret ref NAMES | 2 → DHAN_CLIENT_ID<=system3-dhan-client-id:latest, WORKER_PUSH_TOKEN<=system3-dashboard-worker-push-token:latest |

## 2. Revisions (top 5)

- `genesis-system3-web-00384-tuw` traffic=100% ready=True created=08/15/2026 21:46:01
- `genesis-system3-web-00381-hoj` traffic=0% ready=True created=08/15/2026 19:58:30
- `genesis-system3-web-00378-hay` traffic=0% ready=True created=08/15/2026 12:57:48
- `genesis-system3-web-00287-ngg` traffic=0% ready=True created=08/15/2026 11:19:25
- `genesis-system3-web-00286-2ls` traffic=0% ready=True created=08/15/2026 10:30:41

## 3. Cloud Run Jobs (genesis/system3)

Matching (9): genesis-system3-control-plane-verify, genesis-system3-dhan-token-rotate, genesis-system3-forecast, genesis-system3-ml-history-bootstrap, genesis-system3-rank, genesis-system3-scheduler-collector, genesis-system3-signals, genesis-system3-smoke, genesis-system3-validate

### Token rotate `genesis-system3-dhan-token-rotate`
- Image: `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:a48e7b3c7c08-1786830179`
- SA: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`
- Last 5 executions:
  - `genesis-system3-dhan-token-rotate-25szr` completed=False succ= fail= @  — spec.template.spec.containers[0].env[12].value_from.secret_key_ref.name: Failed to access secret projects/system3-openalgo-safe/secrets/dhan-totp-secret/versions/latest: Secret Version [projects/802404398783/secrets/dhan-totp-secret/versions/8] is in DESTROYED state.
  - `genesis-system3-dhan-token-rotate-56gcf` completed=True succ=1 fail= @ 08/16/2026 04:38:01 — Execution completed successfully in 18.81s.
  - `genesis-system3-dhan-token-rotate-dnr2r` completed=True succ=1 fail= @ 08/16/2026 03:40:43 — Execution completed successfully in 30.79s.
  - `genesis-system3-dhan-token-rotate-2nbfj` completed=True succ=1 fail= @ 08/16/2026 02:00:21 — Execution completed successfully in 18.69s.
  - `genesis-system3-dhan-token-rotate-rbvhd` completed=True succ=1 fail= @ 08/15/2026 20:19:11 — Execution completed successfully in 58.44s.

**Note:** Newest listed execution (`25szr`) shows Completed=False with DESTROYED `dhan-totp-secret` version access failure; prior 4 succeeded.

## 4. Cloud Scheduler (asia-south1)

- `genesis-system3-forecast-daily` schedule=`0 4 * * MON-FRI` tz=UTC state=ENABLED target=http:https://run.googleapis.com/v2/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-forecast:run
- `genesis-system3-signals-schedule` schedule=`0 10 * * 1-5` tz=UTC state=PAUSED target=http:https://www.googleapis.com/run/v1/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-signals:run
- `genesis-system3-validate-daily` schedule=`5 10 * * MON-FRI` tz=UTC state=ENABLED target=http:https://run.googleapis.com/v2/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-validate:run
- `genesis-system3-dhan-token-rotate-daily` schedule=`30 7 * * *` tz=Asia/Kolkata state=ENABLED target=http:https://run.googleapis.com/v2/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-dhan-token-rotate:run
- `genesis-system3-rank-daily` schedule=`45 3 * * MON-FRI` tz=UTC state=ENABLED target=http:https://run.googleapis.com/v2/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-rank:run
- `genesis-system3-rank-schedule` schedule=`50 3 * * 1-5` tz=UTC state=PAUSED target=http:https://www.googleapis.com/run/v1/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-rank:run
- `genesis-system3-forecast-schedule` schedule=`0 4,5,6,7,8,9 * * 1-5` tz=UTC state=PAUSED target=http:https://www.googleapis.com/run/v1/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-forecast:run
- `genesis-system3-signals-daily` schedule=`15 13 * * MON-FRI` tz=UTC state=ENABLED target=http:https://run.googleapis.com/v2/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-signals:run
- `genesis-system3-scheduler-collector-every-minute` schedule=`* * * * *` tz=UTC state=ENABLED target=http:https://run.googleapis.com/v2/projects/system3-openalgo-safe/locations/asia-south1/jobs/genesis-system3-scheduler-collector:run

Duplicates elsewhere: **none** in us-central1 / us-east1 / europe-west1 / asia-east1 (asia-south2 & global = invalid locations).

## 5. Secret Manager (dhan-* names only)

Names: DHAN_BROKER_TOKEN, dhan-access-token, dhan-app-id, dhan-app-secret, dhan-pin, dhan-totp-secret, system3-dhan-access-token, system3-dhan-client-id

`dhan-access-token` enabled versions: **257** (IDs + createTime only; no payloads). Latest 10 in `SUMMARY.json`.

## 6. Artifact Registry

Serving image: `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3@sha256:0906924c1ececd24787a7b35ffbaebfe85d786d7cb87bddcc4643262252b83f9`

Describe: see `06_artifact_image_describe.json` / `06_artifact_summary.json`.

## 7. Logs (last ~2h samples)

| Signal | Sample count (capped) |
|--------|------------------------|
| severity>=ERROR | 0 (limit 200) |
| HTTP 429 | 8 (limit 200) |
| timeout text | 0 (limit 200) |

First log query failed (bad `-2h` timestamp literal); retry with `--freshness=2h` succeeded.

## 8. IAM (names only — not changed)

- Web SA: `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`
- Rotator SA: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`
- Distinct SAs (expected isolation). No IAM policy mutations.

## Failures recorded

1. logging `timestamp>='-2h'` INVALID_ARGUMENT → retried OK
2. scheduler location `asia-south2` invalid
3. scheduler location `global` invalid
4. secrets filter `name:dhan` deprecation WARNING

## Key artifact paths

- `SUMMARY.json` / `FORENSIC_SUMMARY.md`
- `01_service_summary.json` / `01_service_describe_raw.json`
- `02_revisions_summary.json`
- `03_jobs_summary.json` / `03_token_rotate_*`
- `04_scheduler_summary.json`
- `05_secrets_summary.json`
- `06_artifact_summary.json`
- `07_logs_summary.json`
- `08_iam_sa_names.json`
- `COMMANDS_AND_FAILURES.md`

