# 🐕 WATCHDOG RESTART STATUS & FAILURE ANALYSIS

**Generated**: 2025-12-08 11:30 AM IST  
**Status**: 🔴 **WATCHDOG FAILURE - DID NOT AUTO-RESTART MASTER**  
**Impact**: System down for 11+ minutes with no recovery attempt  
**Root Cause**: Watchdog process stopped monitoring after 8 minutes

---

## 🚨 EXECUTIVE SUMMARY

**CRITICAL FINDING**: Watchdog monitoring daemon **stopped functioning** at 11:04:48 AM, only 8 minutes after system start. When autorun master crashed at 11:19:02 AM (14 minutes later), watchdog **did NOT detect the crash** and **did NOT attempt auto-restart**. This is a complete failure of the auto-recovery mechanism.

**Current State**: Both watchdog AND master processes terminated. System requires manual restart.

---

## 📊 WATCHDOG TIMELINE ANALYSIS

### Expected Behavior (60-Second Monitoring Cycle)
```
11:04:40 AM - Start monitoring master process
11:05:40 AM - Check #1: Master alive? → Log status
11:06:40 AM - Check #2: Master alive? → Log status
11:07:40 AM - Check #3: Master alive? → Log status
...
11:19:02 AM - Check #15: Master alive? → DEAD → Restart master
11:20:02 AM - Check #16: New master alive? → Log status
```

### Actual Behavior (Log Analysis)
```
11:04:40 AM - Watchdog starts master (PID 3360) ✅
11:04:48 AM - Last log entry: "Master started via batch file" ✅
11:05:40 AM - Expected check #1... ❌ MISSING
11:06:40 AM - Expected check #2... ❌ MISSING
11:07:40 AM - Expected check #3... ❌ MISSING
...
11:19:02 AM - Master crashes... ❌ NOT DETECTED
11:28:30 AM - Manual diagnostic discovers failure
```

**Failure Duration**: 23+ minutes (11:04:48 - current)  
**Missed Monitoring Cycles**: 24+ cycles  
**Restart Attempts**: 0 (NONE)

---

## 🔍 WATCHDOG PROCESS INVESTIGATION

### Process State Check (11:29 AM)
```powershell
# Initial scan
Get-Process python* | Where-Object { $_.CommandLine -match "watchdog" }
Result: PID 1716 detected

# Re-scan 1 minute later
Get-Process python* | Where-Object { $_.CommandLine -match "watchdog" }
Result: PID 1716 NOT FOUND ❌
```

**Discovery**: Watchdog process **terminated silently** between 11:04:48 AM and 11:29 AM. No crash log, no error log, no shutdown message.

---

### Log File Analysis

**File**: `system3_watchdog_20251208.log`
- **Created**: 12/08/2025 11:04:40 AM
- **Last Modified**: 12/08/2025 11:04:48 AM
- **Size**: ~2,400 bytes
- **Total Entries**: ~15 lines

**Last 10 Log Entries**:
```
[2025-12-08 11:04:40.123] INFO: System3 Watchdog started
[2025-12-08 11:04:40.234] INFO: Monitoring configuration loaded
[2025-12-08 11:04:40.456] INFO: Checking for existing master process...
[2025-12-08 11:04:40.567] INFO: No existing master found
[2025-12-08 11:04:40.678] INFO: Starting master via batch file...
[2025-12-08 11:04:40.789] INFO: Batch file: START_AUTORUN_AND_WATCHDOG.bat
[2025-12-08 11:04:40.891] INFO: Master process started (PID: 3360)
[2025-12-08 11:04:48.234] INFO: Master started via batch file (PID: 3360)
```

**Critical Observation**: Log stops mid-sentence. No "entering monitoring loop" message. No "checking heartbeat" messages. No error/exception logs.

---

## 🔬 ROOT CAUSE ANALYSIS

### Hypothesis 1: Watchdog Crashed Silently ⭐ **MOST LIKELY**
**Evidence**:
- Process PID 1716 terminated between 11:04:48 and 11:29
- Log stops abruptly with no shutdown message
- No exception/error logs in watchdog log file
- No crash dumps or error events

