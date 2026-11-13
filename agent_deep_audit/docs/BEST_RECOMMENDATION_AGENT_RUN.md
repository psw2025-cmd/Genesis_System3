# Best Recommendation – So the Agent Can Run Reliably

**One place to read:** what you need once, what to run, and in what order.

---

## 1. What you need once (on your laptop)

So the agent (and you) can run the full sequence from `C:\Genesis_System3` without “can’t run here” issues:

| Requirement | Why |
|-------------|-----|
| **Python 3.10** installed and on PATH (`py -3.10` or `python` works from cmd) | Run-All creates `.venv` and runs all Python scripts. |
| **Git** installed | Run-All does `git add/commit/push` (or you can use a Run-All variant that skips git). |
| **Node.js + npm** installed | React frontend: `npm run dev` in `dashboard/frontend`. |
| **PowerShell** allows scripts | So `Run-FullGovernance.ps1` and `Run-FullQA.ps1` run when Run-All calls them. If needed: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. |

Optional: **Docker** only if you want Run-All’s Docker build/push steps to run.

---

## 2. Best order to run (every time)

From **`C:\Genesis_System3`** in cmd or PowerShell:

1. **Environment + Governance + QA + start services**  
   ```bat
   Run-All.bat
   ```  
   If it fails → open `proof\archive\RUN_ALL_FAIL_*.json`, fix per `next_actions`, rerun.

2. **Dashboard full test**  
   ```bat
   .\.venv\Scripts\python.exe scripts\run_dashboard_full_test.py
   ```  
   If it fails → open `proof\archive\DASHBOARD_FULL_TEST_*.json`, fix per `next_actions`, rerun.

3. **Phase orchestrator (201–310)**  
   ```bat
   .\.venv\Scripts\python.exe scripts\run_phase_orchestrator.py
   ```  
   If it fails → open `proof\archive\PHASE_ORCHESTRATOR_FAIL_*.json`, fix per `next_actions`, rerun.

The agent is instructed to run these **by itself first**; only after failing multiple times does it hand you a User Action Plan (what/why/how + what it will run next).

---

## 3. One-time readiness check (optional)

Before relying on the agent or Run-All, you can verify the basics:

From `C:\Genesis_System3`:

```bat
py -3.10 --version
git --version
node --version
npm --version
```

If all four succeed, Run-All and the Python scripts can run. If any fail, install or fix that tool first.

---

## 4. Summary

- **Best recommendation:**  
  - You: install **Python 3.10, Git, Node/npm**, and allow **PowerShell scripts** once.  
  - Then always run in order: **Run-All.bat** → **dashboard full test** → **phase orchestrator**.  
  - Use the JSON reports in `proof\archive\` when something fails; the agent uses the same sequence and only asks you to run things after it has failed the same step multiple times.

This keeps everything runnable from your laptop in one place (`C:\Genesis_System3`) and avoids “I can’t run here” except for real environment gaps, which the readiness check and the failure reports make clear.
