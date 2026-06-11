@echo off
set PYTHON_PATH=C:\Genesis_System3\venv\Scripts\python.exe
set SCRIPT_PATH=core\engine\angel_pnl_simulator.py

echo ============================================================================
echo Running PnL Simulator
echo ============================================================================
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo ============================================================================

%PYTHON_PATH% %SCRIPT_PATH%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PnL Simulator failed with exit code %ERRORLEVEL%
    exit /b 1
)

echo.
echo [OK] PnL Simulator completed successfully
exit /b 0

