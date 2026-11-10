# Cursor → ChatGPT handoff — W4 LIVE_GATE alert leak

WAVE=CURSOR-W4-LIVE-GATE-ALERT-LEAK
OWNER_AT_HANDOFF=CURSOR
NEXT_OWNER=CHATGPT
CURRENT_MAIN_BASE=9d9f53613ff5f286290bd352a3eb61ea0cb2a20c
LIVE=false
ORDERS=false
TOKEN_MUTATION=false
IAM_MUTATION=false
USER_ACTION_REQUIRED=false

## Defect reproduced

Exact-serving SHA `9d9f53613` Alerts tab: `1 ACTIVE` was the live-trading gate
join text telling the owner to set `live_trading_approved=true`. Live Readiness
already said BLOCKED BY DESIGN. `/api/alerts/recent` returned
`type=system_alert`, `id=OPS_LIVE_GATE`, `severity=info`.

## Fix

- Synth LIVE_GATE rows now have `type=LIVE_GATE` and `code=LIVE_GATE`.
- Message no longer instructs flipping `kill_switch.json`.
- Frontend `alertTruth.ts` classifies LIVE_GATE / OPS_LIVE_GATE / leaked
  kill-switch wording as live-readiness, not Active.
- `human_approved` gate detail says PAPER does not require LIVE approval.

## Tests

- tests/evals/test_eval_live_gate_alert_leak.py
- tests/test_paper_alert_truth_contract.py
- tests/test_live_ui_truth_remediation_contract.py

## Unresolved

- Remaining ChatGPT W4 items (WebSocket vs broker semantics, mobile breakpoints)
  are not in this PR.
- ChatGPT still owns exact-serving 22-tab URL acceptance after deploy.
- Do not treat this as a LIVE-enablement change. `kill_switch.json`
  `live_trading_approved` stays false.
