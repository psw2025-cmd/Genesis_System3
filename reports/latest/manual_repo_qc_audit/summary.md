# Manual Repo QC Audit Summary

Updated UTC: `2026-06-23T20:16:38.053448Z`

## Audit results (automated run)

- Dhan schema audit: **PASS**
- Dashboard browser proof: **PASS_WITH_WARNINGS**
- Trader requirements audit: **NOT_PROVEN**
- Real market data proof: **PASS_WITH_WARNINGS**
- Truth bridge: **PASS**
- Production viability: **NOT_PROVEN**

## Remaining blockers
- prediction_vs_market_not_proven
- TRADE_READY_FALSE
- trade_history_fields_not_exposed
- portfolio_detail_fields_missing
- nse_comparison_proof_missing
- real_market_analyzer_paper_lifecycle_not_proven
- REAL_PAPER_LIFECYCLE_NOT_PROVEN

## Next exact action
1. Run market-session analyzer paper lifecycle proof with broker connected.
2. Re-run dashboard browser proof during market hours for option-chain fields.
3. Add trade history and portfolio detail API exposure for trader audit PASS.