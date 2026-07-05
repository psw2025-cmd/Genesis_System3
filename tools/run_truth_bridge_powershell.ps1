# System3 Truth Bridge - PowerShell No-Python Runner
# Runs from this cloned repo. Uses no Python and no GitHub Actions minutes.
# Read-only against live dashboard APIs. No secrets. No orders. No live trading.

$ErrorActionPreference = "Continue"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$BaseUrl = $env:SYSTEM3_BASE_URL
if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = "https://genesis-system3-backend.onrender.com"
}
$UnderlyingsRaw = $env:SYSTEM3_UNDERLYINGS
if ([string]::IsNullOrWhiteSpace($UnderlyingsRaw)) {
    $UnderlyingsRaw = "NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY"
}
$Underlyings = $UnderlyingsRaw.Split(",") | ForEach-Object { $_.Trim().ToUpper() } | Where-Object { $_ }

$TruthDir = Join-Path $RepoRoot "reports/latest/system3_truth_bridge"
$ProdDir = Join-Path $RepoRoot "reports/latest/production_viability_bridge"
New-Item -ItemType Directory -Force -Path $TruthDir | Out-Null
New-Item -ItemType Directory -Force -Path $ProdDir | Out-Null

function Get-JsonSafe {
    param([string]$Url)
    $started = Get-Date
    try {
        $data = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 30 -Headers @{ "User-Agent" = "System3TruthBridge-PowerShell/1.0" }
        $elapsed = [int]((Get-Date) - $started).TotalMilliseconds
        return [ordered]@{ ok = $true; url = $Url; elapsed_ms = $elapsed; data = $data }
    } catch {
        $elapsed = [int]((Get-Date) - $started).TotalMilliseconds
        return [ordered]@{ ok = $false; url = $Url; elapsed_ms = $elapsed; error = $_.Exception.Message }
    }
}

function Read-JsonFileSafe {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return [ordered]@{ ok = $false; missing = $true; path = $Path }
    }
    try {
        $data = Get-Content -Raw -Path $Path | ConvertFrom-Json
        return [ordered]@{ ok = $true; path = $Path; data = $data }
    } catch {
        return [ordered]@{ ok = $false; path = $Path; error = $_.Exception.Message }
    }
}

function Add-Issue {
    param(
        [System.Collections.ArrayList]$Issues,
        [string]$Severity,
        [string]$Code,
        [string]$Message,
        $Proof = @{}
    )
    [void]$Issues.Add([ordered]@{ severity = $Severity; code = $Code; message = $Message; proof = $Proof })
}

$Endpoints = [ordered]@{}
$Targets = [ordered]@{
    state = "$BaseUrl/api/state"
    health = "$BaseUrl/api/health"
    broker_status = "$BaseUrl/api/broker/status"
    debug_state_source = "$BaseUrl/api/debug/state_source"
    underlyings = "$BaseUrl/api/underlyings"
    qc = "$BaseUrl/api/qc"
}
foreach ($u in $Underlyings) {
    $Targets["chain_$u"] = "$BaseUrl/api/chain/$u"
}
foreach ($name in $Targets.Keys) {
    Write-Host "[INFO] Fetching $name -> $($Targets[$name])"
    $Endpoints[$name] = Get-JsonSafe -Url $Targets[$name]
}

$ProofFiles = [ordered]@{
    full_trading_pipeline_readiness = "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json"
    proof_status_matrix = "reports/latest/proof_status_matrix/proof_status_matrix.json"
    dashboard_truth_proof = "reports/latest/dashboard_truth_proof/summary.json"
    fresh_data_automation_proof = "reports/latest/fresh_data_automation_proof/summary.json"
    analyzer_paper_lifecycle_proof = "reports/latest/analyzer_paper_lifecycle_proof/summary.json"
    analyzer_paper_lifecycle_raw = "reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_142129.json"
    model_training_load_proof = "reports/latest/model_training_load_proof/summary.json"
    live_current_issues = "reports/latest/live_current_issue_check/issues.json"
}
$Proofs = [ordered]@{}
foreach ($name in $ProofFiles.Keys) {
    $Proofs[$name] = Read-JsonFileSafe -Path (Join-Path $RepoRoot $ProofFiles[$name])
}

