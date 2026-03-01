# Best Practices Implementation Checklist — Genesis System3

**Purpose:** Map NIST/OWASP-style best practices to current state. High-leverage, low-friction items first.

---

## 1. Versioning, Dependencies, Reproducibility

| Practice | Status | Location | Gap / Action |
|----------|--------|----------|--------------|
| Pin deps in lockfile, keep in VCS | ✅ Done | `requirements_runtime.txt`, `requirements-dev.txt` | pip-compile output = lockfile; committed |
| CI installs from lockfile, not .in | ✅ Done | Run-All.bat, Run-FullGovernance.ps1 | `pip install -r requirements_*.txt` |
| Separate runtime vs dev deps | ✅ Done | `requirements_runtime.txt`, `requirements-dev.txt` | Runtime minimal; dev has bandit, pytest, etc. |
| Regular dependency audit | ✅ Done | pip-audit, safety in Run-FullQA.ps1 | Report-only; remediation backlog in PRODUCTION_READINESS |
| Frontend lockfile | ✅ Done | `dashboard/frontend/package-lock.json` | npm ci uses it |

**Quick win:** Ensure `scripts\compile_requirements.bat` runs in CI before install (already in GOVERNANCE_DUAL_REQUIREMENTS).

---

## 2. Security-by-Default

| Practice | Status | Location | Gap / Action |
|----------|--------|----------|--------------|
| Keep software up to date | ✅ Partial | P1.6 remediation | 9 vulns blocked (flask, werkzeug, keras, protobuf); track in P1_SECURITY_REMEDIATION |
| Vulnerability scans in CI | ✅ Done | pre-commit, Run-FullQA.ps1 | bandit, pip-audit, safety |
| Treat high/critical as blockers | ⚠️ Partial | Run-FullQA.ps1 | pip-audit/safety report-only; consider fail-fast for critical |
| Environment segmentation | ⚠️ Partial | `.env`, config/ | No Vault/K8s Secrets; use env vars, avoid committing secrets |
| Avoid eval / dynamic code loading | ✅ Done | Codebase | No eval; pickle only for trusted models (document) |
| Harden container images | ⚠️ Partial | Dockerfile.backend | Add non-root user, drop setuid; scan images (hadolint in pre-commit) |

**Quick wins:**
- Add `USER nonroot` to Dockerfiles when host volumes (outputs/, logs/) are chowned to match; else container may fail to write.
- Document: "Do not load untrusted pickle/model files."

---

## 3. CI/CD and Change Management

| Practice | Status | Location | Gap / Action |
|----------|--------|----------|--------------|
| Feature-branch workflow | ✅ Assumed | Git | Short-lived branches; merge to main |
| Lint/format as gates | ✅ Done | pre-commit, Run-FullQA.ps1 | black, flake8, isort |
| Type checks (mypy) | ✅ Done | pre-commit | mypy in hooks |
| Unit/integration tests | ✅ Done | pytest in Run-FullQA.ps1 | Coverage threshold not enforced |
| Security gates mandatory | ⚠️ Partial | pre-commit | bandit, safety, pip-audit run but report-only in QA |
| Dependency upgrade validation | ⚠️ Partial | Manual | No compatibility matrix; test after each upgrade |
| Immutable deployments | ⚠️ Partial | docker-compose | New image per deploy; no blue/green yet |

**Quick wins:**
- Add `pytest --cov --cov-fail-under=50` (or similar) to enforce coverage.
- Make pip-audit fail on critical vulns: `pip-audit --desc | findstr "critical"` → exit 1.

---

## 4. Observability and Incident Readiness

