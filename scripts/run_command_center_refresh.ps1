# Idempotent Command Center refresh + policy validate + smoke + audit.
# Safe to run repeatedly; overwrites the same coordination artifacts only.
param(
  [string]$RepoRoot = "C:\Users\ADMIN\Genesis_System3\Genesis_System3",
  [switch]$SkipSmoke
)
$ErrorActionPreference = "Stop"
$sdk = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
$env:Path = "$sdk;C:\Users\ADMIN\.local\bin;$env:Path"
Set-Location $RepoRoot

$py = "C:\Pritam_CV_Tier1_EPC\.venv-pr53\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "py" }
function Invoke-Py {
  param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Script,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
  )
  if ($py -eq "py") {
    & py -3 $Script @ScriptArgs
  } else {
    & $py $Script @ScriptArgs
  }
  if ($LASTEXITCODE -ne 0) { throw "failed $Script $($ScriptArgs -join ' ') exit=$LASTEXITCODE" }
}

$env:CC_AGENT_ID = if ($env:CC_AGENT_ID) { $env:CC_AGENT_ID } else { "cursor-composer" }
if (-not $env:CC_RUN_ID) {
  $env:CC_RUN_ID = "local-" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
}
$env:CC_TOKEN_ID = "dryrun-$($env:CC_RUN_ID)"
$env:CC_TOKEN_TTL = "0s-mint-denied"
$env:CC_SIGNER = "agent-id:cursor-composer"

Write-Host "=== validate ACCESS_POLICY ==="
Invoke-Py ".\scripts\validate_access_policy.py"

Write-Host "=== command center refresh (overwrite) ==="
Invoke-Py ".\scripts\system3_command_center_refresh.py"

if (-not $SkipSmoke) {
  Write-Host "=== smoke tests ==="
  try {
    Invoke-Py ".\scripts\command_center_smoke_test.py"
    $auditId = & $py ".\scripts\append_command_center_audit.py" "smoke_test" "pass"
    if ($LASTEXITCODE -ne 0) { throw "failed append_command_center_audit.py smoke_test pass exit=$LASTEXITCODE" }
    Write-Host "audit_entry_id=$auditId"
  } catch {
    & $py ".\scripts\append_command_center_audit.py" "smoke_test" "fail" | Out-Null
    throw
  }
  # Re-write COMMAND_CENTER so smoke_passed + last_audit_entry_id are current
  Write-Host "=== command center status rewrite (post-smoke) ==="
  Invoke-Py ".\scripts\system3_command_center_refresh.py"
}

Write-Host "Done. Open reports\coordination\COMMAND_CENTER.md"
Write-Host "run_id=$($env:CC_RUN_ID) token_id=$($env:CC_TOKEN_ID) (mint denied until VERIFIED signature)"
