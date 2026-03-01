# Incident Runbook — Genesis System3

**Purpose:** Common failures and remediation steps for on-call and ops.

---

## 1. Backend Unhealthy (`/api/health` returns error or 503)

| Symptom | Check | Action |
|---------|-------|--------|
| 503 / timeout | Backend process running? | `docker compose ps` or check uvicorn process |
| `dependencies.broker: false` | SMARTAPI credentials | Verify `.env` or config; broker may be intentionally disconnected |
| `dependencies.outputs_dir: false` | Disk / permissions | Check `outputs/` writable; `logs/` writable |
| `dependencies.db: false` | SQLite/DB path | Check `outputs/` exists; DB file not corrupted |

**Restart:** `docker compose restart backend` or restart uvicorn manually.

---

## 2. Frontend Not Loading / 502

| Symptom | Check | Action |
|---------|-------|--------|
| Blank page | Backend reachable? | Verify `http://localhost:8000/api/health` returns 200 |
| CORS errors | Backend CORS config | Check `dashboard/backend/app.py` CORS origins |
| 502 from nginx | Frontend container | `docker compose logs frontend`; rebuild if needed |

**Restart:** `docker compose restart frontend`.

---

## 3. Pip Check / Dependency Conflicts

| Symptom | Check | Action |
|---------|-------|--------|
| `pip check` fails | Conflicting versions | Run `pip install -r requirements_runtime.txt -r requirements-dev.txt`; if still fails, regenerate: `scripts\compile_requirements.bat` |
| pip-audit vulns | Known CVEs | See `docs/P1_SECURITY_REMEDIATION_2026_02_28.md`; upgrade unblocked packages |

---

## 4. QA / Governance Failures

| Failure | Action |
|---------|--------|
| Black format | `black core scripts tools phases dashboard` |
| Flake8 | Fix reported lines; run `flake8` |
| Pytest | Check `logs/inspector/pytest_report.txt`; fix failing test |
| npm build EPERM | Close editors/processes; retry; or use `npm install` fallback |

---

## 5. Trading / Signal Engine Issues

| Symptom | Check | Action |
|---------|-------|--------|
| No signals | Market hours, thresholds | Verify `outputs/health.json`; check regime/threshold config |
| Broker disconnect | SMARTAPI session | Re-auth; check token expiry |
| Position mismatch | Reconciliation | Run `position_reconciliation.py`; compare broker vs `positions_live.json` |

---

## 6. Escalation

- **Critical:** Backend down, data loss, security incident → immediate triage.
- **High:** Broker disconnect during market hours → manual intervention.
- **Medium:** Dashboard slow, logs full → schedule maintenance.
- **Low:** Non-blocking vulns, bandit findings → backlog.

**Post-incident:** Update this runbook with new scenarios and root causes.
