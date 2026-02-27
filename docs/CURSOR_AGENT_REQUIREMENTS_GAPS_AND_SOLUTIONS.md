# Cursor Agent – Requirements for Full Autonomous Action

**Purpose:** List everything required for the Cursor agent to act fully autonomously on this repo, what is **not** currently in the editor/project setup, and recommended solutions.

---

## 1. What the Cursor Agent Needs for Full Autonomous Action

| Category | Requirement | Why |
|----------|-------------|-----|
| **Project rules** | A single, auto-loaded rules file (e.g. `.cursorrules` or `.cursor/rules`) | Agent must know: Angel-only, no live trading, safe mode, additive-only, where to write (storage/logs/reports). |
| **Python environment** | One consistent venv path and Python version | Agent runs `python`, `pip`, and scripts; must use project venv and correct interpreter. |
| **Terminal permission** | Cursor allowed to run terminal commands in workspace | Without this, agent cannot run `python proof/run_231_260_proof.py`, `pip install`, or verification scripts. |
| **File write permission** | Agent allowed to create/edit files in project | Needed to implement phases, fix bugs, add modules. |
| **Repo context** | Key paths and entry points documented where agent looks | Root path, `run_system3.py`, `storage/`, `logs/`, phase docs so agent does not guess. |
| **Verification script** | Runnable check script (e.g. `tools/verify_cursor_agent_bugs.py`) | Agent can validate changes; must be runnable with project Python. |
| **Phase/spec docs** | Clear, file-based instructions (e.g. MASTER PLAN, Phase 7–9, Batch 4) | Already in `docs/`; agent needs to find them (or have rules point to them). |
| **Optional: extensions** | Python, Pylance, SonarLint, CodeQL if you want in-IDE lint/security | Not strictly required for autonomy; improve feedback. |

---

## 2. What Is NOT in the Current Editor / Project (Gaps)

| # | Missing item | Current state | Impact |
|---|----------------|----------------|--------|
| 1 | **Project rules auto-loaded by Cursor** | No `.cursorrules` or `.cursor/rules` in repo. Instructions live in `docs/GENESIS_VSCODE_AGENT_MASTER_INSTRUCTION.md` and other docs. | Agent may not see “no live trading”, “Angel-only”, “additive-only” unless user pastes or references the doc. |
| 2 | **Single canonical venv name** | `Run-All.bat` and `Run-FullGovernance.ps1` use **`.venv`**. `START_CONTINUOUS_AGENT.bat` and many other `.bat` files use **`venv`**. | If agent (or user) runs scripts expecting `venv`, they fail when only `.venv` exists (or vice versa). |
| 3 | **Cursor workspace settings for agent** | `.cursor/settings.json` only has `cursor-team-kit` enabled. No explicit “allow terminal”, “allow file write”, or “default Python path”. | Depends on Cursor app settings; workspace does not document or enforce them. |
| 4 | **Documented Python version for agent** | Run-All/Run-FullGovernance use **Python 3.10** (`py -3.10 -m venv`). No root-level note that agent should use 3.10 or match project. | Agent might run with system Python 3.14 or wrong venv. |
| 5 | **Extensions list vs Cursor compatibility** | `.cursor/extensions.json` has many recommendations; some IDs (e.g. `ms-vscode.*`) may not exist or differ in Cursor. | “Current editor list” is recommendations only; not all may be installed or available in Cursor. |
| 6 | **Backend/dashboard ports in one place** | `continuous_auto_agent.py` checks backend at 8000 (OK) and dashboard at **8080**. Run-All starts Streamlit on **8501**. | Continuous agent’s dashboard check may always fail; agent or scripts could be confused. |
| 7 | **Entry point for “start here” agent tasks** | No single `AGENT.md` or `README_AGENT.md` at root that says “start here for phase work” and points to MASTER PLAN, Phase 7–9, Batch 4. | Agent must discover docs; no one place that ties phase work to Cursor. |
| 8 | **Pre-commit / hooks vs agent** | Pre-commit runs heavy hooks (safety, bandit, pytest). Not documented whether agent should run pre-commit or skip it. | Unclear if autonomous runs should trigger pre-commit (can block or slow). |
| 9 | **Network/sandbox** | In some environments Cursor agent runs in a sandbox (e.g. no `systeminfo`, limited network). | Agent cannot do full “local machine” or external API checks; only project-local actions. |

---

## 3. Solutions (Concrete)

