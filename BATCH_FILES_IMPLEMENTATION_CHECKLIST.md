# BATCH FILES ANALYSIS - IMPLEMENTATION CHECKLIST

**Target Completion Date:** End of December 2025  
**Phase:** Consolidation & Production Hardening

---

## ✅ PHASE 1: IMMEDIATE ACTIONS (Week 1)

### Documentation & Communication

- [ ] **1.1** Review BATCH_FILES_ANALYSIS_COMPLETE.md (executive summary)
- [ ] **1.2** Share BATCH_FILES_VISUAL_SUMMARY.md with team
- [ ] **1.3** Brief operators on new workflow (safety → launcher)
- [ ] **1.4** Bookmark BATCH_FILES_QUICK_REFERENCE.md for daily use
- [ ] **1.5** Create Slack/Teams channel for batch file updates

### File Deprecation Preparation

- [ ] **1.6** Mark deprecated files with banner comment:
  ```batch
  REM ⚠️  DEPRECATED - Use START_AUTORUN_AND_WATCHDOG.bat instead
  ```
  Files: SYSTEM3_DAILY_START.bat, start_system3_autorun.bat, start_system3_env.bat

- [ ] **1.7** Create archive directory structure:
  ```
  c:\Genesis_System3\archive\deprecated_launchers\
  ```

- [ ] **1.8** Create DEPRECATION_NOTICE.txt:
  ```
  This folder contains deprecated batch file launchers.
  Do not use for production. Reference only.
  
  Migration:
  - OLD: SYSTEM3_DAILY_START.bat → NEW: START_AUTORUN_AND_WATCHDOG.bat
  - OLD: start_system3_autorun.bat → NEW: START_AUTORUN_AND_WATCHDOG.bat
  - OLD: start_system3_env.bat → NEW: START_AUTORUN_AND_WATCHDOG.bat
  
  All 3 replaced by: START_AUTORUN_AND_WATCHDOG.bat (246 lines, comprehensive)
  ```

### Testing & Validation

- [ ] **1.9** Test daily workflow (safety → launcher → monitor → shutdown)
- [ ] **1.10** Verify all 20 test phases pass (20/20 OK)
- [ ] **1.11** Confirm DRY-RUN safety gate works (exits 1 if LIVE mode)
- [ ] **1.12** Validate heartbeat schema v2.0.0 (21 required sections)
- [ ] **1.13** Test watchdog auto-restart (kill autorun, verify recovery)

---

## ✅ PHASE 2: CONSOLIDATION (Week 2-3)

### Archive Deprecated Files

- [ ] **2.1** Move SYSTEM3_DAILY_START.bat → archive/deprecated_launchers/
  - Reason: Menu-driven; 80% overlap with master launcher
  - Keep original in git history
  
- [ ] **2.2** Move start_system3_autorun.bat → archive/deprecated_launchers/
  - Reason: Minimal launcher; missing safeguards; no watchdog
  - Keep original in git history
  
- [ ] **2.3** Move start_system3_env.bat → archive/deprecated_launchers/
  - Reason: Legacy pattern; WMIC deprecated; limited scope
  - Keep original in git history

- [ ] **2.4** Verify archive folder contents:
  ```
  archive/deprecated_launchers/
  ├─ SYSTEM3_DAILY_START.bat
  ├─ start_system3_autorun.bat
  ├─ start_system3_env.bat
  └─ DEPRECATION_NOTICE.txt
  ```

- [ ] **2.5** Remove deprecated file references from production batch files
  - Remove any calls to: DAILY_START, autorun_only, env
  - Verify: All launchers use START_AUTORUN_AND_WATCHDOG.bat

### Update Documentation

- [ ] **2.6** Update README.md:
  - Remove mentions of deprecated launchers
  - Add: "Use START_AUTORUN_AND_WATCHDOG.bat for all startups"
  - Add: "Run system3_daily_safety_check.bat before trading"
  - Add: "Monitor via heartbeat_maintenance.bat (optional, scheduled)"

