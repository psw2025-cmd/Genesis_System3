# Pre-commit Agent Policy (P2.10)

For Cursor/CI agents running pre-commit:

- **Black, flake8, isort**: Run on changed files only when possible. Full runs can be slow.
- **Bandit**: Scans `core/` only. Report-only; do not block on findings.
- **Safety, pip-audit**: Report-only. Vulnerabilities are logged; upgrade per PRODUCTION_READINESS_ISSUES_PRIORITY.md.
- **pytest**: Use `--maxfail=1 -q` for fast feedback. Full suite can be run separately.
- **Optional steps**: Frontend build, hadolint. Skip if environment lacks Node/Docker.

To run a lighter check: `pre-commit run black --all-files` then `pip check`.
