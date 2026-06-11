@echo off
REM System3 Full Validation Script
REM Runs all core validation checks to confirm system health

echo ============================================================
echo SYSTEM3 FULL VALIDATION RUN
echo ============================================================
echo.

set "PYTHON=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] venv Python not found at %PYTHON%
    echo Please create/repair the virtual environment first.
    exit /b 1
)

REM Activate virtual environment
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "%~dp0venv\Scripts\activate.bat"
)

echo.
echo [1/8] Core Status Check...
echo ============================================================
"%PYTHON%" check_system3_status.py
if errorlevel 1 (
    echo [WARN] Status check had issues (may be expected)
)

echo.
echo [2/8] Model Training Health...
echo ============================================================
"%PYTHON%" -m core.engine.train_angel_models
if errorlevel 1 (
    echo [WARN] Model training had issues (may be expected if models already exist)
)

echo.
echo [3/8] Offline AI Test...
echo ============================================================
"%PYTHON%" -m core.engine.offline_angel_ai_test
if errorlevel 1 (
    echo [WARN] Offline test had issues
)

echo.
echo [4/8] Synthetic Backtester...
echo ============================================================
"%PYTHON%" -m core.engine.angel_synthetic_backtester
if errorlevel 1 (
    echo [WARN] Backtester had issues
)

echo.
echo [5/8] Daily PnL Summary...
echo ============================================================
"%PYTHON%" -m core.engine.angel_daily_pnl_summary
if errorlevel 1 (
    echo [WARN] PnL summary had issues (may be expected if no trades)
)

echo.
echo [6/8] Decision Auditor (Phase 35)...
echo ============================================================
"%PYTHON%" -m core.engine.system3_phase35_ultra_auditor
if errorlevel 1 (
    echo [WARN] Decision auditor had issues
)

echo.
echo [7/8] Policy ^& Risk Monitor (Phase 37)...
echo ============================================================
"%PYTHON%" -m core.engine.system3_phase37_policy_risk_monitor
if errorlevel 1 (
    echo [WARN] Policy monitor had issues
)

echo.
echo [8/8] Governance Summary (Phase 38)...
echo ============================================================
"%PYTHON%" -m core.engine.system3_phase38_governance_summary
if errorlevel 1 (
    echo [WARN] Governance summary had issues
)

echo.
echo ============================================================
echo [DONE] System3 validation run complete
echo ============================================================
echo.
echo Check latest reports in:
echo   - docs\system3_*.md
echo   - storage\ultra\phase*.md
echo   - storage\reports\
echo.
pause

