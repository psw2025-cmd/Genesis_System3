# Dashboard Endpoint Coverage Proof

Generated UTC: 2026-06-10T04:53:37.963287+00:00

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
| `core` | `/` | `200` | `True` | `21537` |
| `core` | `/docs` | `200` | `True` | `246` |
| `core` | `/openapi.json` | `200` | `True` | `258` |
| `core` | `/api/health` | `200` | `True` | `221` |
| `core` | `/api/state` | `200` | `True` | `426` |
| `core` | `/api/status` | `200` | `True` | `219` |
| `broker` | `/api/broker/status` | `200` | `True` | `241` |
| `broker` | `/api/broker/deps` | `200` | `True` | `4486` |
| `data` | `/api/underlyings` | `200` | `True` | `214` |
| `signals` | `/api/signal/top` | `200` | `True` | `236` |
| `signals` | `/api/signals` | `200` | `True` | `214` |
| `signals` | `/api/signals/enhanced` | `200` | `True` | `232` |
| `paper` | `/api/positions` | `200` | `True` | `412` |
| `paper` | `/api/pnl` | `200` | `True` | `222` |
| `paper` | `/api/paper` | `200` | `True` | `240` |
| `paper` | `/api/orders` | `200` | `True` | `229` |
| `paper` | `/api/orders/history` | `200` | `True` | `237` |
| `paper` | `/api/trades/today` | `200` | `True` | `218` |
| `risk` | `/api/risk` | `200` | `True` | `214` |
| `risk` | `/api/risk/portfolio` | `200` | `True` | `214` |
| `ml` | `/api/ml/performance` | `200` | `True` | `222` |
| `ml` | `/api/ml/compare` | `200` | `True` | `244` |
| `ml` | `/api/model/behavior` | `200` | `True` | `211` |
| `prediction` | `/api/predict/portfolio` | `200` | `True` | `225` |
| `prediction` | `/api/predict/performance` | `200` | `True` | `226` |
| `validation` | `/api/validate/status` | `200` | `True` | `209` |
| `validation` | `/api/validation/status` | `200` | `True` | `235` |
| `learning` | `/api/learning/status` | `200` | `True` | `372` |
| `learning` | `/api/learning/insights` | `200` | `True` | `224` |
| `agent` | `/api/agent/status` | `200` | `True` | `232` |
| `agent` | `/api/agent/memory` | `200` | `True` | `211` |
| `agent` | `/api/agent/issues` | `200` | `True` | `356` |
| `agent` | `/api/agent/upgrade-plan` | `200` | `True` | `241` |
| `runner` | `/api/runner/test` | `200` | `True` | `221` |
| `runner` | `/api/runner/status` | `200` | `True` | `1285` |
| `forensic` | `/api/forensic/report` | `200` | `True` | `219` |
| `proof` | `/api/proof-pack` | `200` | `True` | `237` |
| `logs` | `/api/logs/tail?lines=40` | `200` | `True` | `222` |
| `security` | `/api/audit/secrets` | `200` | `True` | `231` |

POST/mutating endpoints are intentionally not called.
