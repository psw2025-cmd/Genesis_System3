# Genesis System3 autonomous end-to-end runbook

**Authority marker:** `SYSTEM3_AUTONOMOUS_E2E_RUNBOOK_V1`.
**Current owner directive:** `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md` (2026-10-18). The September local-laptop directive and Claude-only override are `HISTORICAL_NON_AUTHORITY`.

## Mandatory fresh re-read
Read this runbook, the owner directive, `AGENTS.md`, `agent_policy.yaml`, and `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md` from the exact current checked-out commit immediately before:
1. every merge decision;
2. every deployment or production mutation;
3. every acceptance or rollback decision;
4. every issue/blocker closure;
5. every final response claiming completion/current runtime.

Chat memory, an earlier read or `reports/latest/` is not fresh runtime evidence. Record exact main/head SHA, marker and UTC in the active completion ledger.

## Execution authority and owner approval
Latest explicit owner direction > permanent trading/secret/destructive/cost safety > active cloud directive > `AGENTS.md` / machine policy > scoped rules > historical material. GitHub exact approved main is code authority. Target runtime and acceptance are GCP `system3-openalgo-safe`, `asia-south1`, from independently observed deployed SHA/digest plus same-session cloud API/browser evidence. No laptop checkout, localhost port or Windows scheduled task is routine production authority.

**Current authorization is ONLY** autonomous GitHub edits, branches/PRs, CI/testing and read-only GCP inventory. Before ANY billable GCP build/deploy, artifact push, IAM/secret/token/scheduler/resource or billing/config mutation, obtain separately explicit owner approval for that scope. Do not introduce/enable a push-triggered production deploy as a shortcut. Respect cost exposure; budget alerts are not a hard cap.

## Permanent safety
```text
ANALYZE_MODE=1
PAPER_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
AUTO_EXECUTE_TRADES=0
LIVE_ORDER_AUTHORITY=0
ORDER_PLACEMENT_ALLOWED=false
```
No real broker order placement/modification/cancellation/square-off; no order-shaped production endpoint tests. Never reveal broker secrets, token payloads, PIN/TOTP or service-account JSON keys. Dhan broker authority remains read-only at this stage.

## Current safe workflow
1. Read current main and active PR ownership, then inspect workflow triggers/permissions before any GitHub write. Use a dedicated non-destructive branch.
2. Make scoped policy/code corrections, run GitHub-hosted tests and review exact-head CI. Investigate failures without weakening gates. Do not merge an old laptop-only or stale cloud PR blindly.
3. Read-only GCP verification uses explicit project and region; confirm resource ownership, deployment absence/presence, WIF bindings and image provenance without deploying or reading secret values.
4. Stop at the separate owner approval boundary for cloud configuration/deploy. If not approved, mark `BLOCKED_OWNER_APPROVAL` and continue only safe GitHub/read-only work.
5. After later authorized deployment, independently prove source/revision/image traceability; startup and service health; exactly one broker worker lease; session-aware broker, symbols/expiry/option-chain completeness; continuous timestamps; persisted PAPER lifecycle; 22-tab same-session semantic UI/API parity; independent zero-real-order proof; signed or SHA-256 anchored evidence.

`CI green`, `image exists`, `HTTP 200`, `tab rendered` or `connected=true` alone NEVER establish full production PASS. Treat market closure truthfully. Status is `PASS/FAIL/BLOCKED/UNKNOWN/NOT_PROVEN`, each with UTC, project, exact SHA/digest and raw receipt. Historical resources remain historical until newly certified.

Owner is not the routine technical operator: use connected capabilities directly, and request action only for genuine approval, broker MFA or unavailable authorization.
