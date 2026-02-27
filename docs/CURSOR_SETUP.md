# Cursor Setup for Full Agent Autonomy

**Purpose:** One-time checks so the Cursor agent can work fully autonomously without user or manual steps.

---

## 1. Cursor App Settings (User Check Once)

| Setting | Where | Required |
|---------|-------|----------|
| **Allow terminal commands** | Cursor Settings → Features → Agent | Yes – agent runs `python`, `pip`, `git`, scripts |
| **Allow agent to edit files** | Cursor Settings → Features → Agent | Yes – agent implements phases, fixes bugs |
| **Python interpreter** (optional) | Cursor Settings → Python → Interpreter | `C:\Genesis_System3\.venv\Scripts\python.exe` – improves IntelliSense |

These are usually **on by default**. If the agent cannot run commands or edit files, verify these in Cursor.

---

## 2. Project Environment

| Item | Value |
|------|-------|
| **Venv path** | `.venv` (not `venv`) |
| **Python version** | 3.10 |
| **Activate (PowerShell)** | `.venv\Scripts\Activate.ps1` |
| **Activate (cmd)** | `call .venv\Scripts\activate.bat` |
| **Direct run (no activate)** | `.venv\Scripts\python.exe -m pytest ...` |

**Note:** Many legacy `.bat` files reference `venv`. The project standard is `.venv`. Run `Run-All.bat` to create `.venv`. For scripts that use `venv`, either update them to `.venv` or create a symlink: `mklink /D venv .venv` (admin cmd).

---

## 3. Agent Terminal + Venv (Confirmed)

The agent **can** work in the integrated terminal with venv:

- Uses `.venv\Scripts\python.exe` directly (no activation needed)
- Runs: `pytest`, `black`, `flake8`, `git add/commit/push`, verification scripts
- Credentials stored: `git push` works without prompts

---

## 4. Ports (Backend / Dashboard)

| Service | Port | Started by |
|---------|------|------------|
| Backend API | 8000 | Run-All.bat, `uvicorn` |
| Streamlit dashboard | 8501 | Run-All.bat |
| Simple HTTP server (fallback) | 8080 | Some scripts |

`continuous_auto_agent.py` checks 8501 first, then 8080.

---

## 5. Extensions (Optional)

For agent-only autonomy, **no extensions are required**. For better lint/security in the editor: Python, Pylance, and optionally SonarLint/CodeQL if available in Cursor.

---

## 6. Pre-commit vs Agent

When making changes, the agent may run `pre-commit run --all-files` optionally. If it fails, report and fix. For quick verification, `python tools/verify_cursor_agent_bugs.py` is sufficient.

---

## 7. Sandbox / Network

The agent may run in a restricted environment (no system introspection, limited network). Autonomous actions: edit files, run project scripts and tests, read repo. For full machine/Windows checks, run the provided PowerShell/command checklist from a normal terminal.
