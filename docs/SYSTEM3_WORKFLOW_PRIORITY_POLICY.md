# System3 Workflow Priority Policy

## Permanent standing rule

Only the following GitHub Actions workflows are allowed in `.github/workflows`.

### Priority automatic workflows

1. `ci.yml` — blocking analyzer/paper safety validation for pull requests and protected branches.
2. `workflow-priority-guard.yml` — enforces this allow-list whenever workflow policy changes.
3. `cloud-run-auto-deploy.yml` — path-scoped Google Cloud Run deployment from `main`.
4. `gcp-stage2-ci.yml` — focused Google Cloud safety tests for relevant pull-request changes.
5. `gcp-dhan-token-fix-ci.yml` — focused Dhan token/runtime contract checks for relevant pull-request changes.
6. `frontend-runtime-smoke.yml` — focused browser runtime proof for the built dashboard; required to catch compile-success/blank-root UI regressions before merge.
7. `system3-forensic-responder.yml` — read-only event-driven evidence collector for failures from approved workflows and deployment status events. It may observe `workflow_run` and `deployment_status` only under the restrictions below.

### Manual emergency workflow

8. `gcp-dhan-token-rotation.yml` — manual recovery/proof only. Daily rotation remains owned by Google Cloud Scheduler.

## Disabled workflow classes

All other workflows are prohibited from the active workflow directory, including:

- Render-related workflows
- self-hosted or laptop-runner workflows
- scheduled proof and report writers
- legacy workflow-failure trackers that write TODOs, issues, branches, commits, pull requests, deployments, or runtime state
- duplicate dashboard visual-proof workflows
- experimental planners, swarms, repair runners and normalizers
- ML training/proof workflows that are not explicitly promoted to priority

Git history preserves removed workflow files. Restoration requires a reviewed pull request that updates this policy and passes `workflow-priority-guard.yml`.

## Event-driven forensic responder restrictions

`system3-forensic-responder.yml` is the only workflow allowed to use `workflow_run`.

It must:

- monitor only the explicitly approved System3 workflows listed in this policy;
- use `deployment_status` only as a read-only observation trigger;
- keep repository, Actions and deployment permissions read-only;
- execute responder code from the default branch for `workflow_run` handling, never from the triggering run's branch or commit;
- perform no repository write-back, issue creation, pull-request creation, merge, deployment mutation, secret mutation or runtime mutation;
- perform no automatic retry or repair in the first rollout;
- keep all trading/live-order safety flags disabled;
- emit evidence only as job output, step summary and/or retained workflow artifact;
- include pull-request self-tests so the responder is tested before event handling reaches `main`.

No other workflow may use `workflow_run`, `repository_dispatch`, `issue_comment`, `issues`, or a GitHub schedule trigger unless this policy is explicitly changed in a reviewed pull request.

## Operating rules

- Run the smallest required priority workflow first.
- Never start duplicate or overlapping workflow runs.
- Use GitHub-hosted cloud runners only.
- Google Cloud is the sole runtime/deployment authority.
- Render remains retired and prohibited.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Analyzer/paper mode remains authoritative until separate production-readiness proof is approved.
