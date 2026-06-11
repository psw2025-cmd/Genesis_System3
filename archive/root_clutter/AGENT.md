# Cursor Agent – Start Here

Read this first when working on Genesis System3 as the Cursor agent.

## Phase-wise and batch work

- **Phase-wise (safe, additive):**  
  `docs/MASTER PLAN — PHASE-WISE INSTRUCTIONS FOR CURSOR AGENT.txt`
- **Phase 7–9 (real data, blended training, live beta DRY-RUN):**  
  `docs/system3_phase7_9_next_steps_for_cursor_agent.md`
- **Batch 4 modules (market intelligence, action layer, safety):**  
  `docs/cursor_agent_batch4_instructions.md`

## Behavior and rules

- **Master instruction (workflow, editing, safety):**  
  `docs/GENESIS_VSCODE_AGENT_MASTER_INSTRUCTION.md`
- **Project rules (auto-loaded by Cursor):**  
  `.cursorrules` in repo root

## Environment

- **Python:** Use project venv at **`.venv`** (Python 3.10).  
  Activate: `\.venv\Scripts\activate` (PowerShell) or `call .venv\Scripts\activate.bat` (cmd).
- **Root path:** `C:\Genesis_System3`

## Verification after changes

- **Agent bug checks (after edits):**  
  `python tools/verify_cursor_agent_bugs.py`
- **Dashboard full test (production-grade):**  
  `python scripts/run_dashboard_full_test.py`  
  If any step fails, read `proof/archive/DASHBOARD_FULL_TEST_*.json` and follow `next_actions` (files to fix + commands to rerun) in order.
- **Phase 231–260 proof run (targeted):**  
  `python proof/run_231_260_proof.py`
- **Phases 201–310 orchestrator (production-grade):**  
  `python scripts/run_phase_orchestrator.py [--start START --end END]`  
  On failure, read `proof/archive/PHASE_ORCHESTRATOR_FAIL_*.json` and follow `next_actions`.
- **Dashboard / visual verification (Playwright – no user screenshots):**  
  Ensure backend (8000) and Streamlit (8501) are running, then run  
  `python tools/playwright_dashboard_verification.py`.  
  Read the latest `proof/archive/dashboard_verification_*.json` and summarize for the user: passed/failed, issues, and screenshot paths. Full workflow: `docs/AGENT_DASHBOARD_VERIFICATION_PLAYWRIGHT.md`.

## Viewing charts and dashboards (in Cursor and Chrome)

- **Live URLs:** Streamlit `http://127.0.0.1:8501`, API docs `http://127.0.0.1:8000/docs`.
- **In Cursor:** `Ctrl+Shift+P` → **Simple Browser: Show** → enter URL. Or use **Terminal → Run Task** → “Open Streamlit Dashboard” / “Open all live URLs” (opens in default browser).
- **Full guide:** `docs/VIEW_CHARTS_DASHBOARDS_IN_EDITOR_AND_CHROME.md`

## Requirements and setup

- **What the agent needs, what’s missing, and how to fix it:**  
  `docs/CURSOR_AGENT_REQUIREMENTS_GAPS_AND_SOLUTIONS.md`
- **Production-grade strict fail + sequence (whole project):**  
  `docs/PRODUCTION_GRADE_STRICT_FAIL_AND_SEQUENCE.md` and `docs/PRODUCTION_GRADE_WHOLE_PROJECT_RECOMMENDATIONS.md`
- **Best recommendation (what to install once, run order, optional readiness check):**  
  `docs/BEST_RECOMMENDATION_AGENT_RUN.md`

## When the agent cannot proceed automatically

- If you (the agent) try an automated action **multiple times** and still cannot complete it (tool failure, sandbox restriction, missing local setup, or external precondition), **stop** and switch to a **User Action Plan** instead of looping:
  - Clearly list: **what** the user must do, **why** it is needed, and **how** to do it (commands, scripts, UI steps, file paths).
  - Point to the **relevant proof or logs** (e.g. `proof/archive/*.json`, `logs/`, `storage/`) so the user can see the same evidence.
  - Specify **exactly which command/script you will run next** after the user completes those steps (for example: “after you finish steps 1–3, I will rerun `Run-All.bat` then `python scripts/run_dashboard_full_test.py`”).
- Always align this with the production-grade sequence (Run-All → dashboard full test → phase orchestrator), so that once the user has done their part, you can continue in a **predictable, gap-free order**.
