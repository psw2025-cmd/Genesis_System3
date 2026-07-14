# System3 Current Blocker Runbook

This runbook is fail-closed. It does not enable broker orders, alter credentials, or permit a production-grade claim.

## Safety invariants

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- Never print, commit, or copy API keys, access tokens, cookies, session bodies, or broker credentials into proof artifacts.
- Never mark a blocker resolved from HTTP 200 alone.
- Never claim DONE unless the current automated Render visual proof is PASS, authenticated, complete, and fresh.

## Current evidence precedence

When reports disagree, use the newest timestamped report and keep the older result as historical evidence.

1. `reports/latest/dashboard_visible_issue_tracker/summary.json` for the newest rendered 16-tab UI state.
2. `reports/latest/dashboard_visual_production_proof/summary.json` for the strict production visual gate.
3. `reports/latest/system3_public_truth/index.json` for consolidated public truth.
4. `reports/latest/github_render_failure_tracker/summary.json` for distinct current workflow and Render failures.
5. `reports/latest/todo_status_update/summary.json` for the canonical checklist parser state.

A newer visible tracker does not convert an older failed production proof into PASS. The strict production proof must be regenerated.

## Active blocker order

### P0 — Proof freshness and artifact integrity

Before every browser proof run, delete the generated source directory:

```bash
rm -rf reports/latest/dashboard_live_ui_proof
```

This prevents screenshots or endpoint files from an earlier successful run from being reused after authentication, navigation, or Render failure.

The production proof must require all of the following from the same run:

- authenticated session PASS;
- source summary generated in the current run;
- all required screenshots newly created and larger than the minimum size;
- no browser/UI exception;
- no visible red/PEND/BLOCKED issue when evaluating visual PASS;
- no infrastructure blocker;
- no required trade-readiness blocker;
- production claim flag equal to the strict visual-gate result.

### P1 — Dhan read-only session

Current UI evidence shows the broker disconnected or token/session invalid. Correct only the Render secret/runtime session; do not write the token to the repository or reports.

Proof required:

- broker status endpoint HTTP 200;
- `connected=true` for the read-only Dhan session;
- `order_allowed=false`;
- live-trading flags remain OFF;
- no credential value appears in logs or artifacts.

### P2 — Required option chains

Required symbols:

- NIFTY
- BANKNIFTY
- FINNIFTY
- MIDCPNIFTY

Each must prove current or explicitly valid Dhan snapshot rows with:

- source exactly Dhan;
- positive spot;
- positive contract count;
- expiry and security-ID provenance;
- no CSV, synthetic, mock, Yahoo, bhavcopy, or fallback source;
- stale data rejected.

`NO_DHAN_DATA` is an acceptable safe no-trade state, but it remains a readiness blocker.

### P3 — Scanner and CE/PE evidence

Do not patch the scanner to fabricate candidates. A scanner PASS requires at least one candidate produced from valid required-chain rows with visible provenance, liquidity/spread checks, expiry, strike, lot size, and CE/PE side evidence.

Zero candidates is truthful but BLOCKED for money readiness.

### P4 — Paper lifecycle

Paper endpoints returning HTTP 200 with zero rows are transport PASS only. Lifecycle proof requires analyzer-generated entry, update, exit, P&L, timestamps, source/provenance, and confirmation that broker order endpoints were not called.

### P5 — ML proof

ML endpoint/UI visibility is not model proof. Require matured prediction-versus-actual rows, sample size, horizon, accuracy/ranking metrics, and artifact provenance. Keep the model BLOCKED when training or matured evaluation evidence is absent.

### P6 — 1000+ TODO source

The updater expects one genuine canonical checklist:

```text
docs/SYSTEM3_PRODUCTION_GRADE_1000_POINT_QC_TODO.md
```

or the legacy root fallback:

```text
System3_Production_Grade_1000_Point_QC_TODO.md
```

Do not generate artificial completed items. Until the real checklist is restored, report `total=0`, `status=BLOCKED`, and `production_grade_claim_allowed=false`.

## Required rerun sequence

1. Restore the Dhan read-only runtime session without exposing credentials.
2. Verify the deployed commit matches the repository commit.
3. Clear the generated live-proof directory.
4. Run the authenticated live UI proof.
5. Run the strict production visual proof.
6. Run shell/visible-issue checks.
7. Run broker, required-chain, scanner, paper, ML, and gate proof.
8. Run the distinct latest-workflow failure tracker.
9. Run the 1000+ TODO updater.

## Closure contract

DONE/resolved is allowed only when the current strict Render production proof reports:

```text
visual_gate_pass=true
production_grade_claim_allowed=true
auth_ok=true
screenshot_gate_pass=true
infra_blockers=[]
visual_blockers=[]
trade_readiness_blockers=[]
ANALYZE_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
```

Any remaining item must be reported with its exact endpoint, workflow, symbol, proof file, or missing artifact.