$Issues = New-Object System.Collections.ArrayList
foreach ($name in $Endpoints.Keys) {
    if (-not $Endpoints[$name].ok) {
        Add-Issue $Issues "HIGH" "LIVE_ENDPOINT_FAILED" "Live endpoint failed: $name" ([ordered]@{ endpoint = $name; error = $Endpoints[$name].error; url = $Endpoints[$name].url })
    }
}

$State = $null
$Health = $null
$Broker = $null
if ($Endpoints.state.ok) { $State = $Endpoints.state.data }
if ($Endpoints.health.ok) { $Health = $Endpoints.health.data }
if ($Endpoints.broker_status.ok) { $Broker = $Endpoints.broker_status.data }

$mode = $null
$marketOpen = $null
$stateDataSource = $null
$healthDataSource = $null
$brokerConnected = $null
$alertsCount = $null
$liveEnabled = $null
$orderAllowed = $null

try { $mode = $State.mode } catch {}
try { $marketOpen = $State.market.is_open } catch {}
try { $stateDataSource = $State.data_source } catch {}
try { $healthDataSource = $Health.data_source } catch {}
try { $brokerConnected = $State.broker.connected } catch {}
try { $liveEnabled = $State.broker.live_trading_enabled } catch {}
try { $orderAllowed = $State.broker.order_placement_allowed } catch {}
try { $alertsCount = @($State.alerts).Count } catch {}

if ($mode -eq "LIVE" -or $liveEnabled -eq $true -or $orderAllowed -eq $true) {
    Add-Issue $Issues "CRITICAL" "LIVE_SAFETY_BREACH" "Live mode/order placement appears enabled." ([ordered]@{ mode = $mode; live_trading_enabled = $liveEnabled; order_placement_allowed = $orderAllowed })
}

foreach ($name in $Endpoints.Keys) {
    if ($name -like "chain_*" -and $Endpoints[$name].ok) {
        $chain = $Endpoints[$name].data
        $chainStatus = $null
        try { $chainStatus = [string]$chain.status } catch {}
        if ($brokerConnected -eq $true -and $chainStatus.ToLower() -eq "not_ready") {
            Add-Issue $Issues "HIGH" "CHAIN_NOT_READY_WITH_BROKER" "$name says NOT_READY while broker is connected." ([ordered]@{ chain_status = $chainStatus })
        }
    }
}

$Pipeline = $Proofs.full_trading_pipeline_readiness.data
try {
    if ($Pipeline.trade_ready -ne $true) {
        Add-Issue $Issues "CRITICAL" "TRADE_READY_FALSE" "Full trading pipeline is not trade ready." ([ordered]@{ verdict = $Pipeline.verdict })
    }
} catch {}

$Life = $Proofs.analyzer_paper_lifecycle_proof.data
try {
    if ($Life.evidence.full_lifecycle_proven -ne $true -or $Life.evidence.lifecycle_proof_dry_run -eq $true) {
        Add-Issue $Issues "CRITICAL" "REAL_PAPER_LIFECYCLE_NOT_PROVEN" "Real market analyzer paper lifecycle is not proven." ([ordered]@{ full_lifecycle_proven = $Life.evidence.full_lifecycle_proven; dry_run = $Life.evidence.lifecycle_proof_dry_run })
    }
} catch {}

$Generated = (Get-Date).ToUniversalTime().ToString("o")
$Summary = [ordered]@{
    generated_utc = $Generated
    runner = "PowerShell-NoPython"
    repo = "psw2025-cmd/Genesis_System3"
    mode = $mode
    market_open = $marketOpen
    state_data_source = $stateDataSource
    health_data_source = $healthDataSource
    broker_connected = $brokerConnected
    alerts_count = $alertsCount
    issue_count = $Issues.Count
    live_trading_enabled = $liveEnabled
    order_placement_allowed = $orderAllowed
}

