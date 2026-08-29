# System3 MRI Concern List

Captured: `2026-08-24T14:03:00Z`  
Evidence class: request-scoped repository/GitHub review plus the production UI capture from `2026-08-24T12:52:18Z–12:53:18Z`.

| ID | Severity | Status | Concern / evidence | Owner and next action | Acceptance |
|---|---|---|---|---|---|
| MRI-20260824-001 | P0 | OPEN | BANKNIFTY production chain reproduced at 0 contracts/0 strikes with `Batch chains timeout — waiting for cache warm`; NIFTY, FINNIFTY and MIDCPNIFTY were populated. | Backend chain-cache lane: diagnose paced warm asymmetry, add regression, deploy through canonical PR path, repeat exact-serving browser/API proof. | BANKNIFTY and the other required indices expose verified Dhan rows in a new request-scoped session without a warm-timeout placeholder. |
| MRI-20260824-002 | P1 | OPEN | The live proof parser returned `source_value=null` although visible text contained `source=dhan`; current parser expects symbol and source on one line. Draft PR #335 owns the proof-harness lane. | PR #335 owner: rebase and reconcile the parser with the current two-line UI layout. | Focused parser test plus post-deploy proof reports Dhan source for every required chain. |
| MRI-20260824-003 | P1 | BLOCKED_REVIEW | PRs #347 and #348 have green exact-head checks but current main protection requires independent approval. PR #347 owns the runbook. | Independent reviewer; then rebase this schema lane and add any still-missing runbook addendum without overwriting #347. | Approved, exact-head green merge with current-main reconciliation. |
| MRI-20260824-004 | P1 | BLOCKED_EXTERNAL | Bloomberg/TradingView/editorial catalyst ingestion and named AI connectors have no request-scoped entitlement, redistribution/ML rights, secret onboarding, quota or connector-health proof. | Connector owner: verify exact official product, rights and server-side Secret Manager/OAuth path before implementation. | Entitlement record, least-privilege identity, sanitized health, lineage, failure isolation and PAPER-only canary evidence. |
| MRI-20260824-005 | P1 | UNPROVEN | No new request-scoped evidence proves available GCP GPU/TPU quota, cost guard, reproducible training job or immutable artifact registry for this request. | MLOps lane: profile the workload and quotas read-only; compare CPU baseline before requesting accelerator capacity. | Reproducible job/run, dataset/model hashes, cost/quota bounds and champion/challenger result. |
| MRI-20260824-006 | P1 | OPEN | Canonical v4 policy schema did not require the existing MRI/catalyst/connector/compute safety blocks, allowing silent removal or unsafe edits to pass schema validation. | This branch: strengthen the existing schema and add mutation tests. | YAML validates and each unsafe mutation fails validation. |

No concern authorizes LIVE trading, real orders, browser-visible secrets, scraping/paywall bypass, or uncontrolled model/champion mutation.