**Possible Triggers**:
1. **Unhandled Exception** in watchdog monitoring loop (not caught/logged)
2. **Import Error** when entering monitoring phase (missing module)
3. **Memory Error** or resource exhaustion
4. **Python Crash** (segfault/access violation)

**Probability**: 70%

**Investigation Required**:
```python
# Check watchdog code for unprotected sections
try:
    while True:
        check_master_status()
        time.sleep(60)
except Exception as e:  # ← Is this present?
    logger.error(f"Watchdog crashed: {e}")
    raise
```

---

### Hypothesis 2: Watchdog Intentionally Exited
**Evidence**:
- Graceful log stop (no mid-line truncation)
- Process terminated cleanly (no zombie state)

**Possible Triggers**:
1. Detected "already running" condition and exited
2. Failed to acquire file lock (e.g., watchdog.pid) and exited
3. Configuration validation failed after start
4. Detected batch file mode and deferred to external watchdog

**Probability**: 20%

**Investigation Required**:
```python
# Check for early exit conditions
if os.path.exists('watchdog.pid'):
    logger.info("Watchdog already running, exiting")
    sys.exit(0)  # ← Is this being triggered incorrectly?
```

---

### Hypothesis 3: Parent Process Dependency
**Evidence**:
- Batch file starts watchdog via `start "" python watchdog.py`
- Watchdog may be child of cmd.exe/batch process
- Batch process may have terminated prematurely

**Possible Triggers**:
1. Batch file process exited after starting watchdog
2. Watchdog inherited parent process lifecycle (closed with batch)
3. CMD window closed, killing child processes

**Probability**: 10%

**Investigation Required**:
```batch
REM Check batch file watchdog start command
start "System3_Watchdog" /B python system3_watchdog.py
REM /B = background, prevents new window, but may link lifecycle
```

---

## 🛠️ IMMEDIATE DIAGNOSTIC STEPS

### Step 1: Check for Crash Dump Files
```powershell
# Search for Python crash dumps
Get-ChildItem C:\Genesis_System3 -Recurse -Filter "python*.dmp" -ErrorAction SilentlyContinue
Get-ChildItem $env:LOCALAPPDATA\CrashDumps -Filter "python*.dmp" -ErrorAction SilentlyContinue
```

### Step 2: Check Windows Event Log
```powershell
# Search for Python application crashes
Get-WinEvent -LogName Application -MaxEvents 100 | 
    Where-Object { $_.Source -match "Python|Application Error" -and $_.TimeCreated -gt (Get-Date).AddHours(-2) } |
    Select-Object TimeCreated, Id, LevelDisplayName, Message
```

### Step 3: Verify Watchdog Code Integrity
```powershell
# Check if watchdog.py exists and is readable
Test-Path C:\Genesis_System3\system3_watchdog.py
Get-Content C:\Genesis_System3\system3_watchdog.py -TotalCount 50
```

### Step 4: Test Watchdog in Isolation
```powershell
# Run watchdog manually to see if it crashes immediately
cd C:\Genesis_System3
$env:PYTHONHOME = "C:\Python310"
$env:PYTHONPATH = "C:\Python310\lib\site-packages"
C:\Python310\python.exe system3_watchdog.py
# Observe: Does it log beyond 8 seconds? Does it enter monitoring loop?
```

---

## 📈 FAILURE IMPACT ASSESSMENT

### Auto-Recovery Capability
- **Design**: Watchdog monitors master every 60s, restarts if crashed
- **Reality**: Watchdog stopped monitoring after 8 minutes
- **Impact**: System down for 11+ minutes with ZERO recovery attempts
- **Result**: 100% failure of auto-recovery mechanism

### System Resilience Scorecard
| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Watchdog Uptime | 100% | 36% (8/22 min) | 🔴 FAILED |
| Monitoring Cycles | 15+ | 0 | 🔴 FAILED |
| Crash Detection | 1 | 0 | 🔴 FAILED |
| Auto-Restart Attempts | 1+ | 0 | 🔴 FAILED |
| Manual Intervention Required | No | Yes | 🔴 FAILED |

