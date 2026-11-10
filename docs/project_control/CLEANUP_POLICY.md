# System3 Proof-First Cleanup Policy

## Goal

Keep the repository and developer/GitHub storage clean without breaking the working runtime or deleting evidence/source based on filename guesses.

## Canonical cleanup authority

Use only:

- `scripts/system3_repo_clean_forensic_toolkit.py`
- `.github/workflows/repo-clean-forensic-toolkit.yml`
- `docs/project_control/REPO_CLEAN_FORENSIC_TOOLKIT.md`

Older cleanup reports/scripts are historical helpers unless explicitly incorporated into this canonical toolkit. Do not create parallel cleanup authorities.

## Report-only rule

The canonical toolkit never deletes or moves files. It inventories every current tracked file and separately reports current worktree bytes, Git-history/object bytes, GitHub Actions artifact bytes, and local ignored/untracked disk bytes.

Actual deletion must be a separate cleanup PR.

## Highest-confidence deletion class

Only `DELETE_PROVEN_100` rows in the fresh toolkit artifact are eligible for automatic cleanup-PR generation. This class requires the V1 evidence contract documented in `REPO_CLEAN_FORENSIC_TOOLKIT.md`.

Source/runtime files fail closed even when byte-identical; they are `QUARANTINE_FIRST_SOURCE_DUPLICATE` until a deletion PR passes normal mandatory CI.

## Never delete from weak signals

The following are **not** deletion proof by themselves:

- same filename;
- `old`, `backup`, `copy`, `archive`, `tmp`, `legacy`, or `quarantine` in a path;
- no result from one grep;
- old modification date;
- large file size;
- an old report saying “unused”;
- a previous agent/session recommendation;
- a GitHub storage warning without determining whether the bytes are worktree, history, or Actions artifacts.

## Required proof dimensions

Before deletion, use the canonical toolkit to establish as applicable:

1. SHA-256 content identity and authoritative replacement when claiming duplicate deletion.
2. No runtime/import reachability.
3. No workflow/Docker/package/config critical reference.
4. No literal path/basename reference that makes the file operationally required.
5. File is not protected governance/runtime authority.
6. Correct storage layer is being remediated.
7. Cleanup PR mandatory gates pass.
8. A rollback path exists through Git history/PR until any later history compaction is separately approved.

## Auto-clean local/generated noise

Generated OS/cache/build artifacts may be classified `DELETE_PROVEN_100` only when they are tracked and pass the canonical zero-reference/protected-authority gates. Local ignored/generated directories are reported separately and may be cleaned from local disk according to their tool-specific regeneration rules.

## Git history

Deleting a file from current `main` does not remove old blobs from Git history. History rewrite, BFG/filter-repo, force push, or destructive object cleanup is a separate high-risk operation and is never authorized by this cleanup policy alone.

## GitHub Actions storage

Actions artifacts are not repository source files. The toolkit reports their storage separately. Use retention/artifact cleanup to reclaim Actions storage; do not delete source files to solve artifact storage.

## Self-improvement

Every discovered cleanup misclassification must become a regression test in `tests/test_repo_clean_forensic_toolkit.py`. Improve this canonical toolkit instead of creating a new scanner.

## Non-negotiable safety

- Analyzer/PAPER mode only.
- Do not enable live trading during cleanup.
- Do not expose or commit credentials/private secrets.
- Never delete files based only on filename similarity.
- Toolkit execution itself performs zero deletions, zero history rewrites, zero broker/order actions, and zero IAM mutation.
