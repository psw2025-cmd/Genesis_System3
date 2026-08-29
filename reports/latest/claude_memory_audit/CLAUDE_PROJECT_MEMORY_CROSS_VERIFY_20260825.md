# Claude.ai project memory — cross-verify (2026-08-25)

**Source ingested:** Claude project “System3” memory + scheduled jobs + file list (user paste 2026-08-25 ~15:06 IST).  
**Memory stamp in paste:** Last updated **Aug 16** (stale relative to GitHub/Cloud).  
**Authorities used for verify:** `origin/main`, live `/api/deploy_info`, `/api/broker/status`, `/api/auto_gates`, primary laptop clone.

## Live compare snapshot (same session)

| Plane | Value |
|---|---|
| Laptop toplevel | `C:/Users/ADMIN/Genesis_System3/Genesis_System3` |
| Laptop branch | `fix/p0-188-bankex-paced-cache-20260824` @ `146eb69…` |
| GitHub `origin/main` | `2c0b44a43837c1de5d05721b61329e9269d0a8a0` |
| Live serving `git_sha` | `719566d23fd9aeb783a72fcec9493557f783781f` |
| Broker | `connected=true`, `AUTH_OK`, secret `dhan-access-token` **v319** |
| Cloud Run instance (broker) | `genesis-system3-web-00590-zab` |
| Gates | **2/7** pass; `trade_ready=false`; `analyzer_ready=true` |
| `/api/auto_gates` | **200** (not timing out) |
| `/api/ml/performance` | **200** (not timing out) |
| `/api/holdings` `/api/funds` `/api/charts/NIFTY` | **404** |

## Verdict legend

- **KEEP** — durable principle; re-verify with live proof each session  
- **REFRESH** — direction still useful; numbers/SHAs/revisions must be re-fetched  
- **REJECT** — false, dangerous, or superseded; do not act on it  

See master runbook §9 for full claim matrix + ingest checklist.
