@echo off
REM ======================================================================
REM SYSTEM3 PHASES 131-200 - VALIDATION TEST SCRIPT
REM ======================================================================
REM This script runs all phases 131-200 for validation
REM Date: 2025-11-30

setlocal enabledelayedexpansion

set "PYTHON=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] venv Python not found at %PYTHON%
    echo Please create/repair the virtual environment first.
    pause
    exit /b 1
)

set "PATH=%~dp0venv\Scripts;%PATH%"

echo ======================================================================
echo SYSTEM3 PHASES 131-200 - VALIDATION TEST SCRIPT
echo ======================================================================
echo.

REM Activate virtual environment
call c:\Genesis_System3\venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo ======================================================================
echo PHASE GROUP 131-135: Master Session Bootstrap
echo ======================================================================
echo.

echo [TEST] Phase 131 - Master Session Config...
python -m core.engine.system3_phase131_master_session_config
if errorlevel 1 echo [FAILED] Phase 131
echo.

echo [TEST] Phase 132 - Master Session Health Snapshot...
python -m core.engine.system3_phase132_master_health_snapshot
if errorlevel 1 echo [FAILED] Phase 132
echo.

echo [TEST] Phase 133 - Master Safety ^& Kill-Switch...
python -m core.engine.system3_phase133_master_safety_guard
if errorlevel 1 echo [FAILED] Phase 133
echo.

echo [TEST] Phase 134 - Master DRY-RUN Session Plan...
python -m core.engine.system3_phase134_master_session_plan
if errorlevel 1 echo [FAILED] Phase 134
echo.

echo [TEST] Phase 135 - Master Session Human Summary...
python -m core.engine.system3_phase135_master_session_summary
if errorlevel 1 echo [FAILED] Phase 135
echo.

echo ======================================================================
echo PHASE GROUP 136-140: Angel Symbols, Expiry, Strikes
echo ======================================================================
echo.

echo [TEST] Phase 136 - Angel Symbol Universe...
python -m core.engine.system3_phase136_angel_symbol_universe
if errorlevel 1 echo [FAILED] Phase 136
echo.

echo [TEST] Phase 137 - Expiry ^& Calendar Map...
python -m core.engine.system3_phase137_expiry_calendar_map
if errorlevel 1 echo [FAILED] Phase 137
echo.

echo [TEST] Phase 138 - Angel Risk Tier Assignment...
python -m core.engine.system3_phase138_risk_tier_assignment
if errorlevel 1 echo [FAILED] Phase 138
echo.

echo [TEST] Phase 139 - Lot Size ^& Margin Estimation...
python -m core.engine.system3_phase139_lot_margin_estimator
if errorlevel 1 echo [FAILED] Phase 139
echo.

echo [TEST] Phase 140 - Capital Guard ^& One-Lot Guardrail...
python -m core.engine.system3_phase140_capital_guardrail
if errorlevel 1 echo [FAILED] Phase 140
echo.

echo ======================================================================
echo PHASE GROUP 141-145: Fill Quality, Slippage, Spread Metrics
echo ======================================================================
echo.

echo [TEST] Phase 141 - Spread ^& Liquidity Estimation...
python -m core.engine.system3_phase141_spread_liquidity_estimator
if errorlevel 1 echo [FAILED] Phase 141
echo.

echo [TEST] Phase 142 - DRY-RUN Slippage Calculator...
python -m core.engine.system3_phase142_slippage_calculator
if errorlevel 1 echo [FAILED] Phase 142
echo.

echo [TEST] Phase 143 - Execution Quality ^& Fill Heatmap...
python -m core.engine.system3_phase143_execution_quality
if errorlevel 1 echo [FAILED] Phase 143
echo.

echo [TEST] Phase 144 - DRY-RUN PnL vs Execution Scenario...
python -m core.engine.system3_phase144_pnl_vs_execution_scenario
if errorlevel 1 echo [FAILED] Phase 144
echo.

echo [TEST] Phase 145 - One-Lot Test-Mode Health Report...
python -m core.engine.system3_phase145_one_lot_health_report
if errorlevel 1 echo [FAILED] Phase 145
echo.

echo ======================================================================
echo PHASE GROUP 146-155: Reserved Meta ^& Extension Layer
echo ======================================================================
echo.

echo [TEST] Phase 146 - Phase Index Catalog...
python -m core.engine.system3_phase146_index_catalog
if errorlevel 1 echo [FAILED] Phase 146
echo.

echo [TEST] Phase 147 - Config Inventory...
python -m core.engine.system3_phase147_config_inventory
if errorlevel 1 echo [FAILED] Phase 147
echo.

echo [TEST] Phase 148 - Storage Inventory...
python -m core.engine.system3_phase148_storage_inventory
if errorlevel 1 echo [FAILED] Phase 148
echo.

echo [TEST] Phase 149 - Log Inventory...
python -m core.engine.system3_phase149_log_inventory
if errorlevel 1 echo [FAILED] Phase 149
echo.

