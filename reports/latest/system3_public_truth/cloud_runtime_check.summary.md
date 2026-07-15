# Cloud Runtime Check

- Generated UTC: `2026-07-15T04:00:57.737936Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `3559642ea760b44957cb2445b4ca1a463eb80a83`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `None`

## Memory
- `before`: rss=`492.0`, pct=`27.3`, status=`OK`
- `after_portfolio`: rss=`252.1`, pct=`14.0`, status=`OK`
- `after_chain`: rss=`252.1`, pct=`14.0`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 502 HTTPError: 502 attempts=4
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=3559642ea760
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan
- **WARNING** `memory_before` — RSS high: 492.0MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`246.9`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`204.8`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`159.4`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`1498.1`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`614.6`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`981.5`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`186.6`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`502`, latency_ms=`297.9`, attempts=`4`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`184.1`, attempts=`3`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`513.8`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`177.8`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`143.0`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`272.1`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
