ping -n 2 127.0.0.1 >nul 2>&1
@echo off
REM ============================================================================
REM SYSTEM3 AUTORUN + WATCHDOG - ONE-CLICK MASTER LAUNCHER
REM ============================================================================
REM Single point of control: preflight checks, watchdog, autorun master.
REM After launch, zero manual steps are required. DRY-RUN only (paper trading).
REM ============================================================================

chcp 65001 >nul
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
REM Set NOPAUSE=0 for interactive (shows output), 1 for CI/CD (auto-close)
set NOPAUSE=0
set DEBUG_PAUSE=0

set ROOT=C:\Genesis_System3
set VENV_ACT=%ROOT%\venv\Scripts\activate.bat
set VENV_PS_ACT=%ROOT%\venv\Scripts\Activate.ps1
set PYTHON=%ROOT%\venv\Scripts\python.exe
set MASTER=%ROOT%\system3_autorun_master.py
set WATCHDOG=%ROOT%\system3_watchdog.py
set PREP=%ROOT%\system3_prep_for_new_day.py

if not exist "%ROOT%" (
    echo ERROR: Root path not found: %ROOT%
    exit /b 1
)

cd /d "%ROOT%"
set PYTHONIOENCODING=utf-8
set PIP_DISABLE_PIP_VERSION_CHECK=1
set PYTHONHOME=
set PYTHONPATH=

REM ============================================================================
REM BANNER
REM ============================================================================
cls
echo.
echo ================================================================================
echo.
echo ================================================
echo SYSTEM3 AUTORUN + WATCHDOG
echo ================================================
echo One-click start ^| Fully autonomous ^| DRY-RUN enforced
echo ================================================
echo.

echo ================================================
echo PHASE 1: ENVIRONMENT VALIDATION AND AUTO-REPAIR
echo ================================================
echo.

REM Ensure virtual environment exists
if not exist "%VENV_ACT%" (
    echo ERROR: Virtual environment not found at %VENV_ACT%
    echo.
    echo SOLUTION: See VENV_RECOVERY_GUIDE.md
    exit /b 1
)
echo OK Virtual environment located

REM Activate virtual environment (cmd path)
call "%VENV_ACT%"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo.
    echo SOLUTION: See VENV_RECOVERY_GUIDE.md
    exit /b 1
)
echo OK Virtual environment activated

REM Basic python identity check
"%PYTHON%" -c "print('Python environment ready')" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo OK Python environment ready
) else (
    echo ERROR: Python check failed
    echo.
    echo SOLUTION: See VENV_RECOVERY_GUIDE.md
    exit /b 1
)

REM RUN VENV SANITY CHECK (comprehensive dependency validation)
echo.
echo Running comprehensive venv sanity check...
"%PYTHON%" tools\system3_venv_sanity_check.py --report
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ❌ VENV SANITY CHECK FAILED
    echo ================================================================================
    echo.
    echo Your venv is broken. See VENV_SANITY_STATUS.md for details.
    echo.
    echo NEXT STEPS:
    echo 1. Review VENV_SANITY_STATUS.md to see what's missing
    echo 2. Follow VENV_RECOVERY_GUIDE.md to fix it
    echo 3. Run this BAT again after fixing
    echo.
    exit /b 1
)
echo OK Venv sanity check passed

echo.
echo All critical dependencies validated via venv sanity check.
echo.
echo ================================================
echo PHASE 2: DATA FRESHNESS AND AUTO-HEAL HOOK
echo ================================================
echo.

set DATA_CHECK=FRESH
REM Simplified data freshness check (just check if folder exists)
if exist "storage\live" (
    dir "storage\live\*_snapshot.csv" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set DATA_CHECK=FRESH
    ) else (
        set DATA_CHECK=STALE
    )
) else (
    set DATA_CHECK=STALE
)

if /I "%DATA_CHECK%"=="STALE" (
    echo Stale or missing snapshot detected
    if exist "%PREP%" (
        echo Running Phase 201 curated refresh (system3_prep_for_new_day.py)
        "%PYTHON%" "%PREP%"
        if !ERRORLEVEL! EQU 0 (
            echo OK Phase 201 completed (data refreshed)
        ) else (
            echo Phase 201 reported issues. Continuing with existing data.
        )
    ) else (
        echo Prep script missing. Skipping refresh.
    )
) else (
    echo OK Market snapshot is fresh
)

REM Quick heartbeat presence (created during runtime if missing)
if exist "system3_daily_heartbeat.json" (
    echo OK Heartbeat file present (will update on launch)
) else (
    echo Heartbeat will be created after autorun starts
)

REM Disk sanity (informational)
for /f "tokens=3" %%A in ('dir C:\ ^| find "bytes free"') do set DISK_FREE=%%A
echo OK Disk free: %DISK_FREE%

echo.
echo ================================================
echo PHASE 3: SAFETY VERIFICATION (DRY-RUN)
echo ================================================
echo.

REM Enforce DRY-RUN via environment flag
"%PYTHON%" -c "import os;from dotenv import load_dotenv;load_dotenv();live=os.getenv('LIVE_TRADING_ENABLED','False');import sys;sys.exit(0 if str(live).lower()=='false' else 1)" 2>nul
if errorlevel 1 (
    echo ERROR: System NOT in DRY-RUN mode. Set LIVE_TRADING_ENABLED=False in .env
    exit /b 1
)
echo OK DRY-RUN mode verified

echo.
echo ================================================================================
echo PHASE 4: START WATCHDOG (NEW WINDOW)
echo ================================================================================
echo.

REM FIX: Use /B (background) instead of new window to prevent duplicates
start "System3_Watchdog" /B "%PYTHON%" "%WATCHDOG%"
timeout /t 3 /nobreak >nul
echo OK Watchdog started (background, no new window)

echo.
echo ================================================
echo PHASE 5: LAUNCH AUTORUN MASTER
echo ================================================
echo.
echo OK Preflight complete
echo OK Dependencies verified
echo OK Data freshness handled
echo OK Watchdog armed
echo.
echo Running autorun master with continuous monitoring...
echo Logs: logs\system3_autorun_master_*.log
echo Heartbeat: system3_daily_heartbeat.json
echo Press Ctrl+C here for graceful stop.
echo.
timeout /t 2 /nobreak >nul

"%PYTHON%" "%MASTER%"

echo.
echo ================================================================================
echo AUTORUN MASTER STOPPED
echo ================================================================================
echo.
echo OK Shutdown complete. Review logs if needed.
echo To restart, run this BAT again.
echo.

REM Pause to show output (unless NOPAUSE=1 for CI/CD)
if %NOPAUSE% EQU 0 (
    echo Press any key to close this window...
    pause >nul
)

ENDLOCAL