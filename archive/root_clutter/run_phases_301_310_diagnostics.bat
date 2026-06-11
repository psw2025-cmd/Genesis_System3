@echo off
set PYTHON_PATH=C:\Genesis_System3\venv\Scripts\python.exe
set SCRIPT_PATH=system3_phases_301_310_diagnostics.py

echo ============================================================================
echo Running Phases 301-310 Diagnostics
echo ============================================================================
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo ============================================================================

%PYTHON_PATH% %SCRIPT_PATH%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Diagnostics failed with exit code %ERRORLEVEL%
    exit /b 1
)

echo.
echo [OK] Diagnostics completed
exit /b 0

