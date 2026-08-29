# System3 Actions Storage Forensic Contract

Canonical module: `scripts/system3_actions_storage_forensic.py`.

This is a submodule of the permanent Repo Clean Forensic Toolkit. It exists because repository source files, Git history, GitHub Actions artifacts, and GitHub Actions caches are different storage layers and must not be cleaned with the same evidence rule.

## Artifact deletion-evidence rule

The module is report-only. It may emit `ACTIONS_DELETE_PROVEN_100` only on an exact `main` authority run and only when all of these are true:

1. GitHub reports the same artifact name.
2. GitHub reports the same `sha256:` artifact digest.
3. The artifact size agrees with the retained identical copy.
4. A non-expired identical copy is explicitly retained.
5. The candidate is at least seven days old by default.
6. The candidate is not evidence attached to the current main SHA.
7. The candidate itself is not already expired/server-side expiring.
8. The run is `refs/heads/main` on `push` or `workflow_dispatch`; PR scans are report-only even when exact duplicates are found.

The report records deleted-candidate artifact IDs and the retained identical artifact ID. Actual deletion is a separate destructive action and must preserve this manifest first.

## Cache policy

Actions caches are reproducible build acceleration, not source-of-truth evidence. The module still fails closed: it preserves `refs/heads/main` caches and caches accessed within the last 14 days by default. Older non-main caches are reported as `CACHE_RECLAIM_CANDIDATE`; the module does not delete them.

## Completeness

The module records the GitHub API total count, number inventoried, pages scanned, and whether inventory is complete. A truncated scan may prove specific exact-digest duplicate candidates inside the observed set, but it must never be presented as the final storage total.

PR runs intentionally cap artifact pages for fast regression proof. Main/manual runs use the large pagination budget required to inventory the current repository Actions storage as completely as GitHub API limits permit.

## Safety

No artifact deletion, cache deletion, source deletion, history rewrite, broker call, token rotation, secret read, IAM change, LIVE change, or order action is performed by this module.
