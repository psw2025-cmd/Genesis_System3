# System3 Ultra: Master Monitoring & Operations Script
# Comprehensive script for all daily monitoring and operational tasks
# 
# TO RUN:
# Option 1: Double-click system3_ultra_master_monitor.bat (recommended)
# Option 2: powershell -ExecutionPolicy Bypass -File .\system3_ultra_master_monitor.ps1

param(
    [string]$Mode = "menu"  # "menu", "daily", "full", "quick"
)

# Colors for output
function Write-Header {
    param([string]$Text)
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Text)
    Write-Host "`n--- $Text ---" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor White
}

function Write-Warn {
    param([string]$Text)
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

# Check and activate virtual environment
function Ensure-Venv {
    if (-not $env:VIRTUAL_ENV) {
        Write-Warn "Virtual environment not activated. Activating..."
        if (Test-Path "C:\Genesis_System3\venv\Scripts\Activate.ps1") {
            & "C:\Genesis_System3\venv\Scripts\Activate.ps1"
            Write-Success "Virtual environment activated"
        } else {
            Write-Error "Virtual environment not found at C:\Genesis_System3\venv"
            Write-Info "Please activate venv manually: venv\Scripts\activate"
            return $false
        }
    }
    return $true
}

# 1. Daily Quick Check (2-3 minutes)
function Run-DailyQuickCheck {
    Write-Header "SYSTEM3 ULTRA: DAILY QUICK CHECK"
    
    if (-not (Ensure-Venv)) { return }
    
    Write-Section "1. Policy & Risk Monitor"
    python -m core.engine.system3_phase37_policy_risk_monitor
    Write-Host ""
    
    Write-Section "2. Governance Summary"
    python -m core.engine.system3_phase38_governance_summary
    Write-Host ""
    
    Write-Section "3. Shadow Trades Check"
    $shadowFile = "storage\live\angel_index_ai_ultra_trades_shadow.csv"
    if (Test-Path $shadowFile) {
        $shadowCount = (Get-Content $shadowFile | Measure-Object -Line).Lines - 1
        if ($shadowCount -gt 0) {
            Write-Success "Shadow trades found: $shadowCount"
            Write-Info "Review: type $shadowFile | Select-Object -First 10"
        } else {
            Write-Info "No shadow trades yet (expected with conservative signals)"
        }
    } else {
        Write-Info "Shadow trades file not created yet"
    }
    
    Write-Header "DAILY QUICK CHECK COMPLETE"
    Write-Info "Review outputs in storage\ultra\"
}

# 2. Full Daily Check (10-15 minutes)
function Run-FullDailyCheck {
    Write-Header "SYSTEM3 ULTRA: FULL DAILY CHECK"
    
    if (-not (Ensure-Venv)) { return }
    
    Write-Section "1. Ultra Decision Fusion (Phase 31)"
    python -m core.engine.system3_phase31_ultra_fusion
    Write-Host ""
    
    Write-Section "2. Ultra vs Baseline Comparator (Phase 32)"
    python -m core.engine.system3_phase32_ultra_vs_baseline
    Write-Host ""
    
    Write-Section "3. Decision Auditor (Phase 35)"
    python -m core.engine.system3_phase35_ultra_auditor
    Write-Host ""
    
    Write-Section "4. Promotion Planner (Phase 33)"
    python -m core.engine.system3_phase33_promotion_planner
    Write-Host ""
    
    Write-Section "5. Policy & Risk Monitor (Phase 37)"
    python -m core.engine.system3_phase37_policy_risk_monitor
    Write-Host ""
    
    Write-Section "6. Governance Summary (Phase 38)"
    python -m core.engine.system3_phase38_governance_summary
    Write-Host ""
    
    Write-Section "7. Shadow Trades Check"
    $shadowFile = "storage\live\angel_index_ai_ultra_trades_shadow.csv"
    if (Test-Path $shadowFile) {
        $shadowCount = (Get-Content $shadowFile | Measure-Object -Line).Lines - 1
        if ($shadowCount -gt 0) {
            Write-Success "Shadow trades found: $shadowCount"
        } else {
            Write-Info "No shadow trades yet"
        }
    } else {
        Write-Info "Shadow trades file not created yet"
    }
    
    Write-Header "FULL DAILY CHECK COMPLETE"
    Write-Info "All reports saved to storage\ultra\"
}

# 3. Check Latest Decisions
function Check-LatestDecisions {
    Write-Header "CHECKING LATEST DECISIONS"
    
    if (-not (Ensure-Venv)) { return }
    
    Write-Section "Running Phase 31: Ultra Decision Fusion"
    python -m core.engine.system3_phase31_ultra_fusion
    Write-Host ""
    
    Write-Section "Decision Summary"
    $decisionsFile = "storage\ultra\phase31_ultra_fused_decisions.csv"
    if (Test-Path $decisionsFile) {
        $decisions = Import-Csv $decisionsFile
        $total = $decisions.Count
        $hold = ($decisions | Where-Object { $_.final_action -eq "HOLD" }).Count
        $buy = ($decisions | Where-Object { $_.final_action -like "BUY*" }).Count
        $safe = ($decisions | Where-Object { $_.final_risk_flag -eq "SAFE" }).Count
        $risky = ($decisions | Where-Object { $_.final_risk_flag -eq "RISKY" }).Count
        
        Write-Info "Total decisions: $total"
        Write-Info "HOLD: $hold"
        Write-Info "BUY signals: $buy"
        Write-Info "SAFE risk: $safe"
        Write-Info "RISKY risk: $risky"
        
        if ($buy -gt 0) {
            Write-Success "BUY signals detected! Review: type $decisionsFile | Where-Object {`$_.final_action -like 'BUY*'} | Select-Object -First 10"
        } else {
            Write-Info "No BUY signals yet (expected with conservative thresholds)"
        }
    }
}

# 4. Check Shadow Trades
function Check-ShadowTrades {
    Write-Header "CHECKING SHADOW TRADES"
    
    $shadowFile = "storage\live\angel_index_ai_ultra_trades_shadow.csv"
    
    if (Test-Path $shadowFile) {
        $shadowCount = (Get-Content $shadowFile | Measure-Object -Line).Lines - 1
        if ($shadowCount -gt 0) {
            Write-Success "Shadow trades found: $shadowCount"
            Write-Host ""
            Write-Section "Recent Shadow Trades (Last 10)"
            Get-Content $shadowFile | Select-Object -First 11
        } else {
            Write-Info "No shadow trades yet (file exists but empty)"
            Write-Info "Shadow trades will appear when BUY signals have SAFE risk flag"
        }
    } else {
        Write-Info "Shadow trades file not created yet"
        Write-Info "Run Phase 34 to generate shadow trades"
    }
}

# 5. Check Promotion Status
function Check-PromotionStatus {
    Write-Header "CHECKING PROMOTION STATUS"
    
    if (-not (Ensure-Venv)) { return }
    
    Write-Section "Running Phase 33: Promotion Planner"
    python -m core.engine.system3_phase33_promotion_planner
    Write-Host ""
    
    Write-Section "Promotion Plan Summary"
    $planFile = "storage\ultra\phase33_promotion_plan.md"
    if (Test-Path $planFile) {
        Write-Info "Review full plan: type $planFile"
        Write-Host ""
        Get-Content $planFile | Select-Object -First 30
    }
    
    $jsonFile = "storage\ultra\phase33_promotion_plan.json"
    if (Test-Path $jsonFile) {
        $plan = Get-Content $jsonFile | ConvertFrom-Json
        $eligible = ($plan.PSObject.Properties | Where-Object { $_.Value.eligible -eq $true }).Count
        Write-Host ""
        Write-Info "Eligible for promotion: $eligible/5 underlyings"
    }
}

# 6. Compare Performance
function Compare-Performance {
    Write-Header "COMPARING ULTRA VS BASELINE PERFORMANCE"
    
    if (-not (Ensure-Venv)) { return }
    
    Write-Section "Running Phase 32: Ultra vs Baseline Comparator"
    python -m core.engine.system3_phase32_ultra_vs_baseline
    Write-Host ""
    
    Write-Section "Comparison Summary"
    $summaryFile = "storage\ultra\phase32_ultra_vs_baseline_summary.md"
    if (Test-Path $summaryFile) {
        Write-Info "Review full comparison: type $summaryFile"
        Write-Host ""
        Get-Content $summaryFile | Select-Object -First 40
    }
}

# 7. System Health Check
function Run-SystemHealthCheck {
    Write-Header "SYSTEM HEALTH CHECK"
    
    if (-not (Ensure-Venv)) { return }
    
    Write-Section "1. Decision Auditor"
    python -m core.engine.system3_phase35_ultra_auditor
    Write-Host ""
    
    Write-Section "2. Policy & Risk Monitor"
    python -m core.engine.system3_phase37_policy_risk_monitor
    Write-Host ""
    
    Write-Section "3. Governance Summary"
    python -m core.engine.system3_phase38_governance_summary
    Write-Host ""
    
    Write-Section "4. File System Check"
    $requiredFiles = @(
        "storage\ultra\phase31_ultra_fused_decisions.csv",
        "storage\ultra\phase35_decision_audit_report.md",
        "storage\ultra\phase37_policy_risk_dashboard.md",
        "storage\ultra\phase38_governance_summary.md"
    )
    
    $allExist = $true
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "$file exists"
        } else {
            Write-Error "$file missing"
            $allExist = $false
        }
    }
    
    if ($allExist) {
        Write-Success "All required files present"
    }
}

