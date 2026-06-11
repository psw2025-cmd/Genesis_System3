@echo off
REM System3 Launcher - Automated Environment Setup and Execution
REM Automatically detects project root and venv location
REM Logs output to logs folder with timestamp

REM Get the directory where this batch file is located (project root)
set "PROJECT_DIR=%~dp0"
REM Remove trailing backslash
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

REM Set venv directory
set "VENV_DIR=%PROJECT_DIR%\venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

REM Display detected paths
echo ========================================
echo System3 Environment Launcher
echo ========================================
echo.
echo Project Directory: %PROJECT_DIR%
echo Virtual Env:       %VENV_DIR%
echo.

REM Verify venv exists
if not exist "%VENV_DIR%\Scripts\Activate.ps1" (
    echo ERROR: Virtual environment not found at %VENV_DIR%
    echo Please ensure venv is created in the project root.
    echo.
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: venv Python not found at %PYTHON_EXE%
    echo Please repair or recreate the virtual environment.
    echo.
    pause
    exit /b 1
)

REM Create logs folder if it doesn't exist
if not exist "%PROJECT_DIR%\logs" (
    echo Creating logs directory...
    mkdir "%PROJECT_DIR%\logs"
)

REM Generate timestamp for log file (YYYY-MM-DD_HHMM format)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set LOG_TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%
set "LOG_FILE=%PROJECT_DIR%\logs\system3_%LOG_TIMESTAMP%.log"

echo Log File:          %LOG_FILE%
echo.
echo Starting System3 in PowerShell...
echo ========================================
echo.

REM Launch PowerShell with the activation and run command
REM -NoExit keeps the window open after script finishes
REM -ExecutionPolicy Bypass allows script execution
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Write-Host 'System3 Environment Activated' -ForegroundColor Green; Write-Host 'Project: %PROJECT_DIR%' -ForegroundColor Cyan; Write-Host 'Log: %LOG_FILE%' -ForegroundColor Cyan; Write-Host '========================================'; Write-Host ''; cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; & '%PYTHON_EXE%' run_system3.py 2>&1 | Tee-Object -FilePath '%LOG_FILE%'"
