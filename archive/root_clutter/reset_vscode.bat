@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM  MAGIC_COPILOT_VISION_FIX.bat
REM  Fix for: Request Failed: 400 {"code":"vision_attachment_not_accessible"}
REM  What it does:
REM   1) Closes VS Code
REM   2) Backs up VS Code user settings
REM   3) Clears Copilot/Copilot Chat storage + caches
REM   4) Reinstalls Copilot extensions
REM   5) Repairs TEMP folder permissions (common attachment staging area)
REM   6) Generates a detailed log report
REM ============================================================

set "TS=%DATE:~-4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "TS=%TS: =0%"
set "LOGDIR=%~dp0logs"
set "LOG=%LOGDIR%\copilot_vision_fix_%TS%.log"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

call :log "=== MAGIC COPILOT VISION FIX START ==="
call :log "Timestamp: %TS%"
call :log "User: %USERNAME%"
call :log "Computer: %COMPUTERNAME%"
call :log "TEMP: %TEMP%"
call :log "APPDATA: %APPDATA%"

REM ---- Locate VS Code CLI (code.cmd) ----
set "CODECLI="
if exist "%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd" set "CODECLI=%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd"
if exist "%ProgramFiles%\Microsoft VS Code\bin\code.cmd" set "CODECLI=%ProgramFiles%\Microsoft VS Code\bin\code.cmd"
if exist "%ProgramFiles(x86)%\Microsoft VS Code\bin\code.cmd" set "CODECLI=%ProgramFiles(x86)%\Microsoft VS Code\bin\code.cmd"

if "%CODECLI%"=="" (
  call :log "ERROR: VS Code CLI not found (code.cmd)."
  call :log "Install/repair VS Code, then re-run."
  echo.
  echo VS Code CLI not found. Install/repair VS Code and re-run.
  exit /b 1
)

call :log "VS Code CLI: %CODECLI%"

REM ---- Close VS Code ----
call :log "Closing VS Code (Code.exe)..."
taskkill /F /IM Code.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM ---- Backup settings.json ----
set "USERDIR=%APPDATA%\Code\User"
set "SETTINGS=%USERDIR%\settings.json"
set "BACKUPDIR=%LOGDIR%\backup_%TS%"
mkdir "%BACKUPDIR%" >nul 2>&1

if exist "%SETTINGS%" (
  copy /y "%SETTINGS%" "%BACKUPDIR%\settings.json.bak" >nul 2>&1
  call :log "Backed up settings.json to %BACKUPDIR%"
) else (
  call :log "No settings.json found (OK)."
)

REM ---- Save extension list ----
call :log "Exporting extension list..."
"%CODECLI%" --list-extensions > "%BACKUPDIR%\extensions_list.txt" 2>nul
call :log "Saved extensions list to %BACKUPDIR%\extensions_list.txt"

REM ---- Uninstall Copilot extensions ----
call :log "Uninstalling Copilot extensions (if present)..."
"%CODECLI%" --uninstall-extension github.copilot        --force >nul 2>&1
"%CODECLI%" --uninstall-extension github.copilot-chat   --force >nul 2>&1
"%CODECLI%" --uninstall-extension github.copilot-nightly --force >nul 2>&1
"%CODECLI%" --uninstall-extension github.copilot-chat-nightly --force >nul 2>&1

REM ---- Clear Copilot storage/caches ----
set "GLOBAL=%APPDATA%\Code\User\globalStorage"
set "WSSTORE=%APPDATA%\Code\User\workspaceStorage"
set "CACHES=%APPDATA%\Code\Cache"
set "CACHED=%APPDATA%\Code\CachedData"

call :log "Clearing Copilot globalStorage..."
call :rmdir_safe "%GLOBAL%\github.copilot"
call :rmdir_safe "%GLOBAL%\github.copilot-chat"
call :rmdir_safe "%GLOBAL%\github.copilot-nightly"
call :rmdir_safe "%GLOBAL%\github.copilot-chat-nightly"

REM Some builds store under these IDs too
for /d %%D in ("%GLOBAL%\*copilot*") do (
  call :log "Found Copilot-like storage: %%~fD"
)

REM ---- Clear workspace storage entries that mention copilot (safe targeted pass) ----
call :log "Scanning workspaceStorage for Copilot remnants (targeted delete)..."
if exist "%WSSTORE%" (
  for /d %%W in ("%WSSTORE%\*") do (
    if exist "%%W\state.vscdb" (
      findstr /i /m "copilot github.copilot copilot-chat" "%%W\state.vscdb" >nul 2>&1
      if !errorlevel!==0 (
        call :log "Deleting workspaceStorage folder (Copilot hit): %%~fW"
        call :rmdir_safe "%%~fW"
      )
    )
  )
)

REM ---- Repair TEMP permissions (attachment staging often uses TEMP) ----
call :log "Repairing TEMP folder ACL (current user full control)..."
icacls "%TEMP%" /grant "%USERNAME%":(OI)(CI)F /T /C >nul 2>&1

REM ---- Quick TEMP write test ----
call :log "TEMP write test..."
echo test>"%TEMP%\copilot_temp_test_%TS%.txt" 2>nul
if exist "%TEMP%\copilot_temp_test_%TS%.txt" (
  del /f /q "%TEMP%\copilot_temp_test_%TS%.txt" >nul 2>&1
  call :log "TEMP write test: OK"
) else (
  call :log "TEMP write test: FAILED (permissions or AV policy). This can cause attachment failures."
)

REM ---- Reinstall Copilot extensions ----
call :log "Reinstalling Copilot extensions..."
"%CODECLI%" --install-extension github.copilot      --force >nul 2>&1
"%CODECLI%" --install-extension github.copilot-chat --force >nul 2>&1

REM ---- Show VS Code + extension versions in log ----
call :log "VS Code version:"
"%CODECLI%" --version >> "%LOG%" 2>&1
call :log "Copilot extensions after reinstall:"
"%CODECLI%" --list-extensions --show-versions | findstr /i "copilot" >> "%LOG%" 2>&1

REM ---- Launch VS Code ----
call :log "Launching VS Code..."
start "" "%CODECLI%"

call :log "=== MAGIC COPILOT VISION FIX END ==="
echo.
echo DONE.
echo Log file: "%LOG%"
echo.
echo IMPORTANT (1 minute):
echo 1) In VS Code, press Ctrl+Shift+P
echo 2) Run: "GitHub Copilot: Sign Out" then sign in again (required once)
echo 3) Try attaching the image again.
echo.
echo If it still fails, copy the image file to: %TEMP% and attach from there.
echo (Some setups block attachments from protected folders/clipboard.)
echo.
exit /b 0

REM ===================== helpers =====================
:log
>>"%LOG%" echo [%DATE% %TIME%] %~1
echo %~1
exit /b 0

:rmdir_safe
set "TARGET=%~1"
if exist "%TARGET%" (
  attrib -r -s -h "%TARGET%" /s /d >nul 2>&1
  rmdir /s /q "%TARGET%" >nul 2>&1
  if exist "%TARGET%" (
    call :log "WARN: Could not fully remove: %TARGET%"
  ) else (
    call :log "Removed: %TARGET%"
  )
) else (
  call :log "Skip (not found): %TARGET%"
)
exit /b 0
