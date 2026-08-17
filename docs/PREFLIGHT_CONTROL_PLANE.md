# System3 Permanent Preflight Control Plane

Authority: `SYSTEM3_PREFLIGHT_CONTROL_PLANE_V1`.

## Purpose

Before any production-relevant transition, agents must refresh current GitHub truth instead of assuming the previous step is still current. The preflight complements the continuous-closure system; it does not replace live production URL proof.

Run:

```bash
python scripts/system3_preflight_control_plane.py
```

Generated snapshot:

- `reports/latest/control_plane/workflow_issue_artifact_snapshot.json`
- `reports/latest/control_plane/NEXT_ACTION.md`

These generated files are snapshots only. They must be regenerated before the next transition and must never be promoted to live truth after they become stale.

## Mandatory sequence

1. Read current remote `main`.
2. Read newest Issue #188 `SYSTEM3_COORDINATION_V1`, `SYSTEM3_URL_SINGLE_TRUTH_V1`, and `SYSTEM3_AUTONOMOUS_COORDINATION_V1` markers.
3. Inventory every configured GitHub Actions workflow and its latest run.
4. Capture all currently active runs and any failed run whose head is current `main` or an active PR head.
5. Capture artifact metadata for every workflow's latest run and actionable runs; capture failing job/step metadata for actionable failures.
6. Read active PR heads/base/mergeability and recently updated open issues.
7. Compute the next transition without guessing.
8. Revalidate critical claims against the authoritative source before acting.

## Transition law

- Exact-head mandatory CI green -> merge without unnecessary waiting.
- Merge complete -> immediately check canonical Cloud Run deployment.
- Deployment active -> `STATUS=WAITING`; do not run acceptance against the previous serving SHA.
- Deployment complete -> independently verify current remote main and exact production serving SHA.
- Exact serving SHA -> generate a NEW production-browser semantic URL proof.
- URL proof failure -> freeze evidence, investigate root cause, and open/continue the next remediation immediately.
- Current-main/active-PR workflow failure -> inspect failed job, failed step, logs and artifacts before proceeding.
- Old unrelated workflow failure -> historical context only unless fresh evidence makes it relevant.
- Stop only for a genuine external dependency or an approval/action that delegated automation cannot safely perform.

## Status contract

Every agent response during active remediation should expose:

- `STATUS=WORKING | WAITING | BLOCKED | IDLE`
- `IN_PROGRESS=<workflow/deploy/test/none>`
- `CURRENT_STEP=<exact step>`
- `NEXT_ACTION=<automatic next action>`
- `USER_ACTION=<none or exact approval needed>`

`WAITING` is valid only when a verified external dependency is actually active. An agent must continue any other non-conflicting safe work while that dependency runs.

## Evidence boundaries

A green workflow proves only its own tested contract. A stored artifact is not current runtime truth. Production acceptance still requires the canonical GCP URL, exact-serving-SHA verification, fresh browser evidence, same-session API correlation where relevant, and semantic state validation.

## Automated refresh

`.github/workflows/system3-preflight-control-plane.yml` refreshes the snapshot on every push to `main`, hourly, and on manual dispatch. Agents must still run/read a fresh preflight before a production transition; the scheduled artifact is a convenience and historical audit trail, not a substitute for current verification.

## Safety

The preflight is read-only. It must never rotate tokens, mutate IAM/GCP, deploy, access raw secret payloads, enable LIVE trading, or invoke order paths.
