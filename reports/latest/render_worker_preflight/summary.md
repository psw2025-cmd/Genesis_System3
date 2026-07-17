# System3 Render Worker Preflight

Generated UTC: `2026-07-17T07:57:22.283656Z`
Status: **BLOCKED**
Backend base: `https://genesis-system3-backend.onrender.com`

## Blockers

- [ ] backend /api/health not reachable: status=502 error=HTTPError
- [ ] backend /api/state not reachable: status=502 error=HTTPError
- [ ] DHAN_CLIENT_ID missing in worker env
- [ ] DHAN_ACCESS_TOKEN missing/too short in worker env
- [ ] WORKER_PUSH_TOKEN missing/too short in worker env
- [ ] backend web service returning 502; worker push cannot succeed until backend restarts/deploys

## Safe env presence checks

| Name | Present | Length OK | Length |
|---|---:|---:|---:|
| `DHAN_CLIENT_ID` | False | False | 0 |
| `DHAN_ACCESS_TOKEN` | False | False | 0 |
| `DHAN_PIN` | False | False | 0 |
| `DHAN_TOTP_SECRET` | False | False | 0 |
| `WEB_SERVICE_URL` | True | True | 44 |
| `SYSTEM3_API_BASE` | True | True | 44 |
| `WORKER_PUSH_TOKEN` | False | False | 0 |

## Safety

- Live trading enabled: `false`
- Order routes called: `false`
- Secrets printed: `false`
