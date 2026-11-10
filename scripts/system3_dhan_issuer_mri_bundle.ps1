[CmdletBinding()]
param(
    [string]$RepoPath = "",
    [string]$OutDir = "reports/latest/dhan_issuer_mri_bundle",
    [int]$LookbackHours = 72,
    [switch]$SkipCloud,
    [switch]$SkipGitHub,
    [switch]$SkipLiveApi
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$repo = if ($RepoPath) { (Resolve-Path -LiteralPath $RepoPath).Path } else { (Resolve-Path (Join-Path $PSScriptRoot "..")).Path }
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$runDir = Join-Path $repo (Join-Path $OutDir $stamp)
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

function Run-Cli {
    param([string]$Exe, [string[]]$Args)
    try {
        $lines = & $Exe @Args 2>&1
        return [ordered]@{ ok = ($LASTEXITCODE -eq 0); exit_code = $LASTEXITCODE; lines = @($lines | ForEach-Object { [string]$_ }) }
    } catch {
        return [ordered]@{ ok = $false; exit_code = -1; lines = @($_.Exception.Message) }
    }
}

function Safe-JsonCli {
    param([string]$Exe, [string[]]$Args)
    $r = Run-Cli $Exe $Args
    if (-not $r.ok) { return [ordered]@{ ok = $false; error_type = "CLI_FAILED"; exit_code = $r.exit_code } }
    try { return [ordered]@{ ok = $true; data = (($r.lines -join "`n") | ConvertFrom-Json) } }
    catch { return [ordered]@{ ok = $false; error_type = "JSON_PARSE_FAILED"; exit_code = $r.exit_code } }
}

function Markers-InText {
    param([string]$Text)
    $markers = @()
    foreach ($m in @("generate_token", "generateAccessToken", "refresh_token", "DHAN_PIN", "DHAN_TOTP_SECRET", "dhan-pin", "dhan-totp-secret", "dhan-token-rotate")) {
        if ($Text -match [regex]::Escape($m)) { $markers += $m }
    }
    return @($markers | Sort-Object -Unique)
}

function Secret-RefsFromContainer {
    param($Container)
    $refs = @()
    $envNames = @()
    foreach ($e in @($Container.env)) {
        if ($null -eq $e) { continue }
        $envNames += [string]$e.name
        if ($e.valueFrom.secretKeyRef.name) {
            $refs += [ordered]@{ env = [string]$e.name; secret = [string]$e.valueFrom.secretKeyRef.name; version = [string]$e.valueFrom.secretKeyRef.key }
        }
    }
    return [ordered]@{ env_names = @($envNames | Sort-Object -Unique); secret_refs = $refs }
}

$started = (Get-Date).ToUniversalTime()
$result = [ordered]@{
    schema = "system3-dhan-issuer-mri-bundle-v1"
    started_at_utc = $started.ToString("o")
    repo = $repo
    safety = [ordered]@{
        read_only = $true; cloud_mutations = $false; broker_mutations = $false
        order_calls = $false; raw_token_exposed = $false; pin_exposed = $false; totp_exposed = $false
    }
    local = [ordered]@{}
    github = [ordered]@{}
    gcp = [ordered]@{}
    live_api = [ordered]@{}
    anomalies = @()
}

# Local Git truth. Status paths are safe; file contents are never copied.
$head = Run-Cli git @("-C", $repo, "rev-parse", "HEAD")
$origin = Run-Cli git @("-C", $repo, "rev-parse", "origin/main")
$status = Run-Cli git @("-C", $repo, "status", "--short")
$result.local.git = [ordered]@{
    head = if ($head.ok) { $head.lines[0] } else { $null }
    origin_main = if ($origin.ok) { $origin.lines[0] } else { $null }
    status_paths = @($status.lines)
    clean = ($status.ok -and $status.lines.Count -eq 0)
}

# Process command lines are inspected in memory, but only process identity and marker names are emitted.
try {
    $processes = foreach ($p in Get-CimInstance Win32_Process) {
        $markers = Markers-InText ([string]$p.CommandLine)
        if ($markers.Count) { [ordered]@{ pid = $p.ProcessId; name = $p.Name; markers = $markers } }
    }
    $result.local.processes = [ordered]@{ ok = $true; matches = @($processes) }
} catch {
    $result.local.processes = [ordered]@{ ok = $false; error_type = "ACCESS_DENIED_OR_UNAVAILABLE" }
    $result.anomalies += "LOCAL_PROCESS_INVENTORY_UNAVAILABLE"
}

# Task arguments are never emitted because they may contain credentials.
try {
    $tasks = foreach ($t in Get-ScheduledTask) {
        $joined = (@($t.Actions | ForEach-Object { "$( $_.Execute ) $( $_.Arguments )" }) -join " ")
        $markers = Markers-InText ("$($t.TaskName) $($t.TaskPath) $joined")
        if ($markers.Count) {
            [ordered]@{ task_name = $t.TaskName; task_path = $t.TaskPath; state = [string]$t.State; markers = $markers; executables = @($t.Actions | ForEach-Object { Split-Path -Leaf ([string]$_.Execute) }) }
        }
    }
    $result.local.scheduled_tasks = [ordered]@{ ok = $true; matches = @($tasks) }
} catch {
    $result.local.scheduled_tasks = [ordered]@{ ok = $false; error_type = "ACCESS_DENIED_OR_UNAVAILABLE" }
    $result.anomalies += "LOCAL_SCHEDULED_TASK_INVENTORY_UNAVAILABLE"
}

# Names-only credential caller/file inventory. Values and matching lines are never retained.
$hits = @()
$roots = @("scripts", "core", "dashboard", ".github", ".cursor", "config", "deploy", "infra", "tools")
foreach ($rootName in $roots) {
    $rootPath = Join-Path $repo $rootName
    if (-not (Test-Path $rootPath)) { continue }
    Get-ChildItem -LiteralPath $rootPath -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -le 2MB -and $_.Extension -in @(".py", ".ps1", ".yml", ".yaml", ".json", ".toml", ".ini", ".env", ".md", ".txt", ".sh") } |
        ForEach-Object {
            try {
                $text = [IO.File]::ReadAllText($_.FullName)
                $markers = Markers-InText $text
                if ($markers.Count) { $hits += [ordered]@{ path = $_.FullName.Substring($repo.Length + 1).Replace("\", "/"); markers = $markers } }
            } catch { }
        }
}
$result.local.names_only_caller_files = @($hits | Sort-Object path)

if (-not $SkipGitHub) {
    $repoMeta = Safe-JsonCli gh @("api", "repos/psw2025-cmd/Genesis_System3")
    $runs = Safe-JsonCli gh @("run", "list", "--repo", "psw2025-cmd/Genesis_System3", "--limit", "100", "--json", "databaseId,name,event,status,conclusion,createdAt,updatedAt,headSha,url")
    $result.github.repository = if ($repoMeta.ok) { [ordered]@{ ok = $true; private = $repoMeta.data.private; visibility = $repoMeta.data.visibility; default_branch = $repoMeta.data.default_branch; pushed_at = $repoMeta.data.pushed_at } } else { $repoMeta }
    $result.github.runs = $runs
    $workflowHits = foreach ($f in Get-ChildItem (Join-Path $repo ".github/workflows") -File -ErrorAction SilentlyContinue) {
        $text = [IO.File]::ReadAllText($f.FullName)
        $markers = Markers-InText $text
        if ($markers.Count) {
            [ordered]@{ file = $f.Name; markers = $markers; has_schedule = ($text -match "(?m)^\s*schedule\s*:"); has_dispatch = ($text -match "workflow_dispatch") }
        }
    }
    $result.github.workflow_mint_markers = @($workflowHits)
}

if (-not $SkipCloud) {
    $project = "system3-openalgo-safe"; $region = "asia-south1"
    $jobs = Safe-JsonCli gcloud @("run", "jobs", "list", "--project", $project, "--region", $region, "--format=json")
    $jobInventory = @()
    if ($jobs.ok) {
        foreach ($j in @($jobs.data)) {
            $name = [string]$j.metadata.name
            $d = Safe-JsonCli gcloud @("run", "jobs", "describe", $name, "--project", $project, "--region", $region, "--format=json")
            if (-not $d.ok) { $jobInventory += [ordered]@{ name = $name; ok = $false }; continue }
            $spec = $d.data.spec.template.spec.template.spec
            $containers = foreach ($c in @($spec.containers)) { Secret-RefsFromContainer $c }
            $allRefs = @($containers | ForEach-Object { $_.secret_refs } | ForEach-Object { $_ })
            $pin = @($allRefs | Where-Object { $_.secret -eq "dhan-pin" }).Count -gt 0
            $totp = @($allRefs | Where-Object { $_.secret -eq "dhan-totp-secret" }).Count -gt 0
            $jobInventory += [ordered]@{ name = $name; service_account = [string]$spec.serviceAccountName; containers = @($containers); mint_capable = ($pin -and $totp); execution_count = $d.data.status.executionCount; latest_execution = $d.data.status.latestCreatedExecution }
        }
    }
    $result.gcp.jobs = [ordered]@{ ok = $jobs.ok; inventory = $jobInventory }

    $services = Safe-JsonCli gcloud @("run", "services", "list", "--project", $project, "--region", $region, "--format=json")
    $serviceInventory = @()
    if ($services.ok) {
        foreach ($svc in @($services.data)) {
            $name = [string]$svc.metadata.name
            $d = Safe-JsonCli gcloud @("run", "services", "describe", $name, "--project", $project, "--region", $region, "--format=json")
            if (-not $d.ok) { $serviceInventory += [ordered]@{ name = $name; ok = $false }; continue }
            $spec = $d.data.spec.template.spec
            $containers = foreach ($c in @($spec.containers)) { Secret-RefsFromContainer $c }
            $allRefs = @($containers | ForEach-Object { $_.secret_refs } | ForEach-Object { $_ })
            $pin = @($allRefs | Where-Object { $_.secret -eq "dhan-pin" }).Count -gt 0
            $totp = @($allRefs | Where-Object { $_.secret -eq "dhan-totp-secret" }).Count -gt 0
            $serviceInventory += [ordered]@{ name = $name; service_account = [string]$spec.serviceAccountName; revision = $d.data.status.latestReadyRevisionName; containers = @($containers); mint_capable = ($pin -and $totp) }
        }
    }
    $result.gcp.services = [ordered]@{ ok = $services.ok; inventory = $serviceInventory }

    $result.gcp.schedulers = Safe-JsonCli gcloud @("scheduler", "jobs", "list", "--project", $project, "--location", $region, "--format=json")
    $result.gcp.rotator_executions = Safe-JsonCli gcloud @("run", "jobs", "executions", "list", "--job", "genesis-system3-dhan-token-rotate", "--project", $project, "--region", $region, "--limit", "100", "--format=json")
    foreach ($secret in @("dhan-access-token", "dhan-access-token-candidate", "dhan-pin", "dhan-totp-secret")) {
        $versions = Safe-JsonCli gcloud @("secrets", "versions", "list", $secret, "--project", $project, "--limit", "100", "--format=json")
        $iam = Safe-JsonCli gcloud @("secrets", "get-iam-policy", $secret, "--project", $project, "--format=json")
        $safeVersions = @()
        if ($versions.ok) { $safeVersions = @($versions.data | ForEach-Object { [ordered]@{ name = $_.name; create_time = $_.createTime; state = $_.state } }) }
        $safeBindings = @()
        if ($iam.ok) { $safeBindings = @($iam.data.bindings | ForEach-Object { [ordered]@{ role = $_.role; members = @($_.members) } }) }
        $result.gcp["secret_$($secret.Replace('-', '_'))"] = [ordered]@{ versions_ok = $versions.ok; versions = $safeVersions; iam_ok = $iam.ok; iam_bindings = $safeBindings }
    }
    $mintJobs = @($jobInventory | Where-Object { $_.mint_capable })
    $mintServices = @($serviceInventory | Where-Object { $_.mint_capable })
    if (-not $jobs.ok) { $result.anomalies += "GCP_JOB_INVENTORY_UNAVAILABLE" }
    elseif ($mintJobs.Count -ne 1 -or $mintJobs[0].name -ne "genesis-system3-dhan-token-rotate") { $result.anomalies += "GCP_JOB_MINT_AUTHORITY_NOT_SINGLE_CANONICAL" }
    if (-not $services.ok) { $result.anomalies += "GCP_SERVICE_INVENTORY_UNAVAILABLE" }
    elseif ($mintServices.Count) { $result.anomalies += "GCP_SERVICE_HAS_PIN_AND_TOTP" }
}

if (-not $SkipLiveApi) {
    $oldHttp = $env:HTTP_PROXY; $oldHttps = $env:HTTPS_PROXY; $oldAll = $env:ALL_PROXY
    try {
        $env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:ALL_PROXY = ""
        $base = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
        foreach ($path in @("/api/deploy/info", "/api/health", "/api/broker/status", "/api/broker/truth", "/api/batch/chains?symbols=NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY")) {
            try {
                $o = Invoke-RestMethod -Uri ($base + $path) -Method Get -TimeoutSec 90
                if ($path -eq "/api/deploy/info") { $safe = [ordered]@{ git_sha = $o.git_sha } }
                elseif ($path -eq "/api/health") { $safe = [ordered]@{ status = $o.status; broker_status = $o.broker_status; connected = $o.broker.connected; live_allowed = $o.live_allowed } }
                elseif ($path -eq "/api/broker/status") { $safe = [ordered]@{ connected = $o.connected; error = $o.error; auth_classification = $o.auth_classification; upstream_code = $o.upstream_code; latency_ms = $o.latency_ms; order_placement_allowed = $o.order_placement_allowed } }
                elseif ($path -eq "/api/broker/truth") { $b = $o.broker; $safe = [ordered]@{ connected = $b.connected; error = $b.error; auth_classification = $b.auth_classification; upstream_code = $b.upstream_code; secret_version = $b.token_proof.secret_version; expires_at_utc = $b.token_proof.expires_at_utc; token_value_exposed = $b.token_proof.token_value_exposed } }
                else {
                    $safeChains = [ordered]@{}
                    foreach ($n in @("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")) { $c = $o.chains.$n; $safeChains[$n] = [ordered]@{ count = $c.total_contracts; source = $c.data_source; live = $c.live; stale = $c.stale; status = $c.status } }
                    $safe = [ordered]@{ chains = $safeChains }
                }
                $result.live_api[$path] = [ordered]@{ ok = $true; observed_at_utc = (Get-Date).ToUniversalTime().ToString("o"); data = $safe }
            } catch { $result.live_api[$path] = [ordered]@{ ok = $false; error_type = $_.Exception.GetType().Name } }
        }
    } finally { $env:HTTP_PROXY = $oldHttp; $env:HTTPS_PROXY = $oldHttps; $env:ALL_PROXY = $oldAll }
}

$result.anomalies = @($result.anomalies | Sort-Object -Unique)
$result.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
$result.overall = if ($result.anomalies.Count -eq 0) { "PASS_NO_DUPLICATE_ISSUER_FOUND" } else { "FAIL_ANOMALIES_FOUND" }
$jsonPath = Join-Path $runDir "issuer_mri.json"
$mdPath = Join-Path $runDir "SHARE_THIS_SUMMARY.md"
$result | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$md = @(
    "# System3 Dhan Issuer MRI (redacted)", "", "- Started UTC: $($result.started_at_utc)",
    "- Completed UTC: $($result.completed_at_utc)", "- Overall: **$($result.overall)**",
    "- Raw token/PIN/TOTP exposed: **false**", "", "## Anomalies", ""
)
if ($result.anomalies.Count) { $md += @($result.anomalies | ForEach-Object { "- $_" }) } else { $md += "- None detected by this collector." }
$md += @("", "## Share", "", "Share this Markdown file and `issuer_mri.json`. Never share token, PIN, TOTP seed, QR, `.env`, or Secret Manager payloads.")
$md | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Output "MRI_JSON=$jsonPath"
Write-Output "SHARE_SUMMARY=$mdPath"
Write-Output "OVERALL=$($result.overall)"
Write-Output "RAW_SECRETS_EXPOSED=false"
if ($result.anomalies.Count) { exit 2 }
exit 0
