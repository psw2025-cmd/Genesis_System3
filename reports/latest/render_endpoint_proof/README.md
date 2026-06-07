# Render Endpoint Proof

Generated UTC: 2026-06-07T11:14:36.711311+00:00

Base URL: `https://genesis-system3-backend.onrender.com`

| Path | HTTP | OK | ms |
|---|---:|---:|---:|
| `/` | `200` | `True` | `21309` |
| `/docs` | `200` | `True` | `203` |
| `/api/health` | `200` | `True` | `158` |
| `/api/state` | `200` | `True` | `145` |
| `/api/broker/status` | `200` | `True` | `158` |

Core endpoints OK: `True`
Broker endpoint OK: `True`

Note: broker endpoint can respond OK while broker itself is disconnected; inspect JSON body preview in `endpoint_summary.json`.
