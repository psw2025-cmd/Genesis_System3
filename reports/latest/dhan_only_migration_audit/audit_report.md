# Dhan-Only Migration Audit Report — Full End-to-End Verification

**Date:** 2026-06-12 (re-verified pass 2)  
**Verdict: PASS** — No active runtime path uses Angel One / SmartAPI.

---

## Summary

Full end-to-end re-verification sweep across all Python files, workflow files,
menu handlers, and import paths. All active Angel/SmartAPI broker paths are
disabled. Every remaining reference either:
- Is in the `archive/` directory (excluded)
- Is a docs/reporting string (not an import or call)
- Is a disabled shim that raises `RuntimeError` on instantiation
- Is dead code guarded by `if False:` or an early `return`

---

## A. Backend

| File | Status |
|------|--------|
| `dashboard/backend/app.py` | ✅ PASS — Dhan-only, py_compile OK |
| `dashboard/backend/requirements.txt` | ✅ PASS — `dhanhq>=2.2.0`, no SmartAPI |

---

## B. Critical Shim Files

| File | Module-level import | Instantiation result |
|------|--------------------|--------------------|
| `core/brokers/angel_one/broker.py` | ✅ No SmartApi import | Raises `RuntimeError` |
| `src/angel/live_chain_ws.py` | ✅ No SmartApi import | Raises `RuntimeError` |
| `src/angel/live_chain_rest.py` | ✅ Uses shim only | Fails at runtime via shim |

---

## C. Active Entrypoints — py_compile + Import Smoke

All files pass `python -m py_compile`. Import smoke results:

| Module | Import | Notes |
|--------|--------|-------|
| `src.angel.live_chain_ws` | ✅ OK | Full disabled shim |
| `src.angel.live_chain_rest` | ✅ OK | Uses AngelOneBroker shim |
| `core.brokers.angel_one.broker` | ✅ OK | Disabled shim |
| `core.engine.ultra_live_signals_shadow` | ✅ OK | numpy/joblib guarded |
| `system3_ultra_runtime_loops` | ✅ OK | live_signal_loop disabled |
| `scripts.connectivity_probe` | ✅ OK | Dhan-probe rewrite |

Verified behaviour:
- `AngelOneBroker()` → raises `RuntimeError: Angel One / SmartAPI broker path is disabled`
- `LiveChainWebSocket()` → raises `RuntimeError: LiveChainWebSocket is disabled`
- `run_ultra_live_shadow_once()` → returns `{"status": "DISABLED"}` immediately
- `live_signal_loop()` → prints DISABLED notice and returns

---

## D. Menu Cleanup — system3_ultra.py

| Options | Status | Notes |
|---------|--------|-------|
| 1-3 | ✅ Active (core/health/data) | No Angel One dependency |
| 4-50 | ✅ DISABLED in menu + handler | `_ANGEL_BASELINE_CHOICES` guard |
| 51-64 | ✅ DISABLED in menu + handler | `_ANGEL_LEARNING_CHOICES` guard |
| 65-72 | ✅ DISABLED in menu + handler | `_ANGEL_OBSERVABILITY_CHOICES` guard |
| 73-79 | ✅ Active (ultra shadow/features) | No direct Angel broker |
| 80 | ✅ DISABLED in menu + handler | `ultra_live_signals_shadow` uses Angel broker |
| 81-83 | ✅ Active (trade sim/pnl/promo) | No direct Angel broker |
| 84-117 | ✅ Active (ultra phases) | No direct Angel broker |
| 118+ | ✅ Active (GENI phases) | No direct Angel broker |

---

## E. run_system3.py

`show_menu()` replaced with DISABLED notice — no options displayed.  
`main()` only accepts "0) Exit". All Angel One dispatch (choices 1-107) removed.

---

## F. system3_ultra_runtime_loops.py

