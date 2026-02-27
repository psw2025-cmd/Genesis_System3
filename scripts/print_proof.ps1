# PowerShell Proof Script - Safe output for Windows
# Usage: powershell -ExecutionPolicy Bypass -File scripts\print_proof.ps1

$ErrorActionPreference = "Continue"
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================================"
Write-Host "OPTION CHAIN AUTOMATION SYSTEM - PROOF OUTPUT"
Write-Host "================================================================================"
Write-Host ""

$outputDir = "outputs"

# 1. Check top_trade_signal.json
Write-Host "1. TOP TRADE SIGNAL (outputs/top_trade_signal.json):"
Write-Host "--------------------------------------------------------------------------------"
$signalFile = Join-Path $outputDir "top_trade_signal.json"
if (Test-Path $signalFile) {
    try {
        $signalContent = Get-Content $signalFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $signalContent | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "[ERROR] Failed to read signal file: $_"
        Get-Content $signalFile -Raw
    }
} else {
    Write-Host "[WARN] File not found: $signalFile"
}
Write-Host ""
Write-Host ""

# 2. Check qc_report_live.json
Write-Host "2. QC REPORT (outputs/qc_report_live.json):"
Write-Host "--------------------------------------------------------------------------------"
$qcFile = Join-Path $outputDir "qc_report_live.json"
if (Test-Path $qcFile) {
    try {
        $qcContent = Get-Content $qcFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $qcContent | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "[ERROR] Failed to read QC file: $_"
        Get-Content $qcFile -Raw
    }
} else {
    Write-Host "[WARN] File not found: $qcFile"
}
Write-Host ""
Write-Host ""

# 3. Check health.json
Write-Host "3. HEALTH METRICS (outputs/health.json):"
Write-Host "--------------------------------------------------------------------------------"
$healthFile = Join-Path $outputDir "health.json"
if (Test-Path $healthFile) {
    try {
        $healthContent = Get-Content $healthFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $healthContent | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "[ERROR] Failed to read health file: $_"
        Get-Content $healthFile -Raw
    }
} else {
    Write-Host "[WARN] File not found: $healthFile"
}
Write-Host ""
Write-Host ""

# 4. Check chain_raw_live.csv (first 20 lines)
Write-Host "4. CHAIN DATA (outputs/chain_raw_live.csv - First 20 lines):"
Write-Host "--------------------------------------------------------------------------------"
$chainFile = Join-Path $outputDir "chain_raw_live.csv"
if (Test-Path $chainFile) {
    try {
        $chainLines = Get-Content $chainFile -TotalCount 20 -Encoding UTF8
        $chainLines | ForEach-Object { Write-Host $_ }
        Write-Host ""
        $totalLines = (Get-Content $chainFile -Encoding UTF8).Count
        Write-Host "[INFO] Total lines in file: $totalLines"
    } catch {
        Write-Host "[ERROR] Failed to read chain file: $_"
    }
} else {
    Write-Host "[WARN] File not found: $chainFile"
}
Write-Host ""
Write-Host ""

# 5. Check underlying_rank_live.csv (first 20 lines)
Write-Host "5. UNDERLYING RANKING (outputs/underlying_rank_live.csv - First 20 lines):"
Write-Host "--------------------------------------------------------------------------------"
$rankFile = Join-Path $outputDir "underlying_rank_live.csv"
if (Test-Path $rankFile) {
    try {
        $rankLines = Get-Content $rankFile -TotalCount 20 -Encoding UTF8
        $rankLines | ForEach-Object { Write-Host $_ }
    } catch {
        Write-Host "[ERROR] Failed to read rank file: $_"
    }
} else {
    Write-Host "[WARN] File not found: $rankFile"
}
Write-Host ""
Write-Host ""

Write-Host "================================================================================"
Write-Host "PROOF OUTPUT COMPLETE"
Write-Host "================================================================================"
