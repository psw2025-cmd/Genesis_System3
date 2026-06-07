# System3 Proof-First Cleanup Policy

## Goal

Keep the repository clean without breaking the working runtime.

## Auto-delete allowed

The following tracked files can be automatically removed from Git tracking whenever found:

- `audit_artifacts/`
- `__pycache__/`
- `*.pyc`
- `desktop.ini`
- `.DS_Store`
- `.pytest_cache/`
- real `.env` files, private keys, and secret-style files accidentally committed

## Auto-delete not allowed without proof

Do not delete source/runtime files only because they look old, duplicated, copied, or unused.

Examples requiring proof-first classification:

- duplicate `.py` files
- `old`, `backup`, `copy`, `archive`, `tmp`, `quarantine` source folders
- duplicate dashboards
- duplicate broker modules
- duplicate model/training/backtest files
- reports that may be referenced by dashboard/docs/tests

## Required proof before source deletion

Before deleting source-like files, create proof showing:

1. File is not imported by runtime path.
2. File is not referenced by workflows/tests/docs needed for current operation.
3. File is not the authoritative implementation.
4. Better authoritative replacement is identified.
5. A rollback path exists.

## Approved sequence

1. Full repo scan.
2. Runtime reachability map.
3. Duplicate/source classification.
4. Quarantine or delete generated files.
5. For source files, quarantine first if uncertain.
6. Run compile/runtime/proof gates.
7. Delete only after proof passes.

## Current active cleanup workflows

- `.github/workflows/cleanup-generated-files.yml`
- `.github/workflows/repo-cleanliness-gate.yml`
- `.github/workflows/full-repo-scan-clean.yml`

## Non-negotiable safety

- Analyzer/Paper mode only.
- Do not enable live trading during cleanup.
- Do not commit credentials or private secrets.
- Never delete files based only on filename similarity.
