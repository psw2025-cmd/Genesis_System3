# Dhan-Only Migration Audit Report

**Date:** 2026-06-12  
**Verdict:** PARTIAL → PASS (all active runtime paths are Dhan-only; Angel/SmartAPI code is disabled shim or docs-only)

---

## Summary

System3 has been fully migrated to Dhan-only broker mode. No active runtime path
installs, imports, or invokes SmartAPI or Angel One broker functionality.

---

## A. Backend

| File | Status | Notes |
|------|--------|-------|
| `dashboard/backend/app.py` | ✅ PASS | Dhan-only; py_compile OK |
| `dashboard/backend/requirements.txt` | ✅ PASS | `dhanhq>=2.2.0`; no SmartAPI |

---

## B. Active Entrypoints — py_compile Results

All 13 target files pass `python -m py_compile`.

| File | py_compile | Import smoke |
|------|-----------|--------------|
| `run_system3.py` | ✅ PASS | ✅ PASS |
| `system3_ultra.py` | ✅ PASS | ✅ PASS |
| `scripts/run_live_chain.py` | ✅ PASS | ✅ PASS |
| `scripts/connectivity_probe.py` | ✅ PASS | ✅ PASS |
| `src/angel/live_chain_ws.py` | ✅ PASS | ✅ PASS |
| `src/angel/live_chain_rest.py` | ✅ PASS | ✅ PASS |
| `core/brokers/angel_one/broker.py` | ✅ PASS | ✅ PASS |
| `core/engine/angel_options_watch.py` | ✅ PASS | — |
| `core/engine/angel_options_watch_loop.py` | ✅ PASS | — |
| `core/engine/auto_fetch_option_chain_hourly.py` | ✅ PASS | — |
| `core/engine/fetch_all_indices_option_chain.py` | ✅ PASS | — |
| `core/engine/ultra_live_signals_shadow.py` | ✅ PASS | — |
| `core/validation/option_chain_validator.py` | ✅ PASS | — |

---

## C. Classification of Remaining Angel Code

| File | Classification |
|------|---------------|
| `core/brokers/angel_one/broker.py` | **Disabled shim** — imports succeed; instantiation raises RuntimeError |
| `src/angel/live_chain_ws.py` | **Disabled shim** — no SmartApi import; LiveChainWebSocket raises on instantiation |
| `src/angel/live_chain_rest.py` | **Disabled at runtime** — uses AngelOneBroker shim which raises on use |
| `core/engine/angel_*.py` | **Archived in place** — not in any active menu or auto-triggered path |
| `run_system3.py` | **Blocked with proof** — show_menu() replaced with DISABLED notice; main() exits only |

---

## D. Menu Cleanup

| Script | Status |
|--------|--------|
| `run_system3.py` | ✅ `show_menu()` replaced with DISABLED notice pointing to system3_ultra.py |
| `system3_ultra.py` | ✅ Options 4-50 replaced with `[DISABLED]` notice in menu; handler returns False for 4-50 |

---

## E. SmartAPI Import Status

| Module | Status |
|--------|--------|
| `src/angel/live_chain_ws.py` | ✅ No `from SmartApi` at module level — fully replaced with disabled shim |
| All other active files | ✅ No SmartAPI imports |

### Import smoke test results:
```
src.angel.live_chain_ws: OK (LiveChainWebSocket = <class>)
src.angel.live_chain_rest: OK (LiveChainREST = <class>)
core.brokers.angel_one.broker: OK (AngelOneBroker = <class>)
AngelOneBroker() instantiation: PASS — raises RuntimeError as expected
```

---

## F. Workflow Trigger Matrix

| Workflow | Triggers | SmartAPI ref | Notes |
|----------|----------|-------------|-------|
| `main.yml` | push, workflow_dispatch | none | CI read-only |
| `ci.yml` | push, pull_request, workflow_dispatch | none | installs requirements-ci.txt |
| `qa.yml` | push, pull_request, schedule, workflow_dispatch | none | installs dhanhq |
| `render-cli-deploy.yml` | push, workflow_dispatch | none | real deploy |
| `render-inject-dhan-env.yml` | push (DEPLOY_REFRESH_TRIGGER.md), workflow_dispatch | none | Dhan env injection |
| `cleanup-generated-files.yml` | workflow_dispatch only | none | manual |
| `patch-render-root-and-smartapi.yml` | workflow_dispatch only | none | manual |
| `run-backend-root-url-patcher.yml` | workflow_dispatch only | none | manual |
| `system3-master-status-publisher.yml` | workflow_dispatch only | grep pattern in report string (docs) | manual |
| `entrypoint-classification.yml` | workflow_dispatch only | regex pattern string (classification tool) | manual |
| All others | workflow_dispatch or schedule | none | no active SmartAPI usage |

**No workflow installs SmartAPI.** The two SmartAPI references found are in:
1. A regex pattern string used to classify files (not an install)
2. A fallback key name in a dict lookup for reporting (not an install)

---

## G. Verdict

**PASS** — All criteria met:

- ✅ No active runtime path uses Angel One / SmartAPI
- ✅ No master menu exposes active Angel One broker/data/trading options
- ✅ No workflow installs or invokes SmartAPI
- ✅ Remaining Angel code classified: shim (disabled) or archived in place
- ✅ All py_compile checks pass
- ✅ Import smoke tests pass (no module-level crash)
- ✅ Live trading remains disabled
- ✅ .env, secrets, DB, model artifacts untouched

---

## Files Modified in This Audit

1. `core/brokers/angel_one/broker.py` — replaced with disabled shim
2. `src/angel/live_chain_ws.py` — replaced with disabled shim (no SmartApi import)
3. `src/angel/live_chain_rest.py` — disabled at runtime via AngelOneBroker shim
4. `run_system3.py` — show_menu() and main() replaced with disabled stubs
5. `system3_ultra.py` — options 4-50 DISABLED in menu + handler guard added
6. `scripts/connectivity_probe.py` — rewritten to probe Dhan only
7. `scripts/run_live_chain.py` — pytz guarded; shim imports only
8. `.github/workflows/restore-backend-app-once.yml` — deleted
9. `.github/workflows/cleanup-generated-files.yml` — manual-only
10. `.github/workflows/patch-render-root-and-smartapi.yml` — manual-only
11. `.github/workflows/run-backend-root-url-patcher.yml` — manual-only
12. `.github/workflows/system3-master-status-publisher.yml` — manual-only
13. `.github/workflows/render-inject-dhan-env.yml` — removed self-trigger

---

*Generated by Claude Code Dhan-only migration audit — 2026-06-12*