- [ ] **2.7** Update .gitignore:
  - Add: `archive/` (keep locally, don't push)
  - Or: `archive/deprecated_launchers/` (if archiving in repo)

- [ ] **2.8** Create LAUNCHER_MIGRATION_GUIDE.md:
  ```markdown
  # Batch File Migration Guide
  
  ## OLD vs NEW
  
  Old: SYSTEM3_DAILY_START.bat → New: START_AUTORUN_AND_WATCHDOG.bat
  Old: start_system3_autorun.bat → New: START_AUTORUN_AND_WATCHDOG.bat
  Old: start_system3_env.bat → New: START_AUTORUN_AND_WATCHDOG.bat
  
  ## Why?
  - START_AUTORUN_AND_WATCHDOG is production-ready
  - Comprehensive preflight checks
  - Watchdog monitoring for auto-restart
  - DRY-RUN safety enforcement
  
  ## How to Use
  1. Run: system3_daily_safety_check.bat (pre-market gating)
  2. Run: START_AUTORUN_AND_WATCHDOG.bat (production startup)
  3. Monitor: Watchdog window + heartbeat
  4. Stop: Ctrl+C in autorun window
  ```

- [ ] **2.9** Update OPERATOR_CHEAT_SHEET.md:
  - Daily workflow (safety → launcher → monitor)
  - Emergency procedures (Ctrl+C, force stop)
  - Troubleshooting (7 common issues)

### Verify Consolidation

- [ ] **2.10** Search codebase for references to deprecated files:
  ```batch
  REM In PowerShell:
  grep -r "SYSTEM3_DAILY_START\|start_system3_autorun\|start_system3_env" --include="*.py" --include="*.bat"
  ```
  Result: Should be 0 matches in production code

- [ ] **2.11** Verify all entry points use START_AUTORUN_AND_WATCHDOG:
  - Main batch: ✓ START_AUTORUN_AND_WATCHDOG.bat
  - Windows Task Scheduler: ✓ START_AUTORUN_AND_WATCHDOG.bat
  - Documentation: ✓ All reference new launcher

- [ ] **2.12** Test consolidated launcher end-to-end (30 min test):
  - Phase 1: Environment validation ✓
  - Phase 2: Data freshness ✓
  - Phase 3: DRY-RUN safety ✓
  - Phase 4: Watchdog spawn ✓
  - Phase 5: Autorun launch ✓

---

## ✅ PHASE 3: SCHEDULING (Week 4)

### Windows Task Scheduler Setup

- [ ] **3.1** Create "System3" task folder:
  ```powershell
  # Admin PowerShell:
  New-Item -Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\System3" -Force
  ```

- [ ] **3.2** Schedule heartbeat freshness check (every 5 minutes):
  ```powershell
  $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -RepeatDuration (New-TimeSpan -Hours 10)
  $action = New-ScheduledTaskAction -Execute "C:\Genesis_System3\heartbeat_maintenance.bat"
  Register-ScheduledTask -TaskName "System3\Heartbeat-Freshness" -Trigger $trigger -Action $action
  ```
  Expected: Runs every 5 min during market hours (09:15 - 15:30 IST)

- [ ] **3.3** Schedule heartbeat archival (every 60 minutes):
  ```powershell
  $trigger = New-ScheduledTaskTrigger -At "09:15AM" -RepetitionInterval (New-TimeSpan -Hours 1) -RepeatDuration (New-TimeSpan -Hours 10)
  $action = New-ScheduledTaskAction -Execute "C:\Genesis_System3\heartbeat_maintenance.bat"
  Register-ScheduledTask -TaskName "System3\Heartbeat-Archive" -Trigger $trigger -Action $action
  ```
  Expected: Runs every 60 min, snapshots archived

- [ ] **3.4** Verify scheduled tasks:
  ```powershell
  Get-ScheduledTask -TaskPath "\System3\*" -TaskName "*Heartbeat*" | Select TaskName, State, Triggers
  ```
  Expected: Both tasks enabled, correct schedules

- [ ] **3.5** Test scheduled tasks manually:
  ```powershell
  Start-ScheduledTask -TaskPath "\System3\" -TaskName "Heartbeat-Freshness"
  Start-ScheduledTask -TaskPath "\System3\" -TaskName "Heartbeat-Archive"
  ```
  Expected: heartbeat_maintenance.bat runs successfully

### Logging & Monitoring

- [ ] **3.6** Create scheduled task output log:
  ```
  c:\Genesis_System3\logs\heartbeat_maintenance_*.log
  ```

- [ ] **3.7** Configure task retry:
  - Retry count: 3
  - Retry interval: 5 minutes
  - On failure: Log error to logs/errors_heartbeat.log

- [ ] **3.8** Set environment variables for scheduled tasks:
  - HEARTBEAT_FRESHNESS_THRESHOLD_SECONDS=180
  - HEARTBEAT_ARCHIVE_RETENTION_DAYS=30

---

## ✅ PHASE 4: PRODUCTION HARDENING (Week 5-6)

### Code Quality Fixes (High Priority)

- [ ] **4.1** Fix Issue #1: Validate Phase 4 watchdog spawn
  ```batch
  REM Current:
  start "System3 Watchdog" cmd /k "..."
  timeout /t 2 /nobreak >nul
  
  REM Fixed:
  start "System3 Watchdog" cmd /k "..."
  if errorlevel 1 (
      echo ERROR: Failed to start watchdog
      exit /b 1
  )
  timeout /t 2 /nobreak >nul
  ```
  File: START_AUTORUN_AND_WATCHDOG.bat (line ~170)

- [ ] **4.2** Fix Issue #2: Add timeout to pip installs
  ```batch
  REM Current:
  pip install %%m --quiet
  
  REM Fixed:
  set TIMEOUT_PIP=120
  timeout /t %TIMEOUT_PIP% /nobreak >nul & pip install %%m --quiet
  if errorlevel 1 (
      echo ERROR: Failed to install %%m (network timeout?)
      exit /b 1
  )
  ```
  File: START_AUTORUN_AND_WATCHDOG.bat (line ~85)

- [ ] **4.3** Fix Issue #3: Replace WMIC with PowerShell (Windows 11 compatibility)
  Files affected:
  - SYSTEM3_DAILY_START.bat (archived, but fix for reference)
  - start_system3_env.bat (archived, but fix for reference)
  
  Current:
  ```batch
  for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
  ```
  
  Fixed:
  ```batch
  for /f "delims=" %%I in ('powershell -Command "Get-Date -Format yyyyMMddHHmmss"') do set datetime=%%I
  ```

- [ ] **4.4** Fix Issue #4: Hardcoded paths in heartbeat_maintenance.bat
  ```batch
  REM Current:
  cd /d C:\Genesis_System3
  
  REM Fixed:
  set "ROOT=%~dp0"
  set "ROOT=%ROOT:~0,-1%"
  cd /d "%ROOT%"
  ```
  File: heartbeat_maintenance.bat (line ~5)

- [ ] **4.5** Fix Issue #5: Add conflict detection (prevent multiple instances)
  ```batch
  REM New: Check if autorun master already running
  tasklist | find "python.exe" | find "system3_autorun_master" >nul
  if errorlevel 1 (
      REM Already running; prompt user
      echo ERROR: System3 autorun master already running
      echo Use Task Manager to stop if necessary
      pause
      exit /b 1
  )
  ```
  File: START_AUTORUN_AND_WATCHDOG.bat (add after Phase 5 preamble)

### Documentation & Testing

- [ ] **4.6** Update BATCH_FILES_TECHNICAL_REFERENCE.md:
  - Mark fixed issues with ✓ FIXED
  - Add dates of fixes
  - Reference git commit hashes

- [ ] **4.7** Run comprehensive tests:
  - [ ] Venv check (missing venv) → exits 1 ✓
  - [ ] Dependency install (missing pandas) → installs ✓
  - [ ] Data freshness (stale data) → runs Phase 201 ✓
  - [ ] DRY-RUN safety (LIVE mode) → exits 1 ✓
  - [ ] Watchdog spawn (verify new window) → spawns ✓
  - [ ] Autorun launch (runs trading) → launches ✓
  - [ ] Graceful shutdown (Ctrl+C) → clean exit ✓
  - [ ] Heartbeat valid (v2.0.0 schema) → valid ✓
  - [ ] Multiple instances (launch 2×) → blocks 2nd ✓
  - [ ] Timeout on pip (simulate network hang) → timeout ✓

- [ ] **4.8** Update test_phases_311_330.py:
  - Add: Test for heartbeat schema v2.0.0
  - Add: Test for DRY-RUN mode enforcement
  - Add: Test for watchdog process
  - Expected: All tests pass (20/20 + 3 new)

---

## ✅ PHASE 5: DOCUMENTATION COMPLETION (Week 7)

### Documentation Finalization

- [ ] **5.1** Review all 5 documentation files:
  - [ ] BATCH_FILES_ANALYSIS_COMPLETE.md (executive summary)
  - [ ] BATCH_FILES_QUICK_REFERENCE.md (operator guide)
  - [ ] BATCH_FILES_MICRO_ANALYSIS.md (technical analysis)
  - [ ] BATCH_FILES_TECHNICAL_REFERENCE.md (developer reference)
  - [ ] BATCH_FILES_VISUAL_SUMMARY.md (diagrams & visuals)

- [ ] **5.2** Create final index document:
  - [x] BATCH_FILES_DOCUMENTATION_INDEX.md (cross-references)

- [ ] **5.3** Create operator quick card (A4 printable):
  ```
  ┌─────────────────────────────────────┐
  │ SYSTEM3 DAILY STARTUP - QUICK CARD  │
  ├─────────────────────────────────────┤
  │ 08:00 IST: Safety Check             │
  │  $ system3_daily_safety_check.bat   │
  │                                     │
  │ 08:15 IST: Launch (if PASS)         │
  │  $ START_AUTORUN_AND_WATCHDOG.bat   │
  │                                     │
  │ 15:30 IST: Shutdown                 │
  │  Ctrl+C in autorun window           │
  │                                     │
  │ Troubleshooting: See              │
  │ BATCH_FILES_QUICK_REFERENCE.md    │
  └─────────────────────────────────────┘
  ```

- [ ] **5.4** Create developer API reference:
  - Quick reference to batch patterns
  - Variable scoping cheat sheet
  - Common gotchas (delayed expansion, exit codes, etc.)

- [ ] **5.5** Update main README.md:
  ```markdown
  ## Startup
  
  **Daily Workflow:**
  1. `system3_daily_safety_check.bat` (pre-market gating)
  2. `START_AUTORUN_AND_WATCHDOG.bat` (production startup)
  3. Monitor: logs/ + system3_daily_heartbeat.json
  4. Shutdown: Ctrl+C in autorun window
  
  **More Info:**
  - [Quick Reference](BATCH_FILES_QUICK_REFERENCE.md)
  - [Complete Analysis](BATCH_FILES_ANALYSIS_COMPLETE.md)
  - [Visual Summary](BATCH_FILES_VISUAL_SUMMARY.md)
  ```

### Knowledge Transfer

- [ ] **5.6** Schedule training session (operators):
  - Topic: New startup workflow
  - Duration: 30 minutes
  - Materials: QUICK_REFERENCE.md + VISUAL_SUMMARY.md
  - Attendees: All trading operators

- [ ] **5.7** Schedule training session (developers):
  - Topic: Batch script patterns & modification
  - Duration: 60 minutes
  - Materials: TECHNICAL_REFERENCE.md
  - Attendees: All dev/devops staff

- [ ] **5.8** Create video tutorial (optional):
  - Screen capture: Daily startup workflow
  - Narration: 3-step procedure
  - Duration: 5-10 minutes
  - Upload: Internal wiki/documentation system

---

## ✅ PHASE 6: VALIDATION & SIGN-OFF (Week 8)

### System Testing

- [ ] **6.1** Full end-to-end test (8-hour market session):
  - Run safety check (all 3 pass) ✓
  - Launch system (all phases OK) ✓
  - Monitor for 8 hours (heartbeat stays fresh) ✓
  - Shutdown gracefully (Ctrl+C works) ✓
  - Logs complete and readable ✓

- [ ] **6.2** Edge case testing:
  - [ ] Network failure during startup
  - [ ] Disk full (> 90% usage)
  - [ ] Python process crash (watchdog restarts)
  - [ ] Both processes crash (manual restart required)
  - [ ] Stale heartbeat (> 180s old)

- [ ] **6.3** Performance validation:
  - Startup time: < 120 seconds ✓
  - Heartbeat update: < 1 second ✓
  - Watchdog check: < 10 seconds ✓
  - Memory usage: < 2 GB ✓
  - CPU usage: < 50% ✓

### Team Sign-Off

- [ ] **6.4** Operations team sign-off:
  - Operator testing: 3 full days of trading
  - Result: All systems stable, no crashes
  - Sign-off: YES / NO (timestamp)

- [ ] **6.5** Development team sign-off:
  - Code review: APPROVED / REWORK
  - Testing: All 20+ tests pass
  - Documentation: Complete & accurate
  - Sign-off: YES / NO (timestamp)

- [ ] **6.6** Management approval:
  - Consolidation complete ✓
  - No breaking changes ✓
  - All systems stable ✓
  - Documentation ready ✓
  - Sign-off: YES / NO (date)

### Post-Implementation

- [ ] **6.7** Archive old documentation:
  - Move to docs/deprecated/
  - Keep for reference (1 year)
  - Remove from active docs

- [ ] **6.8** Update maintenance schedule:
  - Weekly: Review logs for errors
  - Monthly: Heartbeat archive size check
  - Quarterly: Performance audit
  - Yearly: Batch script refresh

- [ ] **6.9** Document lessons learned:
  - What went well
  - What could improve
  - Recommendations for next iteration

---

## 📊 TRACKING DASHBOARD

### Status By Phase

```
PHASE 1: Immediate Actions (Week 1)
├─ Documentation & Communication (5/5) _____ 100%
├─ File Deprecation Preparation (3/3) _____ 100%
└─ Testing & Validation (5/5) _____________ 100%

PHASE 2: Consolidation (Week 2-3)
├─ Archive Deprecated Files (5/5) ________ TBD
├─ Update Documentation (4/4) ____________ TBD
└─ Verify Consolidation (3/3) ___________ TBD

PHASE 3: Scheduling (Week 4)
├─ Windows Task Scheduler Setup (5/5) _____ TBD
└─ Logging & Monitoring (3/3) ____________ TBD

PHASE 4: Production Hardening (Week 5-6)
├─ Code Quality Fixes (5/5) _______________ TBD
├─ Documentation & Testing (3/3) _________ TBD
└─ Status: TBD

PHASE 5: Documentation Completion (Week 7)
├─ Documentation Finalization (5/5) ______ TBD
└─ Knowledge Transfer (3/3) ______________ TBD

PHASE 6: Validation & Sign-Off (Week 8)
├─ System Testing (3/3) __________________ TBD
├─ Team Sign-Off (3/3) __________________ TBD
└─ Post-Implementation (3/3) ____________ TBD

TOTAL PROGRESS: _____________________ TBD
```

---

## 🎯 SUCCESS CRITERIA CHECKLIST

### Functional
- [ ] Single master launcher (START_AUTORUN_AND_WATCHDOG.bat) in use
- [ ] All preflight checks automated (venv, deps, data, safety)
- [ ] Watchdog + autorun parallel architecture working
- [ ] DRY-RUN safety gate enforced (exits 1 if live trading)
- [ ] Heartbeat continuous (60s updates) and fresh (< 180s old)
- [ ] Graceful shutdown (Ctrl+C) working
- [ ] All 20+ test phases passing
- [ ] Pre-market safety gating in place

### Operational
- [ ] Operators trained on 3-step workflow
- [ ] Documentation complete (5 documents)
- [ ] Scheduled tasks configured (heartbeat monitoring)
- [ ] Logs properly captured and rotated
- [ ] Heartbeat archives created hourly

### Quality
- [ ] All code quality issues fixed (5 problems resolved)
- [ ] Windows 11 21H2+ compatibility verified
- [ ] Performance expectations met (startup < 120s)
- [ ] 100% uptime during market hours (pilot week)
- [ ] No crashes or hangs (8-hour test)

### Documentation
- [ ] Executive summary complete (ANALYSIS_COMPLETE.md)
- [ ] Operator guide complete (QUICK_REFERENCE.md)
- [ ] Technical analysis complete (MICRO_ANALYSIS.md)
- [ ] Developer reference complete (TECHNICAL_REFERENCE.md)
- [ ] Visual summary complete (VISUAL_SUMMARY.md)
- [ ] Index document complete (DOCUMENTATION_INDEX.md)
- [ ] Deprecated files archived with migration guide

### Sign-Off
- [ ] Operations team: APPROVED ✓
- [ ] Development team: APPROVED ✓
- [ ] Management: APPROVED ✓

---

## 📞 CONTACT & ESCALATION

**Questions:**
- Batch files: See BATCH_FILES_QUICK_REFERENCE.md
- Architecture: See BATCH_FILES_TECHNICAL_REFERENCE.md
- Strategy: See BATCH_FILES_ANALYSIS_COMPLETE.md

**Issues:**
- Startup problems: Troubleshooting section (QUICK_REFERENCE.md)
- Code questions: Ask developer team
- Operational: Contact operations lead

**Escalation:**
- Critical issue: Page on-call engineer
- Documentation issues: Update INDEX.md
- Feature requests: Propose in next quarterly review

---

**END OF IMPLEMENTATION CHECKLIST**

**Completion Target:** December 31, 2025  
**Last Updated:** December 6, 2025  
**Status:** READY TO IMPLEMENT
