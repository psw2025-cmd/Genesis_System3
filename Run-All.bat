@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM Master Automation Script - Genesis_System3
REM Production-grade STRICT: if a step fails we STOP, report reason,
REM impact, and next actions (files/scripts to fix and run in sequence).
REM Report written to proof/archive/RUN_ALL_FAIL_*.json
REM ============================================================

cd /d C:\Genesis_System3

REM --- Step 2: Clean old environment
echo Cleaning old environment...
if exist .venv (
    rmdir /s /q .venv
    echo Deleted old venv
) else (
    echo No .venv found - will create new.
)
powershell -Command "Get-ChildItem -Recurse -Include '__pycache__','*.pyc','*.pyo','*.log','*.tmp' -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue" 2>nul
echo Cleaned residual artifacts

REM --- Step 3: Create new venv with Python 3.10
echo Creating new venv...
py -3.10 -m venv .venv 2>nul
if errorlevel 1 python -m venv .venv 2>nul
if not exist .venv\Scripts\activate.bat (
  set RUN_ALL_FAIL_STEP=Step 3: Create venv
  set RUN_ALL_FAIL_REASON=py -3.10 -m venv .venv and python -m venv .venv both failed or .venv\Scripts\activate.bat missing
  set RUN_ALL_FAIL_IMPACT=No virtual environment; pip and all later steps will fail
  set RUN_ALL_FAIL_NEXT=Install Python 3.10 or fix path: use py -3.10 or python; ensure .venv is not locked by another process; rerun Run-All.bat
  REM Try to run failure reporter with the best available Python.
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3.10 scripts\run_all_report_fail.py
  ) else (
    python scripts\run_all_report_fail.py
  )
  exit /b 1
)
call .venv\Scripts\activate.bat

REM --- Step 5: Upgrade pip/setuptools/wheel
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  set RUN_ALL_FAIL_STEP=Step 5: Upgrade pip/setuptools/wheel
  set RUN_ALL_FAIL_REASON=pip install --upgrade failed
  set RUN_ALL_FAIL_IMPACT=Package installs may be wrong; Step 6 may fail
  set RUN_ALL_FAIL_NEXT=Check network and proxy; Run manually: .venv\Scripts\pip install --upgrade pip setuptools wheel; Rerun Run-All.bat
  python scripts\run_all_report_fail.py
  exit /b 1
)

REM --- Step 6: Install runtime + dev requirements
echo Installing runtime dependencies...
pip install -r requirements_runtime.txt
if errorlevel 1 (
  set RUN_ALL_FAIL_STEP=Step 6: Install runtime requirements
  set RUN_ALL_FAIL_REASON=pip install -r requirements_runtime.txt failed
  set RUN_ALL_FAIL_IMPACT=Backend and dashboard will not run; missing fastapi, pandas, etc.
  set RUN_ALL_FAIL_NEXT=Check requirements_runtime.txt and fix broken or missing packages; Run: pip install -r requirements_runtime.txt; Rerun Run-All.bat
  python scripts\run_all_report_fail.py
  exit /b 1
)
echo Installing dev dependencies...
pip install -r requirements-dev.txt
if errorlevel 1 (
  set RUN_ALL_FAIL_STEP=Step 6: Install dev requirements
  set RUN_ALL_FAIL_REASON=pip install -r requirements-dev.txt failed
  set RUN_ALL_FAIL_IMPACT=Testing and lint tools missing; Governance/QA may fail
  set RUN_ALL_FAIL_NEXT=Check requirements-dev.txt; Run: pip install -r requirements-dev.txt; Rerun Run-All.bat
  python scripts\run_all_report_fail.py
  exit /b 1
)

REM --- Step 7: Run Governance Script
echo Running Governance checks...
powershell -ExecutionPolicy Bypass -File Run-FullGovernance.ps1
if errorlevel 1 (
  set RUN_ALL_FAIL_STEP=Step 7: Governance (Run-FullGovernance.ps1)
  set RUN_ALL_FAIL_REASON=Governance script exited with failure
  set RUN_ALL_FAIL_IMPACT=Governance checks (deps, security, etc.) not passing; deployment/CI may be blocked
  set RUN_ALL_FAIL_NEXT=Open Run-FullGovernance.ps1 and fix reported issues; Rerun: powershell -ExecutionPolicy Bypass -File Run-FullGovernance.ps1; Then Rerun Run-All.bat
  python scripts\run_all_report_fail.py
  exit /b 1
)

