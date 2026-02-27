@echo off
REM System3 Post-Close Signal Consistency Audit
REM Verifies logged signals are consistent with thresholds

call C:\Genesis_System3\venv\Scripts\activate.bat
C:\Genesis_System3\venv\Scripts\python.exe core\validation\post_close_signal_audit.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo AUDIT FAILED - Review inconsistencies in report
    echo ================================================================================
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo AUDIT COMPLETE - Check report for details
    echo ================================================================================
    exit /b 0
)

