@echo off
REM System3 Full Verification Checklist
REM Runs all verification commands from validation master document

echo ============================================================
echo SYSTEM3 FULL VERIFICATION CHECKLIST
echo ============================================================
echo Date: %date% %time%
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
echo ============================================================
echo VERIFICATION 1: Core Status ^& Menu
echo ============================================================
"%PYTHON%" check_system3_status.py
if errorlevel 1 (
    echo [WARN] Status check had issues
) else (
    echo [PASS] Core status check completed
)

echo.
echo ============================================================
echo VERIFICATION 2: Models ^& Training Health
echo ============================================================
"%PYTHON%" -m core.engine.train_angel_models
if errorlevel 1 (
    echo [WARN] Model training had issues (may be expected if models exist)
) else (
    echo [PASS] Model training completed
)

"%PYTHON%" -m core.engine.offline_angel_ai_test
if errorlevel 1 (
    echo [WARN] Offline test had issues
) else (
    echo [PASS] Offline AI test completed
)

echo.
echo ============================================================
echo VERIFICATION 3: Live Pipeline (DRY-RUN)
echo ============================================================
echo [INFO] Checking live pipeline module...
"%PYTHON%" -c "from core.engine.angel_live_ai_signals import main; print('[PASS] Live pipeline module exists')" 2>nul
if errorlevel 1 (
    echo [WARN] Could not import live pipeline module
) else (
    echo [PASS] Live pipeline module verified
)

"%PYTHON%" -c "from core.engine.angel_automation_config import AUTOMATION_CONFIG; print('[PASS] Auto-execute:', AUTOMATION_CONFIG.auto_execute_trades)" 2>nul
if errorlevel 1 (
    echo [WARN] Could not check automation config
)

echo.
echo ============================================================
echo VERIFICATION 4: Backtester ^& PnL
echo ============================================================
"%PYTHON%" -m core.engine.angel_synthetic_backtester
if errorlevel 1 (
    echo [WARN] Backtester had issues
) else (
    echo [PASS] Synthetic backtester completed
)

"%PYTHON%" -m core.engine.angel_daily_pnl_summary
if errorlevel 1 (
    echo [WARN] PnL summary had issues (may be expected if no trades)
) else (
    echo [PASS] Daily PnL summary completed
)

echo.
echo ============================================================
echo VERIFICATION 5: Monitoring ^& Governance
echo ============================================================
"%PYTHON%" -m core.engine.system3_phase35_ultra_auditor
if errorlevel 1 (
    echo [WARN] Decision Auditor had issues
) else (
    echo [PASS] Decision Auditor completed
)

"%PYTHON%" -m core.engine.system3_phase37_policy_risk_monitor
if errorlevel 1 (
    echo [WARN] Policy Monitor had issues
) else (
    echo [PASS] Policy ^& Risk Monitor completed
)

"%PYTHON%" -m core.engine.system3_phase38_governance_summary
if errorlevel 1 (
    echo [WARN] Governance Summary had issues
) else (
    echo [PASS] Governance Summary completed
)

echo.
echo ============================================================
echo VERIFICATION 6: Ultra Phases 39-45
echo ============================================================
"%PYTHON%" verify_phases_39_45.py
if errorlevel 1 (
    echo [WARN] Phases 39-45 verification had issues
) else (
    echo [PASS] Phases 39-45 verification completed
)

echo.
echo ============================================================
echo VERIFICATION CHECKLIST COMPLETE
echo ============================================================
echo.
echo Check outputs above for any warnings or errors.
echo Review reports in:
echo   - docs\system3_*.md
echo   - storage\ultra\phase*.md
echo   - storage\reports\
echo.
pause

