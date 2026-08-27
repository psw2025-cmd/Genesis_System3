# System3 Ultra MRI Control Plane

Authority: `SYSTEM3_ULTRA_MRI_CONTROL_PLANE_V1`.

## Purpose

Provide one reusable, agent-independent way to certify whether the current GitHub -> Google Cloud -> production UI control path is actually usable before dependent System3 work proceeds.

The user provides the goal. Agents own the technical preflight, implementation, recovery, takeover, testing, deployment and proof. A later `missing access` explanation is not acceptable when the missing capability could have been detected by this preflight.

## Canonical run paths

### GitHub UI
Actions -> **System3 Ultra MRI** -> **Run workflow**.

### GitHub CLI

```bash
gh workflow run system3-ultra-mri.yml --repo psw2025-cmd/Genesis_System3
```

### Any authenticated clone / Cloud Shell

```bash
python scripts/system3_ultra_mri.py
```

For the complete delegated GCP path, prefer the GitHub workflow because it uses the canonical keyless WIF identity.

## What it captures

- GitHub/GCP execution context and exact SHA.
- Active GCP identity and project authority.
- Enabled APIs.
- Project IAM bindings and service accounts.
- Workload Identity Federation inventory when permitted.
- Cloud Run services, revisions and jobs with sensitive env values redacted.
- Cloud Scheduler jobs and targets.
- Secret Manager secret names/version metadata only; never payload data.
- Firestore database inventory, Cloud Storage buckets, Artifact Registry, Cloud SQL and selected ancillary resource classes.
- Recent bounded Cloud Run logs with sensitive fields redacted.
- Current production service URL.
- Same-session read-only health, deploy, broker, state, gates, option-chain, QC, scheduler and UI-shell probes.
- Canonical all-tab production browser proof using `scripts/gcp_public_dashboard_runtime_proof.py`.
- Repository tracked-file and exact-SHA evidence.
- `CAPABILITY_MATRIX.csv`, `FINAL_VERDICT.json`, and `FINAL_VERDICT.md`.

## Credential validation rule

Plaintext credentials are not proof and must not be copied into the evidence artifact.

For duplicate/candidate credentials:

1. inventory secret/reference names and versions;
2. identify the actual consuming service/job;
3. validate the candidate through the same harmless authenticated read-only consumer path;
4. identify the canonical working credential/reference;
5. prove zero consumers before retiring a duplicate;
6. re-run Ultra MRI and production UI proof after cleanup.

The scanner therefore verifies *operational validity* rather than merely `secret exists`.

## Fail-closed access contract

`ACCESS_CERTIFIED=true` only when every critical capability passes.

Any critical failure must immediately become an agent-owned access-resolution/takeover action before dependent implementation continues. The owner is asked to act only when the failed capability crosses a genuinely owner-only external account/billing/identity approval boundary.

Cursor, Claude or any other unavailable agent is never a reason for the lane to remain idle. The next capable agent must read current `main`, Issue #188 and active PR ownership, then take over non-overlapping unfinished work.

## Completion boundary

Ultra MRI proves control capability; it does not prove trading quality.

System3 user-visible completion still requires the full chain:

`source/data -> durable history/schema -> features -> model/backtest -> prediction -> later actual -> PAPER lifecycle/P&L -> APIs -> frontend -> live production UI -> stability`.

For every user-visible feature, final acceptance remains fresh exact-serving production UI proof, not code/PR/CI alone.

## Safety invariants

- Secret payloads are never dumped into artifacts.
- LIVE trading and real-order authority remain separate and locked unless explicitly authorized through their own readiness gate.
- Ultra MRI itself performs read-only infrastructure and API/UI probes; it does not delete resources, widen IAM, mint tokens or place orders.
