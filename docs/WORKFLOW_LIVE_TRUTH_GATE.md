# Genesis System3 Live Workflow Truth Gate

## Authority

Google Cloud Platform is the production authority. GitHub Actions is the deployment/test control plane. Historical artifacts, old workflow runs, and old serving revisions are context only and must never be used as current PASS evidence.

## Mandatory execution order

1. Resolve the current `main` SHA from GitHub at runtime.
2. Generate `reports/latest/workflow_control/workflow_truth.json` and `.md` with `scripts/github_workflow_truth.py`.
3. Inspect mandatory exact-SHA CI. Never merge a remediation while required PR CI is red unless the red check is proven unrelated and explicitly documented.
4. If CI is green, merge without unnecessary delay.
5. Re-resolve `main`; discard pre-merge evidence if the SHA changed.
6. Confirm the Cloud Run deployment workflow ran for the exact merged SHA.
7. Confirm GCP reports the exact SHA/revision at 100% production traffic.
8. Run exact-serving-SHA API and browser/UI proof.
9. If URL/UI proof fails, immediately open or continue the next remediation path; do not declare PASS from CI or deployment alone.
10. After any fix, repeat exact-SHA smoke, broker truth, required option-chain truth, and safety proof.

## Mandatory workflows

The workflow-truth collector gates these workflows against the exact current `main` SHA:

- Genesis System3 Global Safety CI
- GCP Stage 2 Safety Checks
- GCP Dhan Token Fix CI
- Security Audit Evidence
- Cloud Run Auto Deploy
- Frontend Browser Runtime Smoke
- Full Cloud Audit and Forensic Consensus

A workflow whose latest run belongs to an older SHA is `STALE`, not PASS. A running current-SHA workflow is `PENDING`. A current-SHA completed unsuccessful workflow is `FAIL`.

## Permanent evidence files

`reports/latest/workflow_control/workflow_truth.json` is the machine-readable control record. It contains:

- current `main` SHA;
- every active workflow and its latest run;
- exact-SHA classification;
- job conclusions;
- artifact names/IDs/expiry metadata;
- mandatory blockers;
- recently updated open issues and pull requests.

`reports/latest/workflow_control/workflow_truth.md` is the human-readable summary.

The `Workflow Live Truth Gate` workflow uploads both files as a 30-day GitHub Actions artifact after each monitored workflow completes and on manual dispatch. Concurrency is keyed by serving-source SHA and older in-progress truth runs are cancelled to avoid agent/workflow collision.

## Broker pre-check before remediation or proof

Before any broker-related mutation or token recovery attempt, prove all of the following from fresh evidence:

- exact current `main` SHA and exact serving revision;
- `/api/broker/status` truth, including upstream error taxonomy;
- token source/version/expiry without exposing the token;
- scheduler and rotator authority state;
- recent rotator execution history;
- current Dhan throttling/rate-limit evidence;
- all callers that can request rotation/recovery;
- LIVE trading and order placement remain disabled.

Do not mint/rotate merely because a generic UI string says a token is expired. `DH-906` and `805` must not be treated as authentication rejection unless current Dhan semantics and sanitized upstream evidence prove otherwise.

## Post-fix smoke criteria

A broker/data remediation is not closed until the exact serving SHA proves:

- broker connected/read-only ready;
- no uncontrolled rotation or retry storm;
- no Dhan 429/805 throttling during sustained dashboard use;
- NIFTY, BANKNIFTY, FINNIFTY, and MIDCPNIFTY option chains all show non-zero contracts/strikes;
- all canonical UI tabs render;
- health/auto-gates are ready for PAPER/analyzer mode;
- LIVE trading remains OFF and order placement remains disallowed;
- full cloud audit and browser runtime smoke both PASS.
