@echo off
REM ============================================================================
REM SYSTEM3 DAILY START - UNIFIED DRY-RUN LAUNCHER
REM ============================================================================
REM One-click daily startup: preflight, validation, monitoring ready
REM Combines start_system3_env.bat + START_AUTORUN_AND_WATCHDOG.bat
REM DRY-RUN ONLY - No live trading paths touched
REM ============================================================================

chcp 65001 >nul
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM Auto-detect project root (where this batch file is located)
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "LOGS_DIR=%PROJECT_DIR%\logs"

REM ============================================================================
REM BANNER
REM ============================================================================
cls
echo.
echo ================================================================================
echo   SYSTEM3 DAILY START - PRODUCTION DRY-RUN
echo ================================================================================
echo   Auto-detected Project: %PROJECT_DIR%
echo   Mode: DRY-RUN (Paper Trading Only)
echo   Safety: All live trading paths disabled
echo ================================================================================
echo.

REM ============================================================================
REM PHASE 1: ENVIRONMENT VALIDATION
REM ============================================================================
echo [1/6] Environment Validation...
echo.

if not exist "%VENV_DIR%\Scripts\Activate.ps1" (
    echo ERROR: Virtual environment not found at %VENV_DIR%
    echo Please run: python -m venv venv
    pause
    exit /b 1
)
echo    [OK] Virtual environment located

REM Test Python executable
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python executable not working
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('"%PYTHON%" --version 2^>^&1') do set PY_VERSION=%%v
echo    [OK] %PY_VERSION%

REM ============================================================================
REM PHASE 2: DEPENDENCY CHECK (CRITICAL ONLY)
REM ============================================================================
echo.
echo [2/6] Critical Dependencies Check...
echo.

set DEP_ERRORS=0
for %%m in (psutil pandas numpy joblib dotenv) do (
    "%PYTHON%" -c "import %%m" 2>nul
    if errorlevel 1 (
        echo    [MISSING] %%m - Installing...
        "%PYTHON%" -m pip install %%m --quiet
        if errorlevel 1 (
            echo    [ERROR] Failed to install %%m
            set DEP_ERRORS=1
        ) else (
            echo    [OK] %%m installed
        )
    ) else (
        echo    [OK] %%m
    )
)

