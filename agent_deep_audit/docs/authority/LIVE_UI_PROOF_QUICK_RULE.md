# System3 Live UI Proof — Quick Rule

**Marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

When anyone asks what the production UI shows **now/currently/live**:

```text
DO NOT read an old screenshot as current truth.
DO NOT use reports/latest as current truth.
DO NOT use a green deploy/CI run as semantic UI truth.

START NEW PRODUCTION BROWSER SESSION
  -> actual GCP Cloud Run UI
  -> fresh screenshots + visible text
  -> same-session read-only APIs
  -> timestamps
  -> compare UI vs API
  -> report truth
```

After any fix/deploy/recovery, run the sequence again.

For a full audit, capture all 22 canonical tabs with `scripts/gcp_live_ui_snapshot.py`.
Validate stored manifests with `scripts/system3_temporal_truth_guard.py` before any time-sensitive reuse.

Stored evidence is historical after capture. Use it for comparison/timeline, not to answer a later `show me now` request.
