# Pending Tests — Archived 2026-10-30

These 5 test files reference modules that were never committed to the repository:

- scripts/gcp_full_dashboard_acceptance.py
- scripts/gcp_live_ui_semantic_proof.py
- scripts/gcp_rhui_strict_semantic_gate.py
- scripts/gcp_dhan_rotator_forensic.py
- scripts/gcp_public_dashboard_runtime_proof.py

Git history confirms none of these ever existed. The tests were written but the
modules were never committed. This caused collection errors that blocked ALL
test execution.

To restore these tests:
1. Write the 5 missing modules in scripts/
2. Move the test files back from tests/_pending/

Documented in: SYSTEM3_MICRO_MRI_INVENTORY.csv, various MRI docs.
Archived on: 2026-10-30 04:47:48

## Archived: test_dhan_single_token_authority.py — 2026-10-30

This test file was archived because it tests private helpers that never existed in:
  scripts/gcp_dhan_token_rotation_job.py

The production file (122 lines) has only:
  - log()
  - env()
  - main()

The tests expect:
  - _should_rotate()          ← never existed in any branch or commit
  - _non_rotation_status()    ← never existed in any branch or commit

Git forensics:
  - scripts/gcp_dhan_token_rotation_job.py: 2 commits (fc425c3, 17abec8), both identical 122 lines
  - tests/test_dhan_single_token_authority.py: 1 commit (72f4eb9), a frontend axios PR
  - Neither _should_rotate nor _non_rotation_status exists in git history

The tests were likely written for a refactor that was never completed.
The production file works as-is.

To restore this test file:
  1. Refactor scripts/gcp_dhan_token_rotation_job.py to extract those helpers
  2. Move test file back from tests/_pending/
