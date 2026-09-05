# Multi-Agent Consensus

Independent lanes (this audit):

| Lane | Focus | Primary evidence |
|------|-------|------------------|
| A | Production UI 22 tabs Playwright | REQUEST_SCOPED_LIVE_BROWSER |
| B | FE↔BE wiring | CURRENT_GITHUB_MAIN |
| C | GCP runtime | LIVE_GCP_RESOURCE / LOG |
| D | Dhan market data | CURRENT_GITHUB_MAIN + LIVE_API |
| E | Lineage | CURRENT_GITHUB_MAIN |
| F | ML/training | CURRENT_GITHUB_MAIN |
| G | Adversarial | contradictions across lanes |

## Agreements

- Broker connected now; live off — lanes A/C/API agree.
- Chain provenance visible — A + B agree (disproves UI-missing-source hypothesis).
- Full universe #188 not done — D/E/B agree.
- OC durability ephemeral — D/E agree.
- ML institutional gaps — F agrees with blueprint.

## Contradictions resolved

- Handoff (2026-08-15) disconnected vs today connected → temporal truth; handoff HISTORICAL.
- First 4-chain large HTTP bodies vs later NO_DHAN_DATA → concurrency/timeout; not “no data forever”.
- GCP “429” logs ≠ Dhan 429 without payload proof.

Agent consensus never overrides live evidence.
