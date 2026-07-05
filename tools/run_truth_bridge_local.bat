@echo off
REM System3 Truth Bridge - Local No-Billing Runner
REM Runs from this cloned repo. Uses no GitHub Actions minutes.

cd /d "%~dp0\.."

if exist .venv\Scripts\python.exe (
  set PY=.venv\Scripts\python.exe
) else (
  set PY=python
)

echo [INFO] Repo folder: %CD%
echo [INFO] Running System3 Truth Bridge locally...
%PY% scripts\system3_truth_bridge.py
if errorlevel 1 goto fail

echo [INFO] Running Production Viability Bridge locally...
%PY% scripts\system3_production_viability_bridge.py
if errorlevel 1 goto fail

echo.
echo [DONE] Reports generated locally:
echo reports\latest\system3_truth_bridge\summary.md
echo reports\latest\production_viability_bridge\summary.md
echo.
echo Optional Git commands if you want to upload reports:
echo git add reports/latest/system3_truth_bridge reports/latest/production_viability_bridge
echo git commit -m "proof: update local truth bridge reports"
echo git push
goto end

:fail
echo [FAIL] Truth bridge run failed. Copy this window output to ChatGPT.
exit /b 1

:end
pause
