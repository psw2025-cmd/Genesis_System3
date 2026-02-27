@echo off
echo ================================================================================
echo   BUILDING ADVANCED EXCEL WITH AI PREDICTIONS - 1 LAKH METHOD
echo ================================================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo.
echo [STEP] Building Excel with full AI predictions and accuracy metrics...
echo.
python scripts\build_advanced_excel_with_ai_predictions.py

echo.
echo ================================================================================
echo   EXCEL BUILD COMPLETE
echo ================================================================================
echo.
echo File location: outputs\OptionChain_Master_v3_AI_FINAL.xlsx
echo.
echo Sheets created:
echo   - PNL_SUMMARY (with real data)
echo   - ACCURACY_METRICS (prediction accuracy)
echo   - AI_PREDICTIONS (top 100 predictions)
echo   - TOP_OPPORTUNITIES (best trades)
echo   - TRADE_SIGNALS (actionable signals)
echo   - OptionChain_Data (full chain data)
echo   - Summary (system overview)
echo.
pause
