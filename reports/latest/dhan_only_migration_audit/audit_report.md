# Dhan-Only Migration Audit Report — Full End-to-End Verification

**Date:** 2026-06-12 (pass 3 — final clean sweep)  
**Verdict: PASS** — No active runtime path uses Angel One / SmartAPI.

---

## Summary

Full end-to-end sweep across all Python files, workflow files, menu handlers, and
import paths. All Angel/SmartAPI broker paths are disabled. Every remaining
reference either:
- Is in the `archive/legacy_angel_one/` directory (excluded from active code)
- Is a docs/reporting string (not an import or call)
- Is a disabled shim that raises `RuntimeError` on instantiation
- Is a commented-out placeholder (not active code)
- Is a shim-presence check in diagnostic/validation files

### Mandatory Verification Greps (pass 3 — final)

```
GREP 1 — active AngelOneBroker instantiation (excluding archive/, reports/):
  NONE FOUND
  Result: PASS ✅ (zero results)

GREP 2 — active AngelOneBroker import (excluding archive/, reports/):
  scripts/connectivity_probe.py:41  →  ALLOWED — explicit shim-presence check inside try/except
  Result: PASS ✅ (one result, matches carve-out exception: shim validation probe)

GREP 3 — module-level SmartApi imports (excluding archive/, reports/):
  NONE FOUND
  Result: PASS ✅ (zero results)
```

Notes on GREP 2 remaining hit:
- `connectivity_probe.py:41` — Comment block reads "Angel One broker shim (should import cleanly, raise only on use)".
  Import is inside `try/except`, used only to confirm the disabled shim is importable without crashing.
  This is the "shim validation" exception per audit mandate.

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
| `src/angel/live_chain_rest.py` | ✅ No AngelOneBroker import — uses `Any` type hint | Constructor takes external broker arg; never instantiates broker itself |

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
| `core.validation.option_chain_validator` | ✅ OK | Disabled shim |

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

## I. File-by-File Classification (All 18 Flagged Files + Additional)

| File | Classification | Action Taken |
|------|---------------|-------------|
| `core/brokers/angel_one/broker.py` | **Disabled shim** — defines shim only, raises RuntimeError on instantiation | Converted to disabled shim (prior session) |
| `src/angel/live_chain_ws.py` | **Disabled shim** — no SmartApi import; raises RuntimeError | Converted to disabled shim (prior session) |
| `src/angel/live_chain_rest.py` | **Disabled at runtime** — AngelOneBroker import removed; uses `Any` type hint; broker arg never instantiated here | AngelOneBroker import removed (pass 3 final) |
| `validate_option_chain_system.py` | **ARCHIVED** — validated the old Angel One system; unreferenced by any active file | `git mv` to `archive/legacy_angel_one/` |
| `scripts/connectivity_probe.py` | **Shim-presence check** — imports AngelOneBroker to confirm shim; probes Dhan only | Rewritten to Dhan-only probe |
| `run_system3.py` | **Legacy menu disabled** — show_menu() shows DISABLED; main() accepts only "0) Exit" | Replaced menu+dispatch |
| `system3_ultra.py` | **Active entrypoint; Angel options guarded** — options 4-72, 80 blocked at display+handler | Guard sets added |
| `system3_ultra_runtime_loops.py` | **live_signal_loop() disabled** — prints DISABLED notice and returns immediately | Function body replaced |
| `core/engine/ultra_live_signals_shadow.py` | **Disabled shim** — run_ultra_live_shadow_once() returns DISABLED immediately | Full 237-line body replaced |
| `option_chain_automation_master.py` | **Disabled shim** — class raises RuntimeError on init; run/start/main all raise | Converted (2254→25 lines) |
| `core/validation/option_chain_validator.py` | **Disabled shim (interface preserved)** — broker init raises RuntimeError; static validate_dataframe kept | Converted to disabled shim |
| `scripts/run_live_chain.py` | **Guarded** — raises RuntimeError for non-sim_mode; sim_mode path does not use broker | RuntimeError guard added |
| `scripts/comprehensive_end_to_end_verification.py` | **Guarded** — verify_index_fetch() returns DISABLED immediately | Returns DISABLED directly |
| `core/engine/angel_monday_diagnostic.py` | **Guarded** — broker check hardcoded to DISABLED/unavailable | Broker block replaced |
| `core/engine/system3_phase205_broker_selftest.py` | **Guarded** — writes DISABLED_DHAN_ONLY status to file; no broker instantiation | Broker block replaced |
| `scripts/production_readiness_check.py` | **Fixed** — AngelOneBroker import removed from check_imports() | Import line removed |
| `core/engine/angel_executor_live_prep.py` | **ARCHIVED** — pure Angel One live-order executor; commented-out broker lines still matched GREP 1/2; unreferenced by any active file | `git mv` to `archive/legacy_angel_one/core_engine/` |
| `core/engine/angel_automation_config.py` | **Retained active (safety config)** — provides AUTOMATION_CONFIG/DRY_RUN safety gates used by system3_ultra.py and 15+ other active files; does not import Angel broker | No change needed |

