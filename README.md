# Genesis System3

Genesis System3 is a cloud-authoritative, proof-first market-analysis and PAPER
trading system. It is not authorized for real orders.

## Authority

- Code/configuration: GitHub `psw2025-cmd/Genesis_System3` current `main`.
- Production/runtime: GCP project `system3-openalgo-safe`, region `asia-south1`.
- Cloud Run service: `genesis-system3-web`.
- Production UI: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/
- Coordination/status bus: GitHub Issue #188.
- Broker authority: Dhan. Render and Angel-era production instructions are retired.

## Agent start here

Every agent must read, in order:

1. `AGENTS.md`
2. `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md`
3. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
4. `docs/authority/USER_ACTION_AUTONOMY_SPEED_POLICY.md`
5. `docs/RUHI_RULE_V2.md`
6. Current remote `main`, active PR ownership, and latest Issue #188 status

## Owner blocker and acceleration rule

When any blocker, access gap, permission, setting, approval, subscription, or
external account action can directly or indirectly delay dashboard content,
market data, API/UI parity, predictions, PAPER records, proof, deployment, or
agent throughput, the agent must:

- continue every safe unblocked task;
- tell the owner immediately in chat;
- send the same concise action card through the verified connected mail channel;
- put the fastest safe option first and list all materially different safe
  alternatives with time, benefit, risk, and proof;
- use kid-level `WHY / WHERE / CLICK / SET / DO NOT / RESULT / PROOF / URGENCY`
  steps;
- retain a stable action ID and repeat only the unresolved delta until fresh
  evidence proves completion;
- prioritize the least-privilege access/setup action that unlocks the most
  downstream dashboard work.

The canonical contract, reminder cadence, deduplication, and safety boundaries
are in `docs/authority/USER_ACTION_AUTONOMY_SPEED_POLICY.md`.

## Local development

Local execution is for development/testing only and is never production truth.

```powershell
.\.venv\Scripts\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\streamlit.exe run dashboard\app.py --server.address 127.0.0.1 --server.port 8501
```

## Safety defaults

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- No real order placement, modification, cancellation, or square-off
- No secret/token/PIN/TOTP exposure
- No service-account JSON keys
- No gate, IAM/WIF, or proof dilution

> I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT
> CLAIMED UNTIL PAPER AND LIVE PROOF PASS.
