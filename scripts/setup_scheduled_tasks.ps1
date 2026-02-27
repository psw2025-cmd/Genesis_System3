# Create Windows Task Scheduler tasks for System3 Ultra maintenance.
# Run as Administrator to create tasks. Adjust PROJECT_ROOT if needed.
$ErrorActionPreference = "Stop"
$PROJECT_ROOT = "C:\Genesis_System3"
$DailyBat = Join-Path $PROJECT_ROOT "scripts\run_daily_monitor.bat"
$WeeklyBat = Join-Path $PROJECT_ROOT "scripts\run_weekly_qc.bat"

if (-not (Test-Path $DailyBat)) { Write-Error "Not found: $DailyBat" }
if (-not (Test-Path $WeeklyBat)) { Write-Error "Not found: $WeeklyBat" }

$trDaily = "cmd /c `"$DailyBat`""
$trWeekly = "cmd /c `"$WeeklyBat`""

# Daily: 6:00 AM (current user)
schtasks /Create /TN "System3 Ultra Daily Monitor" /TR $trDaily /SC DAILY /ST 06:00 /F
Write-Host "[OK] Task created: System3 Ultra Daily Monitor (daily 06:00)"

# Weekly: Sunday 7:00 AM (current user)
schtasks /Create /TN "System3 Ultra Weekly QC Audit" /TR $trWeekly /SC WEEKLY /D SUN /ST 07:00 /F
Write-Host "[OK] Task created: System3 Ultra Weekly QC Audit (weekly Sun 07:00)"
Write-Host "Tasks run under current user. To change schedule: Task Scheduler -> System3 Ultra Daily Monitor / Weekly QC Audit."
