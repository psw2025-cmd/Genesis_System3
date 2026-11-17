# Runtime Crash / Failed Revision Runbook

## Trigger

Use this runbook when a new `genesis-system3-web` Cloud Run candidate does not become Ready, emits startup exceptions, or fails its tagged HTTP proof.

## Safety invariants

- LIVE remains OFF/LOCKED.
- Never route traffic to a candidate that has not passed exact-revision readiness and HTTP proof.
- Never use `latestReadyRevisionName` as rollback authority.
- Never relax `assert_runtime_manifest()` or required Firestore state to make a candidate start.
- Never expose Secret Manager payloads in logs or incident artifacts.

## Automatic path

The canonical authority is `scripts/gcp_cloud_run_auto_deploy.py`.

1. Capture the exact pre-deploy immutable revision-to-percent traffic map.
2. Build an image for the exact Git SHA.
3. Create the candidate with `--no-traffic` and the `candidate` tag.
4. Require the exact candidate to become Ready.
5. On failure, run `scripts/gcp_failed_revision_forensic.py` against that exact revision.
6. Preserve/restore the exact previous traffic map and prove it matches.
7. Do not retry the same failed SHA automatically more than twice in 15 minutes.
8. If the same root-cause signature persists after two safe attempts, stop automated deployment and escalate with revision, SHA, build ID, forensic artifact and logs query.

## Diagnosis order

1. `MUTATION_MANIFEST_INVALID`: fix route classification/duplicates in source; never catch-and-continue.
2. Required Firestore `PermissionDenied`: repair IAM in infrastructure; never change `SYSTEM3_STATE_BACKEND_REQUIRED=1` to make production start.
3. Import/module error: patch dependency/import and reproduce through CI import smoke.
4. Memory/OOM: inspect actual memory evidence; do not simply raise resources without evidence.
5. Secret metadata/mount error: verify secret name/version/IAM metadata only; do not print secret values.
6. Startup port error: first inspect the Python traceback because Cloud Run's port error is often a consequence of an earlier application exception.

## Closure proof

A runtime incident is not closed until the exact merged SHA has:

- candidate Ready;
- candidate tagged HTTP proof PASS;
- `/ui` public PAPER proof PASS;
- MutationPolicy runtime proof PASS;
- LIVE flags OFF;
- exact candidate promoted to 100% traffic;
- deployment/runtime status SUCCESS;
- incident evidence linked from the master audit report.
