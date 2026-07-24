# System3 Render Worker Preflight

Generated UTC: `2026-07-24T12:46:59.708175Z`
Status: **BLOCKED**
Backend base: `http://127.0.0.1:8000`

## Blockers

- [ ] backend /api/health not reachable: status=0 error=URLError
- [ ] backend /api/state not reachable: status=0 error=URLError
- [ ] DHAN_CLIENT_ID missing in worker env
- [ ] DHAN_ACCESS_TOKEN missing/too short in worker env
- [ ] WORKER_PUSH_TOKEN missing/too short in worker env

## Safe env presence checks

| Name | Present | Length OK | Length |
|---|---:|---:|---:|
| `DHAN_CLIENT_ID` | False | False | 0 |
| `DHAN_ACCESS_TOKEN` | False | False | 0 |
| `DHAN_PIN` | False | False | 0 |
| `DHAN_TOTP_SECRET` | False | False | 0 |
| `WEB_SERVICE_URL` | True | True | 21 |
| `SYSTEM3_API_BASE` | True | True | 21 |
| `WORKER_PUSH_TOKEN` | False | False | 0 |

## Safety

- Live trading enabled: `false`
- Order routes called: `false`
- Secrets printed: `false`
