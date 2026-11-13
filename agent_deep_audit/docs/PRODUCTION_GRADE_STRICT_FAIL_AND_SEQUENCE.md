# Production-Grade: Strict Fail + Reason / Impact / Next Actions (No Gap)

**Principle:** When something **fails**, we **do not proceed**. We **stop**, report **reason**, **impact**, and **next actions** (files/scripts to fix and run in sequence) so you and the agent know exactly what to do. There is **no gap** in the project flow.

---

## 1. What “Production-Grade” Means Here

- **On failure:** STOP (exit non-zero). Do not silently continue.
- **Report:** For each failed step, record:
  - **Reason** — why it failed (from the step or exception).
  - **Impact** — what parts of the system are affected.
  - **Next actions** — which files to correct and which scripts to run next, in sequence.
- **Artifact:** Write a JSON report to `proof/archive/` (e.g. `RUN_ALL_FAIL_*.json`, `DASHBOARD_FULL_TEST_*.json`, `PHASE_ORCHESTRATOR_FAIL_*.json`) so you and the agent can fix and rerun in order.
- **Sequence:** Run steps in a fixed order; later steps may be skipped if a prerequisite failed (e.g. dashboard tests skip API checks if backend is down).

---

## 2. Where This Is Applied

| Area | On failure | Report location | Next (run in sequence after fix) |
|------|------------|------------------|----------------------------------|
| **Run-All.bat** | Stop, call `scripts/run_all_report_fail.py` | `proof/archive/RUN_ALL_FAIL_YYYYMMDD_HHMMSS.json` | Reason/impact/next printed in console; follow next_actions in the JSON. |
| **Dashboard full test** | Exit 1; do not proceed to later steps if a prerequisite failed | `proof/archive/DASHBOARD_FULL_TEST_YYYYMMDD_HHMMSS.json` | Fix files/scripts listed in failed step’s next_actions; rerun `python scripts/run_dashboard_full_test.py`. |
| **Phase orchestrator (201–310)** | Stop at first phase that returns ERROR or raises | `proof/archive/PHASE_ORCHESTRATOR_FAIL_YYYYMMDD_HHMMSS.json` | Fix the phase module (see next_actions); rerun `python scripts/run_phase_orchestrator.py`. |

---

## 3. Run-All.bat (Strict)

- **Step 3 (venv):** If `.venv\Scripts\activate.bat` missing → set env vars, call `python scripts/run_all_report_fail.py` → exit /b 1.
- **Step 5–6 (pip):** If pip upgrade or install fails → report (reason, impact, next_actions) → exit /b 1.
- **Step 7 (Governance):** If `Run-FullGovernance.ps1` fails → report → exit /b 1.
- **Step 8 (QA):** If `Run-FullQA.ps1` fails → report → exit /b 1.
- **Step 12 (pre-commit):** If pre-commit fails → report → exit /b 1.
- **Step 13 (git):** If commit or push fails → report → exit /b 1.
- **Step 14–15 (Docker):** If build or push fails (when attempted) → report → exit /b 1.

No step is “proceed anyway”; each failure produces a report and stops the run.

---

## 4. Dashboard Full Test (Strict)

- **Script:** `scripts/run_dashboard_full_test.py`
- Runs: Backend running, SSOT, synthetic data, risk limits, API endpoints, frontend pages, data consistency; optionally Playwright.
- **On first FAIL:** Writes `proof/archive/DASHBOARD_FULL_TEST_*.json` with `failed_phase` (step name), `reason`, `impact`, `next_actions`; exits 1.
- **If a step is SKIPPED** (e.g. backend down → later steps skipped): recorded in report; overall status FAIL; exit 1.
- **Next:** Fix the files/scripts in `next_actions` for the failed step, then rerun `python scripts/run_dashboard_full_test.py`.

---

## 5. Phase Orchestrator (Strict)

- **Script:** `scripts/run_phase_orchestrator.py`
- Runs: Phases 201–310 (or `--range START END`) in sequence using the same phase imports as `system3_autorun_master_hardened.py`.
- **On first ERROR** (or exception): Writes `proof/archive/PHASE_ORCHESTRATOR_FAIL_*.json` with `failed_phase` (phase number), `reason`, `impact`, `next_actions`; exits 1.
- **Impact** is derived from phase ranges (e.g. 231–240 = virtual orders/trades; 249–255 = LSTM/ML).
- **Next:** Fix the phase module and rerun `python scripts/run_phase_orchestrator.py`.

---

## 6. Recommended Order (No Gap)

Run in this order so the project stays in sequence:

1. **Run-All.bat** — Environment, governance, QA, backend/dashboard start, pre-commit, git, Docker.  
   If it fails → fix using `proof/archive/RUN_ALL_FAIL_*.json` → rerun Run-All.bat.

2. **Dashboard full test** — Backend and frontend are up; verify APIs and pages.  
   If it fails → fix using `proof/archive/DASHBOARD_FULL_TEST_*.json` → rerun `python scripts/run_dashboard_full_test.py`.

3. **Phase orchestrator** — Phases 201–310 in sequence.  
   If it fails → fix using `proof/archive/PHASE_ORCHESTRATOR_FAIL_*.json` → rerun `python scripts/run_phase_orchestrator.py`.

This way you and the agent always know: **what failed**, **what it impacts**, **what to fix**, and **what to run next** — with no gap.
