# Repo Cleanup Manifest — 2026-06-16

Repository: `psw2025-cmd/Genesis_System3`

## Scope

This manifest is the authoritative cleanup register for GitHub-side cleanup. It is intentionally conservative:

- No runtime source under `core/`, `dashboard/`, `services/`, broker, model, database, or config is deleted without local import graph proof.
- Deletion requires all of these: `NOT_REFERENCED + GENERATED_OR_ARCHIVE_OR_DUPLICATE + SAFE_TO_REGENERATE`.
- If any condition is unknown, classification is `REVIEW`, not `DELETE`.
- Live trading remains disabled; cleanup must not enable broker write paths.

## Completed actions

| Path | Class | Action | Proof basis |
|---|---|---|---|
| `.github/workflows/*` except `ci.yml` | DELETE | Removed active extra workflow files | Consolidated CI policy requires only `.github/workflows/ci.yml` |
| `.github/scripts/root_architecture_gate.py` | KEEP | Updated stale required file list | Removed deleted `qa.yml` reference |
| `state/system3_master.pid` | DELETE | Removed tracked runtime state | PID file is generated runtime state; `state/` is ignored in `.gitignore` |
| `state/system3_watchdog.pid` | DELETE | Removed tracked runtime state | PID file is generated runtime state; `state/` is ignored in `.gitignore` |

## Current high-confidence classifications

| Path / Pattern | Class | Reason | Delete now? |
|---|---|---|---:|
| `.github/workflows/ci.yml` | KEEP | Single active global CI guard | No |
| `.github/scripts/root_architecture_gate.py` | KEEP | Blocking architecture/trading safety gate | No |
| `.gitignore` | KEEP | Protects env, state, logs, generated outputs | No |
| `run_system3.py` | REVIEW | Legacy disabled menu but still required by CI gate | No |
| `system3_ultra.py` | KEEP | Existing System3 Ultra control panel entrypoint | No |
| `render.yaml` | KEEP | Active Render runtime map | No |
| `dashboard/backend/app.py` | KEEP | Backend runtime entrypoint | No |
| `dashboard/backend/Dockerfile` | KEEP | Backend Docker runtime | No |
| `state/*.pid` | DELETE | Generated runtime state; safe to regenerate | Yes, when tracked |
| `storage/`, `logs/`, `audit_artifacts/`, `reports/*` except allowed latest proofs | DELETE/ARCHIVE | Generated outputs; should not be source | Only if tracked and not required proof |
| `*.bak`, `*.bat`, `*.ps1`, `*.cmd` | REVIEW | Ignored by policy, but may still contain useful local operations | No blind delete |
| `docs/system3_phases_*` | ARCHIVE/REVIEW | Historical implementation docs; may be redundant | No blind delete |
| `docs/*SUCCESS*`, `docs/*COMPLETE*`, `docs/*FINAL*` | ARCHIVE/REVIEW | Historical status docs; likely archival | No blind delete |
| `scripts/*fix*`, `scripts/*verify*`, `scripts/*auto*` | REVIEW/MERGE | Candidate for merge into control plane; may still be useful | No blind delete |
| `core/engine/system3_phase*.py` | REVIEW/MERGE | Phase modules may be runtime-reachable; local import graph required | No blind delete |
| `core/tools/*cleaner*`, `*duplicate*`, `*backup*` | REVIEW/MERGE | Cleanup tools may be callable; require reference proof | No blind delete |

## Review candidates found by GitHub search

| Path | Classification | Reason |
|---|---|---|
| `core/engine/system3_phase171_file_backup.py` | REVIEW | Runtime path under `core/engine`; name suggests backup but cannot delete without import graph |
| `core/engine/system3_phase97_backup_recovery.py` | REVIEW | Recovery module; may be operational |
| `scripts/auto_retrain.py` | REVIEW | Model workflow candidate; live/promotion policy must be checked |
| `scripts/fix_csv_structure.py` | REVIEW/MERGE | Utility candidate for control-plane merge |
| `scripts/verify_csv_files.py` | REVIEW/MERGE | Utility candidate for control-plane merge |
| `scripts/combined_auto_system_fixed.py` | REVIEW | Name suggests legacy/fixed script, but must prove unreferenced |
| `core/tools/system3_history_cleaner.py` | REVIEW/MERGE | Cleanup tool; may be useful from control plane |
| `core/engine/system3_phase209_duplicate_purger.py` | REVIEW/MERGE | Duplicate cleanup logic; must be governed by safe control plane |
| `scripts/world_class_comparison.py` | REVIEW/MERGE | Audit utility candidate |
| `docs/system3_phases_*.md` | ARCHIVE/REVIEW | Historical docs; can be archived after docs index is created |

## Required local proof before source deletion

The following must be run locally or by a trusted CI job before deleting source files:

```powershell
Set-Location C:\openalgo-main
.\.venv\Scripts\python.exe -m compileall .
rg --files > reports\ci_truth\file_inventory.txt
rg "<candidate_module_or_filename>" . > reports\ci_truth\reference_check_<candidate>.txt
```

A candidate becomes deletable only if:

1. It is not imported or executed by runtime/test/dashboard paths.
2. It is not referenced by active docs or control-plane configuration.
3. It is generated/archive/duplicate by content and naming evidence.
4. CI still passes after removal.

## Next cleanup sequence

1. Generate full file inventory using local `rg --files`.
2. Generate import/reference graph.
3. Classify every file as `KEEP / DELETE / ARCHIVE / MERGE / REVIEW`.
4. Move scattered utilities behind a single control-plane registry.
5. Delete only high-confidence generated/archive files.
6. Keep all trading/broker/model/database code locked until analyzer-paper lifecycle proof is complete.
