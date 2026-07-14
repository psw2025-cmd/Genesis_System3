# Cloud Runtime Check

- Generated UTC: `2026-07-14T06:14:53.316435Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `7205705cafe44b9ef89fc6a287f2d2cc37b647b9`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`494.9`, pct=`27.5`, status=`OK`
- `after_portfolio`: rss=`494.9`, pct=`27.5`, status=`OK`
- `after_chain`: rss=`494.9`, pct=`27.5`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=7205705cafe4
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan
- **WARNING** `memory_before` — RSS high: 494.9MB
- **WARNING** `memory_after_portfolio` — RSS high: 494.9MB
- **WARNING** `memory_after_chain` — RSS high: 494.9MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`295.9`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`161.2`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`405.7`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`795.6`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`593.7`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1120.8`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`172.2`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`9509.9`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`145.9`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`585.8`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`151.8`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`167.0`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`165.6`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
