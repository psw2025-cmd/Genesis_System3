@echo off
REM Run the System3 paper-trading E2E test using the project's venv
REM Usage: run this from the repository root (double-click or run in PowerShell/CMD)

REM Use UTF-8 for console and Python I/O to avoid UnicodeEncodeError on Windows
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
setlocal enabledelayedexpansion
cd /d %~dp0
set "PYTHON=%~dp0venv\Scripts\python.exe"

REM Ensure logs/inspector exists
if not exist "logs\inspector" mkdir "logs\inspector"

REM Check if Python script exists
if not exist "tools\run_paper_trading_e2e_test.py" (
  echo ERROR: tools\run_paper_trading_e2e_test.py not found!
  echo Please ensure you're running from the repository root.
  pause
  exit /b 2
)

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
) else (
  echo Virtual environment not found at venv\Scripts\activate.bat
  echo Please create/activate your venv and retry.
  pause
  exit /b 2
)

if not exist "%PYTHON%" (
  echo [ERROR] venv Python not found at %PYTHON%
  echo Please create/repair the virtual environment and retry.
  pause
  exit /b 2
)

echo Checking Python syntax for tools\run_paper_trading_e2e_test.py ...
"%PYTHON%" -m py_compile "tools\run_paper_trading_e2e_test.py" 2> "logs\inspector\compile_err.txt"
if %ERRORLEVEL% NEQ 0 (
  echo Compilation failed. See logs\inspector\compile_err.txt for details.
  echo.
  type "logs\inspector\compile_err.txt"
  pause
  exit /b 2
)

echo Compilation OK. Running E2E test now...
"%PYTHON%" "tools\run_paper_trading_e2e_test.py" > "logs\inspector\e2e_run_stdout.txt" 2> "logs\inspector\e2e_run_stderr.txt"
set rc=%ERRORLEVEL%

echo.
echo E2E script finished with exit code %rc%
echo Contents of logs\inspector:
dir "logs\inspector" /b

echo.
REM Find latest report file (e2e_test_report_*.md) and display first 200 lines
set "latest="
for /f "delims=" %%F in ('dir "logs\inspector\e2e_test_report_*.md" /b /od 2^>nul') do set "latest=%%F"
if defined latest (
  echo Showing head of %latest%:
  powershell -Command "Get-Content -Path 'logs\inspector\%latest%' -TotalCount 200"
) else (
  echo No report file found matching logs\inspector\e2e_test_report_*.md
  echo.
)

echo.
echo Standard output (last 200 lines):
powershell -Command "Get-Content -Path 'logs\inspector\e2e_run_stdout.txt' -Tail 200"
echo.
echo Standard error (last 200 lines):
powershell -Command "Get-Content -Path 'logs\inspector\e2e_run_stderr.txt' -Tail 200"

echo.
echo Done. Exit code %rc%
pause
exit /b %rc%
