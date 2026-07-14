# System3 Render Worker Environment Audit

Generated UTC: `2026-07-14T12:15:01.949679Z`
Status: **BLOCKED**

## Required env presence

| Env | Present |
|---|---:|
| `DHAN_CLIENT_ID` | `False` |
| `DHAN_ACCESS_TOKEN` | `False` |
| `WORKER_PUSH_TOKEN` | `False` |
| `WEB_SERVICE_URL` | `True` |

## Interpretation

- Worker push `401` means `WORKER_PUSH_TOKEN` is missing or different between Render web and worker.
- Dhan `401` means Dhan token/client-id is invalid or the worker/backend has not reloaded after token update.
- Backend `502` means backend web service crashed, did not start, listened on wrong port, or deploy is blocked.
- This audit checks presence only and never prints secret values.
- Live trading remains OFF.
