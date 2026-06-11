@echo off
REM ====================================================================
REM RUN TRADING ENGINE - Wrapper to ensure output is visible
REM ====================================================================

cd /d "%~dp0"

echo.
echo ====================================================================
echo   PAPER TRADING ENGINE - STARTING
echo ====================================================================
echo.
echo Current directory: %CD%
echo.

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Location: %CD%\venv\Scripts\activate.bat
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Check Python script exists
if not exist "scripts\smart_live_chain_runner.py" (
    echo [ERROR] Script not found!
    echo Location: %CD%\scripts\smart_live_chain_runner.py
    pause
    exit /b 1
)

echo Running Python script...
echo Command: python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket
echo.
echo ====================================================================
echo.

REM Run the script with unbuffered output
echo.
echo Executing Python script now...
echo.
python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket
set PYTHON_EXIT_CODE=%ERRORLEVEL%

REM If script exits, show message
echo.
echo ====================================================================
if %PYTHON_EXIT_CODE% EQU 0 (
    echo   SCRIPT FINISHED (Exit code: 0)
) else (
    echo   SCRIPT EXITED WITH ERROR (Exit code: %PYTHON_EXIT_CODE%)
)
echo ====================================================================
echo.
echo If you see this message, the Python script has stopped.
echo This should NOT happen - the script should run continuously.
echo.
echo Check the output above for error messages.
echo.
pause
