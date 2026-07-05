@echo off
setlocal
cd /d "%~dp0.."
echo [INFO] Multi-agent production coordination (proof-only, no live trading)
python tools\multi_agent_production_coordinator.py
python tools\generate_audit_reports.py
echo [DONE] reports\latest\production_grade_readiness\summary.md
endlocal
