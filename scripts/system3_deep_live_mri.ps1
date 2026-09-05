param(
  [string]$BaseUrl = 'https://genesis-system3-web-doq2wplepa-el.a.run.app',
  [string]$OutRoot = 'C:\Temp',
  [int]$Samples = 5,
  [int]$DelaySeconds = 20,
  [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = 'Continue'
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$out = Join-Path $OutRoot "System3_DEEP_MRI_$ts"
New-Item -ItemType Directory -Force -Path $out | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $out 'samples') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $out 'network') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $out 'ui') | Out-Null

$summary = Join-Path $out '00_SUMMARY.txt'
"GENESIS SYSTEM3 DEEP LIVE MRI - READ ONLY" | Set-Content $summary
"Generated: $(Get-Date -Format o)" | Add-Content $summary
"BaseUrl: $BaseUrl" | Add-Content $summary
"Samples: $Samples" | Add-Content $summary
"DelaySeconds: $DelaySeconds" | Add-Content $summary
"Machine: $env:COMPUTERNAME" | Add-Content $summary
"PowerShell: $($PSVersionTable.PSVersion)" | Add-Content $summary
"LIVE MUTATION: NONE" | Add-Content $summary

$endpoints = @(
  '/',
  '/api/health',
  '/api/state',
  '/api/deploy/info',
  '/api/broker/status',
  '/api/auto_gates',
  '/api/pnl',
  '/api/accuracy_trend',
  '/api/instruments/health',
  '/api/chain/NIFTY',
  '/api/chain/BANKNIFTY',
  '/api/chain/FINNIFTY',
  '/api/chain/MIDCPNIFTY',
  '/api/state',
  '/api/market/status',
  '/api/scanner/status',
  '/api/alerts',
  '/api/paper/positions',
  '/api/paper/trades',
  '/api/model/status',
  '/api/model/metrics',
  '/api/storage/health'
)

function SafeName([string]$s) {
  $n = $s.Trim('/') -replace '[^a-zA-Z0-9_-]','_'
  if ([string]::IsNullOrWhiteSpace($n)) { return 'root' }
  return $n
}

$latencyRows = New-Object System.Collections.Generic.List[object]
$sampleMeta = New-Object System.Collections.Generic.List[object]

for ($i = 1; $i -le $Samples; $i++) {
  $sampleDir = Join-Path $out ('samples\sample_{0:D2}' -f $i)
  New-Item -ItemType Directory -Force -Path $sampleDir | Out-Null
  "--- SAMPLE $i / $Samples : $(Get-Date -Format o) ---" | Add-Content $summary

  foreach ($ep in $endpoints) {
    $name = SafeName $ep
    $url = "$BaseUrl$ep"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $status = $null
    $bytes = 0
    $err = $null
    try {
      $resp = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec $TimeoutSeconds -UseBasicParsing
      $sw.Stop()
      $status = [int]$resp.StatusCode
      $bytes = [Text.Encoding]::UTF8.GetByteCount([string]$resp.Content)
      $headers = @{}
      foreach ($k in $resp.Headers.Keys) { $headers[$k] = [string]$resp.Headers[$k] }
      $headers | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $sampleDir "$name.headers.json") -Encoding UTF8
      try {
        ($resp.Content | ConvertFrom-Json) | ConvertTo-Json -Depth 60 | Set-Content (Join-Path $sampleDir "$name.json") -Encoding UTF8
      } catch {
        $resp.Content | Set-Content (Join-Path $sampleDir "$name.txt") -Encoding UTF8
      }
    } catch {
      $sw.Stop()
      $err = $_.Exception.Message
      ($_ | Out-String) | Set-Content (Join-Path $sampleDir "$name.ERROR.txt") -Encoding UTF8
      if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
        try { $status = [int]$_.Exception.Response.StatusCode } catch {}
      }
    }
    $latencyRows.Add([pscustomobject]@{
      sample=$i; timestamp=(Get-Date -Format o); endpoint=$ep; http_status=$status;
      elapsed_ms=[math]::Round($sw.Elapsed.TotalMilliseconds,2); bytes=$bytes; error=$err
    })
  }

  $sampleMeta.Add([pscustomobject]@{sample=$i; timestamp=(Get-Date -Format o)})
  if ($i -lt $Samples) { Start-Sleep -Seconds $DelaySeconds }
}

$latencyRows | Export-Csv (Join-Path $out '10_ENDPOINT_LATENCY.csv') -NoTypeInformation
$sampleMeta | Export-Csv (Join-Path $out '11_SAMPLE_TIMES.csv') -NoTypeInformation

