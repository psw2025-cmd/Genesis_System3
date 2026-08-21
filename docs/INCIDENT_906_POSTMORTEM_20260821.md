# INCIDENT POSTMORTEM 906 - Dhan Auth Failure
DATE: 2026-08-21
STATUS: RECOVERED_PENDING_STABILITY_VERIFICATION
SERVICE: genesis-system3-web @ asia-south1 @ system3-openalgo-safe

## OBSERVED FACTS
1. Secret v283 was ENABLED and not expired. Expiry: 2026-08-22T09:00:13Z. But Dhan rejected with 906.
2. Secret v284 created via rotation job at 2026-08-21T11:00:25Z. Dhan accepted. connected: True.
3. Env vars SELF_HEAL set to 1. Need 3 hourly cycles to verify auto-recovery works.
4. Git SHA on laptop: bf8efd9bd9b9473530d7f51bdfc3fd96d5421ec4. Remote status:

```text
On branch fix/smoke-chain-semantic-settle
Your branch is ahead of 'origin/fix/smoke-chain-semantic-settle' by 1 commit.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  modified:   .cursor/rules/continuous-closure.mdc
  modified:   .gitignore
  modified:   AGENTS.md
  modified:   System3_Master_MRI_Control.xlsx
  modified:   agent_policy.yaml
  modified:   deploy/gcp/system3_iam_baseline.json
  modified:   docs/CONTINUOUS_CLOSURE_SYSTEM.md
  modified:   reports/latest/continuous_closure/summary.json
  modified:   scripts/gcp_authority_repair.py
  modified:   scripts/system3_master_mri_workbook_builder.py
  modified:   system3_audit_dashboard.html
  modified:   tests/test_gcp_authority_repair_contract.py

Untracked files are present, including local reports, handoffs, audit artifacts, tools, and the .worktrees directory.
No changes added to commit.
```

5. Root cause hypothesis: Non-canonical token issuance or Dhan-side invalidation. Investigation ongoing.

## ACTIONS TAKEN
1. Set SYSTEM3_STARTUP_TOKEN_REFRESH=1 and DHAN_CANONICAL_ROTATION_SELF_HEAL=1
2. Executed canonical rotation job to generate v284
3. Verified v284 connected successfully once

## NEXT REQUIRED STEPS
1. Monitor for 3 hourly cycles to confirm v284 stays connected
2. Align local Git with GitHub main branch
3. Investigate why v283 was rejected while not expired

## PERMANENT RULES FOR ALL AGENTS
RULE 1: Always use canonical rotation job for new tokens. Never manual.
RULE 2: Secret name is dhan-access-token lowercase
RULE 3: Authoritative health check: /api/broker/dhan/status
RULE 4: Before claiming FIXED, provide 3-cycle stability proof + alignment output
RULE 5: Never delete old docs. Archive them with reason.

