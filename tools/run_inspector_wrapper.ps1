<#
  Wrapper script to run `system3_full_inspector.py` and redirect output to a timestamped log.
  Safe, no-network operations; intended to be called by Task Scheduler.
#>
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")

$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$logDir = Join-Path $projectRoot 'logs\inspector'
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$inspectorScript = Join-Path $projectRoot 'system3_full_inspector.py'
if (!(Test-Path $inspectorScript)) {
    Write-Output "Inspector script not found: $inspectorScript"
    exit 1
}

$logFile = Join-Path $logDir "inspector_$ts.log"

# Run python and capture both stdout and stderr
try {
    & python $inspectorScript *> $logFile
    $exitCode = $LASTEXITCODE
} catch {
    $_ | Out-File -FilePath $logFile -Append -Encoding utf8
    $exitCode = 1
}

"Finished run at $(Get-Date -Format o) with exit code $exitCode" | Out-File -FilePath $logFile -Append -Encoding utf8

exit $exitCode
