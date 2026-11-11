# External SSOT Proposal Decision Record

**Class:** `REFERENCE` — requirement intake and deduplication record, not live
runtime truth.

Source observed at request start `2026-08-24T18:40:35Z`:
`C:\Users\ADMIN\Desktop\output.txt`, 37,410 bytes, 312 lines, SHA-256
`4EC04856F44DEE69F1D967EBF3BCB6A1199B617753212E693BA961CF5A496BCF`.
The source contains mojibake and copied advertising. It is not committed.

## Complete disposition

| Source scope | Unique intent | Canonical disposition |
|---|---|---|
| SSOT fields 1–62 | Run/SHA/time, GitHub/GCP discovery, tools, sanitized secret metadata, IAM, browser/F12, health, artifacts, verdict, governance | Reuse current preflight, temporal truth, proof ledger, issue ledger and policy v4. The evidence catalog now makes them discoverable. Secret payloads and broad environment enumeration remain forbidden. |
| Cloud/data/model inventory 71–118 | Discover storage, ingestion, features, training, backtests, predictions, ground truth, lineage, charts and UI gaps | Preserve as conditional capability classes. Use the runtime/data map and prediction benchmark policy. BigQuery, GCS, Dataflow, Vertex, Looker, Cloud SQL and separate endpoints are not assumed to exist or be required. |
| Proposed row schemas 119–133 | Prediction, feature, backtest, artifact and run lineage | Reuse canonical policy schema and prediction lineage rules. New product schemas require ownership discovery and migration tests; the prose examples are not canonical schemas. |
| UI ideas 135–158 | Equity/drawdown, accuracy/calibration, confusion/ROC, feature importance, drift, reconciliation, per-symbol and provenance views | Requirements input for the existing 22-tab dashboard. They require current backend data contracts and fresh exact-serving browser/API semantic proof; images or stubs cannot prove closure. |
| Verification rules 160–180 | Checksums, signatures, freshness, reproducibility, DH-906, schemas, UI completeness and agent access | Checksums, freshness, lineage and fail-closed evidence are retained. Mandatory signing/OPA/raw-public URLs and a universal 120-second window are conditional design choices. Bare DH-906 is classified by the bounded Dhan authority, not automatically token expiry. |
| Advertising 200–210 | Sponsored Google Cloud copy and duplicated links | Rejected as non-requirement noise. |
| Self-healing rows 1–5 | Tools, secret gates, APIs, IAM and storage | Required tools are task-specific. No root CSV gate, secret payload discovery, blind API enablement or detector-driven IAM repair. Reuse least-privilege remediation and immutable-audit policies. |
| Self-healing rows 6–10 | Locking, signing, Playwright/HAR and health | Reuse current CI concurrency, browser proof and health contracts. Redis, signing and new workflows/endpoints are conditional, never auto-created merely because absent. |
| Self-healing rows 11–18 | Dhan, pipelines, features, training, models, backtests, prediction and reconciliation | Reuse Dhan bounded authority and prediction benchmark lifecycle. Do not auto-rotate from web runtime, treat PAPER as real execution, or create ungoverned cloud products. |
| Self-healing rows 19–25 | Artifact index, OPA, agent APIs, BigQuery, alerts and quarantine | Proof/issue ledgers and preflight are canonical. OPA, POST verification API, Prometheus and quarantine infrastructure remain conditional and require threat/cost/ownership review. |
| Self-healing rows 26–32 | UI charts, manifests, lineage, nightly job, cache, dependency and smoke tests | Reuse the 22-tab proof harness, lineage policy and existing Actions. Add capabilities only through focused tests and immutable Action SHAs; no uncontrolled nightly mutation. |
| Self-healing rows 33–40 | DR, metrics, compliance, governance, issue templates, append-only audit, helpers and finalizer | Reuse autonomous operations, IAM recovery, proof ledger and existing issue workflow. Missing optional templates do not block every run; required safety authority missing does fail closed. |
| Proposed runtime loop | Discover, validate, remediate, PR, CI, publish and repeat | Reuse the runbook lifecycle. Routine safe work continues; only genuine account/break-glass gates wait for the user. No fixed 10-minute concern spam, blind issue creation, direct-to-main writes or unsigned-PASS invention. |

## Result

The proposal did not justify a competing `GENESIS_MRI_MASTER_STATUS.json`, root
`CSV_GATE.csv`, OPA control plane or second verification API. The durable
improvement is a versioned discovery index embedded into every existing GitHub
preflight snapshot. Agents can locate and rerun the canonical authority without
mistaking the index or a stored report for current GitHub, GCP, Dhan or UI truth.
