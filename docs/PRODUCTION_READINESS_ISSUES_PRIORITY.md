# Genesis System3 — Production Readiness Issues (Priority-Based)

**Generated:** 2026-02-28  
**Purpose:** Comprehensive list of issues to fix for production readiness, ordered by priority.

---

## Priority Legend

| P | Level | Definition |
|---|-------|------------|
| **P0** | Critical | Blocks production; must fix before deploy |
| **P1** | High | Security/stability; fix within 1–2 sprints |
| **P2** | Medium | Operations/reliability; fix before scale |
| **P3** | Low | Nice-to-have; backlog |

---

## P0 — Critical (Must Fix)

| # | Issue | Status | Location | Action |
|---|-------|--------|----------|--------|
| 1 | `ds` undefined in bootstrap health.json | ✅ Fixed | `state_sync_service.py:143` | Use `updates.get("data_source", "not_ready")` |
| 2 | pip check fails (wheel vs packaging) | ✅ Fixed | `requirements_runtime.txt` | Pinned `wheel==0.46.2`, `packaging>=24` |
| 3 | Black format failures block CI | ✅ Fixed | Multiple files | Run `black` on lint targets |

---

## P1 — High (Security & Stability)

| # | Issue | Status | Location | Action |
|---|-------|--------|----------|--------|
| 1 | **44 safety vulnerabilities** | ✅ Fixed | 16 packages | Upgraded per remediation table |
| 2 | **pip-audit: 49 vulns in 20 packages** | ✅ Fixed | `requirements_runtime.txt` | aiohttp 3.9.4, requests 2.32.4, cryptography 42.0.4, python-multipart 0.0.22, protobuf 4.25.8, fastapi≥0.109, starlette 0.52+, streamlit 1.37 |
| 3 | **wheel 0.45.1 vulnerable** | ✅ Fixed | `requirements_runtime.txt` | wheel 0.46.2 + packaging 24 + streamlit 1.37 |
| 4 | **torch RCE (torch.load)** | ✅ Fixed | torch 2.10.0 | Upgraded to torch≥2.6 |
| 5 | **lightgbm RCE** | ✅ Fixed | lightgbm 4.6.0 | Upgraded to 4.6.0 |
| 6 | **aiohttp request smuggling** | ✅ Fixed | aiohttp 3.9.4 | Upgraded to 3.9.4 |
| 7 | **python-multipart path traversal** | ✅ Fixed | 0.0.22 | Upgraded to 0.0.22 |
| 8 | **marshmallow DoS** | ✅ Fixed | 3.26.2 | Upgraded to 3.26.2 |

---

## P2 — Medium (Operations & Reliability)

| # | Issue | Status | Location | Action |
|---|-------|--------|----------|--------|
| 1 | **No startup orchestration** | ✅ Fixed | `docker-compose.yml` | Docker Compose for backend + frontend; see docs/DOCKER_ORCHESTRATION.md |
| 2 | **No centralized error logging** | ✅ Fixed | `structured_logging.py` | JSON to logs/backend.jsonl; loguru rotation 10MB/7d |
| 3 | **No monitoring/alerting** | ✅ Fixed | `/metrics` | Prometheus text format; uptime, request count |
| 4 | **No log rotation** | ✅ Fixed | `scripts/log_rotation.ps1` | Daily rotation; retain 7 days |
| 5 | **npm ci/build EPERM failures** | Intermittent | QA script | File in use (rollup.node); close editors/processes; or make npm steps fully optional |
| 6 | **Frontend chunk > 500KB** | ✅ Fixed | `vite.config.ts` | manualChunks for vendor-react, vendor-charts, vendor-utils |
| 7 | **Broker position reconciliation TODO** | ✅ Fixed | `position_reconciliation.py`, `broker.py` | Implemented get_positions(); broker position fetch |
| 8 | **Signal engine TODOs** | ✅ Fixed | `system3_signal_engine.py` | _get_execution_state() from positions_live.json, virtual_orders |
| 9 | **No health check dependency validation** | ✅ Fixed | `/api/health` | Added `dependencies` (broker, db, outputs_dir writable) |
| 10 | **Pre-commit can block/slow** | ✅ Fixed | `docs/PRE_COMMIT_AGENT_POLICY.md` | Documented agent policy for lighter CI runs |

---

## P3 — Low (Backlog)

| # | Issue | Status | Location | Action |
|---|-------|--------|----------|--------|
| 1 | **Regime classifier TODO** | Open | `system3_phase79_adaptive_thresholds.py:68` | Use actual regime classifier from Phase 14/46/49 |
| 2 | **DEBUG logging in production** | Open | `system3_phase390_smote_balancing.py`, `data_balancing_v2.py` | Set log level via env (e.g. `LOG_LEVEL=INFO`) |
| 3 | **DEBUG print statements** | Open | `smart_live_chain_runner.py` | Remove or gate behind `--verbose` |
| 4 | **Legacy venv references** | Partial | Some `.bat` files | Standardize on `.venv`; update remaining scripts |
| 5 | **Streamlit vs React** | Info | Two dashboards | Document which is primary; consider deprecating Streamlit |
| 6 | **safety command deprecated** | ✅ Fixed | Run-FullQA.ps1 | Migrated to `safety scan`; fallback to `safety check` |

---

## Remediation Table (P1 Security)

| Package | Current | Fix Version | Risk |
|---------|---------|-------------|------|
| aiohttp | 3.9.3 | 3.9.4 / 3.12.14 | Request smuggling, XSS |
| cryptography | 41.0.7 | 42.0.4 | PKCS12/OpenSSL |
| requests | 2.31.0 | 2.32.4 | TLS, .netrc leak |
| python-multipart | 0.0.6 | 0.0.22 | Path traversal, ReDoS |
| protobuf | 4.25.3 | 4.25.8 | Recursion DoS |
| fastapi | 0.104.1 | 0.109.1 | ReDoS with multipart |
| starlette | 0.27.0 | 0.47.2 | Form DoS |
| streamlit | 1.31.0 | 1.37.0 | Path traversal (Windows) |
| marshmallow | 3.20.1 | 3.26.2 | DoS |
| lightgbm | 4.3.0 | 4.6.0 | RCE |
| torch | 2.2.1 | 2.6.0+ | RCE (torch.load) |
| wheel | 0.45.1 | 0.46.2 | Path traversal (conflicts streamlit) |

---

## Verification Commands

```powershell
# P0/P1 checks
pip check
black --check core scripts tools phases dashboard
Run-FullGovernance.ps1
Run-FullQA.ps1

# Backend
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing

# Frontend
cd dashboard\frontend; npm run build
```

---

## Summary

| Priority | Count | Resolved |
|----------|-------|----------|
| P0 | 3 | 3 |
| P1 | 8 | 8 |
| P2 | 10 | 9 |
| P3 | 6 | 1 |

**P1.5 (2026-02-28):** Additional upgrades applied: aiohttp 3.13.3, cryptography 46.0.5, dash 2.18.2, scikit-learn 1.7.2.

**P1.6 (2026-02-28):** pip-audit vuln fixes: duckdb≥1.1, pyarrow≥17, pillow≥12.1.1, streamlit≥1.40.

**Remaining accepted risks (blocked by tensorflow 2.15 / dash 2.x):**
- werkzeug 3.0.6, flask 3.0.3 (dash 2.x requires Flask<3.1, Werkzeug<3.1)
- keras 2.15 (tensorflow 2.15 pins it)
- protobuf 4.25.8 (tensorflow pins it)

**Next actions:** P2 orchestration and monitoring in place. P3 backlog: regime classifier, DEBUG logging, venv standardization.
