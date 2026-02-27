# Secrets Verification Script
# Scans logs and endpoints for secrets

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
Set-Location $rootDir

Write-Host "=== SECRETS VERIFICATION ===" -ForegroundColor Cyan
Write-Host ""

$foundSecrets = @()
$scanPaths = @(
    (Join-Path $rootDir "logs"),
    (Join-Path $rootDir "outputs")
)

# Patterns to check
$patterns = @(
    @{ Pattern = "Feed token obtained:\s+[A-Za-z0-9_-]+"; Name = "Feed token leak" },
    @{ Pattern = "[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"; Name = "JWT token" },
    @{ Pattern = "jwtToken.*[A-Za-z0-9_.-]{20,}"; Name = "JWT token in log" },
    @{ Pattern = "Bearer\s+[A-Za-z0-9_-]{20,}"; Name = "Bearer token" }
)

foreach ($scanPath in $scanPaths) {
    if (Test-Path $scanPath) {
        Write-Host "Scanning: $scanPath" -ForegroundColor Yellow
        $files = Get-ChildItem -Path $scanPath -Recurse -File -Include *.log,*.txt,*.json,*.jsonl -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            try {
                $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    foreach ($patternInfo in $patterns) {
                        if ($content -match $patternInfo.Pattern) {
                            $foundSecrets += "Found $($patternInfo.Name) in $($file.FullName)"
                            Write-Host "  [FAIL] $($patternInfo.Name) found in $($file.Name)" -ForegroundColor Red
                        }
                    }
                }
            } catch {
                # Skip files that can't be read
            }
        }
    }
}

# Check backend API logs endpoint
try {
    $backendUrl = "http://localhost:8000/api/logs/tail"
    $response = Invoke-WebRequest -Uri $backendUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $logs = $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($logs) {
            foreach ($logEntry in $logs) {
                $logText = $logEntry | ConvertTo-Json -Compress
                foreach ($patternInfo in $patterns) {
                    if ($logText -match $patternInfo.Pattern) {
                        $foundSecrets += "Found $($patternInfo.Name) in backend API logs"
                        Write-Host "  [FAIL] $($patternInfo.Name) found in backend API logs" -ForegroundColor Red
                    }
                }
            }
        }
    }
} catch {
    Write-Host "  [INFO] Backend API not available for scanning" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== VERIFICATION RESULT ===" -ForegroundColor Cyan
if ($foundSecrets.Count -eq 0) {
    Write-Host "SECRETS_STATUS=PASS" -ForegroundColor Green
    Write-Host "No secrets found in logs or endpoints" -ForegroundColor Green
    exit 0
} else {
    Write-Host "SECRETS_STATUS=FAIL" -ForegroundColor Red
    Write-Host "Found $($foundSecrets.Count) potential secret leaks:" -ForegroundColor Red
    foreach ($secret in $foundSecrets) {
        Write-Host "  - $secret" -ForegroundColor Red
    }
    exit 1
}
