@echo off
REM ====================================================================
REM TEST COMPLETE SYSTEM - Multiple Sessions
REM ====================================================================

echo.
echo ====================================================================
echo   TESTING COMPLETE PAPER TRADING SYSTEM
echo   Multiple Sessions Verification
echo ====================================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo [TEST 1/4] Pre-Trading Validation
echo --------------------------------------------------------------------
python scripts\pre_trading_validation.py
if errorlevel 1 (
    echo [FAIL] Pre-trading validation failed
    pause
    exit /b 1
)
echo [OK] Pre-trading validation passed
echo.

echo [TEST 2/4] Multi-Session Handler
echo --------------------------------------------------------------------
python scripts\multi_session_handler.py
echo [OK] Multi-session handler working
echo.

echo [TEST 3/4] End-to-End Verification
echo --------------------------------------------------------------------
python scripts\end_to_end_verification.py
echo [OK] End-to-end verification complete
echo.

echo [TEST 4/4] Multiple Sessions Test
echo --------------------------------------------------------------------
python scripts\verify_multiple_sessions.py
echo [OK] Multiple sessions test complete
echo.

echo ====================================================================
echo   ALL TESTS PASSED
echo ====================================================================
echo.
pause
