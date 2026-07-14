# Cloud Runtime Check

- Generated UTC: `2026-07-14T04:00:28.029861Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `a2f76348b16aed929ea5ce2f4cceff65aaaabc0c`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`361.6`, pct=`20.1`, status=`OK`
- `after_portfolio`: rss=`361.8`, pct=`20.1`, status=`OK`
- `after_chain`: rss=`361.8`, pct=`20.1`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=a2f76348b16a
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`222.3`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`186.4`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`97.0`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`417.0`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`608.4`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1070.2`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`189.8`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`8540.3`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`128.1`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`163.9`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`96.6`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`91.3`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`152.2`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