REM --- Step 8: Run QA Guardian Script
echo Running QA Guardian checks...
powershell -ExecutionPolicy Bypass -File Run-FullQA.ps1
if errorlevel 1 (
  set RUN_ALL_FAIL_STEP=Step 8: QA Guardian (Run-FullQA.ps1)
  set RUN_ALL_FAIL_REASON=QA script exited with failure
  set RUN_ALL_FAIL_IMPACT=QA checks not passing; quality gate failed
  set RUN_ALL_FAIL_NEXT=Open Run-FullQA.ps1 and fix reported issues; Rerun: powershell -ExecutionPolicy Bypass -File Run-FullQA.ps1; Then Rerun Run-All.bat
  python scripts\run_all_report_fail.py
  exit /b 1
)

REM --- Step 9: Start Backend (FastAPI/Uvicorn)
echo Starting Backend service...
start cmd /k "cd /d C:\Genesis_System3\dashboard\backend && C:\Genesis_System3\.venv\Scripts\activate.bat && uvicorn app:app --host 127.0.0.1 --port 8000"

REM --- Step 10: Start Dashboard (Streamlit)
echo Starting Dashboard service...
start cmd /k "cd /d C:\Genesis_System3 && .venv\Scripts\activate.bat && streamlit run dashboard/app.py --server.port=8501 --server.address=127.0.0.1"

REM --- Step 11: Start React Frontend (Vite dev server on port 3000)
echo Starting React frontend...
start cmd /k "cd /d C:\Genesis_System3\dashboard\frontend && npm run dev"

REM --- Step 12: Pre-commit hooks
echo Running pre-commit hooks...
pre-commit run --all-files
if errorlevel 1 (
  set RUN_ALL_FAIL_STEP=Step 12: Pre-commit hooks
  set RUN_ALL_FAIL_REASON=pre-commit run --all-files failed
  set RUN_ALL_FAIL_IMPACT=Code style or lint issues; commit may be blocked
  set RUN_ALL_FAIL_NEXT=Fix issues reported by pre-commit (black, flake8, etc.); Run: pre-commit run --all-files; Then Rerun Run-All.bat
  python scripts\run_all_report_fail.py
  exit /b 1
)

REM --- Step 13: Git add, commit, push
if exist .git (
  echo Pushing code to GitHub...
  git add .
  git commit -m "Automated Governance + QA + Deployment"
  if errorlevel 1 (
    set RUN_ALL_FAIL_STEP=Step 13: Git commit
    set RUN_ALL_FAIL_REASON=git commit failed (nothing to commit or commit error)
    set RUN_ALL_FAIL_IMPACT=Changes not committed; push will not run
    set RUN_ALL_FAIL_NEXT=Check git status; Resolve conflicts or add files; Run: git commit -m "Automated Governance + QA + Deployment"; Then Rerun Run-All.bat
    python scripts\run_all_report_fail.py
    exit /b 1
  )
  git push origin main
  if errorlevel 1 (
    set RUN_ALL_FAIL_STEP=Step 13: Git push
    set RUN_ALL_FAIL_REASON=git push failed (remote, auth, or network)
    set RUN_ALL_FAIL_IMPACT=Code not pushed to remote
    set RUN_ALL_FAIL_NEXT=Check remote and credentials; Run: git push origin main; Then Rerun Run-All.bat
    python scripts\run_all_report_fail.py
    exit /b 1
  )
) else (
  echo Skipping Step 13 (Git): no .git folder found.
  echo To enable: run "git init", add a remote, then rerun Run-All.bat
)

