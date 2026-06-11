@echo off
REM ============================================================================
REM System3 Thresholds Upgrade - Complete Workflow
REM ============================================================================
REM This batch file runs the complete threshold upgrade workflow:
REM   1. Phase 221: Generate forward returns
REM   2. Phase 222: Compute EV tables
REM   3. Threshold Proposer: Generate thresholds
REM   4. Test Mode: Validate thresholds
REM   5. Summary: Show results
REM ============================================================================

setlocal enabledelayedexpansion

set "PYTHON=%~dp0venv\Scripts\python.exe"

echo.
echo ============================================================================
echo SYSTEM3 THRESHOLDS UPGRADE - COMPLETE WORKFLOW
echo ============================================================================
echo.
echo Date: %date% %time%
echo.

if not exist "%PYTHON%" (
    echo [ERROR] venv Python not found at %PYTHON%
    echo Please create/repair the virtual environment first.
    pause
    exit /b 1
)

REM Check if venv is activated
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not available. Please activate venv first.
    echo.
    echo To activate venv, run:
    echo   venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM ============================================================================
REM STEP 1: Phase 221 - Forward Returns Calculator
REM ============================================================================
echo ============================================================================
echo STEP 1: PHASE 221 - FORWARD RETURNS CALCULATOR
echo ============================================================================
echo.

"%PYTHON%" core\engine\system3_phase221_forward_returns.py
if errorlevel 1 (
    echo.
    echo [ERROR] Phase 221 failed. Check errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Phase 221 completed successfully
echo.

REM ============================================================================
REM STEP 2: Phase 222 - Signal Edge Estimator
REM ============================================================================
echo ============================================================================
echo STEP 2: PHASE 222 - SIGNAL EDGE ESTIMATOR
echo ============================================================================
echo.

"%PYTHON%" core\engine\system3_phase222_signal_edge.py
if errorlevel 1 (
    echo.
    echo [ERROR] Phase 222 failed. Check errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Phase 222 completed successfully
echo.

REM ============================================================================
REM STEP 3: Threshold Proposer
REM ============================================================================
echo ============================================================================
echo STEP 3: THRESHOLD PROPOSER
echo ============================================================================
echo.

"%PYTHON%" core\engine\system3_threshold_proposer.py
if errorlevel 1 (
    echo.
    echo [ERROR] Threshold proposer failed. Check errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Threshold proposer completed successfully
echo.

REM ============================================================================
REM STEP 4: Test Mode - Validate Thresholds
REM ============================================================================
echo ============================================================================
echo STEP 4: TEST MODE - VALIDATE THRESHOLDS
echo ============================================================================
echo.

echo Running test mode with auto-thresholds...
"%PYTHON%" system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds
if errorlevel 1 (
    echo.
    echo [WARN] Test mode with auto-thresholds had issues. Continuing...
    echo.
) else (
    echo.
    echo [OK] Test mode with auto-thresholds completed
    echo.
)

echo Running test mode with live-thresholds...
"%PYTHON%" system3_signal_test_mode.py --lookback-snapshots 200 --use-live-thresholds
if errorlevel 1 (
    echo.
    echo [WARN] Test mode with live-thresholds had issues. Continuing...
    echo.
) else (
    echo.
    echo [OK] Test mode with live-thresholds completed
    echo.
)

echo Running test mode with BOTH flags to generate comparison...
"%PYTHON%" system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds --use-live-thresholds
if errorlevel 1 (
    echo.
    echo [WARN] Test mode comparison had issues. Continuing...
    echo.
) else (
    echo.
    echo [OK] Test mode comparison completed
    echo.
)

REM ============================================================================
REM STEP 5: Summary and Results
REM ============================================================================
echo ============================================================================
echo STEP 5: SUMMARY AND RESULTS
echo ============================================================================
echo.

echo [INFO] Checking generated files...
echo.

REM Check forward returns file
if exist "storage\live\angel_index_ai_signals_with_forward.csv" (
    echo [OK] Forward returns file exists: storage\live\angel_index_ai_signals_with_forward.csv
) else (
    echo [WARN] Forward returns file not found
)

REM Check EV report
if exist "logs\research\system3_signal_edge_report.md" (
    echo [OK] EV report exists: logs\research\system3_signal_edge_report.md
) else (
    echo [WARN] EV report not found
)

REM Check live thresholds
if exist "storage\meta\system3_live_thresholds.json" (
    echo [OK] Live thresholds file exists: storage\meta\system3_live_thresholds.json
    echo.
    echo [INFO] Thresholds loaded:
    "%PYTHON%" -c "import json; data = json.load(open('storage/meta/system3_live_thresholds.json')); print('  Global:', data.get('global', {})); print('  Per-underlying:', list(data.get('per_underlying', {}).keys()))"
) else (
    echo [WARN] Live thresholds file not found
)

REM Check comparison report
if exist "docs\system3_thresholds_comparison.md" (
    echo [OK] Comparison report exists: docs\system3_thresholds_comparison.md
) else (
    echo [INFO] Comparison report not generated (run both --auto-thresholds and --use-live-thresholds to generate)
)

echo.
echo ============================================================================
echo WORKFLOW COMPLETE
echo ============================================================================
echo.
echo Next steps:
echo   1. Review EV tables in: logs\research\system3_signal_edge_report.md
echo   2. Review thresholds in: storage\meta\system3_live_thresholds.json
echo   3. Review comparison in: docs\system3_thresholds_comparison.md
echo   4. Monitor signal generation with new thresholds
echo.
echo The signal engine will automatically use the new thresholds from
echo system3_live_thresholds.json on the next signal generation cycle.
echo.
pause