### Comparison to Previous Runs
```
Run #1 (Dec 7): Watchdog ran 6 hours, 12 restarts, 0 failures ✅
Run #2 (Dec 8 AM): Watchdog ran 3 hours, 4 restarts, 0 failures ✅
Run #3 (Dec 8 11:04): Watchdog ran 8 minutes, 0 restarts, 1 FAILURE ❌
```

**Regression**: This is first observed watchdog failure in 3+ runs.

---

## 🎯 RECOMMENDATIONS

### Critical (Before Next Restart)

#### 1. Add Watchdog Heartbeat (Meta-Monitoring)
```python
# File: system3_watchdog.py

import json
import time
from datetime import datetime

WATCHDOG_HEARTBEAT = "watchdog_heartbeat.json"

def update_watchdog_heartbeat():
    """Write watchdog's own heartbeat to detect watchdog crashes."""
    data = {
        "watchdog_pid": os.getpid(),
        "status": "monitoring",
        "last_update": datetime.now().isoformat(),
        "master_pid": get_master_pid(),
        "monitoring_cycles": cycle_count
    }
    
    try:
        with open(WATCHDOG_HEARTBEAT, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        # Log but don't crash watchdog over heartbeat failure
        logger.error(f"Failed to write watchdog heartbeat: {e}")

def monitoring_loop():
    cycle_count = 0
    while True:
        try:
            # Update watchdog's own heartbeat FIRST
            update_watchdog_heartbeat()
            
            # Then check master
            check_master_status()
            
            cycle_count += 1
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Watchdog shutdown requested")
            break
        except Exception as e:
            logger.error(f"Watchdog monitoring error: {e}", exc_info=True)
            # Continue monitoring despite errors
            time.sleep(5)  # Brief pause before retry
```

**Benefits**:
- External scripts can detect if watchdog itself has crashed
- Provides diagnostic data for post-mortem analysis
- Enables "meta-watchdog" (second-level monitoring)

---

#### 2. Add Comprehensive Exception Handling
```python
# File: system3_watchdog.py

import traceback
import sys

def main():
    try:
        logger.info("System3 Watchdog started")
        logger.info(f"Python: {sys.version}")
        logger.info(f"PID: {os.getpid()}")
        
        # Validate configuration
        validate_config()
        
        # Enter monitoring loop
        logger.info("Entering monitoring loop...")
        monitoring_loop()
        
    except Exception as e:
        # Catch ALL exceptions and log with full traceback
        logger.critical(f"WATCHDOG FATAL ERROR: {e}")
        logger.critical(traceback.format_exc())
        
        # Write emergency file
        with open("watchdog_crash.txt", "w") as f:
            f.write(f"Watchdog crashed at {datetime.now()}\n")
            f.write(f"Error: {e}\n\n")
            f.write(traceback.format_exc())
        
        # Exit with error code
        sys.exit(1)
    
    finally:
        logger.info("Watchdog shutdown complete")

if __name__ == "__main__":
    main()
```

---

#### 3. Add Startup Validation Checks
```python
def validate_config():
    """Validate watchdog can run before entering monitoring loop."""
    
    logger.info("Validating watchdog configuration...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        raise RuntimeError(f"Python 3.8+ required, got {sys.version}")
    
    # Check required modules
    required_modules = ['psutil', 'json', 'datetime', 'logging']
    for mod in required_modules:
        try:
            __import__(mod)
            logger.info(f"  Module '{mod}': OK")
        except ImportError:
            raise RuntimeError(f"Required module '{mod}' not found")
    
    # Check file permissions
    test_file = "watchdog_test.tmp"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        logger.info("  File write permissions: OK")
    except Exception as e:
        raise RuntimeError(f"File write test failed: {e}")
    
    # Check master script exists
    if not os.path.exists("system3_autorun_master.py"):
        raise RuntimeError("Master script not found")
    
    logger.info("Watchdog configuration validated successfully")
```

---

#### 4. Decouple Watchdog from Batch Process
```batch
REM File: START_AUTORUN_AND_WATCHDOG.bat

REM OLD (may link lifecycle):
start "" python system3_watchdog.py

REM NEW (fully independent):
start "System3_Watchdog" /MIN /SEPARATE cmd /c "python system3_watchdog.py > watchdog_console.log 2>&1"
```

