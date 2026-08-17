# Meta-Sovereign Architecture — grounded for Genesis System3

**Status:** analysis / plan (not implemented as claimed)  
**Safety:** LIVE trading remains OFF. No in-flight production graph rewrite.  
**Source flowchart:** user “Beyond 2026 Limits” four-layer diagram.

This document translates the claimed architecture into System3 terms so agents
do not treat marketing language as runtime authority.

## Verdict

Keep the **four-layer control model**. Reject literal delivery of:

- 100,000x advancement
- quantum-safe execution ring
- zero-knowledge formal proof of every patch
- metamorphic mutation of prompt weights / tool schemas in production
- full sovereign self-governance without human LIVE authority

Those claims cannot be proven on this stack and several would break
`agent_policy.yaml` and `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md`.

## Layer mapping

| Claimed | System3 authority today | Allowed evolution |
|---------|-------------------------|-------------------|
| L0 Intent spec & meta-compiler | `agent_policy.yaml`, Issue #188, `resume_state.json`, Git `main` | Typed intent/constraint YAML compiled **into PRs**, never into a hot Cloud Run graph |
| L0 Neural topology synthesizer | Cursor/Codex/Gemini loops proposing code | Same agents; output is git diff + tests, not a live topology rewrite |
| L1 Atomic state router | GitHub Actions + Cloud Scheduler + Cloud Run Jobs with separated SAs | Keep WIF + least privilege; no new quantum SDK |
| L1 Formal logic / AST clusters | pytest evals, contract tests, frontend build, safety greps | More specialist CI jobs; still empirical |
| L2 Invariant checker | Proof gates, LIVE locks, IAM baseline, temporal-truth policy | Expand machine-checkable invariants; do not label them ZK |
| L2 Metamorphic mutator | Bounded recoveries (Dhan rotate Job, IAM repair) | Mutate **code via PR** after a failing eval; never mutate live risk/LIVE |
| L2 Proof ledger | Git history + Cloud Logging + dated `reports/archive/` | Add SHA256-chained evidence records (no secret payloads) |
| L3 Cloud Run enclave | `genesis-system3-web` PAPER/ANALYZER | Optional later: binary provenance / Confidential VM — not a prerequisite |
| L3 Audit stream | Overview banner, `/api/continuous_closure`, GCP logs | Structured self-describing JSON with capture UTC + evidence class |

## Explicit rejects

1. **In-flight graph recompilation** on production Cloud Run. Deployment authority is GitOps: PR → CI → merge `main` → Cloud Run Auto Deploy → fresh live verify.
2. **Auto-evolving agents immune to a class of error.** Permanent immunity is not a real property. Fixes require tests and live SHA proof.
3. **Nuclear / defense regulatory completeness.** System3 is a PAPER/analyzer Dhan control plane. Do not claim that bar.
4. **Enabling Parameter Manager, Model Armor, or other Marketplace APIs** just because they appeared in `docs/google_cloud.pptx`. Enable only with a concrete ticket.

## Build plan (phased)

### Phase 1 — bind language to existing plane (no cloud change)

- This document + agent rule: claimed “meta-compiler” = Git + evals.
- Hash-stamp existing extracts (`gcp_google_cloud_pptx_live`, continuous closure) with capture UTC.
- No downloads, no new GCP APIs, no LIVE change.

### Phase 2 — evidence ledger + intent contracts

- `scripts/system3_proof_ledger.py`: append-only JSONL of decision/evidence hashes (repo SHA, Cloud Run revision, broker connected flag **without tokens**, gate IDs).
- Intent spec for each autonomous tick: `next_id`, constraints (`LIVE=false`, no secret mint except rotator), success criteria.
- Specialist clusters remain named existing jobs (rotate, rank, forecast, signals, CI), not a new multi-agent runtime.

### Phase 3 — optional hardening (only after Phase 2 is live-proven)

- Artifact Registry image digest pinning already used; keep it.
- Optional SLSA/provenance attestations on deploy.
- Confidential Computing only if there is a measured threat; not required for PAPER.

## Settings / downloads

**None required** to adopt this plan. Use existing:

- Local: `git`, `python`, `gcloud.cmd`, `pytest`
- Cloud: project `system3-openalgo-safe`, Cloud Run, Secret Manager, Scheduler, WIF
- GitHub: Issue #188 coordination bus

Do not enable Parameter Manager API from the pptx Enable screen unless a later
ticket needs parameters distinct from Secret Manager.

## Success criteria (honest)

- Every autonomous change still has a failing `tests/evals/` spec first.
- Production claims still need request-scoped live evidence.
- Proof ledger exists and is append-only.
- LIVE and order locks remain false until a separate human process.
- No agent claims ZK, quantum, or 100,000x.
