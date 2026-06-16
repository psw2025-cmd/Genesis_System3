# Genesis System3 Global Control Plane Structure — 2026-06-16

## Goal

Replace scattered ad-hoc scripts and proof workflows with one governed control-plane structure while keeping runtime trading safe.

## Current authority

| Layer | Authoritative item | Status |
|---|---|---|
| CI workflow | `.github/workflows/ci.yml` | KEEP — only active GitHub Actions workflow |
| CI safety gate | `.github/scripts/root_architecture_gate.py` | KEEP — blocks unsafe changes |
| Runtime backend | `dashboard/backend/app.py` | KEEP |
| Runtime Docker | `dashboard/backend/Dockerfile` | KEEP |
| Render config | `render.yaml` | KEEP |
| Legacy menu | `run_system3.py` | REVIEW — disabled legacy shell, kept because CI still checks it |
| Ultra menu | `system3_ultra.py` | KEEP — current local panel |

## Target control-plane layout

```text
system3_control_plane.py                 # one human-facing entrypoint
core/control_plane/
  __init__.py
  registry.py                            # command registry and allowed operations
  safety.py                              # analyzer-only, no-live, no-secret checks
  inventory.py                           # file inventory and classification
  proofs.py                              # proof artifact validation
  cleanup.py                             # safe cleanup executor
  readiness.py                           # readiness matrix builder
  trading_lifecycle.py                   # analyzer-paper lifecycle proof hooks only
  model_governance.py                    # model/data/backtest proof checks only
  dashboard_checks.py                    # dashboard/API/UI proof checks
reports/ci_truth/                        # CI-generated proof output only
reports/latest/                          # selected latest proof artifacts only
```

## Control-plane command policy

| Command family | Allowed now? | Notes |
|---|---:|---|
| `inventory` | Yes | Read-only file inventory |
| `classify` | Yes | Classify files into KEEP/DELETE/ARCHIVE/MERGE/REVIEW |
| `proofs` | Yes | Validate existing proof artifacts |
| `cleanup --dry-run` | Yes | No deletion without proof |
| `cleanup --apply` | Restricted | Only generated/archive files proven safe |
| `model --train` | No | Blocked until retrain/promotion policy is approved |
| `broker --live` | No | Live trading disabled |
| `trade --live` | No | Live trading disabled |
| `paper-lifecycle` | Yes | Analyzer/paper proof only |

## Required safety invariants

1. Live trading remains disabled by default.
2. No broker write operation can run from CI.
3. No `.env`, token, TOTP, API key, DB, or model artifact is committed.
4. Generated runtime state must not be tracked.
5. Every cleanup deletion must have manifest proof.
6. Every runtime source deletion requires import/reference proof.
7. CI uses read-only repository permissions.
8. Deploy workflows stay removed until paper lifecycle proof is complete.

## Replacement strategy

### Phase 1 — Completed

- Removed extra active workflows.
- Kept only `ci.yml` as the GitHub Actions workflow.
- Removed stale `qa.yml` reference from root architecture gate.
- Removed tracked generated PID state files.

### Phase 2 — In progress

- Add cleanup manifest.
- Add global control-plane structure document.
- Classify candidate files.
- Do not delete uncertain source files.

### Phase 3 — Next implementation

Add a real `system3_control_plane.py` wrapper that only calls safe read-only/dry-run commands first:

```bash
python system3_control_plane.py inventory
python system3_control_plane.py classify
python system3_control_plane.py proofs
python system3_control_plane.py cleanup --dry-run
```

### Phase 4 — Later after proof

Merge scattered scripts into `core/control_plane/*` modules, then delete old script entrypoints only after reference checks prove they are unused.

## Non-negotiable blocker

The latest trading readiness proof still reported `trade_ready=false` because `live_market_analyzer_paper_trade_not_proven`. Therefore, no live trading or deploy automation should be restored until analyzer-paper lifecycle proof passes.
