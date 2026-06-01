# PR20 Authoritative Runtime and Data Map

## Purpose

Create the first control-plane boundary after PR19. This file defines how System3 identifies authoritative runtime surfaces, data surfaces, duplicate/stale candidates, and the minimum proof required before future autonomous ML upgrades.

## Scope

This PR is architecture and proof-map only.

It does not modify:

- trading logic
- broker configuration
- environment or secret files
- database files
- model artifacts
- live runtime mode files
- deployment workflows

## Decision

System3 must not treat filenames as truth. Every runtime surface must be proven by entrypoint, import, workflow, launcher, or report evidence before it can be called authoritative.

The runtime authority map has four states:

| State | Meaning | Allowed action |
|---|---|---|
| AUTHORITATIVE | Proven wired into runtime, CI, launcher, workflow, or documented control plane | Improve only with proof |
| CANDIDATE | Looks useful but runtime wiring is not proven | Investigate, do not depend on it |
| LEGACY_RISK | Duplicate/stale/same-purpose file that can confuse runtime or humans | Quarantine proposal only |
| REJECTED | Proven unsafe, obsolete, or superseded | Delete only after repeated proof cycles |

## Current authoritative surfaces

| Surface | Authoritative path/status | Proof basis | Current risk |
|---|---|---|---|
| Repository default branch | `main` | GitHub repo default branch | None |
| Architecture roadmap | `docs/architecture/MASTER_PR_ROADMAP.md` | PR19 roadmap | Needs execution PRs |
| Brutal gap analysis | `docs/architecture/SYSTEM3_BRUTAL_GAP_ANALYSIS.md` | PR19 gap matrix | High gaps remain |
| Autonomous ML blueprint | `docs/architecture/INSTITUTIONAL_AUTONOMOUS_ML_TRADING_BLUEPRINT.md` | PR19 architecture decision | Planning only |
| Runtime authority inventory | `reports/authority_inventory/ROOT_RUNTIME_AUTHORITY_INVENTORY.md` | PR12 report-only inventory | Needs deeper PR20+ wiring proof |
| Backend Docker path | `dashboard/backend/Dockerfile` | PR13/PR15/PR16 chain | Build-proof only |
| Backend app candidate | `dashboard/backend/app.py` | GCP proof path references | Production runtime not proven |
| GCP backend proof workflow | `.github/workflows/gcp-cloud-run-backend-proof.yml` | PR18 manual workflow | Manual-only, dry-run first |
| Azure CD workflow | `.github/workflows/cd.yml` | Existing CD path | Azure readiness not proven |
| Root safety gate | CI governance/root architecture gate | PR10 | Keep blocking |

## Runtime authority proof requirements

A file can be marked AUTHORITATIVE only when at least one proof is available:

1. It is called by a workflow file.
2. It is imported by an authoritative runtime entrypoint.
3. It is invoked by a launcher script that is itself authoritative.
4. It is referenced by the active deployment path.
5. It is used by CI or a blocking safety gate.
6. It appears in a runtime report with timestamp and provenance.

## Data authority map

| Data layer | Target authoritative source | Current status | Required next proof |
|---|---|---|---|
| Raw market data | Immutable partitioned files under future `data/raw/` policy | Not proven | Data contract PR |
| Curated features | Versioned feature tables under future feature-store policy | Not proven | Feature contract PR |
| Options chain | Full expiry/strike/OI/IV/liquidity snapshots | Not proven | Options schema gate |
| Lifecycle ledger | Paper/analyzer trade lifecycle truth table/report | Partial/unknown | Runtime lifecycle authority proof |
| Model registry | Active/candidate model manifest and rollback target | Not proven | MLflow/manifest PR |
| Dashboard truth | API-backed live state with provenance labels | Not proven | Dashboard data contract PR |
| Deployment image | Backend image built from proven Dockerfile and runtime endpoint | Build-proof only | FastAPI/uvicorn container PR |

## Duplicate and stale-file policy

No deletion is allowed in this phase.

Safe sequence:

```text
search -> classify -> prove runtime authority -> propose quarantine -> run CI/runtime proof -> monitor -> delete later only after repeated evidence
```

## Protected zones

Future PRs must treat these as protected unless the PR explicitly proves safety:

- live trading enable flags
- broker credentials or broker adapters
- `.env`, `.env.*`, secrets, or publish profiles
- database files and migrations
- model artifacts and trained binaries
- order execution and risk-gate code
- runtime launchers and scheduler tasks
- dashboard truth API contracts

## Immediate blockers after this PR

1. Runtime authority is still not fully machine-proven.
2. Data lineage contracts are not implemented.
3. Model registry and promotion gates are not implemented.
4. Backend container is build-proof oriented, not production runtime proof.
5. Dashboard is not proven as live truth source.
6. Old high-risk open PR #1 must not be merged as-is.

## Next required PRs

| PR | Target | Purpose |
|---|---|---|
| PR21 | Data contracts and schema gates | Define raw/curated/lifecycle/options schemas |
| PR22 | Nightly ingestion orchestrator | Create post-market ingestion workflow skeleton |
| PR23 | Feature store boundary | Define offline/online feature versioning |
| PR24 | Daily replay and backtest engine | Build reproducible after-cost replay path |
| PR36 | Production FastAPI backend container proof | Replace build-proof `http.server` container with runtime proof |

## Final PR20 verdict

PASS for creating the first authoritative runtime and data map.

WARN because this is still a planning/control-plane artifact, not a runtime implementation.

BLOCK real live trading until multi-week analyzer evidence, model promotion gates, and runtime safety proof exist.
