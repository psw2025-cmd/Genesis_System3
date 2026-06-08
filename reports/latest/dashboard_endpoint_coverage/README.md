# Dashboard Endpoint Coverage Proof

Generated UTC: 2026-06-08T05:00:11.850717+00:00

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
| `core` | `/` | `200` | `True` | `21276` |
| `core` | `/docs` | `200` | `True` | `156` |
| `core` | `/openapi.json` | `200` | `True` | `270` |
| `core` | `/api/health` | `200` | `True` | `160` |
| `core` | `/api/state` | `200` | `True` | `174` |
| `core` | `/api/status` | `200` | `True` | `171` |
| `broker` | `/api/broker/status` | `200` | `True` | `193` |
| `broker` | `/api/broker/deps` | `200` | `True` | `4597` |
| `data` | `/api/underlyings` | `200` | `True` | `152` |
| `signals` | `/api/signal/top` | `200` | `True` | `158` |
| `signals` | `/api/signals` | `200` | `True` | `192` |
| `signals` | `/api/signals/enhanced` | `200` | `True` | `155` |
| `paper` | `/api/positions` | `200` | `True` | `148` |
| `paper` | `/api/pnl` | `200` | `True` | `152` |
| `paper` | `/api/paper` | `200` | `True` | `148` |
| `paper` | `/api/orders` | `200` | `True` | `208` |
| `paper` | `/api/orders/history` | `200` | `True` | `160` |
| `paper` | `/api/trades/today` | `200` | `True` | `157` |
| `risk` | `/api/risk` | `200` | `True` | `148` |
| `risk` | `/api/risk/portfolio` | `200` | `True` | `150` |
| `ml` | `/api/ml/performance` | `200` | `True` | `146` |
| `ml` | `/api/ml/compare` | `200` | `True` | `150` |
| `ml` | `/api/model/behavior` | `200` | `True` | `149` |
| `prediction` | `/api/predict/portfolio` | `200` | `True` | `155` |
| `prediction` | `/api/predict/performance` | `200` | `True` | `149` |
| `validation` | `/api/validate/status` | `200` | `True` | `145` |
| `validation` | `/api/validation/status` | `200` | `True` | `198` |
| `learning` | `/api/learning/status` | `200` | `True` | `145` |
| `learning` | `/api/learning/insights` | `200` | `True` | `166` |
| `agent` | `/api/agent/status` | `200` | `True` | `171` |
| `agent` | `/api/agent/memory` | `200` | `True` | `197` |
| `agent` | `/api/agent/issues` | `200` | `True` | `148` |
| `agent` | `/api/agent/upgrade-plan` | `200` | `True` | `151` |
| `runner` | `/api/runner/test` | `200` | `True` | `156` |
| `runner` | `/api/runner/status` | `200` | `True` | `1442` |
| `forensic` | `/api/forensic/report` | `200` | `True` | `152` |
| `proof` | `/api/proof-pack` | `200` | `True` | `200` |
| `logs` | `/api/logs/tail?lines=40` | `200` | `True` | `151` |
| `security` | `/api/audit/secrets` | `200` | `True` | `151` |

POST/mutating endpoints are intentionally not called.
