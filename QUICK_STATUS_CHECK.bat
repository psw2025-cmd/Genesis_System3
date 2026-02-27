@echo off
REM ====================================================================
REM QUICK STATUS CHECK - Check current system status
REM ====================================================================

title Quick Status Check

cd /d "%~dp0"

echo.
echo ====================================================================
echo   QUICK STATUS CHECK
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs

echo [INFO] Checking file status...
echo.

venv\Scripts\python.exe -c "from pathlib import Path; from datetime import datetime; import json; outputs = Path('outputs'); files = ['chain_raw_live.csv', 'pnl_live.json', 'positions_live.json', 'top_trade_signal.json']; print('File Status:'); print('-' * 80); [print(f\"{f}: {'EXISTS' if (outputs/f).exists() else 'MISSING'} - Age: {((datetime.now().timestamp() - (outputs/f).stat().st_mtime)/60):.1f} min\" if (outputs/f).exists() else f\"{f}: MISSING\") for f in files]; print('-' * 80); pnl = outputs/'pnl_live.json'; print(f\"PnL Data: {json.load(open(pnl)) if pnl.exists() else 'EMPTY'}\"); pos = outputs/'positions_live.json'; print(f\"Positions: {len(json.load(open(pos)).get('open_positions', []))} open\" if pos.exists() and json.load(open(pos)) else 'EMPTY')"

echo.
echo ====================================================================
echo   STATUS CHECK COMPLETE
echo ====================================================================
echo.
pause
