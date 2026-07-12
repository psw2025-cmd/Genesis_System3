# Parallel Audit — paper_lifecycle

- Status: **BLOCKED**
- Blockers: `2`

## Findings
- Paper UI now has provenance panel.
- Inactive/route trading module contains fake fixture rejection logic.

## Blockers
- Trading router may be inactive if app.py duplicate routes are authoritative.
- Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.

## Required fixes
- Move paper provenance logic into active app.py route or confirm active endpoint response includes paper_truth.
- Run paper lifecycle proof with actual Dhan-derived candidate after scanner/ranker pass.
