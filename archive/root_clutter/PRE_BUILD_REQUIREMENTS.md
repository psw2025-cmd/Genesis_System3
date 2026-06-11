# Pre-Build Requirements (Before Building the Installer)

**Do these checks first.** If anything is missing, the installer build can fail or the final exe may not work. Fix all [FAIL] items before running `build_fresh_installer.bat`.

---

## Quick check (one command)

Open **Command Prompt** or **PowerShell**, go to the project folder, then run:

```text
cd C:\Genesis_System3
python check_build_requirements.py
```

- If it says **ALL CHECKS PASSED** → you can run `build_fresh_installer.bat`.
- If it shows **[FAIL]** → follow the sections below to fix, then run the script again.

---

## 1. Python (3.8 or higher)

**What it is:** The language the backend and scripts use.

**Check:** In Command Prompt type `python --version` and press Enter.

**If missing or version too old:**
- Download Python from https://www.python.org/downloads/
- Run the installer; **check "Add Python to PATH"**.
- Restart the terminal and run `python --version` again.

---

## 2. Virtual environment (venv)

**What it is:** A separate folder for this project’s Python packages so they don’t mix with other projects.

**Check:** Run `check_build_requirements.py`. It will say whether you’re inside a venv or not.

**If you need to create venv:**
1. Open Command Prompt.
2. `cd C:\Genesis_System3`
3. Run: `python -m venv venv`
4. Activate it:
   - **PowerShell:** `.\venv\Scripts\Activate.ps1`
   - **CMD:** `venv\Scripts\activate.bat`
5. You should see `(venv)` at the start of the line.

**Before building or running Python scripts:** Always activate the venv first (step 4).

---

## 3. Python dependencies

**What they are:** Packages like `requests`, `pandas`, `fastapi`, `uvicorn` that the backend and scripts need.

**Check:** Run `check_build_requirements.py`; it checks for key packages.

**If any are missing:**
1. Activate venv (see section 2).
2. Install project packages:
   ```text
   pip install -r requirements.txt
   pip install -r dashboard\backend\requirements.txt
   ```
3. Run `python check_build_requirements.py` again.

---

## 4. Node.js and npm

**What they are:** Needed to build the frontend (dashboard UI) and the Electron desktop app (installer).

**Check:** In Command Prompt run `node --version` and `npm --version`. You need **Node.js 18 or higher** and **npm 8 or higher**.

**If missing or too old:**
- Download the LTS version from https://nodejs.org
- Run the installer (default options are fine).
- Restart the terminal and check `node --version` and `npm --version` again.

---

## 5. Frontend dependencies (dashboard/frontend)

**What they are:** JavaScript/React packages for the dashboard. They must be installed so `npm run build` works.

**Check:** Run `check_build_requirements.py`; it looks for `dashboard\frontend\node_modules`.

**If missing:**
1. Open Command Prompt.
2. `cd C:\Genesis_System3\dashboard\frontend`
3. Run: `npm install`
4. Wait until it finishes, then run `check_build_requirements.py` again.

---

## 6. Desktop app dependencies (desktop_app)

**What they are:** Electron and electron-builder for creating the installer.

**Check:** Run `check_build_requirements.py`; it looks for `desktop_app\node_modules`.

**If missing:**
1. Open Command Prompt.
2. `cd C:\Genesis_System3\desktop_app`
3. Run: `npm install`
4. Wait until it finishes, then run `check_build_requirements.py` again.

---

## 7. Folders that get packaged into the exe

**What they are:** The build copies these into the installer:

- **dashboard/backend** – Python backend (required).
- **dashboard/frontend/dist** – Created when you run `npm run build` in `dashboard/frontend` (build script does this).
- **agent_memory** – Optional; only needed if your app uses it.

**Check:** Run `check_build_requirements.py`. It checks that `dashboard/backend` and (if needed) `agent_memory` exist. The script does not build the frontend; `build_fresh_installer.bat` does that.

---

## Order to do things (kid-level)

1. **Install Python 3.8+** and add it to PATH.
2. **Create and activate venv** in `C:\Genesis_System3` (create once, activate every time you open a new terminal for this project).
3. **Install Python packages:**  
   `pip install -r requirements.txt`  
   `pip install -r dashboard\backend\requirements.txt`
4. **Install Node.js 18+** from nodejs.org.
5. **Install frontend packages:**  
   `cd dashboard\frontend` → `npm install`
6. **Install desktop app packages:**  
   `cd desktop_app` → `npm install`
7. **Run the check:**  
   `cd C:\Genesis_System3` → `python check_build_requirements.py`
8. When it says **ALL CHECKS PASSED**, run **build_fresh_installer.bat** to build the exe.

---

## Summary table

| Requirement           | How to check                    | How to fix |
|-----------------------|----------------------------------|------------|
| Python 3.8+           | `python --version`              | Install from python.org, add to PATH |
| Virtual environment   | `check_build_requirements.py`   | `python -m venv venv` then activate |
| Python deps           | Same script                     | `pip install -r requirements.txt` (+ backend requirements) |
| Node.js 18+ & npm     | `node --version`, `npm --version` | Install from nodejs.org |
| Frontend node_modules | Same script                     | `cd dashboard\frontend` then `npm install` |
| Desktop node_modules  | Same script                     | `cd desktop_app` then `npm install` |
| dashboard/backend     | Same script                     | Must exist in project |
| agent_memory          | Same script                     | Create folder if your app needs it |

After all requirements are confirmed, you can safely proceed with the building activity (run `build_fresh_installer.bat`).
