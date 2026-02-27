@echo off
echo ================================================================================
echo   COMPREHENSIVE END-TO-END VERIFICATION
echo ================================================================================
echo.
echo This will verify:
echo   1. All indices data fetching (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)
echo   2. All calculations correctness (pOI, pVolume, Greeks, etc.)
echo   3. Paper trading functionality
echo   4. Parallel processing capability
echo   5. Multi-validation checks
echo   6. QC audit
echo   7. End-to-end process
echo.
echo ================================================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

echo [STEP 1] Running Comprehensive End-to-End Verification...
echo.
venv\Scripts\python.exe scripts\comprehensive_end_to_end_verification.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Verification failed. Check output above.
    pause
    exit /b 1
)

echo.
echo [STEP 2] Verifying Parallel Processing...
echo.
venv\Scripts\python.exe scripts\verify_parallel_processing.py

echo.
echo ================================================================================
echo   VERIFICATION COMPLETE
echo ================================================================================
echo.
echo Check outputs/verification_results.json for detailed results.
echo.
pause