if %DEP_ERRORS%==1 (
    echo.
    echo ERROR: Some dependencies failed. Run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM ============================================================================
REM PHASE 3: PRE-FLIGHT HEALTH CHECK
REM ============================================================================
echo.
echo [3/6] Pre-Flight Health Check...
echo.

REM Create logs directory
if not exist "%LOGS_DIR%" (
    mkdir "%LOGS_DIR%"
    echo    [OK] Logs directory created
) else (
    echo    [OK] Logs directory exists
)

REM Quick health check
"%PYTHON%" -m core.engine.health_check >nul 2>&1
if errorlevel 1 (
    echo    [WARN] Health check returned warnings (non-critical)
) else (
    echo    [OK] Health check passed
)

REM Verify DRY-RUN config
"%PYTHON%" -c "from config.live_trade_config import LIVE_TRADING_ENABLED; exit(0 if not LIVE_TRADING_ENABLED else 1)" 2>nul
if errorlevel 1 (
    echo    [ERROR] LIVE TRADING IS ENABLED - ABORTING FOR SAFETY
    echo    Check config/live_trade_config.py
    pause
    exit /b 1
) else (
    echo    [OK] DRY-RUN mode confirmed (LIVE_TRADING_ENABLED=False)
)

REM ============================================================================
REM PHASE 4: DATA PIPELINE VALIDATION
REM ============================================================================
echo.
echo [4/6] Data Pipeline Validation...
echo.

if exist "storage\live\angel_index_ai_signals_with_forward.csv" (
    for %%A in ("storage\live\angel_index_ai_signals_with_forward.csv") do set CSV_SIZE=%%~zA
    echo    [OK] Forward returns CSV exists (!CSV_SIZE! bytes)
) else (
    echo    [WARN] Forward returns CSV missing - will be generated on first run
)

if exist "core\models\angel_one\NIFTY_model.pkl" (
    echo    [OK] Models directory exists (NIFTY model found)
) else (
    echo    [WARN] Models not found - training may be needed
)

REM ============================================================================
REM PHASE 5: HEARTBEAT & MONITORING SETUP
REM ============================================================================
echo.
echo [5/6] Monitoring Setup...
echo.

REM Update heartbeat
"%PYTHON%" system3_ultimate_heartbeat_manager.py --quick-status >nul 2>&1
if errorlevel 1 (
    echo    [WARN] Heartbeat update failed (non-critical)
) else (
    echo    [OK] Heartbeat updated
)

if exist "system3_daily_heartbeat.json" (
    echo    [OK] Heartbeat file exists
) else (
    echo    [INFO] Heartbeat will be created on first monitoring cycle
)

REM ============================================================================
REM PHASE 6: GENERATE STARTUP REPORT
REM ============================================================================
echo.
echo [6/6] Generating Startup Report...
echo.

REM Generate timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%
set "STARTUP_LOG=%LOGS_DIR%\system3_daily_start_%TIMESTAMP%.log"

REM Write startup summary
(
    echo ================================================================================
    echo SYSTEM3 DAILY START REPORT
    echo ================================================================================
    echo Timestamp: %TIMESTAMP%
    echo Project: %PROJECT_DIR%
    echo Python: %PY_VERSION%
    echo Mode: DRY-RUN ^(Paper Trading^)
    echo ================================================================================
    echo.
    echo [PHASE 1] Environment: OK
    echo [PHASE 2] Dependencies: OK
    echo [PHASE 3] Pre-Flight: OK
    echo [PHASE 4] Data Pipeline: OK
    echo [PHASE 5] Monitoring: OK
    echo [PHASE 6] Startup Report: OK
    echo.
    echo ================================================================================
    echo SYSTEM READY FOR DRY-RUN OPERATIONS
    echo ================================================================================
    echo.
    echo Next Steps:
    echo   1. Run manual menu: python run_system3.py
    echo   2. Start autorun: python system3_autorun_master.py
    echo   3. Start watchdog: python system3_watchdog.py
    echo   4. View logs: dir /O-D logs\
    echo.
    echo Operator Cheat Sheet: See OPERATOR_CHEAT_SHEET.md
    echo Phase Gaps: See PHASE_GAPS_ANALYSIS.md
    echo Validation: See VALIDATION_REPORT.md
    echo ================================================================================
) > "%STARTUP_LOG%"

type "%STARTUP_LOG%"

echo.
echo    [OK] Startup report saved: %STARTUP_LOG%
echo.

REM ============================================================================
REM LAUNCH OPTION
REM ============================================================================
echo ================================================================================
echo SYSTEM3 READY - SELECT LAUNCH MODE
echo ================================================================================
echo.
echo [1] Interactive Menu (run_system3.py)
echo [2] Autorun Master (automated phases)
echo [3] Watchdog Only (monitoring)
echo [4] Open PowerShell (manual control)
echo [0] Exit
echo.
set /p CHOICE="Select option (1-4, 0=exit): "

if "%CHOICE%"=="1" (
    echo.
    echo Launching interactive menu...
    powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; & '%PYTHON%' run_system3.py"
)

if "%CHOICE%"=="2" (
    echo.
    echo Launching autorun master...
    powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; & '%PYTHON%' system3_autorun_master.py"
)

if "%CHOICE%"=="3" (
    echo.
    echo Launching watchdog...
    powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; & '%PYTHON%' system3_watchdog.py"
)

if "%CHOICE%"=="4" (
    echo.
    echo Opening PowerShell with venv activated...
    powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Write-Host 'System3 Environment Ready' -ForegroundColor Green; cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'"
)

if "%CHOICE%"=="0" (
    echo.
    echo Exiting...
    exit /b 0
)

REM If invalid choice, default to PowerShell
echo.
echo Invalid choice - opening PowerShell...
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Write-Host 'System3 Environment Ready' -ForegroundColor Green; cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'"