$TruthReport = [ordered]@{
    generated_utc = $Generated
    base_url = $BaseUrl
    runner = "PowerShell-NoPython"
    purpose = "GitHub-readable dashboard truth report generated without Python."
    live = $Endpoints
    proofs = $Proofs
    issues = $Issues
    summary = $Summary
}

$TruthJsonPath = Join-Path $TruthDir "latest.json"
$TruthMdPath = Join-Path $TruthDir "summary.md"
$TruthReport | ConvertTo-Json -Depth 50 | Set-Content -Encoding UTF8 -Path $TruthJsonPath

$md = @()
$md += "# System3 Truth Bridge"
$md += ""
$md += "Generated UTC: ``$Generated``"
$md += ""
$md += "## Summary"
$md += ""
$md += "| Field | Value |"
$md += "|---|---|"
foreach ($k in $Summary.Keys) { $md += "| ``$k`` | ``$($Summary[$k])`` |" }
$md += ""
$md += "## Issues"
$md += ""
$md += "| Severity | Code | Message |"
$md += "|---|---|---|"
foreach ($i in $Issues) { $md += "| $($i.severity) | ``$($i.code)`` | $($i.message) |" }
if ($Issues.Count -eq 0) { $md += "| NONE | - | No issues detected by bridge rules. |" }
$md | Set-Content -Encoding UTF8 -Path $TruthMdPath

$ProdSummary = [ordered]@{
    generated_utc = $Generated
    runner = "PowerShell-NoPython"
    production_live_ready = $false
    paper_analyzer_allowed = $true
    strategy_quarantined_for_live = $true
    reason = "Production/live readiness remains blocked until real market paper lifecycle, broker freshness, tick health, execution quality and positive net expectancy are proven."
}
$ProdReport = [ordered]@{
    generated_utc = $Generated
    summary = $ProdSummary
    blockers = @(
        [ordered]@{ severity = "HIGH"; code = "LIVE_DISABLED_UNTIL_PROVEN"; message = "Live trading remains disabled until all production gates pass." },
        [ordered]@{ severity = "HIGH"; code = "WEBSOCKET_TICK_HEALTH_NOT_PROVEN"; message = "WebSocket tick health proof is not available from PowerShell bridge." },
        [ordered]@{ severity = "HIGH"; code = "FRICTION_EXPECTANCY_NOT_PROVEN_POSITIVE"; message = "Positive expectancy after all costs is not proven." }
    )
}
$ProdReport | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 -Path (Join-Path $ProdDir "latest.json")

$pm = @()
$pm += "# System3 Production Viability Bridge"
$pm += ""
$pm += "Generated UTC: ``$Generated``"
$pm += ""
$pm += "## Summary"
$pm += ""
$pm += "| Field | Value |"
$pm += "|---|---|"
foreach ($k in $ProdSummary.Keys) { $pm += "| ``$k`` | ``$($ProdSummary[$k])`` |" }
$pm += ""
$pm += "## Blockers"
$pm += ""
$pm += "| Severity | Code | Message |"
$pm += "|---|---|---|"
foreach ($b in $ProdReport.blockers) { $pm += "| $($b.severity) | ``$($b.code)`` | $($b.message) |" }
$pm | Set-Content -Encoding UTF8 -Path (Join-Path $ProdDir "summary.md")

Write-Host "[DONE] Reports generated without Python:"
Write-Host "  $TruthMdPath"
Write-Host "  $(Join-Path $ProdDir 'summary.md')"
Write-Host ""
Write-Host "Optional upload:"
Write-Host "  git add reports/latest/system3_truth_bridge reports/latest/production_viability_bridge"
Write-Host "  git commit -m 'proof: update PowerShell truth bridge reports'"
Write-Host "  git push"