# 8. Show Menu
function Show-Menu {
    Write-Header "SYSTEM3 ULTRA: MASTER MONITORING & OPERATIONS"
    Write-Host "Select an option:" -ForegroundColor White
    Write-Host ""
    Write-Host "1) Daily Quick Check (2-3 min) - Recommended for daily use" -ForegroundColor Cyan
    Write-Host "2) Full Daily Check (10-15 min) - Complete after-market review" -ForegroundColor Cyan
    Write-Host "3) Check Latest Decisions (Phase 31)" -ForegroundColor Yellow
    Write-Host "4) Check Shadow Trades" -ForegroundColor Yellow
    Write-Host "5) Check Promotion Status (Phase 33)" -ForegroundColor Yellow
    Write-Host "6) Compare Performance (Phase 32)" -ForegroundColor Yellow
    Write-Host "7) System Health Check" -ForegroundColor Green
    Write-Host "8) Run All Phases (31-38)" -ForegroundColor Magenta
    Write-Host "9) Exit" -ForegroundColor Red
    Write-Host ""
}

# 9. Run All Phases
function Run-AllPhases {
    Write-Header "RUNNING ALL ULTRA PHASES (31-38)"
    
    if (-not (Ensure-Venv)) { return }
    
    $phases = @(
        @{Num=31; Module="system3_phase31_ultra_fusion"; Name="Ultra Decision Fusion"},
        @{Num=32; Module="system3_phase32_ultra_vs_baseline"; Name="Ultra vs Baseline Comparator"},
        @{Num=33; Module="system3_phase33_promotion_planner"; Name="Ultra Promotion Planner"},
        @{Num=34; Module="system3_phase34_ultra_shadow_exec"; Name="Ultra Live Shadow Comparison"},
        @{Num=35; Module="system3_phase35_ultra_auditor"; Name="Ultra Decision Auditor"},
        @{Num=36; Module="system3_phase36_cull_orchestrator"; Name="Ultra Continuous Learning Cycle (CULL)"},
        @{Num=37; Module="system3_phase37_policy_risk_monitor"; Name="Ultra Policy & Risk Monitor"},
        @{Num=38; Module="system3_phase38_governance_summary"; Name="Ultra Governance Summary"}
    )
    
    foreach ($phase in $phases) {
        Write-Section "Phase $($phase.Num): $($phase.Name)"
        python -m core.engine.$($phase.Module)
        Write-Host ""
    }
    
    Write-Header "ALL PHASES COMPLETE"
}

