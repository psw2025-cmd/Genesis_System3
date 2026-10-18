# System3 cloud-only PAPER recovery preflight — 18 October 2026

**Status: BLOCKED / predeployment only.** Latest owner directive:
`docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md`. Scope of present authorization:
GitHub repairs/CI and **read-only** GCP inspection; no cloud mutation, billable build,
image push, service/job/scheduler creation, IAM/Secret Manager modification, LIVE
orders or actual broker requests. This document is not owner deployment consent.

## Grounded inventory
- Repository main at investigation: `d453c47975052e7724a358081a778d4236752033`;
  merged security #479 and cloud-only authority #477. A newer main must be re-read.
- Independent read-only `gcloud` query, explicit project `system3-openalgo-safe`,
  number `802404398783`, around `2026-10-18T03:22Z`: ACTIVE; billing enabled;
  Cloud Run services and jobs: none returned, both rc=0; Scheduler `asia-south1`:
  no rows, rc=0. Artifact Registry `asia-south1/system3-containers` exists.
- GitHub provider `github-genesis-system3/providers/github` ACTIVE; repository
  and owner numeric identity restricted to `refs/heads/main`. Provider existence
  alone is not a working deployment-authorization receipt.
- Main push Frontend Browser Runtime Smoke `39090556767`: local 22-tab/browser
  install/build/temporal checks passed; production exact-SHA UI proof failed. Keep
  it red until independent serving revision and browser proof actually pass.
- Main Security Audit, CodeQL, Global Safety CI and Repo Clean completed PASS.
  A green code CI does not prove production runtime.

## Deployment source selection — do not guess
The repository-root `Dockerfile` is **nonproduction**: legacy backend app and
hard-coded port 8000. The historically intended Cloud Run candidate is
`dashboard/backend/Dockerfile` with **repository root as build context**,
multi-stage frontend build and `scripts/start_cloud_run.py` using `PORT` and
`dashboard.backend.secure_app:app`. The canonical image still requires build,
dependency and runtime safety tests before ever being promoted. Do not use an
unverified old Artifact Registry image digest as a shortcut.

The old `.github/workflows/cloud-run-auto-deploy.yml` and
`scripts/gcp_cloud_run_auto_deploy.py` were removed in historical commit
`60034500b52b` (#462). Historical docs that assert push-to-main auto-deploy
are obsolete. Restoring those files byte-for-byte would restore unapproved
mutation pathways. Do not do that.

## Agent-owned next steps BEFORE requesting cloud approval
1. Keep Issue #480 open as this release blocker and inspect the archived
   deployment implementation and all referenced scripts, credentials/secret
   metadata *names only*, IAM, scheduler/job lifecycle, private networking and
   rollback behavior. Never restore an automatic `push: main` cloud workflow.
2. Prepare a manual-only, explicit owner-approval-gated candidate deployment
   workflow with exact source SHA and image digest; fail closed if any prerequisite
   or provider trust condition is missing. It must not launch on ordinary PR/push.
3. Test the full candidate through GitHub-hosted static/unit/sandbox CI without
   contacting GCP or Dhan. Test that unauthorized execution is denied, no LIVE or
   order-shaped request exists, build command names the exact backend Dockerfile,
   and rollback preserves any previous healthy revision.
4. Present a bounded scope/cost summary for the owner's **separate explicit**
   authorization: target project and region, permitted builds/image pushes,
   Cloud Run service/job/scheduler changes, spend exposure and rollback. Budget
   notifications are not hard caps. No billing-account changes or IAM privilege
   escalation should be presumed.
5. After authorization, deploy zero-traffic candidate; independently prove exact
   serving SHA/digest, broker-auth read-only session, freshness/option-chain
   coverage, one writer lease, persisted PAPER evidence, all 22 production tabs
   and backend/API parity, independent broker order-history safety and recovery.
   Sunday simulation does not substitute Monday market-session proof.

## Read-only automated current repository preflight
`python scripts/system3_cloud_paper_preflight.py --sha <exact-source-sha>`
produces the receipt JSON; exit 0 means **report created**, not deployment ready.
`--strict` exits 2 for BLOCKED or NOT_PROVEN. It makes zero network calls,
zero GCP changes, zero broker calls and reads no secrets.
