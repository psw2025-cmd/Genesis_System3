# SAFETY AUDIT

> **Evidence scope:** tracked files in clean GitHub-main snapshot `8c2b4019c67b3a01dc64fbbee979c74d31044e9d`, observed 2026-11-13T22:16:41.190395+00:00. Static findings are not runtime proof. No trades, cloud writes, or deployments performed.

### Kill switch
- `.github/CLAUDE_INSTRUCTIONS.md:10` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:35` — source location only; review content in repository
- `.github/workflows/ci.yml:230` — source location only; review content in repository
- `.github/workflows/ci.yml:427` — source location only; review content in repository
- `.github/workflows/cloud-verify.yml:56` — source location only; review content in repository
- `.github/workflows/cloud-verify.yml:144` — source location only; review content in repository
- `AGENTS.md:30` — source location only; review content in repository
- `CHANGE_LOG.md:8` — source location only; review content in repository
- `CHANGE_LOG.md:9` — source location only; review content in repository
- `CHANGE_LOG.md:1152` — source location only; review content in repository
- `GEMINI.md:12` — source location only; review content in repository
- `SYSTEM3/01_MASTER_STATE/SYSTEM3_MASTER_STATE.json:83` — source location only; review content in repository
### Capital protection
- `.github/workflows/ci.yml:452` — source location only; review content in repository
- `dashboard/backend/autonomous_paper_core.py:23` — source location only; review content in repository
- `dashboard/backend/autonomous_paper_core.py:205` — source location only; review content in repository
- `dashboard/backend/autonomous_paper_core.py:206` — source location only; review content in repository
- `dashboard/backend/autonomous_paper_core.py:321` — source location only; review content in repository
- `dashboard/backend/autonomous_paper_core.py:322` — source location only; review content in repository
- `dashboard/backend/paper_market_replay.py:19` — source location only; review content in repository
- `dashboard/backend/paper_market_replay.py:22` — source location only; review content in repository
- `dashboard/backend/paper_market_replay.py:46` — source location only; review content in repository
- `dashboard/backend/paper_market_replay.py:47` — source location only; review content in repository
- `dashboard/backend/paper_market_replay.py:50` — source location only; review content in repository
- `dashboard/backend/paper_market_replay.py:51` — source location only; review content in repository
### Daily stop
- `tests/test_virtual_market_lifecycle.py:100` — source location only; review content in repository
- `tests/test_virtual_market_lifecycle.py:130` — source location only; review content in repository
### Position/order limits
- `config/live_trade_config.py:29` — source location only; review content in repository
- `core/engine/system3_phase367_safety_guardrail_recommender.py:357` — source location only; review content in repository
- `core/execution/risk_guard.py:147` — source location only; review content in repository
- `core/validation/live_safety_guard.py:5` — source location only; review content in repository
- `core/validation/live_safety_guard.py:77` — source location only; review content in repository
- `core/validation/live_safety_guard.py:79` — source location only; review content in repository
- `core/validation/live_safety_guard.py:166` — source location only; review content in repository
- `core/validation/live_safety_guard.py:167` — source location only; review content in repository
- `core/validation/live_safety_guard.py:170` — source location only; review content in repository
- `core/validation/live_safety_guard.py:219` — source location only; review content in repository
- `core/validation/live_safety_guard.py:220` — source location only; review content in repository
- `core/validation/live_safety_guard.py:222` — source location only; review content in repository
### Circuit breakers
- `.github/scripts/workflow_priority_guard.py:2` — source location only; review content in repository
- `.github/workflows/ci.yml:93` — source location only; review content in repository
- `.github/workflows/ci.yml:210` — source location only; review content in repository
- `.github/workflows/ci.yml:215` — source location only; review content in repository
- `.github/workflows/ci.yml:222` — source location only; review content in repository
- `.github/workflows/ci.yml:291` — source location only; review content in repository
- `.github/workflows/ci.yml:292` — source location only; review content in repository
- `.github/workflows/ci.yml:309` — source location only; review content in repository
- `.github/workflows/ci.yml:312` — source location only; review content in repository
- `.github/workflows/ci.yml:320` — source location only; review content in repository
- `.github/workflows/ci.yml:321` — source location only; review content in repository
- `.github/workflows/ci.yml:413` — source location only; review content in repository
### Recovery
- `.github/agents/genesis-recovery-controller.agent.md:2` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:3` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:8` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:26` — source location only; review content in repository
- `.github/agents/genesis-recovery-controller.agent.md:29` — source location only; review content in repository
- `.github/workflows/frontend-runtime-smoke.yml:76` — source location only; review content in repository
- `CHANGE_LOG.md:24` — source location only; review content in repository
- `CHANGE_LOG.md:28` — source location only; review content in repository
- `CHANGE_LOG.md:35` — source location only; review content in repository
- `CHANGE_LOG.md:36` — source location only; review content in repository
- `CHANGE_LOG.md:58` — source location only; review content in repository
- `CHANGE_LOG.md:554` — source location only; review content in repository

**Safety runtime enforcement: NOT PROVEN** by static inspection; broker-order prohibition remains mandatory.