# Main execution
function Main {
    switch ($Mode.ToLower()) {
        "daily" {
            Run-DailyQuickCheck
        }
        "full" {
            Run-FullDailyCheck
        }
        "quick" {
            Run-DailyQuickCheck
        }
        "menu" {
            do {
                Show-Menu
                $choice = Read-Host "Enter your choice (1-9)"
                Write-Host ""
                
                switch ($choice) {
                    "1" { Run-DailyQuickCheck; Read-Host "`nPress Enter to continue..." }
                    "2" { Run-FullDailyCheck; Read-Host "`nPress Enter to continue..." }
                    "3" { Check-LatestDecisions; Read-Host "`nPress Enter to continue..." }
                    "4" { Check-ShadowTrades; Read-Host "`nPress Enter to continue..." }
                    "5" { Check-PromotionStatus; Read-Host "`nPress Enter to continue..." }
                    "6" { Compare-Performance; Read-Host "`nPress Enter to continue..." }
                    "7" { Run-SystemHealthCheck; Read-Host "`nPress Enter to continue..." }
                    "8" { Run-AllPhases; Read-Host "`nPress Enter to continue..." }
                    "9" { 
                        Write-Info "Exiting..."
                        break
                    }
                    default {
                        Write-Warn "Invalid choice. Please select 1-9."
                        Start-Sleep -Seconds 1
                    }
                }
            } while ($choice -ne "9")
        }
        default {
            Write-Error "Invalid mode: $Mode"
            Write-Info "Valid modes: menu, daily, full, quick"
        }
    }
}

# Run main function
Main

