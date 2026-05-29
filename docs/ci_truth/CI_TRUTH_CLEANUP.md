# CI Truth Cleanup and Root Architecture Gate

## Policy

Architecture and trading safety must be full PASS.

Legacy cleanup can be report-only only temporarily.

## Blocking gate

The blocking gate checks:

- required root files exist
- critical Python files compile
- protected runtime paths are not changed by CI/report-only PRs
- `.env`, DB files, and model artifacts are not changed
- changed files do not contain obvious secret-like values
- changed files do not enable obvious live trading or order placement

## Report-only legacy checks

These remain visible but temporary report-only:

- black
- flake8
- isort
- mypy
- bandit
- pytest
- eslint
- yaml lint
- dockerfile lint

## Protected scope

This PR must not touch:

- trading logic
- broker configuration
- `.env`
- databases
- model artifacts
