# Dashboard Endpoint Coverage Proof

Generated UTC: 2026-06-11T04:58:52.813729+00:00

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
| `core` | `/` | `200` | `True` | `21310` |
| `core` | `/docs` | `200` | `True` | `217` |
| `core` | `/openapi.json` | `200` | `True` | `278` |
| `core` | `/api/health` | `200` | `True` | `226` |
| `core` | `/api/state` | `200` | `True` | `203` |
| `core` | `/api/status` | `200` | `True` | `378` |
| `broker` | `/api/broker/status` | `200` | `True` | `262` |
| `broker` | `/api/broker/deps` | `200` | `True` | `4619` |
| `data` | `/api/underlyings` | `200` | `True` | `212` |
| `signals` | `/api/signal/top` | `200` | `True` | `193` |
| `signals` | `/api/signals` | `200` | `True` | `385` |
| `signals` | `/api/signals/enhanced` | `200` | `True` | `216` |
| `paper` | `/api/positions` | `200` | `True` | `360` |
| `paper` | `/api/pnl` | `200` | `True` | `217` |
| `paper` | `/api/paper` | `200` | `True` | `192` |
| `paper` | `/api/orders` | `200` | `True` | `204` |
| `paper` | `/api/orders/history` | `200` | `True` | `219` |
| `paper` | `/api/trades/today` | `200` | `True` | `215` |
| `risk` | `/api/risk` | `200` | `True` | `354` |
| `risk` | `/api/risk/portfolio` | `200` | `True` | `195` |
| `ml` | `/api/ml/performance` | `200` | `True` | `205` |
| `ml` | `/api/ml/compare` | `200` | `True` | `193` |
| `ml` | `/api/model/behavior` | `200` | `True` | `212` |
| `prediction` | `/api/predict/portfolio` | `200` | `True` | `199` |
| `prediction` | `/api/predict/performance` | `200` | `True` | `202` |
| `validation` | `/api/validate/status` | `200` | `True` | `198` |
| `validation` | `/api/validation/status` | `200` | `True` | `207` |
| `learning` | `/api/learning/status` | `200` | `True` | `209` |
| `learning` | `/api/learning/insights` | `200` | `True` | `200` |
| `agent` | `/api/agent/status` | `200` | `True` | `196` |
| `agent` | `/api/agent/memory` | `200` | `True` | `344` |
| `agent` | `/api/agent/issues` | `200` | `True` | `206` |
| `agent` | `/api/agent/upgrade-plan` | `200` | `True` | `190` |
| `runner` | `/api/runner/test` | `200` | `True` | `197` |
| `runner` | `/api/runner/status` | `200` | `True` | `1463` |
| `forensic` | `/api/forensic/report` | `200` | `True` | `197` |
| `proof` | `/api/proof-pack` | `200` | `True` | `197` |
| `logs` | `/api/logs/tail?lines=40` | `200` | `True` | `199` |
| `security` | `/api/audit/secrets` | `200` | `True` | `209` |

POST/mutating endpoints are intentionally not called.
