# Cursor → ChatGPT handoff — W1 + 906 core

WAVE=CURSOR-W1-BROKER-RELIABILITY-PLUS-906-CORE
OWNER_AT_HANDOFF=CURSOR
NEXT_OWNER=CHATGPT
CURRENT_MAIN_BASE=6fdcb398a67c1cdf57fc231db778be2f62897018
LIVE=false
ORDERS=false
TOKEN_MUTATION=false
IAM_MUTATION=false

## Defect reproduced

Fresh production at 2026-08-18T10:02:39Z, serving SHA 06103b4ab:
- connected=false
- DHAN_REQUEST_REJECTED_906
- JWT valid (secret 269, 23.28h remaining)
- two Profile GETs both 906 (docs then SDK)

Root cause: 906 was in `_PROFILE_FALLBACK_ERRORS`, so the probe multiplied
non-auth rejections and earlier rotation-on-906 could not permanently close it.

## Fix

- Canonical Profile remains access-token-only.
- 906/rate-limit/auth never retry the SDK `dhanClientId` contract.
- Failed second contract does not overwrite the reported canonical contract.
- UI W1: session vs reliability split; 906 painted as non-auth request rejection.

## Tests

- tests/test_dhan_profile_header_reconcile.py
- tests/test_live_ui_truth_remediation_contract.py
- tests/evals/test_eval_dhan_906_no_profile_fallback.py
- tests/test_br1_dhan_auth_reliability.py
- tests/test_dhan_readonly_request_contract.py

## Unresolved

- Live 906 may still be returned by Dhan after hours; this PR stops amplification
  and false token recovery, it does not mint a new token.
- ChatGPT still owns exact-serving 22-tab URL acceptance.
- Claude forensic C1-C9 remains non-overlapping.
