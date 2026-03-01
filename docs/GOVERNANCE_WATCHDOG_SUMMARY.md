# Governance Watchdog — System3 Ultra

**Purpose:** Production-grade readiness enforcement, auto-resolution, and proof artifacts.

---

## Rules of Operation

| # | Rule | Implementation |
|---|------|-----------------|
| 1 | **Self-Diagnosis & Auto-Resolution** | Run-FullQA.ps1, Run-FullGovernance.ps1; npm install fallback; safety auto-install |
| 2 | **Dual Requirements Workflow** | `.in` = editable source; `.txt` = pip-compile output; install from `.txt` only |
| 3 | **Production-Grade Enforcement** | pip upgrade, pip check, black, flake8, bandit, safety, pip-audit, pytest |
| 4 | **Proof & Transparency** | Artifacts in `logs/inspector/`; `/api/governance` dashboard endpoint |
| 5 | **Continuous Governance** | PRODUCTION_READINESS_ISSUES_PRIORITY.md; auto-update counts |
| 6 | **Output Discipline** | Corrected requirements files; governance comments preserved |

---

## Proof Artifacts (`logs/inspector/`)

| Artifact | Source | Purpose |
|----------|--------|---------|
| `pip_audit.json` | pip-audit -f json | Vulnerability scan (report-only) |
| `safety_report.txt` | safety scan | Safety scan (report-only) |
| `pytest_report.txt` | pytest | Test results |
| `flake8_report.txt` | flake8 | Lint results |
| `black_report.txt` | black --check | Format check |
| `black_diff.txt` | black --diff | Formatting changes (proof) |
| `pip_check.txt` | pip check | Dependency consistency |
| `qa_timestamp.txt` | Get-Date | Last QA run |

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | System health, dependencies |
| `GET /api/governance` | Priority counts, artifact status, vuln counts |
| `GET /metrics` | Prometheus metrics |

---

## Requirements Workflow

1. Edit `requirements_runtime.in` or `requirements-dev.in`
2. Regenerate: `scripts\compile_requirements.bat` (or `pip-compile`)
3. Install: `pip install -r requirements_runtime.txt` then `pip install -r requirements-dev.txt`
4. Never install from `.in` directly

---

## Verification Commands

```powershell
pip check
black --check core scripts tools phases dashboard
Run-FullGovernance.ps1
Run-FullQA.ps1
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/governance" -UseBasicParsing
```

---

## Current Status (from PRODUCTION_READINESS_ISSUES_PRIORITY.md)

| Priority | Resolved | Total |
|----------|----------|-------|
| P0 | 3 | 3 |
| P1 | 8 | 8 |
| P2 | 9 | 10 |
| P3 | 1 | 6 |

---

## Related Docs

- `docs/BEST_PRACTICES_IMPLEMENTATION_CHECKLIST.md` — NIST/OWASP-style checklist
- `docs/INCIDENT_RUNBOOK.md` — Common failures and remediation
- `docs/GOVERNANCE_DUAL_REQUIREMENTS.md` — .in/.txt workflow
