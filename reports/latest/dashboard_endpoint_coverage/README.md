# Dashboard Endpoint Coverage Proof

Generated UTC: 2026-06-09T04:49:00.608845+00:00

Base URL: `https://genesis-system3-backend.onrender.com`

Endpoints tested: `39`
OK: `39`
Failed: `0`

## Category summary

| Category | OK | Total | Failed |
|---|---:|---:|---|
| `agent` | `4` | `4` | `-` |
| `broker` | `2` | `2` | `-` |
| `core` | `6` | `6` | `-` |
| `data` | `1` | `1` | `-` |
| `forensic` | `1` | `1` | `-` |
| `learning` | `2` | `2` | `-` |
| `logs` | `1` | `1` | `-` |
| `ml` | `3` | `3` | `-` |
| `paper` | `6` | `6` | `-` |
| `prediction` | `2` | `2` | `-` |
| `proof` | `1` | `1` | `-` |
| `risk` | `2` | `2` | `-` |
| `runner` | `2` | `2` | `-` |
| `security` | `1` | `1` | `-` |
| `signals` | `3` | `3` | `-` |
| `validation` | `2` | `2` | `-` |

## Endpoint table

| Category | Path | HTTP | OK | ms |
|---|---|---:|---:|---:|
| `core` | `/` | `200` | `True` | `21440` |
| `core` | `/docs` | `200` | `True` | `398` |
| `core` | `/openapi.json` | `200` | `True` | `273` |
| `core` | `/api/health` | `200` | `True` | `239` |
| `core` | `/api/state` | `200` | `True` | `239` |
| `core` | `/api/status` | `200` | `True` | `367` |
| `broker` | `/api/broker/status` | `200` | `True` | `237` |
| `broker` | `/api/broker/deps` | `200` | `True` | `4510` |
| `data` | `/api/underlyings` | `200` | `True` | `213` |
| `signals` | `/api/signal/top` | `200` | `True` | `242` |
| `signals` | `/api/signals` | `200` | `True` | `217` |
| `signals` | `/api/signals/enhanced` | `200` | `True` | `207` |
| `paper` | `/api/positions` | `200` | `True` | `200` |
| `paper` | `/api/pnl` | `200` | `True` | `365` |
| `paper` | `/api/paper` | `200` | `True` | `210` |
| `paper` | `/api/orders` | `200` | `True` | `215` |
| `paper` | `/api/orders/history` | `200` | `True` | `208` |
| `paper` | `/api/trades/today` | `200` | `True` | `212` |
| `risk` | `/api/risk` | `200` | `True` | `220` |
| `risk` | `/api/risk/portfolio` | `200` | `True` | `237` |
| `ml` | `/api/ml/performance` | `200` | `True` | `240` |
| `ml` | `/api/ml/compare` | `200` | `True` | `230` |
| `ml` | `/api/model/behavior` | `200` | `True` | `216` |
| `prediction` | `/api/predict/portfolio` | `200` | `True` | `236` |
| `prediction` | `/api/predict/performance` | `200` | `True` | `224` |
| `validation` | `/api/validate/status` | `200` | `True` | `215` |
| `validation` | `/api/validation/status` | `200` | `True` | `223` |
| `learning` | `/api/learning/status` | `200` | `True` | `227` |
| `learning` | `/api/learning/insights` | `200` | `True` | `216` |
| `agent` | `/api/agent/status` | `200` | `True` | `229` |
| `agent` | `/api/agent/memory` | `200` | `True` | `417` |
| `agent` | `/api/agent/issues` | `200` | `True` | `212` |
| `agent` | `/api/agent/upgrade-plan` | `200` | `True` | `211` |
| `runner` | `/api/runner/test` | `200` | `True` | `206` |
| `runner` | `/api/runner/status` | `200` | `True` | `1342` |
| `forensic` | `/api/forensic/report` | `200` | `True` | `207` |
| `proof` | `/api/proof-pack` | `200` | `True` | `208` |
| `logs` | `/api/logs/tail?lines=40` | `200` | `True` | `206` |
| `security` | `/api/audit/secrets` | `200` | `True` | `225` |

POST/mutating endpoints are intentionally not called.
