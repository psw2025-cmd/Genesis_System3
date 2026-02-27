@echo off
REM System3 Phases 101-130 Verification Test Script
REM Run this script from the project root with venv activated

echo ======================================================================
echo SYSTEM3 PHASES 101-130 - VERIFICATION TEST SCRIPT
echo ======================================================================
echo.

set "PYTHON=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] venv Python not found at %PYTHON%
    echo Please create/repair the virtual environment first.
    exit /b 1
)

REM Activate venv if not already activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo ======================================================================
echo STEP 1: Foundation Setup (Phases 101, 102, 105)
echo ======================================================================
echo.

echo [TEST] Phase 101 - Live Trade Config Check...
"%PYTHON%" -m core.engine.system3_phase101_live_trade_config_check
if errorlevel 1 (
    echo [FAILED] Phase 101
) else (
    echo [PASSED] Phase 101
)
echo.

echo [TEST] Phase 102 - Order Ledger Schema...
"%PYTHON%" -m core.engine.system3_phase102_order_ledger_schema
if errorlevel 1 (
    echo [FAILED] Phase 102
) else (
    echo [PASSED] Phase 102
)
echo.

echo [TEST] Phase 105 - Ledger Integrity Check...
"%PYTHON%" -m core.engine.system3_phase105_ledger_integrity_check
if errorlevel 1 (
    echo [FAILED] Phase 105
) else (
    echo [PASSED] Phase 105
)
echo.

echo ======================================================================
echo STEP 2: Exit Rules (Phase 110)
echo ======================================================================
echo.

echo [TEST] Phase 110 - Exit Rule Builder...
"%PYTHON%" -m core.engine.system3_phase110_exit_rule_builder
if errorlevel 1 (
    echo [FAILED] Phase 110
) else (
    echo [PASSED] Phase 110
)
echo.

echo ======================================================================
echo STEP 3: Orchestration (Phases 111, 112)
echo ======================================================================
echo.

echo [TEST] Phase 111 - Live Session Brain...
"%PYTHON%" -m core.engine.system3_phase111_live_session_brain
if errorlevel 1 (
    echo [FAILED] Phase 111
) else (
    echo [PASSED] Phase 111
)
echo.

echo [TEST] Phase 112 - Session Loop Controller...
"%PYTHON%" -m core.engine.system3_phase112_session_loop_controller
if errorlevel 1 (
    echo [FAILED] Phase 112
) else (
    echo [PASSED] Phase 112
)
echo.

echo ======================================================================
echo STEP 4: Health & Reporting (Phases 114, 115, 118, 119, 120)
echo ======================================================================
echo.

echo [TEST] Phase 114 - Live Session Health...
"%PYTHON%" -m core.engine.system3_phase114_live_session_health
if errorlevel 1 (
    echo [FAILED] Phase 114
) else (
    echo [PASSED] Phase 114
)
echo.

echo [TEST] Phase 115 - Intraday Alert Summary...
"%PYTHON%" -m core.engine.system3_phase115_intraday_alert_summary
if errorlevel 1 (
    echo [FAILED] Phase 115
) else (
    echo [PASSED] Phase 115
)
echo.

echo [TEST] Phase 118 - Daily Live PnL Snapshot...
"%PYTHON%" -m core.engine.system3_phase118_daily_live_pnl_snapshot
if errorlevel 1 (
    echo [FAILED] Phase 118
) else (
    echo [PASSED] Phase 118
)
echo.

echo [TEST] Phase 119 - Live Safety Audit...
"%PYTHON%" -m core.engine.system3_phase119_live_safety_audit
if errorlevel 1 (
    echo [FAILED] Phase 119
) else (
    echo [PASSED] Phase 119
)
echo.

echo [TEST] Phase 120 - EOD Live Summary Pack...
"%PYTHON%" -m core.engine.system3_phase120_eod_live_summary_pack
if errorlevel 1 (
    echo [FAILED] Phase 120
) else (
    echo [PASSED] Phase 120
)
echo.

echo ======================================================================
echo STEP 5: End-of-Day (Phases 116, 117)
echo ======================================================================
echo.

echo [TEST] Phase 116 - End-of-Session Auto Stop...
"%PYTHON%" -m core.engine.system3_phase116_end_session_auto_stop
if errorlevel 1 (
    echo [FAILED] Phase 116
) else (
    echo [PASSED] Phase 116
)
echo.

echo [TEST] Phase 117 - Live to Learning Bridge...
"%PYTHON%" -m core.engine.system3_phase117_live_to_learning_bridge
if errorlevel 1 (
    echo [FAILED] Phase 117
) else (
    echo [PASSED] Phase 117
)
echo.

echo ======================================================================
echo VERIFICATION TEST COMPLETE
echo ======================================================================
echo.
echo Check the output above for any [FAILED] phases.
echo All test outputs are saved to storage/live/ and logs/ directories.
echo.

pause

