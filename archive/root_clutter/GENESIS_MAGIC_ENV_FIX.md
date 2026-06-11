@echo off
setlocal ENABLEDELAYEDEXPANSION
 
:: ================================
:: GENESIS System3 Magic Env Fix
:: ================================
 
:: 1) ROOT PATHS – adjust ONLY if your folder is different
set ROOT_DIR=C:\Genesis_System3
set VENV_DIR=%ROOT_DIR%\venv
set LOG_DIR=%ROOT_DIR%\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1
 
set DATETIME=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%
set DATETIME=%DATETIME: =0%
set LOG_FILE=%LOG_DIR%\magic_env_fix_%DATETIME%.log
 
:: Simple logging helper
echo [INFO] Logging to "%LOG_FILE%"
echo === GENESIS System3 Magic Env Fix === > "%LOG_FILE%"
echo ROOT_DIR=%ROOT_DIR% >> "%LOG_FILE%"
echo VENV_DIR=%VENV_DIR% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
 
:: 2) BASIC CHECKS
if not exist "%ROOT_DIR%" (
    echo [ERROR] ROOT_DIR "%ROOT_DIR%" does not exist. >> "%LOG_FILE%"
    echo [ERROR] ROOT_DIR "%ROOT_DIR%" does not exist.
    echo Edit ROOT_DIR in this BAT file if your project path is different.
    goto :END
)
 
cd /d "%ROOT_DIR%"
echo [INFO] Current directory: %CD% >> "%LOG_FILE%"
 
:: 3) KILL STALE PYTHON PROCESSES FROM THIS VENV (if any)
echo [STEP] Killing stale python processes from this venv (if any)... >> "%LOG_FILE%"
for /f "tokens=2 delims=," %%P in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2^>NUL') do (
    rem We cannot reliably detect venv path here without tools, so just log
    echo   Found python.exe PID=%%P (not killing to stay safe) >> "%LOG_FILE%"
)
echo   (No forced kill done; this is a safe read-only check.) >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
 
:: 4) CHECK SYSTEM PYTHON
echo [STEP] Checking system Python... >> "%LOG_FILE%"
where python >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] No python.exe found in PATH. >> "%LOG_FILE%"
    echo [ERROR] Python not found in PATH. Install Python 3.10+ and retry.
    goto :END
)
 
python -V >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%"
 
:: 5) ENSURE VENV EXISTS
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [STEP] Venv not found, creating new venv at "%VENV_DIR%"... >> "%LOG_FILE%"
    python -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to create venv at "%VENV_DIR%". >> "%LOG_FILE%"
        echo See log: "%LOG_FILE%"
        goto :END
    )
) else (
    echo [STEP] Existing venv detected at "%VENV_DIR%". >> "%LOG_FILE%"
)
 
:: 6) ACTIVATE VENV
echo [STEP] Activating venv... >> "%LOG_FILE%"
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate venv. >> "%LOG_FILE%"
    goto :END
)
 
:: 7) UPGRADE PIP (SAFE)
echo [STEP] Upgrading pip... >> "%LOG_FILE%"
python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
 
:: 8) INSTALL PROJECT REQUIREMENTS (IF FILE EXISTS)
if exist "%ROOT_DIR%\requirements.txt" (
    echo [STEP] Installing requirements from requirements.txt... >> "%LOG_FILE%"
    python -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
) else (
    echo [WARN] requirements.txt not found – skipping bulk install. >> "%LOG_FILE%"
)
 
:: 9) QUICK HEALTH CHECK: CORE LIBRARIES
echo [STEP] Running quick library import test... >> "%LOG_FILE%"
python -c "import numpy, pandas, sklearn, xgboost; print('GENESIS_LIB_CHECK_OK')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [WARN] Library import test failed. See log for details. >> "%LOG_FILE%"
) else (
    echo [INFO] Library import test passed. >> "%LOG_FILE%"
)
 
:: 10) OPTIONAL: SIMPLE SYSTEM3 ENV CHECK
if exist "%ROOT_DIR%\tools\system3_env_health_check.py" (
    echo [STEP] Running tools\system3_env_health_check.py... >> "%LOG_FILE%"
    python tools\system3_env_health_check.py >> "%LOG_FILE%" 2>&1
) else (
    echo [INFO] tools\system3_env_health_check.py not found – skipping env script. >> "%LOG_FILE%"
)
 
:: 11) FINAL HINTS FOR VS CODE / COPILOT AGENT
echo. >> "%LOG_FILE%"
echo [INFO] MAGIC ENV FIX COMPLETED. >> "%LOG_FILE%"
echo [INFO] Next manual steps for VS Code agent: >> "%LOG_FILE%"
echo   1) Open VS Code in "%ROOT_DIR%" >> "%LOG_FILE%"
echo   2) Ensure bottom-right Python interpreter is: "%VENV_DIR%\Scripts\python.exe" >> "%LOG_FILE%"
echo   3) Make sure GitHub Copilot / Copilot Chat / Agents extensions are enabled and signed-in. >> "%LOG_FILE%"
echo   4) If agent is still silent, run: Command Palette -> 'Developer: Reload Window'. >> "%LOG_FILE%"
 
echo.
echo ===========================================
echo  GENESIS Magic Env Fix finished.
echo  Log file: "%LOG_FILE%"
echo ===========================================
echo.
echo Now:
echo   1) Start VS Code in C:\Genesis_System3 (or reopen window)
echo   2) In VS Code, select Python interpreter from venv:
echo      %VENV_DIR%\Scripts\python.exe
echo   3) Check that Copilot Agent shows "Connected" and responds.
 
:END
endlocal
 