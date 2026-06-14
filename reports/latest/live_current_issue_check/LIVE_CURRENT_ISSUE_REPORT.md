# System3 Live Current Issue Report

- Generated UTC: `2026-06-14T16:23:15.425037+00:00`
- Repo HEAD: `7d23907f1b38e669a84dac16905839e433102084`
- Backend URL: `https://genesis-system3-backend.onrender.com`
- Verdict: `ANALYZER_ONLY_REVIEW`
- Broker connected: `True`
- Broker error: `None`
- State mode: `PAPER`
- State data source: `SYNTHETIC`
- Issue count: `15`

## Issues

| Severity | Area | Issue | Proof | Action |
|---|---|---|---|---|
| HIGH | data | Dashboard state is not using proven real broker data | data_source=SYNTHETIC | Run broker-connected real data proof. |
| HIGH | data | Fresh broker live data is not proven | Run broker data proof only in secure runtime with Angel/Binance secrets; fallback data must remain labelled as fallback, not broker-live proof. | Run secure broker data proof in cloud with valid Dhan token. |
| HIGH | paper_lifecycle | Signal→order→fill→exit→P&L lifecycle not proven/reconciled | mandatory_fields=['signal_id', 'symbol', 'instrument_token', 'expiry', 'strike', 'option_type', 'entry_time', 'entry_price', 'qty', 'order_id', 'fill_status', 'exit_time', 'exit_price', 'charges', 'gross_pnl', 'net_pnl', 'proof_status'] | Run market-day analyzer paper lifecycle proof. |
| HIGH | pipeline | Full trading pipeline is not trade ready | blockers=['live_market_analyzer_paper_trade_not_proven'] verdict=NOT_TRADE_READY_UNTIL_BLOCKERS_PROVEN_CLEAR | Run fresh training, costed backtest, market paper trade, dashboard proof. |
| HIGH | readiness | Proof matrix trade_ready is false | verdict=ANALYZER_READY_PROOF_INCOMPLETE | Clear all proof warnings before live readiness. |
| MEDIUM | cloud_worker | Worker runtime logs not proven by API endpoint check | render.yaml has worker, but this command cannot read Render service logs | Capture Render worker logs showing token-daemon/watchdog/scheduler started. |
| MEDIUM | dashboard | API/DB/report reconciliation not proven |  | Run dashboard truth reconciliation. |
| MEDIUM | dashboard | Browser visual dashboard proof missing |  | Run screenshot/browser proof. |
| MEDIUM | model | Model promotion not allowed |  | Do not promote models until policy passes. |
| MEDIUM | proof_gate | analyzer_paper_lifecycle_proof is PASS_WITH_WARNINGS | warnings=['full_signal_to_exit_pnl_lifecycle_not_proven', 'lifecycle_proof_broker_not_connected'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | dashboard_truth_proof is PASS_WITH_WARNINGS | warnings=['browser_screenshot_truth_not_proven_in_ci'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | fresh_data_automation_proof is PASS_WITH_WARNINGS | warnings=['dhan_broker_secrets_not_available_to_ci_data_live_probe_skipped'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | model_training_load_proof is PASS_WITH_WARNINGS | warnings=['model_promotion_remains_blocked_without_policy'] blockers=[] | Resolve or produce proof. |
| MEDIUM | proof_gate | repo_authority_and_duplicate_control is PASS_WITH_WARNINGS | warnings=['duplicate_basename_candidates_need_runtime_classification'] blockers=[] | Resolve or produce proof. |
| LOW | live_execution | Live order wrapper is placeholder — live trading intentionally blocked | core/broker/dhan_live_order_wrapper.py | SAFETY FEATURE: keeps live trading impossible until explicitly implemented. Do not implement until all proof gates pass. |