REM --- Step 14: Build Docker Images (only if Dockerfiles exist)
if exist backend\Dockerfile (
  echo Building backend Docker image...
  docker build -t ghcr.io/%USERNAME%/genesis-backend:latest -f backend/Dockerfile .
  if errorlevel 1 (
    set RUN_ALL_FAIL_STEP=Step 14: Docker build backend
    set RUN_ALL_FAIL_REASON=docker build for backend failed
    set RUN_ALL_FAIL_IMPACT=Backend image not built; push will skip
    set RUN_ALL_FAIL_NEXT=Fix backend/Dockerfile and build context; Run: docker build -t ghcr.io/%%USERNAME%%/genesis-backend:latest -f backend/Dockerfile .; Then Rerun Run-All.bat
    python scripts\run_all_report_fail.py
    exit /b 1
  )
)
if exist dashboard\Dockerfile (
  echo Building dashboard Docker image...
  docker build -t ghcr.io/%USERNAME%/genesis-dashboard:latest -f dashboard/Dockerfile .
  if errorlevel 1 (
    set RUN_ALL_FAIL_STEP=Step 14: Docker build dashboard
    set RUN_ALL_FAIL_REASON=docker build for dashboard failed
    set RUN_ALL_FAIL_IMPACT=Dashboard image not built; push will skip
    set RUN_ALL_FAIL_NEXT=Fix dashboard/Dockerfile and build context; Run: docker build -t ghcr.io/%%USERNAME%%/genesis-dashboard:latest -f dashboard/Dockerfile .; Then Rerun Run-All.bat
    python scripts\run_all_report_fail.py
    exit /b 1
  )
)

REM --- Step 15: Push Docker Images (only if GITHUB_TOKEN set and images built)
if defined GITHUB_TOKEN (
  if exist backend\Dockerfile (
    echo Logging into GitHub Container Registry...
    docker login ghcr.io -u %USERNAME% -p %GITHUB_TOKEN%
    if errorlevel 1 (
      set RUN_ALL_FAIL_STEP=Step 15: Docker login
      set RUN_ALL_FAIL_REASON=docker login ghcr.io failed
      set RUN_ALL_FAIL_IMPACT=Cannot push images to GHCR
      set RUN_ALL_FAIL_NEXT=Check GITHUB_TOKEN and username; Run: docker login ghcr.io -u %%USERNAME%% -p %%GITHUB_TOKEN%%; Then Rerun Run-All.bat
      python scripts\run_all_report_fail.py
      exit /b 1
    )
    echo Pushing backend image...
    docker push ghcr.io/%USERNAME%/genesis-backend:latest
    if errorlevel 1 (
      set RUN_ALL_FAIL_STEP=Step 15: Docker push backend
      set RUN_ALL_FAIL_REASON=docker push backend image failed
      set RUN_ALL_FAIL_IMPACT=Backend image not in registry
      set RUN_ALL_FAIL_NEXT=Check network and registry permissions; Run: docker push ghcr.io/%%USERNAME%%/genesis-backend:latest; Then Rerun Run-All.bat
      python scripts\run_all_report_fail.py
      exit /b 1
    )
  )
  if exist dashboard\Dockerfile (
    if not exist backend\Dockerfile (
      echo Logging into GitHub Container Registry...
      docker login ghcr.io -u %USERNAME% -p %GITHUB_TOKEN%
    )
    echo Pushing dashboard image...
    docker push ghcr.io/%USERNAME%/genesis-dashboard:latest
    if errorlevel 1 (
      set RUN_ALL_FAIL_STEP=Step 15: Docker push dashboard
      set RUN_ALL_FAIL_REASON=docker push dashboard image failed
      set RUN_ALL_FAIL_IMPACT=Dashboard image not in registry
      set RUN_ALL_FAIL_NEXT=Check network and registry permissions; Run: docker push ghcr.io/%%USERNAME%%/genesis-dashboard:latest; Then Rerun Run-All.bat
      python scripts\run_all_report_fail.py
      exit /b 1
    )
  )
)

REM --- Success
echo ============================================================
echo All steps completed: Environment, Governance, QA, Backend, Dashboard,
echo Docker Build + Push, GitHub CI/CD
echo Logs available in C:\Genesis_System3\logs\inspector
echo ============================================================
endlocal
exit /b 0
