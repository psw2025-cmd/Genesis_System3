# Production-Grade: Proceed When Something Is Missing

**Note:** This project uses **strict** production-grade behaviour: on failure we **stop**, report **reason**, **impact**, and **next actions** (no silent proceed). See **`docs/PRODUCTION_GRADE_STRICT_FAIL_AND_SEQUENCE.md`** for the current behaviour and run order.

---

**Principle (legacy / optional):** The pipeline and verification must **never block** on optional or missing pieces. We **log** (e.g. `[SKIP]` or `[WARN]`) and **proceed** to the next step. Only truly critical failures (e.g. cannot start services at all) should stop the run.

---

## 1. What “Production-Grade” Means Here

- **Do not** stop the whole run because one step failed or something is missing.
- **Do** run every step that can run; for the rest, log clearly and continue.
- **Do** end the run with a clear summary (what ran, what was skipped, what warned).
- **Do** use exit code **0** so downstream systems (CI, scheduler, human) see “success” and can inspect the log for any `[WARN]` / `[SKIP]`.

---

## 2. Where This Is Applied

| Area | Behavior |
|------|----------|
| **Run-All.bat** | Governance, QA, pre-commit, git push, Docker build/push, pip install issues: on failure or missing → log `[WARN]`/`[SKIP]` and proceed. Backend and dashboard are always started. Script ends with `exit /b 0`. |
| **Dashboard / verification scripts** | Use a “proceed” mode or wrapper (e.g. `run_dashboard_full_test.py`): run all checks, write a report, **exit 0** so the pipeline continues. Failures are in the report, not in the exit code. |
| **Agent / docs** | When we say “X is missing”, we also say “proceeding with Y” and never imply “stop everything”. |

---

## 3. Run-All.bat (Concrete)

- **Step 2:** No `.venv` → “No .venv found - will create new”; clean continues.
- **Step 3:** venv creation fails → `[WARN] venv not created - using system Python. Proceeding.`
- **Step 5–6:** pip upgrade or install fails → `[WARN] ... - proceeding.`
- **Step 7–8:** Governance or QA script fails → `[WARN] ... - proceeding.`
- **Step 12:** pre-commit fails or not installed → `[WARN] ... - proceeding.`
- **Step 13:** nothing to commit or push fails → `[SKIP]` / `[WARN] ... - proceeding.`
- **Step 14–15:** No Dockerfile or no GITHUB_TOKEN → `[SKIP] ... - proceeding.` Docker build/push failure → `[WARN] ... - proceeding.`

The script **always** reaches Step 16 (confirmation) and exits with **0**.

---

## 4. Verification Scripts (Proceed Mode)

- **Canonical “run all dashboard tests”:** `scripts/run_dashboard_full_test.py` (see below). It runs backend/frontend checks and optional Playwright; it **exits 0** and writes a summary so the pipeline always proceeds.
- **Other scripts** (e.g. `verify_dashboard_complete.py`, `validate_all.py`): can be run as-is for local “fail fast”; for **production-grade runs** they are invoked via the wrapper that ignores their exit code and reports pass/fail in the summary (exit 0).

---

## 5. Summary

- **Production-grade solution** = something missing or failing does **not** stop the run; we **proceed** and log.
- Run-All.bat and the dashboard full-test runner are aligned with this; use them as the default for automated or one-click runs.
