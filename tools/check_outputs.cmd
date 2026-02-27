@echo off
REM CMD-safe output checker
REM Usage: tools\check_outputs.cmd

echo === OUTPUTS CHECK ===
echo.

if exist outputs (
    echo Outputs directory exists: YES
    
    if exist outputs\health.json (
        echo   health.json : EXISTS
    ) else (
        echo   health.json : MISSING
    )
    
    if exist outputs\paper_pnl_summary.json (
        echo   paper_pnl_summary.json : EXISTS
    ) else (
        echo   paper_pnl_summary.json : MISSING
    )
    
    if exist outputs\chain_raw_live.csv (
        echo   chain_raw_live.csv : EXISTS
    ) else (
        echo   chain_raw_live.csv : MISSING
    )
    
    if exist outputs\perf_metrics.json (
        echo   perf_metrics.json : EXISTS
    ) else (
        echo   perf_metrics.json : MISSING
    )
) else (
    echo Outputs directory missing!
)