# Cross-sample hash/change detector
$changeRows = New-Object System.Collections.Generic.List[object]
$filesByLogical = @{}
Get-ChildItem (Join-Path $out 'samples') -Recurse -File -Filter '*.json' | ForEach-Object {
  $logical = $_.Name
  if (-not $filesByLogical.ContainsKey($logical)) { $filesByLogical[$logical] = @() }
  $filesByLogical[$logical] += $_.FullName
}
foreach ($logical in $filesByLogical.Keys) {
  $prev = $null
  foreach ($f in ($filesByLogical[$logical] | Sort-Object)) {
    $h = (Get-FileHash $f -Algorithm SHA256).Hash
    $changed = if ($null -eq $prev) { $false } else { $h -ne $prev }
    $changeRows.Add([pscustomobject]@{logical_file=$logical; file=$f; sha256=$h; changed_from_previous=$changed})
    $prev = $h
  }
}
$changeRows | Export-Csv (Join-Path $out '12_CROSS_SAMPLE_HASH_CHANGES.csv') -NoTypeInformation

# Latency anomaly detector: endpoint median + MAD-like threshold using simple robust statistics
$anomalyRows = New-Object System.Collections.Generic.List[object]
$latencyRows | Group-Object endpoint | ForEach-Object {
  $vals = @($_.Group | Where-Object { -not $_.error } | ForEach-Object { [double]$_.elapsed_ms } | Sort-Object)
  if ($vals.Count -gt 0) {
    $mid = [int][math]::Floor($vals.Count/2)
    $median = if ($vals.Count % 2 -eq 1) { $vals[$mid] } else { ($vals[$mid-1]+$vals[$mid])/2 }
    $abs = @($vals | ForEach-Object { [math]::Abs($_-$median) } | Sort-Object)
    $mad = if ($abs.Count % 2 -eq 1) { $abs[[int][math]::Floor($abs.Count/2)] } else { ($abs[$abs.Count/2-1]+$abs[$abs.Count/2])/2 }
    $threshold = $median + [math]::Max(250.0, 6.0*$mad)
    foreach ($r in $_.Group) {
      $isAnom = $false
      if ($r.error) { $isAnom = $true }
      elseif ([double]$r.elapsed_ms -gt $threshold) { $isAnom = $true }
      $anomalyRows.Add([pscustomobject]@{
        endpoint=$r.endpoint; sample=$r.sample; elapsed_ms=$r.elapsed_ms; http_status=$r.http_status;
        median_ms=[math]::Round($median,2); mad_ms=[math]::Round($mad,2); threshold_ms=[math]::Round($threshold,2);
        anomaly=$isAnom; error=$r.error
      })
    }
  }
}
$anomalyRows | Export-Csv (Join-Path $out '13_LATENCY_ANOMALIES.csv') -NoTypeInformation

# Network / DNS / TLS / HTTP headers
$hostName = ([uri]$BaseUrl).Host
try { Resolve-DnsName $hostName | Format-List * | Out-String | Set-Content (Join-Path $out 'network\dns.txt') } catch { $_ | Out-String | Set-Content (Join-Path $out 'network\dns.ERROR.txt') }
try { Test-NetConnection $hostName -Port 443 | Format-List * | Out-String | Set-Content (Join-Path $out 'network\tcp443.txt') } catch { $_ | Out-String | Set-Content (Join-Path $out 'network\tcp443.ERROR.txt') }
try { tracert -d -h 12 $hostName | Out-String | Set-Content (Join-Path $out 'network\tracert.txt') } catch { $_ | Out-String | Set-Content (Join-Path $out 'network\tracert.ERROR.txt') }
try {
  $tcp = New-Object Net.Sockets.TcpClient($hostName,443)
  $ssl = New-Object Net.Security.SslStream($tcp.GetStream(),$false,({$true}))
  $ssl.AuthenticateAsClient($hostName)
  $cert = New-Object Security.Cryptography.X509Certificates.X509Certificate2($ssl.RemoteCertificate)
  [pscustomobject]@{Subject=$cert.Subject;Issuer=$cert.Issuer;NotBefore=$cert.NotBefore;NotAfter=$cert.NotAfter;Thumbprint=$cert.Thumbprint;DaysRemaining=[math]::Round(($cert.NotAfter-(Get-Date)).TotalDays,2)} |
    ConvertTo-Json | Set-Content (Join-Path $out 'network\tls_certificate.json')
  $ssl.Dispose(); $tcp.Close()
} catch { $_ | Out-String | Set-Content (Join-Path $out 'network\tls.ERROR.txt') }