echo [TEST] Phase 150 - Phase Dependency Graph...
python -m core.engine.system3_phase150_dependency_graph
if errorlevel 1 echo [FAILED] Phase 150
echo.

echo [TEST] Phase 151 - Reserved Stub...
python -m core.engine.system3_phase151_reserved_stub
if errorlevel 1 echo [FAILED] Phase 151
echo.

echo [TEST] Phase 152 - Reserved Stub...
python -m core.engine.system3_phase152_reserved_stub
if errorlevel 1 echo [FAILED] Phase 152
echo.

echo [TEST] Phase 153 - Reserved Stub...
python -m core.engine.system3_phase153_reserved_stub
if errorlevel 1 echo [FAILED] Phase 153
echo.

echo [TEST] Phase 154 - Reserved Stub...
python -m core.engine.system3_phase154_reserved_stub
if errorlevel 1 echo [FAILED] Phase 154
echo.

echo [TEST] Phase 155 - Reserved Stub...
python -m core.engine.system3_phase155_reserved_stub
if errorlevel 1 echo [FAILED] Phase 155
echo.

echo ======================================================================
echo PHASE GROUP 156-170: Capital, Risk, Stability Logic
echo ======================================================================
echo.

echo [TEST] Phase 156 - Capital Curve ^& Drawdown Analysis...
python -m core.engine.system3_phase156_capital_curve_analysis
if errorlevel 1 echo [FAILED] Phase 156
echo.

echo [TEST] Phase 157 - Misfire Breakdown...
python -m core.engine.system3_phase157_misfire_breakdown
if errorlevel 1 echo [FAILED] Phase 157
echo.

echo [TEST] Phase 158 - Regime Stability...
python -m core.engine.system3_phase158_regime_stability
if errorlevel 1 echo [FAILED] Phase 158
echo.

echo [TEST] Phase 159 - Threshold Drift...
python -m core.engine.system3_phase159_threshold_drift
if errorlevel 1 echo [FAILED] Phase 159
echo.

echo [TEST] Phase 160 - Error Attribution...
python -m core.engine.system3_phase160_error_attribution
if errorlevel 1 echo [FAILED] Phase 160
echo.

echo [TEST] Phase 161 - Risk Attribution...
python -m core.engine.system3_phase161_risk_attribution
if errorlevel 1 echo [FAILED] Phase 161
echo.

echo [TEST] Phase 162 - Capital Efficiency...
python -m core.engine.system3_phase162_capital_efficiency
if errorlevel 1 echo [FAILED] Phase 162
echo.

echo [TEST] Phase 163 - Trade Frequency...
python -m core.engine.system3_phase163_trade_frequency
if errorlevel 1 echo [FAILED] Phase 163
echo.

echo [TEST] Phase 164 - Win Rate...
python -m core.engine.system3_phase164_win_rate
if errorlevel 1 echo [FAILED] Phase 164
echo.

echo [TEST] Phase 165 - Risk-Reward...
python -m core.engine.system3_phase165_risk_reward
if errorlevel 1 echo [FAILED] Phase 165
echo.

echo [TEST] Phase 166 - Underlying Performance...
python -m core.engine.system3_phase166_underlying_performance
if errorlevel 1 echo [FAILED] Phase 166
echo.

echo [TEST] Phase 167 - Time-of-Day...
python -m core.engine.system3_phase167_time_of_day
if errorlevel 1 echo [FAILED] Phase 167
echo.

echo [TEST] Phase 168 - Volatility Impact...
python -m core.engine.system3_phase168_volatility_impact
if errorlevel 1 echo [FAILED] Phase 168
echo.

echo [TEST] Phase 169 - Confidence Calibration...
python -m core.engine.system3_phase169_confidence_calibration
if errorlevel 1 echo [FAILED] Phase 169
echo.

echo [TEST] Phase 170 - Stability Metrics...
python -m core.engine.system3_phase170_stability_metrics
if errorlevel 1 echo [FAILED] Phase 170
echo.

echo ======================================================================
echo PHASE GROUP 171-195: Resilience, Backup, Holiday, Summaries
echo ======================================================================
echo.

echo [TEST] Phase 171 - File Backup...
python -m core.engine.system3_phase171_file_backup
if errorlevel 1 echo [FAILED] Phase 171
echo.

echo [TEST] Phase 172 - Schema Guard...
python -m core.engine.system3_phase172_schema_guard
if errorlevel 1 echo [FAILED] Phase 172
echo.

echo [TEST] Phase 173 - Holiday Detection...
python -m core.engine.system3_phase173_holiday_detection
if errorlevel 1 echo [FAILED] Phase 173
echo.

echo [TEST] Phase 174 - Retention Policy...
python -m core.engine.system3_phase174_retention_policy
if errorlevel 1 echo [FAILED] Phase 174
echo.

echo [TEST] Phase 175 - Exception Catalog...
python -m core.engine.system3_phase175_exception_catalog
if errorlevel 1 echo [FAILED] Phase 175
echo.

