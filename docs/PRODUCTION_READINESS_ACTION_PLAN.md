# Genesis System3 — Production Readiness Action Plan

**Generated:** 2026-02-28  
**Status:** Verified and applied

---

## Executive Summary

This document provides a step-by-step action plan for verifying and hardening the Genesis System3 system to production grade. All steps have been executed; fixes applied are documented below.

---

## 1. Project Architecture

| Component | Entry Point | Port | Purpose |
|-----------|-------------|------|---------|
| **Trading System** | `option_chain_automation_master.py` | — | Fetches data, runs strategy, writes outputs |
| **Backend API** | `dashboard/backend/app.py` | 8000 | FastAPI, SSOT, state sync, WebSocket |
| **Frontend** | `dashboard/frontend/` | 3000 | React/Vite, connects to backend |
| **Streamlit** | `dashboard/app.py` | 8501 | Legacy dashboard (optional) |

**Data Flow:**
```
Trading System → outputs/health.json, chain_raw_live.csv, etc.
       ↓
State Sync Service (every 5s) → SSOT (runtime_state_store)
       ↓
Backend /api/state, /api/health → Frontend
```

---

## 2. Step-by-Step Verification Order

### Step 1: Environment & Dependencies ✅

**Actions:**
- Verify Python 3.10: `py -3.10 --version` or `.venv\Scripts\python.exe --version`
- Verify venv: `Test-Path .venv\Scripts\python.exe`
- Run `pip check` — must pass

**Fix applied:** Pinned `wheel==0.45.1` in `requirements_runtime.txt` to resolve conflict with `packaging==23.2` (streamlit 1.31 requires packaging<24; wheel 0.46.x requires packaging>=24).

**Verification:**
```powershell
cd c:\Genesis_System3
.venv\Scripts\pip.exe check
# Expected: No broken requirements found.
```

---

### Step 2: Bug Fixes ✅

**Bug 1 — `ds` undefined in state_sync_service.py (FIXED)**

- **Issue:** Variable `ds` used in bootstrap health.json block (line 143) but only defined if market block (lines 57–96) runs successfully. If that block raises, `ds` is undefined → NameError → silently swallowed.
- **Fix:** Replace `ds` with `updates.get("data_source", "not_ready")` in bootstrap block.
- **File:** `dashboard/backend/state_sync_service.py`

---

### Step 3: Backend Startup & Health API ✅

**Actions:**
- Start backend: `cd dashboard\backend && ..\..\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000`
- Test: `Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing`
- Test: `Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/state" -UseBasicParsing`

**Verification:** Both endpoints return 200 with valid JSON.

---

### Step 4: Frontend Build ✅

**Actions:**
- `cd dashboard\frontend && npm run build`
- Verify `dist/` created

**Verification:** Build completes; `dist/index.html` and `dist/assets/*` exist.

---

### Step 5: State Sync & API Integration ✅

**Actions:**
- Backend running; state sync service syncs from `outputs/` every 5s
- `/api/state` returns SSOT (data_source, broker, market, qc, positions, pnl)
- Frontend fetches `/api/state` and `/api/perf`

**Verification:** `/api/state` returns `state_version`, `data_source`, `broker`, `market`, etc.

---

### Step 6: QA & Governance ✅

**Actions:**
- Run `Run-FullGovernance.ps1` — must exit 0
- Run `Run-FullQA.ps1` — must exit 0

**Fixes applied:**
- `wheel==0.45.1` pin (pip check)
- `black` format on `tools/chart_test_script.py`, `dashboard/backend/state_sync_service.py`, `dashboard/backend/app.py`

**Verification:** Both scripts complete with "PASS" or equivalent.

---

### Step 7: Code Quality ✅

**Actions:**
- `black --check core scripts tools phases dashboard` — pass
- `flake8` on lint targets — pass
- `pytest` — pass (core, tools, phases, dashboard)

---

## 3. Production Checklist

| # | Item | Status |
|---|------|--------|
| 1 | Python 3.10 venv | ✅ |
| 2 | pip check passes | ✅ |
| 3 | Backend starts, /api/health OK | ✅ |
| 4 | Backend /api/state OK | ✅ |
| 5 | Frontend builds | ✅ |
| 6 | state_sync_service ds bug fixed | ✅ |
| 7 | wheel/packaging conflict resolved | ✅ |
| 8 | Black format pass | ✅ |
| 9 | Governance script pass | ✅ |
| 10 | QA script pass | ✅ |

---

## 4. Startup Commands (Production)

**Backend:**
```powershell
cd c:\Genesis_System3\dashboard\backend
c:\Genesis_System3\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

**Frontend (dev):**
```powershell
cd c:\Genesis_System3\dashboard\frontend
npm run dev
```

**Full system (Run-All.bat):**
- Runs governance, QA, then starts backend, Streamlit, React frontend.

---

## 5. Known Issues & Deferred Items

| Issue | Status | Notes |
|-------|--------|-------|
| 44 safety vulnerabilities | Report-only | Logged to `logs/inspector/safety_report.txt`; remediation may require major upgrades |
| pip-audit vulnerabilities | Report-only | Logged to `logs/inspector/pip_audit.json` |
| wheel 0.45.1 vs 0.46.2 | Accepted | wheel 0.46.2 requires packaging>=24; streamlit needs packaging<24 |
| Chunk size > 500KB (frontend) | Info | Vite build warning; consider code-splitting |

---

## 6. Files Modified

| File | Change |
|------|--------|
| `dashboard/backend/state_sync_service.py` | `ds` → `updates.get("data_source", "not_ready")` |
| `requirements_runtime.txt` | Added `wheel==0.45.1` |
| `tools/chart_test_script.py` | Black format |
| `dashboard/backend/app.py` | Black format |

---

## 7. Next Steps (Optional)

1. **Trading system test:** Run `option_chain_automation_master.py --sim --cycles 1` to verify outputs written.
2. **Docker:** Add Docker Compose for orchestrated startup.
3. **Monitoring:** Add Prometheus metrics, health check alerts.
4. **Security:** Plan upgrade batch for pip-audit/safety vulnerabilities.