### 14 Files Archived via `git mv` to `archive/legacy_angel_one/`

**`archive/legacy_angel_one/core_engine/`:**
- `angel_options_watch.py`
- `angel_options_watch_loop.py`
- `angel_executor_live_prep.py` *(added pass 3 final)*
- `auto_fetch_option_chain_hourly.py`
- `fetch_all_indices_option_chain.py`
- `test_angelone_api.py`
- `test_angelone_option_chain.py`

**`archive/legacy_angel_one/scripts/`:**
- `start_real_live_trading.py`
- `test_greeks_calculation.py`
- `test_greeks_api.py`
- `verify_all_columns_fetched.py`
- `verify_parallel_processing.py`
- `debug_greeks_calculation.py`

**`archive/legacy_angel_one/` (root):**
- `validate_option_chain_system.py` *(added pass 3 final)*

---

## J. Files Modified (this audit — pass 3)

| File | Change |
|------|--------|
| `core/brokers/angel_one/broker.py` | Disabled shim (prior session) |
| `src/angel/live_chain_ws.py` | Full disabled shim (prior session) |
| `src/angel/live_chain_rest.py` | AngelOneBroker import removed; uses `Any` type hint (pass 3 final) |
| `run_system3.py` | show_menu()+main() replaced with DISABLED stubs |
| `system3_ultra.py` | Options 4-72 disabled in menu+handler; option 80 blocked; options 51-80 guards added |
| `system3_ultra_runtime_loops.py` | live_signal_loop() disabled; option 1 shows DISABLED |
| `core/engine/ultra_live_signals_shadow.py` | run_ultra_live_shadow_once() returns DISABLED immediately; numpy/joblib guarded |
| `scripts/connectivity_probe.py` | Rewritten to probe Dhan only |
| `scripts/run_live_chain.py` | Angel broker init replaced with RuntimeError for non-sim_mode |
| `scripts/comprehensive_end_to_end_verification.py` | verify_index_fetch() returns DISABLED; AngelOneBroker import removed |
| `core/engine/angel_monday_diagnostic.py` | Broker check hardcoded DISABLED |
| `core/engine/system3_phase205_broker_selftest.py` | Broker block writes DISABLED_DHAN_ONLY |
| `option_chain_automation_master.py` | Converted to disabled shim (25 lines) |
| `core/validation/option_chain_validator.py` | Converted to disabled shim (broker init raises RuntimeError) |
| `scripts/production_readiness_check.py` | AngelOneBroker import removed from check_imports() |
| `archive/legacy_angel_one/core_engine/` | 7 files archived via git mv (6 prior + angel_executor_live_prep.py) |
| `archive/legacy_angel_one/scripts/` | 6 files archived via git mv |
| `archive/legacy_angel_one/validate_option_chain_system.py` | Archived via git mv (pass 3 final) |
| `reports/latest/dhan_only_migration_audit/audit_report.md` | This report |

---

## Verdict: PASS

All criteria from the mandatory audit scope are met:

- ✅ No active non-archive file instantiates AngelOneBroker
- ✅ No active non-archive script imports AngelOneBroker except acceptable shim validation/report files
- ✅ All old Angel operational files archived, disabled, or replaced with Dhan
- ✅ Proof report includes file-by-file classification (section I above)
- ✅ No workflow installs SmartAPI
- ✅ py_compile PASS on all 15 target files (pass 3)
- ✅ Import smoke tests PASS (all 7 tested modules import clean)
- ✅ Shim guards verified: AngelOneBroker() raises, LiveChainWebSocket() raises, ultra shadow returns DISABLED
- ✅ Live trading remains disabled
- ✅ .env, secrets, DB, model artifacts untouched

*Generated by Claude Code Dhan-only migration audit — 2026-06-12 (pass 3 final)*
