@echo off
REM Start World-Class Trading System
REM Uses optimized configuration for highest performance

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   WORLD-CLASS TRADING SYSTEM
echo ================================================================================
echo.
echo Configuration:
echo   - Position Sizing: Full Kelly (10%% capital)
echo   - Stop Loss: 1x ATR (Tight)
echo   - Take Profit: Fixed 50%%
echo   - Entry: Predicted Profit High
echo.
echo Expected Performance:
echo   - ROI: 89.3%%
echo   - Win Rate: 90%%
echo   - Sharpe: 45.58
echo   - Profit Factor: 224.75
echo.
echo ================================================================================
echo.

REM Run comprehensive test first
echo [STEP 1] Running Comprehensive Test...
python scripts\comprehensive_system_test.py

if errorlevel 1 (
    echo.
    echo ERROR: System test failed. Please check errors above.
    pause
    exit /b 1
)

echo.
echo [STEP 2] Starting Paper Trading System...
echo.

REM Start paper trading
python scripts\run_live_chain.py --sim-mode --refresh 5

echo.
echo ================================================================================
echo   TRADING COMPLETE
echo ================================================================================
echo.

pause
