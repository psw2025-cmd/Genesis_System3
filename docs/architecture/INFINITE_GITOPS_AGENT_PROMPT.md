# Infinite GitOps Agent Prompt (permanent)

This is the **fail-closed** form of the “full-life infinite loop” prompt.
Agents must not stall routine PAPER/analyzer engineering waiting for chat
approval. They must never self-enable LIVE or invent profit/accuracy.

## Layer 0 — Governance & intent

Artifacts: `agent_policy.yaml`, `resume_state.json`, Git `main`,
`reports/latest/autonomous_loop/intent_tick.json`.

- Parse intent (next card, risk caps, compliance). Compile into **PRs + tests**.
- Re-evaluate the intent spec every tick. `wait_for_user=false` for routine work.
- Guardrails: LIVE=false, no secret leakage, no hot production graph rewrite.

## Layer 1 — Execution ring

Artifacts: Cloud Run Jobs (web, rotator, scheduler, IAM repair) with separated SAs.

- Route analyzer/paper work only. No real orders.
- New strategies live on sandbox branches and merge only after evals + CI.

## Layer 2 — Verification

Artifacts: CI, `tests/evals/`, GitHub Actions + WIF, proof gates.

- Empirical gates (Spearman, expectancy, lifecycle). Do not relabel them ZK.
- Failed invariants → another eval + PR. Do not mutate prompt weights in prod.
- Never lower gate thresholds to satisfy “profit maximization.”

## Layer 3 — Sovereign output

Artifacts: Cloud Run PAPER/ANALYZER, `reports/latest/proof_ledger/ledger.jsonl`.

- Append-only SHA256 chain: repo SHA, revision, broker **connected flag only**,
  gate IDs, intent next_id.
- No secrets in the ledger.
- LIVE stays false until a separate human enablement process.

## Commands

```bash
python scripts/system3_continuous_closure_orchestrator.py --offline
python scripts/system3_proof_ledger.py --offline --next-id A2
python scripts/system3_proof_ledger.py --verify-only
```

## Human-only

LIVE enablement, real orders, billing/org break-glass, broker MFA, WIF destruction.
