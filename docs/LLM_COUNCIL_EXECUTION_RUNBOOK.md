# LLM Council — Owner-Authorized Execution Runbook

## Scope and authority
Repository: psw2025-cmd/Genesis_System3. PR: #650.
Owner authorizes repository code, CI, review, and safe merge actions. This runbook does **not** authorize broker orders, live-trading enablement, bypass of branch protection, secret disclosure, or production Cloud Run deployment.
Keep Genesis System3 LIVE NEW strictly separate from this legacy repository.

## Invariants
- PAPER_MODE=1; LIVE_ORDER_AUTHORITY=0; REAL_BROKER_ORDERS=0.
- Never execute untrusted pull-request code with OpenAI, Anthropic, Gemini, or cloud credentials.
- Review exact immutable PR head SHA; record diff SHA-256.
- Missing provider, missing evidence, malformed result, or high/critical finding => FAIL.
- Mock-replay may validate deterministic offline behavior, never claim real-market proof.
- No merge while required GitHub checks are pending or failing.

## Parallel workstreams
A. Source & correctness: OpenAI reviewer; focus on regression, data integrity, schema, tests.
B. Security: Anthropic reviewer; focus on secrets, prompt injection, privilege boundaries, trading safety.
C. Reliability: Google Gemini reviewer; focus on idempotency, recovery, observability, CI and GCP integration.
D. Deterministic verification: GitHub-hosted unit, syntax, CodeQL, SonarQube, security audit, workflow priority guard, global safety CI, frontend runtime smoke.
Reviews are independent, read-only and run on the same SHA. The orchestrator alone coordinates repository writes.

## Procedure
1. DISCOVER: Read PR #650 head/base SHA and current branch policy; enumerate current workflow runs.
2. READ: Fetch the failed job's step/log; distinguish source defects from environment failures.
3. CORRECT: Modify smallest relevant code/policy surface. Never disable or bypass safety checks.
4. WRITE: Commit changes to PR branch. Record new SHA; discard prior SHA's approval.
5. TEST: Execute deterministic CI and wait for current-head runs. Check run IDs, jobs, conclusions and logs.
6. REVIEW: After trusted workflow is merged to protected main, dispatch trusted review from main with PR number. Never run PR-controlled code with provider keys.
7. EVALUATE: Require 3 valid provider PASS verdicts and no critical/high findings; store reviewed SHA, diff hash, model identity, run URL and artifact.
8. MERGE: Merge only when required checks and approvals are green for exact current head SHA; supply expected_head_sha to prevent race.
9. READBACK: Confirm merged SHA on main; verify run artifact and CI checks against merged source.
10. CLOSE: Publish truthful PASS/FAIL/NOT VERIFIED evidence, including blockers and safe next action.

## Bootstrap caveat
The trusted review workflow cannot be manually dispatched until installed on default branch. Bootstrap PR CI validates only deterministic code and workflow policy; it is not a three-model review. A subsequent PR is needed to exercise trusted council review before making it a mandatory gate.

## Approval matrix
- Read-only audit / unit tests / safe PR edits: authorized.
- Merge into main: authorized only after existing protected-branch requirements pass.
- Cloud Run deployment, infrastructure mutation, real broker orders, changes to LIVE NEW: NOT authorized by this runbook.
- External model data transmission: send reviewed diffs only through trusted workflow, after confirming data classification and provider permissions.

## Evidence contract
Record: repo, PR, base SHA, head SHA, diff SHA256, workflow run IDs, job names, conclusions, provider verdicts, model identifiers, errors, artifact URL/hash, merge SHA, and safety invariant check.
Never label synthetic test results as real trading evidence.
