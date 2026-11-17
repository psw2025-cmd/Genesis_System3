# Genesis Legacy Orchestrator — Verified Resume Ledger

Updated: 2026-11-17 UTC. Scope: **LEGACY** `psw2025-cmd/Genesis_System3` only. This document does not certify Genesis System3 LIVE NEW.

## Immutable verified baseline
- PR #650 merged: https://github.com/psw2025-cmd/Genesis_System3/pull/650
- Merge SHA: `0d1f67e3314a6e107a4b5d4ec1397b3789c1e22d`.
- PR head `b20952199d47110cd2294f3592d0bba89b4c2e5c`: eight pull-request workflow runs concluded success (Workflow Priority Guard, LLM Council Bootstrap Validation, SonarQube Audit, Repo Clean Forensic Toolkit, CodeQL Security Audit, Global Safety CI, Frontend Browser Runtime Smoke, Security Audit Evidence). This is **PR CI proof**, not provider execution proof.
- Trusted workflow exists at `.github/workflows/llm-council-trusted.yml` on `main`. Its `workflow_dispatch` requires `pr_number`, checks out trusted `main`, fetches the PR diff as untrusted data, tests `council/` and runs three provider API calls. CLI flags `--diff`, `--sha`, `--output` match `council/council.py` at merge.
- No authenticated three-provider workflow run, council evidence artifact or independent artifact readback has been verified by this ledger.

## Execution queue (strictly evidence-based)
| ID | State | Owner lane | Dependency | Next executable operation | Exit proof |
| --- | --- | --- | --- | --- | --- |
| LC-01 | PASS | Legacy | none | Recheck on future main SHA changes | PR #650 and merge SHA |
| LC-02 | NOT VERIFIED | Legacy | LC-01 | Discover a trusted workflow-dispatch capability; if available run on `main` with `pr_number=650`, but first validate reviewing merged PR diff is meaningful; otherwise use a fresh, safe review PR | Trusted workflow run URL and exact reviewed SHA |
| LC-03 | NOT VERIFIED | Legacy | LC-02 | Inspect provider step conclusions without revealing secrets; distinguish missing secrets, API failures, invalid JSON and FAIL verdicts | Three independent provider verdicts and zero errors |
| LC-04 | NOT VERIFIED | Legacy | LC-03 | Download council-evidence artifact, validate `schema_version`, reviewed SHA, `diff_sha256`, provider verdicts, and artifact SHA-256 | Verified artifact identifier/hash and readback |
| LC-05 | NOT VERIFIED | Legacy | LC-01 | Recheck current `main` post-merge CI, not just prior PR head CI | Current-main run/job URLs |
| UI-01 | NOT VERIFIED | Legacy | runtime access | Inspect 23 UI tabs/113 audit checks, API and deployed SHA with live evidence | Timestamped tab/API/lineage evidence |
| PAPER-01 | NOT VERIFIED | Legacy | runnable tests | Run safe deterministic paper replay covering lifecycle, duplicate guard, recovery, reconciliation, stale feeds | Test logs + exact SHA, no live orders |

## Next-cycle resume procedure
1. Read this ledger and fresh GitHub/runtime evidence. Never infer current status from historical success.
2. Select highest-priority unblocked NOT VERIFIED/FAIL row. Execute multiple safe tools/commands in sequence; do not stop at a status-only message.
3. On a defect, prepare an isolated branch and PR, run tests, inspect failures and reverify the exact changed SHA. Do not modify another agent's branch.
4. Update the row with links, SHA, date, observed result and next action. Mark PASS only on readback-backed proof; otherwise retain NOT VERIFIED.
5. Merge only after required reviews/branch protection and exact-head CI. No real-money broker orders.

## Safety and isolation
`PAPER_MODE=1`; `LIVE_ORDER_AUTHORITY=0`; `REAL_BROKER_ORDERS=0`; `LIVE_TRADING_ENABLED=0`; `ORDER_PLACEMENT_ALLOWED=false`. These are required invariants, **not runtime-verified values** in this ledger. Never expose API secrets to untrusted PR code. Genesis System3 LIVE NEW has a separate workspace and ledger; do not reuse legacy evidence or infrastructure.
