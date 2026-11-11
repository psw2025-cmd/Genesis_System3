# System3 cloud-only owner directive — 2026-10-18

**Authority marker:** `SYSTEM3_CLOUD_ONLY_OWNER_DIRECTIVE_20261018`
**Status:** ACTIVE upon merge. This records the owner's latest explicit direction and supersedes the 2026-09-07 laptop-only directive, older GCP-exit/RUHI passages, and any inconsistent agent/config/test instructions.

## Purpose and authority
- Code authority: GitHub `psw2025-cmd/Genesis_System3` exact approved main SHA. A commit or passing CI is not production readiness.
- Intended production: GCP project `system3-openalgo-safe` (802404398783), `asia-south1`. Dhan is the designated broker. Render/Angel-era System3 deployments are historical/non-authoritative.
- Runtime, worker, scheduler, token access, persistence, monitoring, proof and dashboard must be cloud-only. Laptop/mobile/Cloud Shell may be transient browser/control devices, **never** routine production dependencies. No local checkout, localhost service or owner-run terminal loop is required for normal operation.
- A desired architecture does not prove a deployed system: live inventory, exact serving digest/SHA, fresh API/browser/broker evidence and independent reconciliation are required.

## Current owner authorization boundary
The owner has authorized **autonomous GitHub repairs, branches/PRs, code review, GitHub-hosted CI/testing and read-only GCP verification only**. The owner has NOT yet authorized any new billable GCP deployment/configuration mutation. Require separate explicit owner approval before Cloud Run/Build deployment, image push, Scheduler/Jobs creation, resource/IAM/Secret Manager changes, token rotation or changes to billing, budgets or resource settings. Do not convert a GitHub PR approval into implied cloud-change approval. Prior positive billing state is not blanket deployment consent; budgets/alerts are not hard cost caps. Do not force-merge, bypass reviews, overwrite parallel branches, or introduce an automatic deployment triggered by branch/PR/main writes without separate approval.

## Trading and secret safety — permanent
```text
ANALYZE_MODE=1
PAPER_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
AUTO_EXECUTE_TRADES=0
LIVE_ORDER_AUTHORITY=0
ORDER_PLACEMENT_ALLOWED=false
```
Never place, modify, cancel or square off a real order. No order-shaped tests against a live broker. No broker token/PIN/TOTP/API secret payloads in logs, reports, chat, GitHub, Drive or code. Use keyless GitHub OIDC/WIF and secret metadata only for the present authorization. The existence of an enabled secret version is not proof that a broker session is valid. No claim of real broker order count zero without independent broker/order-ledger proof.

## Safe execution sequence
1. Re-read current main, active PR ownership, this directive and safety policies; check CI side effects before changes.
2. Fix conflicting authority docs/machine policy/tests on a dedicated branch with governed PR. Keep historical evidence/history intact; keep obsolete laptop-only PRs unmerged.
3. Run GitHub-hosted safety/unit/integration tests. Investigate actual failure output rather than weakening checks. Record exact PR head and main SHA.
4. Independently read current GCP resource ownership by explicit `--project` and region; project/namespace mismatch is a blocker. Old images or Cloud Build success are historical until provenance is established.
5. Pause at the owner-approval boundary before any GCP mutation or billable build/deploy, then execute only the separately approved scope.
6. For actual production acceptance after authorized deployment, require exact serving image/source lineage, a single broker-data worker lease, fresh heartbeats, market-session-aware broker freshness/option-chain coverage, PAPER ledger reconciliation, all 22 dashboard tabs with same-session API parity, independent real-order safety verification, and evidence hashes/timestamps.

## Evidence taxonomy and owner interaction
Use `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `NOT_PROVEN`, `HISTORICAL_ONLY`; command exit 0 means invocation success only, not semantic readiness. Record `UTC_TIMESTAMP | PROJECT | COMMAND/API | EXIT_CODE | OBSERVED | EXPECTED | SOURCE_SHA | EVIDENCE_HASH | VERDICT | NEXT_ACTION`. Never fabricate PASS. Historical artifacts support timelines, not current claims.
Use connected agents/tools for diagnostics and code repair whenever possible; do not repeatedly make the non-coder owner run scripts. Ask only for real owner-only approval, billing/identity/consent or MFA boundaries. If a connected gateway is unavailable, report the limit; never claim unattended activity continued.




---
## OWNER EXPLICIT APPROVAL — 2026-10-28T01:55Z IST

I, Pritam Warghade (owner), hereby give separate explicit approval for:

1. Billable GCP Cloud Run deployment: service `genesis-system3-web`, project `system3-openalgo-safe` (802404398783), region `asia-south1`
2. Scope: Fix `dashboard/backend/routers/ml.py` hardcoded `ready_for_live=False` with REAL validation reader logic (read state/paper_validations/*.json + state/market_validations/*.json, check rho>0.70, hit_rate, freshness). DO NOT fabricate JSON.
3. Allow image build/push, Cloud Run deploy, .dockerignore fix to include state/ folders
4. Mode: PAPER/ANALYZE ONLY - LIVE_TRADING_ENABLED=0, ORDER_PLACEMENT_ALLOWED=false remains
5. Evidence required: UTC timestamp, project, exact SHA/digest, /api/ml/performance local + cloud proof, EVIDENCE_HASH, VERDICT PASS/FAIL/BLOCKED/NOT_PROVEN

This approval is for this specific fix only and does NOT authorize LIVE trading.

Owner signature: Pritam Warghade
Approved at: 2026-10-28 01:55 IST
GitHub main SHA to deploy from: latest approved main after fix
---
