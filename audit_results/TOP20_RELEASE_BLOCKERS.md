# TOP 20 RELEASE BLOCKERS

> **Evidence scope:** tracked files in clean GitHub-main snapshot `8c2b4019c67b3a01dc64fbbee979c74d31044e9d`, observed 2026-11-13T22:16:41.190395+00:00. Static findings are not runtime proof. No trades, cloud writes, or deployments performed.

Priorities are audit triage, not measured failure probabilities. Recorded cloud observations require fresh independent verification.

## 1. P0: Integrated PAPER lifecycle not proven
Remediation: Require durable ledger/position/exit/PnL reconciliation and replay receipts.

Static anchors:
- `.github/agents/genesis-recovery-controller.agent.md:26` — source location only; review content in repository
- `.github/workflows/ci.yml:383` — source location only; review content in repository
- `.github/workflows/ci.yml:413` — source location only; review content in repository

## 2. P0: Failed Cloud Run candidate startup
Remediation: Investigate recorded uvicorn NameError against actual build SHA and entrypoint.

Static anchors:
- `.vscode/tasks.json:34` — source location only; review content in repository
- `CHANGE_LOG.md:769` — source location only; review content in repository
- `CHANGE_LOG.md:1102` — source location only; review content in repository

## 3. P0: Deployed source/image lineage unresolved
Remediation: Derive immutable receipt from serving Cloud Run revision and source SHA.

Static anchors:
- `.github/agents/genesis-recovery-controller.agent.md:31` — source location only; review content in repository
- `SYSTEM3/01_MASTER_STATE/SYSTEM3_MASTER_STATE.json:4` — source location only; review content in repository
- `SYSTEM3/10_HANDOVER/build_initial_mission_package.py:49` — source location only; review content in repository

## 4. P0: Option chain coverage not proven
Remediation: Dhan expiry/chain contract + rate-limited scanner evidence.

Static anchors:
- `CHANGE_LOG.md:120` — source location only; review content in repository
- `CHANGE_LOG.md:947` — source location only; review content in repository
- `CHANGE_LOG.md:968` — source location only; review content in repository

## 5. P0: Market data freshness and parity unverified
Remediation: Preserve exchange event timestamp and prove UI/source parity.

Static anchors:
- `.github/agents/genesis-recovery-controller.agent.md:37` — source location only; review content in repository
- `.github/workflows/ci.yml:395` — source location only; review content in repository
- `.github/workflows/ci.yml:497` — source location only; review content in repository

## 6. P0: Real broker order safety needs independent enforcement proof
Remediation: Prove actual HTTP order endpoint rejects writes.

Static anchors:
- `.github/CLAUDE_INSTRUCTIONS.md:10` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:35` — source location only; review content in repository
- `.github/workflows/ci.yml:230` — source location only; review content in repository

## 7. P0: ML out-of-sample results unverified
Remediation: Execute leakage-safe validation and costed outcomes.

Static anchors:
- `.github/workflows/ci.yml:248` — source location only; review content in repository
- `.github/workflows/ci.yml:522` — source location only; review content in repository
- `.github/workflows/ci.yml:525` — source location only; review content in repository

## 8. P0: 23 UI tab acceptance not proven
Remediation: Run browser route/semantic/screenshots against serving digest.

Static anchors:
- `.cursor/extensions.json:104` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:8` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:20` — source location only; review content in repository

## 9. P1: Secret consumer mapping incomplete
Remediation: Inventory bindings and current revisions without reading payloads.

Static anchors:
- `CHANGE_LOG.md:59` — source location only; review content in repository
- `SYSTEM_STATE.md:36` — source location only; review content in repository
- `audit/USER_RECOMMDATION_FOR _AGENT_UPDATE_RUNBOOK/FOR_INFO_FOR_IMPROMENT.txt:70` — source location only; review content in repository

## 10. P1: Cloud scheduling ownership and duplicate triggers unverified
Remediation: Inventory job execution targets/leases and rate controls.

Static anchors:
- `.github/CLAUDE_INSTRUCTIONS.md:8` — source location only; review content in repository
- `.github/scripts/root_architecture_gate.py:24` — source location only; review content in repository
- `.github/scripts/root_architecture_gate.py:163` — source location only; review content in repository

## 11. P1: Risk limits need persistent runtime proof
Remediation: Execute boundary tests for capital and stop loss.

Static anchors:
- `agent_memory/architecture_current.md:59` — source location only; review content in repository
- `agent_memory/tasks.json:1` — source location only; review content in repository
- `core/engine/dhan_alerting_system.py:8` — source location only; review content in repository

## 12. P1: Backend API route contracts need end-to-end tests
Remediation: Compare OpenAPI and frontend consumers.

Static anchors:
- `.cursor/extensions.json:109` — source location only; review content in repository
- `agent_memory/inventory.md:73` — source location only; review content in repository
- `core/brokers/dhan/instruments.py:21` — source location only; review content in repository

## 13. P1: Prediction history lineage unverified
Remediation: Verify stable IDs and point-in-time outcomes.

Static anchors:
- `dashboard/backend/app.py:9013` — source location only; review content in repository
- `dashboard/backend/ml_performance_tracking.py:147` — source location only; review content in repository
- `dashboard/backend/ml_performance_tracking.py:148` — source location only; review content in repository

## 14. P1: Writer concurrency/reconciliation unverified
Remediation: Use lease and replay tests.

Static anchors:
- `.github/agents/genesis-recovery-controller.agent.md:40` — source location only; review content in repository
- `.github/workflows/ci.yml:102` — source location only; review content in repository
- `.github/workflows/ci.yml:230` — source location only; review content in repository

## 15. P1: Restart recovery lacks certification
Remediation: Crash mid-fill and replay exactly once.

Static anchors:
- `.github/agents/genesis-recovery-controller.agent.md:2` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:3` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:8` — source location only; review content in repository

## 16. P1: Cost/fee accounting unproven
Remediation: Costed broker fees/tax/spread/slippage receipts.

Static anchors:
- `AGENT_COORDINATION_LOG.md:100` — source location only; review content in repository
- `config/live_trade_config.py:11` — source location only; review content in repository
- `core/data/historical_data_pipeline.py:4` — source location only; review content in repository

## 17. P1: Cloud observability missing acceptance proof
Remediation: Log/error/metric alert readback.

Static anchors:
- `.github/CLOUD_ACCESS.md:15` — source location only; review content in repository
- `.github/CLOUD_ACCESS.md:34` — source location only; review content in repository
- `.github/CLOUD_ACCESS.md:35` — source location only; review content in repository

## 18. P1: Database migration/data retention unverified
Remediation: Read-only schema and retention inspection.

Static anchors:
- `.github/scripts/root_architecture_gate.py:21` — source location only; review content in repository
- `CHANGE_LOG.md:133` — source location only; review content in repository
- `CHANGE_LOG.md:514` — source location only; review content in repository

## 19. P2: React hook and stale closure review requires path corroboration
Remediation: ESLint exhaustive-deps with exact source ownership.

Static anchors:
- `COMPREHENSIVE_FIX_PLAN.md:37` — source location only; review content in repository
- `DEPLOYMENT_READY_FIXES.md:49` — source location only; review content in repository
- `dashboard/frontend/src/App.tsx:1` — source location only; review content in repository

## 20. P2: Complexity and type coverage need reproducible baseline
Remediation: Static complexity/type lint and targeted tests.

Static anchors:
- `.pre-commit-config.yaml:48` — source location only; review content in repository
- `.pre-commit-config.yaml:51` — source location only; review content in repository
- `.scripts/system3_authority_inventory.py:16` — source location only; review content in repository