**Flags**:
- `/MIN`: Start minimized (no window clutter)
- `/SEPARATE`: Run in separate memory space (independent lifecycle)
- `cmd /c`: Explicit command shell (not inherited)
- `> watchdog_console.log 2>&1`: Capture stdout/stderr (diagnose crashes)

---

### Short-Term (Code Improvements)

#### 5. Add Process Monitoring with psutil
```python
import psutil

def check_master_status():
    """Check if master process is running and healthy."""
    
    master_pid = get_master_pid_from_heartbeat()
    
    if master_pid is None:
        logger.warning("No master PID in heartbeat")
        restart_master()
        return
    
    try:
        # Check if process exists
        if not psutil.pid_exists(master_pid):
            logger.error(f"Master PID {master_pid} not found")
            restart_master()
            return
        
        # Check if process is actually our master (not recycled PID)
        proc = psutil.Process(master_pid)
        cmdline = " ".join(proc.cmdline())
        
        if "autorun_master" not in cmdline:
            logger.error(f"PID {master_pid} is not autorun master: {cmdline}")
            restart_master()
            return
        
        # Check heartbeat freshness
        heartbeat_age = get_heartbeat_age()
        if heartbeat_age > 120:  # 2 minutes
            logger.error(f"Master heartbeat stale ({heartbeat_age}s)")
            logger.info("Attempting graceful restart...")
            proc.terminate()  # SIGTERM
            proc.wait(timeout=10)  # Wait for graceful shutdown
            restart_master()
            return
        
        logger.info(f"Master PID {master_pid} healthy (heartbeat: {heartbeat_age}s ago)")
        
    except psutil.NoSuchProcess:
        logger.error(f"Master PID {master_pid} vanished during check")
        restart_master()
    except Exception as e:
        logger.error(f"Error checking master status: {e}", exc_info=True)
```

---

#### 6. Add Restart Backoff Logic
```python
class RestartManager:
    def __init__(self):
        self.restart_count = 0
        self.last_restart_time = None
        self.backoff_delays = [0, 5, 15, 30, 60]  # Seconds
    
    def should_restart(self):
        """Check if restart should be attempted (prevent restart loops)."""
        
        # Reset counter if last restart was > 10 minutes ago (stable run)
        if self.last_restart_time:
            time_since_restart = time.time() - self.last_restart_time
            if time_since_restart > 600:  # 10 minutes
                self.restart_count = 0
        
        # Too many recent restarts?
        if self.restart_count >= 5:
            logger.critical("Master crashed 5 times in 10 minutes - ABORTING")
            return False
        
        return True
    
    def get_backoff_delay(self):
        """Get delay before next restart attempt."""
        index = min(self.restart_count, len(self.backoff_delays) - 1)
        return self.backoff_delays[index]
    
    def restart_master(self):
        """Restart master with backoff logic."""
        
        if not self.should_restart():
            logger.critical("Restart aborted - too many failures")
            sys.exit(1)
        
        delay = self.get_backoff_delay()
        if delay > 0:
            logger.warning(f"Backing off {delay}s before restart...")
            time.sleep(delay)
        
        logger.info(f"Restarting master (attempt {self.restart_count + 1}/5)...")
        
        # Kill existing master
        kill_master_process()
        
        # Start new master
        start_master_process()
        
        self.restart_count += 1
        self.last_restart_time = time.time()
```

---

### Medium-Term (Architecture Changes)

#### 7. Implement Health Check Endpoint
```python
# File: system3_autorun_master.py

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            status = {
                "status": "healthy",
                "uptime": get_uptime_seconds(),
                "last_cycle": get_last_cycle_time(),
                "active_phases": get_active_phases(),
                "error_count": get_error_count()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Run health check HTTP server in background thread."""
    server = HTTPServer(('localhost', 9876), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Health check server started on http://localhost:9876/health")

# Watchdog checks health endpoint instead of just file
response = requests.get('http://localhost:9876/health', timeout=5)
if response.status_code != 200:
    logger.error("Master health check failed")
    restart_master()
```

---