| Practice | Status | Location | Gap / Action |
|----------|--------|----------|--------------|
| Centralized JSON logging | ✅ Done | `structured_logging.py` | logs/backend.jsonl; loguru rotation |
| Structured fields | ✅ Done | timestamp, level, service, request_id | Add correlation_id if multi-service |
| Prometheus metrics | ✅ Done | `/metrics` | uptime, request count |
| Health checks | ✅ Done | `/api/health`, `dependencies` | broker, db, outputs_dir |
| Liveness/readiness probes | ✅ Done | docker-compose healthcheck | Backend health before frontend |
| Dashboards / alerting | ⚠️ Partial | `/api/governance` | No Grafana/PagerDuty; manual monitoring |
| Runbooks / on-call | ❌ Open | — | Add docs/INCIDENT_RUNBOOK.md |

**Quick wins:**
- Add `docs/INCIDENT_RUNBOOK.md` with common failures and remediation.
- Expose error rate in `/metrics` if not already.

---

## 5. Reliability and Resilience

| Practice | Status | Location | Gap / Action |
|----------|--------|----------|--------------|
| Idempotent deploys | ✅ Done | Docker | Rebuild + up; can retry |
| Backups / DR | ⚠️ Partial | outputs/, config/ | No automated backup; document restore |
| Data integrity | ⚠️ Partial | CSV validation | Checksums/schema migrations not formalized |
| Chaos testing | ❌ Open | — | Future: fault injection |

---

## 6. Trading/ML-Specific

| Practice | Status | Location | Gap / Action |
|----------|--------|----------|--------------|
| Separate compute paths | ✅ Partial | Backend vs trading scripts | Ingestion, inference, execution separated |
| Model governance | ⚠️ Partial | outputs/, phases | No formal versioning; track in docs |
| Resource governance | ❌ Open | — | No quotas, autoscaling, budget alerts |
| Deterministic ML builds | ✅ Done | requirements_runtime.txt | Pinned torch, tensorflow, lightgbm |
| Rollback for models | ⚠️ Partial | Manual | Document rollback path |

**Quick wins:**
- Add `docs/MODEL_GOVERNANCE.md`: where models live, how to version, rollback steps.
- Pin model artifact paths and document in config.

---

## 7. Concrete Architecture (Current)

| Component | Implementation |
|-----------|----------------|
| Source of truth | Git; main = production-ready |
| CI pipeline | Run-All.bat → Run-FullGovernance.ps1 → Run-FullQA.ps1; pre-commit |
| Stages | lint (black, flake8), security (bandit, safety, pip-audit), tests (pytest) |
| Deployment | Docker Compose; multi-stage Dockerfile.backend, Dockerfile.frontend |
| Orchestration | docker-compose; healthcheck on backend |
| Secrets | Env vars; no Vault; rotate manually |
| Security controls | pip-audit, safety, bandit in CI; image lint (hadolint) |

---

## 8. Priority Actions (Next 2 Sprints)

| # | Action | Effort | Status |
|---|--------|--------|--------|
| 1 | pip-audit strict mode (PIP_AUDIT_STRICT=1) | Low | ✅ Done |
| 2 | pytest coverage threshold (--cov-fail-under=1) | Low | ✅ Done |
| 3 | Add `docs/INCIDENT_RUNBOOK.md` | Low | ✅ Done |
| 4 | Add `docs/MODEL_GOVERNANCE.md` | Medium | ✅ Done |
| 5 | Harden Dockerfiles (non-root, minimal layers) | Medium | Pending (volume perms) |
| 6 | Add `docs/BACKUP_RESTORE.md` + script | Low | ✅ Done |
| 7 | Address bandit MEDIUM (pickle, subprocess) | Medium | Backlog |

---

## References

- `docs/GOVERNANCE_WATCHDOG_SUMMARY.md` — Governance rules
- `docs/GOVERNANCE_DUAL_REQUIREMENTS.md` — .in/.txt workflow
- `docs/PRODUCTION_READINESS_ISSUES_PRIORITY.md` — P0–P3 tracker
- `docs/P1_SECURITY_REMEDIATION_2026_02_28.md` — Vuln remediation log