| Gap | Solution | How |
|-----|----------|-----|
| **1. Project rules** | Add Cursor rules so the agent always sees project rules. | Create **`.cursorrules`** in repo root (or add under `.cursor/rules/`) with: Angel-only, no live trading, safe/additive-only, key paths, and “read before change”. Optionally: “For full instructions see `docs/GENESIS_VSCODE_AGENT_MASTER_INSTRUCTION.md` and `docs/MASTER PLAN — PHASE-WISE INSTRUCTIONS FOR CURSOR AGENT.txt`.” |
| **2. Single venv name** | Standardize on one venv directory. | **Recommendation:** Use **`.venv`** everywhere (matches Run-All and Run-FullGovernance). Update `START_CONTINUOUS_AGENT.bat` and any other scripts that reference `venv` to use `.venv`, or add a one-line note in a root README: “This project uses `.venv`; scripts under `scripts/` and Run-All use `.venv`.” So agent (and humans) know to activate `.venv`. |
| **3. Workspace settings** | Document what Cursor should allow. | Add a short **`docs/CURSOR_SETUP.md`** (or section in main README): “For full agent autonomy: enable terminal and file write in Cursor; optional: set Python interpreter to `C:\Genesis_System3\.venv\Scripts\python.exe`.” No need to change Cursor binary; just document. |
| **4. Python version** | Document for agent and scripts. | In `.cursorrules` or `docs/CURSOR_SETUP.md`: “Use Python 3.10 for this project; venv is at `.venv` and created with `py -3.10 -m venv .venv`.” |
| **5. Extensions** | Clarify what’s actually needed for agent. | Keep `extensions.json` as recommendations. Add a line in `docs/CURSOR_AGENT_REQUIREMENTS_GAPS_AND_SOLUTIONS.md`: “For agent-only autonomy, no extensions are required. For better lint/security in editor: install Python, Pylance, and optionally SonarLint/CodeQL if available in Cursor.” |
| **6. Dashboard port** | Align port with Run-All. | In `scripts/continuous_auto_agent.py`, change dashboard URL check from port **8080** to **8501** (Streamlit as started by Run-All), or make port configurable via env/config. |
| **7. Agent entry point** | One “start here” file. | Add **`AGENT.md`** at repo root: “For Cursor agent: read this first. Phase-wise work: see `docs/MASTER PLAN — PHASE-WISE INSTRUCTIONS FOR CURSOR AGENT.txt`. Phase 7–9: `docs/system3_phase7_9_next_steps_for_cursor_agent.md`. Batch 4 modules: `docs/cursor_agent_batch4_instructions.md`. Master behavior: `docs/GENESIS_VSCODE_AGENT_MASTER_INSTRUCTION.md`. Verify after changes: `python tools/verify_cursor_agent_bugs.py`.” |
| **8. Pre-commit vs agent** | Document policy. | In `docs/CURSOR_SETUP.md` or `.cursorrules`: “When making changes, agent may run `pre-commit run --all-files` optionally; if it fails, report and fix. For quick verification, running `python tools/verify_cursor_agent_bugs.py` is sufficient.” |
| **9. Sandbox/network** | Set expectations. | In same doc: “Agent may run in a restricted environment (no system introspection, limited network). Autonomous actions are limited to: edit files, run project scripts and tests, read repo. For full machine/Windows checks, run the provided PowerShell/command checklist from a normal terminal.” |

---

## 4. Recommendations (Priority)

1. **Add `.cursorrules`** (or `.cursor/rules`) with: Angel-only, no live trading, additive-only, key paths, and pointer to full instructions. Highest impact for autonomous behavior.
2. **Standardize on `.venv`** and update `START_CONTINUOUS_AGENT.bat` (and any other `venv` references you care about) to `.venv`, or document “project venv is `.venv`” clearly.
3. **Add root `AGENT.md`** that points to MASTER PLAN, Phase 7–9, Batch 4, and verification script so the agent has one place to “start”.
4. **Fix dashboard port** in `continuous_auto_agent.py` (8080 → 8501) or make it configurable.
5. **Add `docs/CURSOR_SETUP.md`** (or equivalent) documenting: Python 3.10, `.venv`, Cursor permissions, optional extensions, and pre-commit vs agent.
6. **Keep** `docs/GENESIS_VSCODE_AGENT_MASTER_INSTRUCTION.md`, `docs/MASTER PLAN — PHASE-WISE INSTRUCTIONS FOR CURSOR AGENT.txt`, and phase/batch docs as the detailed source of truth; reference them from `.cursorrules` and `AGENT.md`.

---

## 5. Summary Table: Requirement vs Current vs Action

| Requirement | In current editor/project? | Action |
|-------------|----------------------------|--------|
| Project rules (no live trade, Angel-only, safe mode) | Only in docs, not auto-loaded | Add `.cursorrules` (or .cursor/rules) |
| Single venv (path + name) | Mixed: `.venv` vs `venv` | Standardize on `.venv`; update or document scripts |
| Python version (3.10) documented | Not in one place for agent | Put in `.cursorrules` or CURSOR_SETUP.md |
| Terminal allowed | Cursor app setting | Document in CURSOR_SETUP.md |
| File write allowed | Cursor app setting | Document in CURSOR_SETUP.md |
| Agent entry point (where to start) | No single file | Add root `AGENT.md` |
| Verification script runnable | Yes (`tools/verify_cursor_agent_bugs.py`) | Ensure run with `.venv` Python |
| Phase/spec docs | Yes in `docs/` | Link from `AGENT.md` and `.cursorrules` |
| Backend/dashboard ports consistent | No (8080 vs 8501) | Fix continuous_auto_agent.py or config |
| Extensions for agent | Recommendations only; some may not apply to Cursor | Document “optional” in CURSOR_SETUP.md |

---

**File created:** `docs/CURSOR_AGENT_REQUIREMENTS_GAPS_AND_SOLUTIONS.md`

**Done in this pass:**  
- Added **`.cursorrules`** at repo root (auto-loaded by Cursor: Angel-only, no live trading, safe mode, key paths, verification commands).  
- Added **`AGENT.md`** at repo root (entry point: phase docs, master instruction, venv, verification).  
- **START_CONTINUOUS_AGENT.bat** now prefers `.venv` then falls back to `venv`.  
- **continuous_auto_agent.py** dashboard check now accepts port 8501 (Streamlit) or 8080.
