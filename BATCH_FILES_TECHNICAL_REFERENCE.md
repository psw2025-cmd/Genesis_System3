# BATCH FILES TECHNICAL DEEP DIVE - FOR DEVELOPERS

**Generated:** December 6, 2025  
**Audience:** Developers, DevOps, system maintainers

---

## TABLE OF CONTENTS

1. [Batch Architecture Patterns](#batch-architecture-patterns)
2. [Variable Scoping & Environment](#variable-scoping--environment)
3. [Error Handling & Exit Codes](#error-handling--exit-codes)
4. [Subprocess Management](#subprocess-management)
5. [File I/O & Logging](#file-io--logging)
6. [Venv Activation Patterns](#venv-activation-patterns)
7. [PowerShell Integration](#powershell-integration)
8. [Code Quality Issues](#code-quality-issues)
9. [Performance Analysis](#performance-analysis)
10. [Testing Checklist](#testing-checklist)

---

## BATCH ARCHITECTURE PATTERNS

### Pattern 1: Sequential Phase Execution (START_AUTORUN_AND_WATCHDOG.bat)

**Model:** Linear waterfall with mandatory gating

```batch
REM Phase 1: Gate-keeper (must pass)
if not exist "%VENV_ACT%" (
    echo ERROR: ...
    exit /b 1
)

REM Phase 2: Dependency loop (auto-repair)
for %%m in (psutil pandas numpy joblib) do (
    "%PYTHON%" -c "import %%m" 2>nul
    if errorlevel 1 (
        echo Installing %%m ...
        pip install %%m --quiet
        if errorlevel 1 (
            echo ERROR: Failed to install %%m
            exit /b 1
        )
    )
)

REM Phase 3: Data validation (soft check)
if /I "%DATA_CHECK%"=="STALE" (
    if exist "%PREP%" (
        echo Running Phase 201 refresh...
        "%PYTHON%" "%PREP%"
    )
)

REM Phase 4: Spawn subprocess (asynchronous)
start "System3 Watchdog" cmd /k "..."

REM Phase 5: Block on main process
"%PYTHON%" "%MASTER%"
```

**Execution Model:**
```
┌─────────────┐
│   Phase 1   │ (exit 1 on failure)
├─────────────┤
│   Phase 2   │ (exit 1 on failure)
├─────────────┤
│   Phase 3   │ (continue on failure)
├─────────────┤
│   Phase 4   │ (spawn async)
│   Phase 5   │ (block until exit)
└─────────────┘
```

**Characteristics:**
- Hard gates: Phases 1-2 exit batch on failure
- Soft checks: Phases 3+ continue on failure (non-blocking)
- Async spawn: Phase 4 starts new window independently
- Blocking I/O: Phase 5 waits for user Ctrl+C or process crash

**Risk:** If Phase 4 fails to spawn, Phase 5 has no watchdog oversight.

---

### Pattern 2: Dependency Loop with Auto-Repair (SYSTEM3_DAILY_START.bat)

**Model:** Conditional installation with retry

```batch
set DEP_ERRORS=0
for %%m in (psutil pandas numpy joblib dotenv) do (
    "%PYTHON%" -c "import %%m" 2>nul
    if errorlevel 1 (
        echo [MISSING] %%m - Installing...
        "%PYTHON%" -m pip install %%m --quiet
        if errorlevel 1 (
            echo [ERROR] Failed to install %%m
            set DEP_ERRORS=1
        ) else (
            echo [OK] %%m installed
        )
    ) else (
        echo [OK] %%m
    )
)

if %DEP_ERRORS%==1 (
    echo.
    echo ERROR: Some dependencies failed.
    exit /b 1
)
```

**Key Points:**
- Uses `errorlevel` (not `%ERRORLEVEL%`  – delayed expansion)
- Non-quoted module names in loop (%%m works in cmd batch)
- Accumulates errors in variable (DEP_ERRORS) for batch-level decision
- Exits 1 only if **any** dependency fails

**Risk:** If pip install has transient network failure, batch fails entirely (no retry logic).

---

### Pattern 3: Menu-Driven Dispatch (SYSTEM3_DAILY_START.bat)

**Model:** User selection → conditional execution

```batch
echo ================================================================================
echo SYSTEM3 READY - SELECT LAUNCH MODE
echo ================================================================================
echo.
echo [1] Interactive Menu (run_system3.py)
echo [2] Autorun Master (automated phases)
echo [3] Watchdog Only (monitoring)
echo [4] Open PowerShell (manual control)
echo [0] Exit
echo.
set /p CHOICE="Select option (1-4, 0=exit): "

if "%CHOICE%"=="1" (
    echo.
    echo Launching interactive menu...
    powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; python run_system3.py"
)

if "%CHOICE%"=="2" (
    echo.
    echo Launching autorun master...
    powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; python system3_autorun_master.py"
)

REM ... more options ...

REM Default (invalid choice)
echo.
echo Invalid choice - opening PowerShell...
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Write-Host 'System3 Environment Ready' -ForegroundColor Green; cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'"
```

**Issue:** No default fallback check for CHOICE being empty or invalid → defaults to PowerShell.

---

### Pattern 4: Timestamp Generation via WMIC

**Model:** Date/time extraction using Windows Management Instrumentation

```batch
REM Single WMIC call
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I

REM Extract components
set LOG_TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%
REM Format: YYYY-MM-DD_HHMM

REM Example:
REM datetime = 20251206123456
REM LOG_TIMESTAMP = 2025-12-06_1234
```

**Strengths:**
- Single system call (efficient)
- Timezone-aware (uses local system time)
- Precision: YYYY-MM-DD_HHMM (minute-level)

**Weakness:** WMIC deprecated in Windows 11 21H2+; recommend migrating to PowerShell `Get-Date`.

---

## VARIABLE SCOPING & ENVIRONMENT

### SETLOCAL / ENDLOCAL Pattern

```batch
@echo off
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

set VAR1=outer

(
    setlocal
    set VAR1=inner
    echo %VAR1%  REM prints "inner"
    endlocal
)

echo %VAR1%  REM prints "outer" (scope exited)

ENDLOCAL
```

**Usage in Code:**

**START_AUTORUN_AND_WATCHDOG.bat:**
```batch
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
... all setup ...
ENDLOCAL
```
✅ Cleanup: variables isolated, environment restored

**heartbeat_maintenance.bat:**
```batch
setlocal
cd /d C:\Genesis_System3
... work ...
endlocal
```
✅ Cleanup: scope exited, cwd restored

**Key Difference:**
- `SETLOCAL` (lowercase) = smaller scope
- `SETLOCAL ENABLEDELAYEDEXPANSION` = enables `!VAR!` expansion in loops

### Delayed Expansion (`!VAR!` vs `%VAR%`)

**Non-Delayed (Static):**
```batch
for %%i in (1 2 3) do (
    set COUNT=%%i
    echo %COUNT%  REM prints previous value (static)
)
REM Output: 0 0 0 (or blank)
```

**Delayed (Dynamic):**
```batch
setlocal enabledelayedexpansion
for %%i in (1 2 3) do (
    set COUNT=%%i
    echo !COUNT!  REM prints current iteration value (dynamic)
)
REM Output: 1 2 3
```

**Usage in Project:**
- **SYSTEM3_DAILY_START.bat** uses `!VAR!` for loop variables (correct)
- **START_AUTORUN_AND_WATCHDOG.bat** uses `%VAR%` (safe, no loops with expansion)

---

## ERROR HANDLING & EXIT CODES

### Exit Code Model

```batch
REM 0 = Success
REM 1 = General error (standard in Project)
REM 2 = Misuse of shell command
REM 3+ = Custom application errors
```

**Pattern: Cascade on Hard Gate**
```batch
REM Phase 1: Hard gate
call "%VENV_ACT%"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
REM If we reach here, Phase 1 passed; continue to Phase 2
```

**Pattern: Soft Check (Continue)**
```batch
REM Phase 3: Soft check
"%PYTHON%" "%PREP%"
if %ERRORLEVEL% EQU 0 (
    echo OK Phase 201 completed
) else (
    echo Phase 201 reported issues. Continuing with existing data.
)
REM Always continue, regardless of Phase 201 result
```

**Observed Patterns:**
- ✅ Hard gates use `if errorlevel 1 { exit /b 1 }`
- ✅ Soft checks use `if errorlevel 1 { log warning; continue }`
- ❌ **Issue:** Some batches don't check errorlevel at all (heartbeat_maintenance.bat doesn't exit on freshness failure)

### Exit Code Cascading

```
START_AUTORUN_AND_WATCHDOG.bat
│
├─ Phase 1 FAILS → exit /b 1 → batch exits with code 1 (venv missing)
├─ Phase 2 FAILS → exit /b 1 → batch exits with code 1 (deps missing)
├─ Phase 3 FAILS → exit /b 1 → batch exits with code 1 (LIVE mode detected)
├─ Phase 4 FAILS → no explicit check; Phase 5 runs without watchdog (risk!)
└─ Phase 5 FAILS → Python process exits; batch exits with Python's exit code (typically 1)
```

**Risk:** Phase 4 (watchdog spawn) doesn't validate success. If `start` command fails, Phase 5 runs unmonitored.

---

## SUBPROCESS MANAGEMENT

### Pattern 1: Spawn New Window (`start` command)

```batch
start "System3 Watchdog" cmd /k "cd /d %ROOT% ^&^& call %VENV_ACT% ^&^& python system3_watchdog.py"
timeout /t 2 /nobreak >nul
```

**Analysis:**
- `start` = new process, independent console window
- Title: "System3 Watchdog" (shown in taskbar)
- `cmd /k` = keep window open after command exits
- `^&^&` = escaped && (literal ampersand in `start` command)
- `timeout /t 2` = wait 2 seconds for spawn to complete

**Risk:** No check on whether `start` succeeded. If watchdog fails to start, autorun runs unmonitored.

**Safer Pattern:**
```batch
start "System3 Watchdog" cmd /k "..."
if errorlevel 1 (
    echo ERROR: Failed to start watchdog
    exit /b 1
)
```

### Pattern 2: Blocking Python Process

```batch
"%PYTHON%" "%MASTER%"

echo.
echo ================================================================================
echo AUTORUN MASTER STOPPED
echo ================================================================================
```

**Analysis:**
- Blocking: batch waits for Python to exit
- On user Ctrl+C: Python catches signal, exits with code 0 (graceful)
- On crash: Python exits with code 1 (error)
- Batch inherits Python's exit code

**Watchdog's Role:** If autorun crashes (exit 1), watchdog should restart it automatically.

---

## FILE I/O & LOGGING

### Logging Pattern 1: Direct File Write (via `>>`)

**START_AUTORUN_AND_WATCHDOG.bat** (minimal logging):
```batch
REM No explicit logging to file; relies on console output
REM Logs are captured by OS redirection if run from scheduler
```

**SYSTEM3_DAILY_START.bat** (rich logging):
```batch
set "STARTUP_LOG=%LOGS_DIR%\system3_daily_start_%TIMESTAMP%.log"

(
    echo ================================================================================
    echo SYSTEM3 DAILY START REPORT
    echo ================================================================================
    echo Timestamp: %TIMESTAMP%
    ...
) > "%STARTUP_LOG%"

type "%STARTUP_LOG%"
```

**Analysis:**
- Parenthesized block: all echo statements buffered
- `> file.txt` redirects entire block to file
- `>>` would append; `>` overwrites
- `type file.txt` prints to console

### Logging Pattern 2: Python Tee (via PowerShell)

**start_system3_env.bat:**
```batch
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; python run_system3.py 2>&1 | Tee-Object -FilePath '%LOG_FILE%'"
```

**Analysis:**
- `2>&1` = redirect stderr to stdout (all output to pipeline)
- `Tee-Object -FilePath` = split output to file and console
- `-NoExit` = keep PowerShell window open after script exits
- Result: console shows live output + file captures for audit

---

## VENV ACTIVATION PATTERNS

### Pattern 1: CMD Batch Activation (Classic)

```batch
call "%VENV_ACT%"
```

**Effect:**
- Modifies current process's environment
- Adds venv\Scripts to PATH
- Activates (python) to point to venv interpreter
- Persistent until batch exits or explicit deactivation

**Limitations:**
- Syntax: cmd.exe batch specific (not PowerShell compatible)
- One-time: can't chain with pipes/redirection

### Pattern 2: PowerShell Activation (Modern)

```batch
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "& '%VENV_DIR%\Scripts\Activate.ps1'; python script.py"
```

**Effect:**
- PowerShell session starts fresh with isolated environment
- Calls Activate.ps1 (PowerShell script)
- Adds venv\Scripts to PATH in PowerShell scope
- Python command runs in activated venv

**Advantages:**
- Better error messages
- Can chain with pipes (| ), redirections (>)
- Supports scripting constructs (if, for, etc.)

**Trade-off:** Requires PowerShell (not pure cmd.exe)

### Pattern 3: Inline Activation (Direct Executable)

```batch
"%PYTHON%" script.py
```

**Requirement:**
- PYTHON variable must be absolute path to venv interpreter
- Example: `set PYTHON=C:\Genesis_System3\venv\Scripts\python.exe`

**Advantage:**
- No activation call needed
- Direct interpreter invocation

---

## POWERSHELL INTEGRATION

### Pattern 1: PowerShell Command in Batch

```batch
powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '%PROJECT_DIR%'; & '%VENV_DIR%\Scripts\Activate.ps1'; python run_system3.py"
```

**Flags:**
- `-NoExit` = keep window open after command exits
- `-ExecutionPolicy Bypass` = allow script execution (Activation.ps1 is a script)
- `-Command` = execute PowerShell command string

**Escaping:**
- Single quotes in batch: `'string'` (no escaping needed)
- Variables in quotes: `'%VAR%'` (batch expands before PowerShell sees it)

### Pattern 2: WMIC via PowerShell (Get-Date)

**Current (WMIC - deprecated):**
```batch
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
```

**Recommended (PowerShell - forward compatible):**
```batch
for /f "delims=" %%I in ('powershell -Command "Get-Date -Format 'yyyyMMddHHmmss'"') do set datetime=%%I
```

**Advantage:** Works in Windows 11 21H2+ where WMIC is deprecated.

---

## CODE QUALITY ISSUES

### Issue 1: Phase 4 Spawn Not Validated (START_AUTORUN_AND_WATCHDOG.bat)

**Current:**
```batch
start "System3 Watchdog" cmd /k "..."
timeout /t 2 /nobreak >nul
echo OK Watchdog started (separate window)
```

**Problem:** No errorlevel check; if watchdog spawn fails, batch continues assuming success.

**Fix:**
```batch
start "System3 Watchdog" cmd /k "..."
if errorlevel 1 (
    echo ERROR: Failed to start watchdog
    exit /b 1
)
timeout /t 2 /nobreak >nul
echo OK Watchdog started (separate window)
```

---

### Issue 2: Missing Errorlevel Check on Python Calls

**Current (multiple places):**
```batch
"%PYTHON%" -c "import %%m" 2>nul
if errorlevel 1 (
    ...
)
```

**Problem:** Only checks import; doesn't check syntax or other errors.

**Better:**
```batch
"%PYTHON%" -c "import %%m" 2>&1 | find "No module named" >nul
if %ERRORLEVEL% EQU 0 (
    echo Missing: %%m
    pip install %%m --quiet
)
```

---

### Issue 3: Hardcoded Paths (heartbeat_maintenance.bat)

**Current:**
```batch
cd /d C:\Genesis_System3
```

**Problem:** Assumes batch always runs from same location. Fails if moved.

**Better:**
```batch
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"
```

---

### Issue 4: WMIC Deprecation (SYSTEM3_DAILY_START.bat, start_system3_env.bat)

**Current:**
```batch
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
```

**Risk:** WMIC disabled by default in Windows 11 21H2+; batch fails on newer systems.

**Recommended (PowerShell):**
```batch
for /f "delims=" %%I in ('powershell -Command "Get-Date -Format 'yyyyMMddHHmmss'"') do set datetime=%%I
```

---

### Issue 5: No Timeout on Dependencies Loop

**Current:**
```batch
for %%m in (psutil pandas numpy joblib) do (
    "%PYTHON%" -c "import %%m" 2>nul
    if errorlevel 1 (
        pip install %%m --quiet
    )
)
```

**Problem:** If pip hangs (network issue), batch hangs indefinitely.

**Better:**
```batch
for %%m in (psutil pandas numpy joblib) do (
    "%PYTHON%" -c "import %%m" 2>nul
    if errorlevel 1 (
        echo Installing %%m ...
        timeout /t 30 /nobreak >nul & pip install %%m --quiet 2>&1 | find "Successfully installed"
        if errorlevel 1 (
            echo ERROR: Failed to install %%m
            exit /b 1
        )
    )
)
```

---

## PERFORMANCE ANALYSIS

### Startup Time Breakdown

**START_AUTORUN_AND_WATCHDOG.bat:**

| Phase | Duration | Critical Path |
|-------|----------|--|
| Phase 1: Venv + Python check | 2-5 sec | Venv activation + Python `-c` test |
| Phase 1: Dependency loop | 5-30 sec | pip install if packages missing |
| Phase 2: Data freshness | 1-3 sec | Dir listing + file size check |
| Phase 2: Prep (if needed) | 30-60 sec | Phase 201 re-download data (soft check) |
| Phase 3: Safety check | 1 sec | Environment variable read |
| Phase 4: Watchdog spawn | 1-2 sec | `start` command + timeout |
| Phase 5: Autorun launch | 5-10 sec | Python startup + initialization |
| **Total (best case)** | ~30 sec | No missing deps, no stale data, quick autorun init |
| **Total (worst case)** | ~120 sec | Missing all deps, stale data refresh, slow network |

**Optimization Opportunities:**
1. Parallelize dependency check → multi-threaded pip install (not in cmd.exe)
2. Cache pip install results → check timestamp instead of reimport
3. Lazy venv activation → only activate when needed (minor improvement)

---

### Memory & Resource Usage

```
Batch Scripts (cmd.exe): ~5-10 MB each
├─ START_AUTORUN_AND_WATCHDOG: 2 windows (main + watchdog) → ~10-20 MB
├─ SYSTEM3_DAILY_START: 1 window → ~5-10 MB
└─ heartbeat_maintenance: 1 window (short-lived) → ~5 MB

Python Processes:
├─ system3_autorun_master.py: ~200-500 MB (depends on data loaded)
├─ system3_watchdog.py: ~50-100 MB
├─ check_heartbeat_freshness.py: ~20-30 MB (short-lived)
└─ archive_heartbeat.py: ~20-30 MB (short-lived)

Heartbeat File:
├─ system3_daily_heartbeat.json: ~50-150 KB
└─ storage/heartbeat_archive/*.json: 50-150 KB × (1440 per day if 1-min archive)
```

---

## TESTING CHECKLIST

### Functional Tests

- [ ] **VEnv Check**: Rename venv, run batch → should exit with clear error
- [ ] **Missing Dependency**: Uninstall pandas, run batch → should auto-install
- [ ] **Data Freshness**: Remove snapshot files, run batch → should run Phase 201
- [ ] **DRY-RUN Safety**: Set LIVE_TRADING_ENABLED=True, run batch → should exit 1
- [ ] **Watchdog Spawn**: Run batch → verify "System3 Watchdog" window opens
- [ ] **Autorun Launch**: Verify autorun master starts in main window
- [ ] **Graceful Shutdown**: Ctrl+C → should log shutdown, close both windows
- [ ] **Heartbeat Update**: Check system3_daily_heartbeat.json → v2.0.0 schema, < 180s old
- [ ] **Safety Checks Pass**: Run system3_daily_safety_check.bat → all 3 checks pass
- [ ] **Safety Checks Fail**: Intentionally break a check → batch exits 1

### Integration Tests

- [ ] **Full Flow**: safety_check → START_AUTORUN_AND_WATCHDOG → trading for 1 hour → shutdown
- [ ] **Watchdog Recovery**: Kill autorun master → watchdog should restart within 10 sec
- [ ] **Heartbeat Freshness**: Check via `python check_heartbeat_freshness.py` → age < 180s
- [ ] **Log Files**: Verify logs\system3_autorun_master_*.log created and populated
- [ ] **Archive Snapshots**: Verify storage/heartbeat_archive/heartbeat_*.json created hourly (if scheduled)

### Edge Cases

- [ ] **Network Failure**: Disconnect internet, run batch → should handle gracefully
- [ ] **Disk Full**: Fill disk to < 100 MB, run batch → should alert but continue
- [ ] **Python Crash**: Kill python.exe → watchdog should restart
- [ ] **Both Crash**: Kill both cmd windows → manual restart required (batch handles)
- [ ] **Multiple Instances**: Start 2 batches simultaneously → second should detect conflict (not implemented; risk!)
- [ ] **Long Session**: Run 8 hours → heartbeat should stay fresh, logs should not grow unboundedly

---

## WINDOWS TASK SCHEDULER INTEGRATION

### Register START_AUTORUN_AND_WATCHDOG

```powershell
# Run as Administrator:
$trigger = New-ScheduledTaskTrigger -AtStartup
$action = New-ScheduledTaskAction -Execute "C:\Genesis_System3\START_AUTORUN_AND_WATCHDOG.bat"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "System3\Autorun" -Trigger $trigger -Action $action -Settings $settings
```

### Register heartbeat_maintenance

```powershell
# Run every 5 minutes during market hours (09:15 - 15:30 IST):
$trigger = New-ScheduledTaskTrigger -AtLogOn -RepetitionInterval (New-TimeSpan -Minutes 5)
$action = New-ScheduledTaskAction -Execute "C:\Genesis_System3\heartbeat_maintenance.bat"
Register-ScheduledTask -TaskName "System3\Heartbeat-Freshness" -Trigger $trigger -Action $action
```

---

## RECOMMENDATIONS FOR PRODUCTION

1. **Replace WMIC with PowerShell** (compatibility with Windows 11 21H2+)
2. **Validate subprocess spawns** (add errorlevel check after `start` command)
3. **Add timeout to pip installs** (prevent indefinite hangs)
4. **Implement conflict detection** (prevent multiple instances)
5. **Use `setlocal` in all batches** (isolate environment)
6. **Document exit codes** (create exit code reference)
7. **Schedule heartbeat maintenance** via Windows Task Scheduler
8. **Centralize logging** (redirect all output to timestamped logs)
9. **Add retry logic** for transient failures (network, file locks)
10. **Monitor heartbeat freshness** continuously (alert if > 180s stale)

---

**END OF TECHNICAL DEEP DIVE**