| Option | Status |
|--------|--------|
| 1) Live Signal Loop | ✅ DISABLED — `live_signal_loop()` prints disabled notice and returns |
| 2-4 | ✅ Active (audit/snapshot/health) |

---

## G. SmartApi Import Sweep (full repo, excluding archive/)

```
Unguarded 'from SmartApi' or 'import SmartApi': NONE FOUND
```

Two SmartAPI string references in workflows — both in regex/reporting patterns, not installs:
- `entrypoint-classification.yml` — regex pattern string for classification
- `system3-master-status-publisher.yml` — fallback key name in dict lookup

---

## H. Workflow Trigger Matrix

| Workflow | Auto-triggers | SmartAPI install |
|----------|--------------|-----------------|
| `main.yml` | push | ❌ none |
| `ci.yml` | push, PR | ❌ none (installs requirements-ci.txt) |
| `qa.yml` | push, PR, schedule | ❌ none (installs dhanhq) |
| `render-cli-deploy.yml` | push | ❌ none |
| `render-inject-dhan-env.yml` | push on DEPLOY_REFRESH_TRIGGER.md | ❌ none |
| All others | workflow_dispatch only | ❌ none |

**No workflow installs SmartAPI.** Confirmed across all 33 workflow files.

---

## I. Remaining Angel Code Classification

| File | Classification |
|------|---------------|
| `archive/root_clutter/*.py` | **Archive** — excluded from audit |
| `core/engine/angel_*.py` | **Archived in place** — disabled menus (4-72) can't call them; all use shim |
| `scripts/start_real_live_trading.py` | **Fail-closed standalone** — not in any menu; fails at import (missing pytz) then at AngelOneBroker (shim) |
| `scripts/test_greeks_*.py`, `scripts/verify_*.py` | **Standalone test scripts** — not in any menu; fail at AngelOneBroker() via shim |
| `core/engine/ultra_live_signals_shadow.py` | **Disabled in-place** — function returns DISABLED; option 80 handler blocked |
| `option_chain_automation_master.py` | **Not in any active menu** — AngelOneBroker() inside try/except; shim raises at runtime |

---

## J. Files Modified (this audit)

| File | Change |
|------|--------|
| `core/brokers/angel_one/broker.py` | Disabled shim (prior session) |
| `src/angel/live_chain_ws.py` | Full disabled shim (prior session) |
| `src/angel/live_chain_rest.py` | Disabled at runtime via shim (prior session) |
| `run_system3.py` | show_menu()+main() replaced with DISABLED stubs |
| `system3_ultra.py` | Options 4-72 disabled in menu+handler; option 80 blocked |
| `system3_ultra_runtime_loops.py` | live_signal_loop() disabled; option 1 shows DISABLED |
| `core/engine/ultra_live_signals_shadow.py` | run_ultra_live_shadow_once() returns DISABLED immediately; numpy/joblib guarded |
| `scripts/connectivity_probe.py` | Rewritten to probe Dhan only |
| `scripts/run_live_chain.py` | pytz guarded; shim imports (prior session) |
| `reports/latest/dhan_only_migration_audit/audit_report.md` | This report |

---

## Verdict: PASS

All criteria from the mandatory audit scope are met:

- ✅ No active runtime path uses Angel One / SmartAPI (all blocked at menu level or return DISABLED)
- ✅ No master menu exposes active Angel One broker/data/trading options (options 4-72, 80 disabled)
- ✅ No workflow installs SmartAPI
- ✅ All remaining Angel code classified: shim / archived-in-place / blocked-with-proof
- ✅ py_compile PASS on all 14 target files
- ✅ Import smoke tests PASS (all 6 tested modules import clean)
- ✅ Shim guards verified: AngelOneBroker() raises, LiveChainWebSocket() raises, ultra shadow returns DISABLED
- ✅ Live trading remains disabled
- ✅ .env, secrets, DB, model artifacts untouched

*Generated by Claude Code Dhan-only migration audit — 2026-06-12 (pass 2)*
