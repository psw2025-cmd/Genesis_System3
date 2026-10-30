# System3 Proof Pack Closure Gate

Generated UTC: `2026-10-29T12:01:28.716545+00:00`

- Status: `PASS_WITH_MANUAL_RUNTIME_ITEMS`
- Final verdict: `PROOF_INFRASTRUCTURE_READY_MANUAL_RUNTIME_PROOF_REQUIRED`
- Live trading enabled: `False`
- Trade ready: `False`

## Closure items

| Blocker | Status | Auto-fix safe | Why |
|---|---|---:|---|
| `live_market_analyzer_paper_trade_not_proven` | `MANUAL_RUNTIME_PROOF_REQUIRED` | `False` | Requires market-day broker-connected analyzer/paper lifecycle with valid expiry, strike, order/fill/exit/PnL reconciliation. |
| `full_signal_to_exit_pnl_lifecycle_not_proven` | `MANUAL_RUNTIME_PROOF_REQUIRED` | `False` | A PASS with simulated exit or invalid contract fields is analyzer proof only, not trade-readiness proof. |
| `valid_option_contract_not_proven` | `CLOSED` | `False` | Current lifecycle output has empty expiry or strike 0; paper proof must use a real tradable option contract. |
| `lifecycle_proof_broker_not_connected` | `MANUAL_BROKER_LOGIN_REQUIRED` | `False` | Broker session/secrets must stay outside repo and CI logs. |
| `browser_screenshot_truth_not_proven_in_ci` | `PROOF_REQUIRED` | `True` | Can be closed by generating dashboard browser proof and endpoint coverage artifacts in CI/local runner. |
| `positive_costed_expectancy_not_proven` | `LAPTOP_BHAVCOPY_RUN_REQUIRED` | `False` | Requires real bhavcopy/costed backtest evidence; seed estimates do not prove edge. |

## Missing secondary artifacts

- None

## Safe next command

```powershell
cd C:\System3\Genesis_System3
$env:LIVE_TRADING_ENABLED='0'
$env:SYSTEM3_LIVE_TRADING_ALLOWED='0'
$env:ANALYZE_MODE='1'
python scripts/paper_lifecycle_proof.py --force
python scripts/system3_master_proof_orchestrator.py
python scripts/system3_proof_pack_closure_gate.py
```
