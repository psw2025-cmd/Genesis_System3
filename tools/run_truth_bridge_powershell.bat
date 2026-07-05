@echo off
REM System3 Truth Bridge - No Python launcher
REM Use this on office PC when VS Code/Git is available but Python is not installed.

cd /d "%~dp0\.."
echo [INFO] Repo folder: %CD%
echo [INFO] Running PowerShell no-python truth bridge...

powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\tools\run_truth_bridge_powershell.ps1"
if errorlevel 1 goto fail

echo.
echo [DONE] PowerShell Truth Bridge completed.
echo Reports:
echo reports\latest\system3_truth_bridge\summary.md
echo reports\latest\production_viability_bridge\summary.md
echo.
echo Optional upload:
echo git add reports/latest/system3_truth_bridge reports/latest/production_viability_bridge
echo git commit -m "proof: update PowerShell truth bridge reports"
echo git push
goto end

:fail
echo [FAIL] PowerShell Truth Bridge failed. Copy this output to ChatGPT.
exit /b 1

:end
pause
