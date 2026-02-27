@echo off
set PYTHON_PATH=C:\Genesis_System3\venv\Scripts\python.exe
set SCRIPT_PATH=core\engine\system3_phase221_forward_returns.py

echo ============================================================================
echo Running Phase 221 - Forward Returns
echo ============================================================================
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo ============================================================================

%PYTHON_PATH% %SCRIPT_PATH%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Phase 221 failed with exit code %ERRORLEVEL%
    exit /b 1
)

echo.
echo [OK] Phase 221 completed successfully
exit /b 0

