# Agent Autonomous Setup

Run this **once** so the AI agent can work fully in your project without manual steps.

---

## One command (PowerShell)

```powershell
cd C:\Genesis_System3
powershell -ExecutionPolicy Bypass -File .\scripts\agent_autonomous_setup.ps1
```

---

## What it does

| Step | Action |
|------|--------|
| 1 | Sets `git config --global credential.helper manager` |
| 2 | Sets `git config --global user.name` and `user.email` (noreply) |
| 3 | Ensures `outputs/` in `.gitignore` |
| 4 | Untracks `logs/` and `outputs/` from Git |
| 5 | Runs `git prune` |
| 6 | Verifies venv and pip |
| 7 | Reports: Done / Pending / Manual |

---

## What you must do once (manual)

1. **GitHub email setting**  
   - Go to: https://github.com/settings/emails  
   - Turn **OFF** "Block command line pushes that expose my email"

2. **First `git push`**  
   - Run `git push` once  
   - Sign in when prompted (Credential Manager stores it for future pushes)

---

## Agent commands (venv)

The agent uses these so it never needs your terminal:

```
.venv\Scripts\python.exe -m pytest ...
.venv\Scripts\python.exe -m black --check .
.venv\Scripts\python.exe -m flake8 ...
git add . ; git commit -m "..." ; git push
```

---

## After setup

- Agent can run all commands in `.venv` without activating it manually  
- Agent can `git push` if credentials are stored  
- `logs/` and `outputs/` are ignored; no more noisy diffs