echo [TEST] Phase 176 - Long-Run Summary...
python -m core.engine.system3_phase176_long_run_summary
if errorlevel 1 echo [FAILED] Phase 176
echo.

echo [TEST] Phase 177 - Performance Trends...
python -m core.engine.system3_phase177_performance_trends
if errorlevel 1 echo [FAILED] Phase 177
echo.

echo [TEST] Phase 178 - System Health Dashboard...
python -m core.engine.system3_phase178_system_health_dashboard
if errorlevel 1 echo [FAILED] Phase 178
echo.

echo [TEST] Phase 179 - Resource Usage Summary...
python -m core.engine.system3_phase179_resource_usage_summary
if errorlevel 1 echo [FAILED] Phase 179
echo.

echo [TEST] Phase 180 - Error Rate Analysis...
python -m core.engine.system3_phase180_error_rate_analysis
if errorlevel 1 echo [FAILED] Phase 180
echo.

echo [TEST] Phase 181 - Config Drift Detection...
python -m core.engine.system3_phase181_config_drift_detection
if errorlevel 1 echo [FAILED] Phase 181
echo.

echo [TEST] Phase 182 - Data Quality Report...
python -m core.engine.system3_phase182_data_quality_report
if errorlevel 1 echo [FAILED] Phase 182
echo.

echo [TEST] Phase 183 - Model Performance Tracking...
python -m core.engine.system3_phase183_model_performance_tracking
if errorlevel 1 echo [FAILED] Phase 183
echo.

echo [TEST] Phase 184 - Signal Quality Metrics...
python -m core.engine.system3_phase184_signal_quality_metrics
if errorlevel 1 echo [FAILED] Phase 184
echo.

echo [TEST] Phase 185 - Trade Execution Summary...
python -m core.engine.system3_phase185_trade_execution_summary
if errorlevel 1 echo [FAILED] Phase 185
echo.

echo [TEST] Phase 186 - Risk Metrics Summary...
python -m core.engine.system3_phase186_risk_metrics_summary
if errorlevel 1 echo [FAILED] Phase 186
echo.

echo [TEST] Phase 187 - Capital Utilization Report...
python -m core.engine.system3_phase187_capital_utilization_report
if errorlevel 1 echo [FAILED] Phase 187
echo.

echo [TEST] Phase 188 - Underlying Performance Trends...
python -m core.engine.system3_phase188_underlying_performance_trends
if errorlevel 1 echo [FAILED] Phase 188
echo.

echo [TEST] Phase 189 - Time Series Analysis...
python -m core.engine.system3_phase189_time_series_analysis
if errorlevel 1 echo [FAILED] Phase 189
echo.

echo [TEST] Phase 190 - Correlation Analysis...
python -m core.engine.system3_phase190_correlation_analysis
if errorlevel 1 echo [FAILED] Phase 190
echo.

echo [TEST] Phase 191 - Feature Importance Summary...
python -m core.engine.system3_phase191_feature_importance_summary
if errorlevel 1 echo [FAILED] Phase 191
echo.

echo [TEST] Phase 192 - Model Comparison Report...
python -m core.engine.system3_phase192_model_comparison_report
if errorlevel 1 echo [FAILED] Phase 192
echo.

echo [TEST] Phase 193 - System Status Dashboard...
python -m core.engine.system3_phase193_system_status_dashboard
if errorlevel 1 echo [FAILED] Phase 193
echo.

echo [TEST] Phase 194 - Operational Metrics...
python -m core.engine.system3_phase194_operational_metrics
if errorlevel 1 echo [FAILED] Phase 194
echo.

echo [TEST] Phase 195 - Master Summary Report...
python -m core.engine.system3_phase195_master_summary_report
if errorlevel 1 echo [FAILED] Phase 195
echo.

echo ======================================================================
echo PHASE GROUP 196-200: Final Readiness ^& Human Gate
echo ======================================================================
echo.

echo [TEST] Phase 196 - DRY-RUN Readiness Checklist...
python -m core.engine.system3_phase196_dry_run_readiness
if errorlevel 1 echo [FAILED] Phase 196
echo.

echo [TEST] Phase 197 - Micro Capital Test Plan...
python -m core.engine.system3_phase197_micro_capital_test_plan
if errorlevel 1 echo [FAILED] Phase 197
echo.

echo [TEST] Phase 198 - Human Gate Checklist...
python -m core.engine.system3_phase198_human_gate_checklist
if errorlevel 1 echo [FAILED] Phase 198
echo.

echo [TEST] Phase 199 - Live Mode Guard Stub...
python -m core.engine.system3_phase199_live_mode_guard_stub
if errorlevel 1 echo [FAILED] Phase 199
echo.

echo [TEST] Phase 200 - Master Status Snapshot...
python -m core.engine.system3_phase200_master_status_snapshot
if errorlevel 1 echo [FAILED] Phase 200
echo.

echo ======================================================================
echo VALIDATION TEST COMPLETE
echo ======================================================================
echo.
echo Check the output above for any [FAILED] phases.
echo All test outputs are saved to storage/ultra/ and storage/config/ directories.
echo.
pause

