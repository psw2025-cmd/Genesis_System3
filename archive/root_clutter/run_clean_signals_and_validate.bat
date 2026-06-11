@echo off
REM System3 CSV Cleaning and Validation Pipeline Runner
REM This script runs the complete cleaning and validation pipeline

cd /d C:\Genesis_System3
call venv\Scripts\activate.bat

echo ================================================================================
echo SYSTEM3 CSV CLEANING AND VALIDATION PIPELINE
echo ================================================================================
echo.

REM Step 1: Schema Audit
echo [1/4] Running schema audit...
C:\Genesis_System3\venv\Scripts\python.exe -m core.tools.schema_audit
if errorlevel 1 (
    echo ERROR: Schema audit failed
    pause
    exit /b 1
)
echo.

REM Step 2: Cleaning Pipeline
echo [2/4] Running cleaning pipeline...
C:\Genesis_System3\venv\Scripts\python.exe -m core.tools.clean_angel_signals_csv
if errorlevel 1 (
    echo ERROR: Cleaning pipeline failed
    pause
    exit /b 1
)
echo.

REM Step 3: Validation
echo [3/4] Running validation...
C:\Genesis_System3\venv\Scripts\python.exe -m core.tools.validate_clean_csv
if errorlevel 1 (
    echo ERROR: Validation failed
    pause
    exit /b 1
)
echo.

REM Step 4: Summary
echo [4/4] Pipeline Summary
echo ================================================================================
echo.
echo Clean files generated:
echo   - storage\clean\angel_index_ai_signals_with_forward_clean.csv
echo   - storage\clean\angel_index_ai_signals_with_forward_ev_ready.csv
echo   - storage\clean\angel_index_ai_signals_sell_anomalies.csv (if anomalies found)
echo.
echo Reports generated:
echo   - docs\SYSTEM3_CSV_SCHEMA_AUTOMATED.md
echo   - docs\SYSTEM3_CSV_CLEAN_VALIDATION_SUMMARY.md
echo.
echo ================================================================================
echo PIPELINE COMPLETE
echo ================================================================================
echo.
pause

