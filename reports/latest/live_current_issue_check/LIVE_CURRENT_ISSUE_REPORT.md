# System3 Live Current Issue Report

- Generated UTC: `2026-06-14T14:22:14.169331+00:00`
- Repo HEAD: `dac219c6b14254b200594c944f1567e5ba5e94e9`
- Backend URL: `https://genesis-system3-backend.onrender.com`
- Verdict: `LIVE_BLOCKED`
- Broker connected: `False`
- Broker error: `TOKEN_EXPIRED_OR_INVALID`
- State mode: `PAPER`
- State data source: `SYNTHETIC`
- Issue count: `21`

## Issues

| Severity | Area | Issue | Proof | Action |
|---|---|---|---|---|
| CRITICAL | broker | Dhan broker is not connected | connected=False error=TOKEN_EXPIRED_OR_INVALID credentials_present=True | Fix Render DHAN_ACCESS_TOKEN / DHAN_PIN / DHAN_TOTP_SECRET, then verify connected=true. |
| CRITICAL | broker | State broker is disconnected | error=TOKEN_EXPIRED_OR_INVALID | Fix Dhan token/session. |
| HIGH | backtest | Recent costed walk-forward not proven |  | Run recent walk-forward with brokerage/slippage/spread/liquidity. |
| HIGH | broker | Broker endpoint reports error | TOKEN_EXPIRED_OR_INVALID | Refresh/regenerate token and re-run proof. |
| HIGH | data | Dashboard state is not using proven real broker data | data_source=SYNTHETIC | Run broker-connected real data proof. |
| HIGH | data | Fresh broker live data is not proven | Run broker data proof only in secure runtime with Angel/Binance secrets; fallback data must remain labelled as fallback, not broker-live proof. | Run secure broker data proof in cloud with valid Dhan token. |
| HIGH | pipeline | Full trading pipeline is not trade ready | blockers=['fresh_training_not_proven', 'recent_backtest_not_proven', 'live_market_analyzer_paper_trade_not_proven', 'full_working_dashboard_not_proven'] verdict=NOT_TRADE_READY_UNTIL_BLOCKERS_PROVEN_CLEAR | Run fresh training, costed backtest, market paper trade, dashboard proof. |
| HIGH | readiness | Proof matrix trade_ready is false | verdict=ANALYZER_READY_PROOF_INCOMPLETE | Clear all proof warnings before live readiness. |
| HIGH | system_health | /api/health is not ready | status=not_ready message=BROKER_NOT_READY - Real data unavailable blockers=['Broker not connected - real data unavailable'] | Fix broker/data health before market proof. |
| MEDIUM | cloud_worker | Worker runtime logs not proven by API endpoint check | render.yaml has worker, but this command cannot read Render service logs | Capture Render worker logs showing token-daemon/watchdog/scheduler started. |
| MEDIUM | dashboard | API/DB/report reconciliation not proven |  | Run dashboard truth reconciliation. |
| MEDIUM | dashboard | Browser visual dashboard proof missing |  | Run screenshot/browser proof. |
| MEDIUM | model | Fresh training metrics not proven |  | Run dry-run model load/training proof with metrics. |
| MEDIUM | model | Model promotion not allowed |  | Do not promote models until policy passes. |
| MEDIUM | proof_gate | analyzer_paper_lifecycle_proof is PASS_WITH_WARNINGS | warnings=['full_signal_to_exit_pnl_lifecycle_not_proven'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | dashboard_truth_proof is PASS_WITH_WARNINGS | warnings=['dashboard_endpoint_coverage_report_missing', 'browser_screenshot_truth_not_proven_in_ci'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | fresh_data_automation_proof is PASS_WITH_WARNINGS | warnings=['binance_crypto_data_candidates_not_proven', 'external_yahoo_fallback_proof_missing', 'dhan_broker_secrets_not_available_to_ci_data_live_probe_skipped'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | model_training_load_proof is PASS_WITH_WARNINGS | warnings=['fresh_training_accuracy_metrics_not_proven', 'model_promotion_remains_blocked_without_policy'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | recent_backtest_walkforward_proof is PASS_WITH_WARNINGS | warnings=['recent_costed_walkforward_result_not_proven'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | repo_authority_and_duplicate_control is PASS_WITH_WARNINGS | warnings=['duplicate_basename_candidates_need_runtime_classification'] blockers=[] | Resolve or produce proof. |
| LOW | live_execution | Live order wrapper is placeholder — live trading intentionally blocked | core/broker/dhan_live_order_wrapper.py | SAFETY FEATURE: keeps live trading impossible until explicitly implemented. Do not implement until all proof gates pass. |