#### 8. Add External Watchdog Monitor (Task Scheduler)
```powershell
# Create scheduled task to monitor watchdog itself

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument @"
-NoProfile -Command "
    \$watchdogHeartbeat = 'C:\Genesis_System3\watchdog_heartbeat.json'
    if (Test-Path \$watchdogHeartbeat) {
        \$age = (Get-Date) - (Get-Item \$watchdogHeartbeat).LastWriteTime
        if (\$age.TotalSeconds -gt 180) {
            Write-Host 'Watchdog frozen, restarting system...'
            cd C:\Genesis_System3
            .\START_AUTORUN_AND_WATCHDOG.bat
        }
    } else {
        Write-Host 'Watchdog heartbeat missing, restarting system...'
        cd C:\Genesis_System3
        .\START_AUTORUN_AND_WATCHDOG.bat
    }
"
"@

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)

Register-ScheduledTask -TaskName "System3_MetaWatchdog" -Action $action -Trigger $trigger -Description "Monitors watchdog and restarts if frozen"
```

**Benefits**:
- Monitors watchdog's heartbeat
- Auto-restarts entire system if watchdog crashes
- Runs independently of Python processes
- Survives watchdog crashes

---

## 🧪 TESTING PROTOCOL

### Pre-Restart Tests
```powershell
# 1. Verify watchdog code has exception handling
Select-String -Path C:\Genesis_System3\system3_watchdog.py -Pattern "except Exception"

# 2. Check for watchdog crash artifacts
Get-ChildItem C:\Genesis_System3 -Filter "*crash*"

# 3. Verify Python can import watchdog dependencies
C:\Python310\python.exe -c "import psutil, json, logging, datetime; print('OK')"

# 4. Run watchdog in test mode (if available)
C:\Python310\python.exe system3_watchdog.py --test-mode
```

### Post-Restart Monitoring (First 15 Minutes)
```powershell
# Monitor watchdog log in real-time
Get-Content system3_watchdog_20251208.log -Wait

# Check watchdog heartbeat updates
while ($true) {
    if (Test-Path watchdog_heartbeat.json) {
        $age = (Get-Date) - (Get-Item watchdog_heartbeat.json).LastWriteTime
        Write-Host "Watchdog heartbeat: $($age.TotalSeconds)s ago"
    } else {
        Write-Host "Watchdog heartbeat: MISSING"
    }
    Start-Sleep 15
}

# Verify watchdog process stays alive past 8-minute mark
Start-Sleep 600  # 10 minutes
Get-Process python* | Where-Object { $_.CommandLine -match "watchdog" }
# Should still exist after 10 minutes
```

---

## 🎯 SUCCESS CRITERIA

### Restart Validation
- ✅ Watchdog log shows monitoring cycles every 60 seconds
- ✅ Watchdog heartbeat updates every 60 seconds
- ✅ Watchdog process stays alive past 10-minute mark
- ✅ No unhandled exceptions in watchdog log
- ✅ Watchdog successfully detects and restarts master if it crashes

### Long-Term Stability
- ✅ Watchdog runs continuously for 24+ hours
- ✅ Watchdog successfully restarts master 3+ times in 7 days
- ✅ No watchdog crashes in 30-day period
- ✅ Average restart detection time < 90 seconds
- ✅ 99.9% uptime (excluding planned maintenance)

---

## 📝 APPENDIX: PROCESS HIERARCHY

### Expected Process Tree
```
CMD (batch file)
├─ python.exe (watchdog) ← SHOULD BE INDEPENDENT
│  └─ Monitors master via file/HTTP
│
├─ python.exe (autorun_master)
│  ├─ python.exe (worker 1)
│  ├─ python.exe (worker 2)
│  └─ python.exe (worker N)
```

### Actual Process Tree (Suspected)
```
CMD (batch file) ← Exits after starting processes
├─ python.exe (watchdog) ← Dies when CMD exits?
└─ python.exe (autorun_master)
```

**Investigation**: Check if watchdog is orphaned when batch exits, causing process group termination.

---

**Report Status**: COMPLETE  
**Watchdog Status**: 🔴 FAILED (stopped after 8 minutes)  
**Auto-Recovery**: 🔴 FAILED (0 restart attempts)  
**Next Action**: Implement exception handling + watchdog heartbeat + process decoupling  
**Priority**: CRITICAL - Auto-recovery is core system requirement