# Static UI shell and optional headless browser screenshots/DOM if Edge or Chrome exists
try { (Invoke-WebRequest -Uri "$BaseUrl/ui" -UseBasicParsing -TimeoutSec $TimeoutSeconds).Content | Set-Content (Join-Path $out 'ui\UI_shell.html') -Encoding UTF8 } catch { $_ | Out-String | Set-Content (Join-Path $out 'ui\UI_shell.ERROR.txt') }

$browserCandidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { $_ -and (Test-Path $_) }
if ($browserCandidates.Count -gt 0) {
  $browser = $browserCandidates[0]
  "Browser: $browser" | Set-Content (Join-Path $out 'ui\browser_used.txt')
  try {
    & $browser --headless=new --disable-gpu --hide-scrollbars --window-size=1920,3000 --virtual-time-budget=15000 --screenshot=(Join-Path $out 'ui\dashboard.png') "$BaseUrl/ui" 2>&1 | Out-String | Set-Content (Join-Path $out 'ui\browser_screenshot.log')
  } catch { $_ | Out-String | Set-Content (Join-Path $out 'ui\browser_screenshot.ERROR.txt') }
  try {
    & $browser --headless=new --disable-gpu --virtual-time-budget=15000 --dump-dom "$BaseUrl/ui" 2>&1 | Out-String | Set-Content (Join-Path $out 'ui\UI_rendered_DOM.html') -Encoding UTF8
  } catch { $_ | Out-String | Set-Content (Join-Path $out 'ui\browser_dom.ERROR.txt') }
} else {
  'No supported Chrome/Edge binary found for optional rendered DOM capture.' | Set-Content (Join-Path $out 'ui\browser_not_found.txt')
}

# GitHub public authority snapshot (read-only)
try {
  $ghHeaders = @{ 'User-Agent'='System3-Deep-MRI' }
  Invoke-RestMethod -Uri 'https://api.github.com/repos/psw2025-cmd/Genesis_System3/commits/main' -Headers $ghHeaders -TimeoutSec 30 |
    ConvertTo-Json -Depth 30 | Set-Content (Join-Path $out '20_GITHUB_MAIN.json') -Encoding UTF8
  Invoke-RestMethod -Uri 'https://api.github.com/repos/psw2025-cmd/Genesis_System3/issues/188' -Headers $ghHeaders -TimeoutSec 30 |
    ConvertTo-Json -Depth 30 | Set-Content (Join-Path $out '21_ISSUE_188.json') -Encoding UTF8
  Invoke-RestMethod -Uri 'https://api.github.com/repos/psw2025-cmd/Genesis_System3/commits/main/status' -Headers $ghHeaders -TimeoutSec 30 |
    ConvertTo-Json -Depth 30 | Set-Content (Join-Path $out '22_GITHUB_MAIN_STATUS.json') -Encoding UTF8
} catch { $_ | Out-String | Set-Content (Join-Path $out '20_GITHUB_PUBLIC.ERROR.txt') }

# Endpoint-level consensus summary
$consensus = $latencyRows | Group-Object endpoint | ForEach-Object {
  $g = $_.Group
  $oks = @($g | Where-Object { $_.http_status -eq 200 -and -not $_.error }).Count
  $errs = @($g | Where-Object { $_.error -or ($_.http_status -and $_.http_status -ne 200) }).Count
  $avg = [math]::Round((($g | Measure-Object elapsed_ms -Average).Average),2)
  [pscustomobject]@{endpoint=$_.Name; samples=$g.Count; http200=$oks; errors=$errs; success_rate=[math]::Round(($oks/[double]$g.Count),3); avg_ms=$avg}
}
$consensus | Export-Csv (Join-Path $out '30_ENDPOINT_CONSENSUS.csv') -NoTypeInformation

# Final manifest excludes itself to avoid file-lock race
$manifestPath = Join-Path $out '99_MANIFEST.csv'
$manifestRows = Get-ChildItem $out -Recurse -File | Where-Object { $_.FullName -ne $manifestPath } | ForEach-Object {
  $h = Get-FileHash $_.FullName -Algorithm SHA256
  [pscustomobject]@{RelativePath=$_.FullName.Substring($out.Length+1);Bytes=$_.Length;SHA256=$h.Hash}
}
$manifestRows | Export-Csv $manifestPath -NoTypeInformation

$zip = "$out.zip"
Compress-Archive -Path (Join-Path $out '*') -DestinationPath $zip -Force
"ZIP: $zip" | Add-Content $summary
Write-Host ''
Write-Host 'SYSTEM3 DEEP MRI COMPLETE' -ForegroundColor Green
Write-Host "UPLOAD THIS ZIP: $zip" -ForegroundColor Green
