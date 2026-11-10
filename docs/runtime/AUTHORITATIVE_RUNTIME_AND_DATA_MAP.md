# Genesis System3 Authoritative Runtime, Data, and Evidence Map

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

## Runtime authority

| Surface | Current authority | Notes |
|---|---|---|
| Repository | `psw2025-cmd/Genesis_System3` / `main` | Source/config authority |
| Production cloud | GCP project `system3-openalgo-safe` | Render/Azure-era deployment material is historical/non-authoritative |
| Region | `asia-south1` | Production region |
| Cloud Run service | `genesis-system3-web` | User-facing production runtime |
| Public UI | `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/` | Authoritative UI boundary |
| Broker | Dhan | Legacy Angel paths are retired for current production authority |
| Cloud auth | GitHub Actions keyless WIF | No long-lived service-account JSON keys |
| Dhan rotation | `genesis-system3-dhan-token-rotate` | Dedicated bounded authority |

This document defines authority categories; it does **not** permanently assert that any runtime component is healthy now. Current health/state must be freshly observed.

## Temporal evidence authority

A filename or directory name is never enough to establish current truth.

| Evidence source | Authority for a new `now/current/live` claim |
|---|---|
| New production Chrome/WebDriver session started after current request | Highest for UI-visible state |
| New same-session production API request | Highest for the API field observed |
| New current-window Cloud Run/log/runtime query | Authoritative for that runtime/log fact |
| Fresh serving revision/SHA/traffic query | Authoritative for deployment metadata |
| Current source/config | Intended implementation only, not runtime proof |
| `reports/latest/` | Historical stored evidence; not live by path/name |
| Previous GitHub artifact/workflow | Historical observation; not proof the state persists |
| `SYSTEM_STATE.md` / `CHANGE_LOG.md` | Historical/contextual only |

Use `scripts/system3_temporal_truth_guard.py` for machine freshness checks and `scripts/gcp_live_ui_snapshot.py` for request-scoped production UI proof.

## Full production UI authority

For a current full-UI claim, the authoritative proof is a new production browser lifecycle capturing all canonical tabs:

`decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

The same lifecycle must bracket the browser session with fresh broker/health API snapshots and capture per-tab visible text + screenshots + UTC timestamps.

A local Vite/Chrome run is useful for code/render regression testing but cannot establish GCP production data/runtime truth.

## Data authority principles

### Broker and account state

Current Dhan connectivity must come from a fresh read-only production broker observation. Token metadata or a previously successful rotation does not prove connectivity now.

### Option/market data

A current market-data claim requires fresh source/provenance and freshness evidence. UI-facing claims additionally require fresh visible production-browser proof.

HTTP 200 does not prove option-chain completeness. A rendered component does not prove contracts/strikes/expiries are present.

### Prediction and ML data

Model/prediction claims must identify the evaluation window, source, sample size, and observation time. Historical model metrics remain valid for that historical window but are not current market-performance proof.

### Paper lifecycle

Paper state must be reconciled across the current authoritative data store/API/UI. An old proof pack does not prove the current ledger/session state.

## Runtime authority states

| State | Meaning |
|---|---|
| `AUTHORITATIVE_PATH` | Correct current source/runtime path, but not necessarily healthy |
| `CURRENT_LIVE_PROVEN` | Fresh request-scoped/current-window observation proves the stated fact |
| `HISTORICAL_EVIDENCE` | Valid evidence of a past observation only |
| `CANDIDATE` | Potentially useful but wiring/authority not proven |
| `LEGACY_NON_AUTHORITATIVE` | Superseded path that must not drive current conclusions |
| `NOT_PROVEN` | Required current evidence absent/invalid |

Never convert `AUTHORITATIVE_PATH` into `CURRENT_LIVE_PROVEN` without a fresh observation.

## Duplicate/stale source policy

Safe sequence:

```text
search -> classify -> identify current authority -> compare history -> observe live -> change -> test -> observe live again
```

Do not delete historical evidence merely because it is stale; label it historical. Remove or quarantine obsolete **instructions** when they can cause an agent to act on retired authority.

## Protected zones

- LIVE/order execution flags;
- broker credential payloads;
- Secret Manager payloads;
- IAM authority;
- Dhan token mint path;
- order/risk code;
- production deployment/traffic;
- durable paper/market/model data;
- UI/API truth contracts.

Changes require bounded authority, exact-head tests, and post-change fresh proof.

## Current-state resolution rule

When current state is requested:

1. note request/investigation UTC start;
2. query current production after that time;
3. for UI, start new production browser session;
4. capture same-session API/runtime truth;
5. report timestamps and contradictions;
6. do not substitute the newest stored artifact.

When agents disagree, generate a new authoritative observation. Historical recency alone does not arbitrate.
