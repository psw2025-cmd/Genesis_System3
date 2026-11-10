# RUHI CAPABILITY MRI V3 — Proof-First Self-Execution and Alternative Escalation Law

Status: proposed canonical addendum to `docs/RUHI_RULE_V2.md`.

`#RUHI #RUHI2` means every agent must apply this law before asking the owner to do routine work.

## 1. Self-test before user escalation

For every blocker, first enumerate the agent's currently exposed read/write capabilities and test the safe, non-destructive paths that can materially resolve it. Never assume a capability from an old conversation, and never assume incapability without a current probe when a safe probe exists.

Required order:

1. direct authenticated tool/API action;
2. alternate authenticated tool/API action;
3. repository/workflow/PR/branch mechanism;
4. another authorized agent with the required capability;
5. exact laptop-agent runnable file/command when local observation is genuinely needed;
6. owner UI action only for a real owner-only boundary.

Do not stop engineering merely because a final merge/review/permission gate is blocked. Continue all non-overlapping work that can safely reach ready-to-merge/proven state.

## 2. Proofed capability matrix

Each capability claim must be one of:

- `PROVEN_READ`: current successful read/list/fetch.
- `PROVEN_WRITE`: current successful safe write/mutation.
- `PROVEN_BLOCKED`: attempted safe operation returned an authoritative permission/policy/tool block.
- `NOT_EXPOSED`: no current tool/API surface exists for the operation.
- `UNTESTED_RISKY`: testing would itself be destructive, security-sensitive, LIVE/order affecting, secret-revealing, or governance-bypassing; do not probe merely to learn capability.

A successful adjacent operation does not prove a different permission. Example: branch creation does not prove merge-to-main; PR comments do not prove independent approval.

## 3. Current ChatGPT GitHub capability baseline

Reconfirm when material because integrations can change. Known safe surfaces include repository/file reads, PR/issue metadata, diffs/patches, branches, workflow/check observations, review observations, file writes on permitted branches, PR creation/metadata/comments, reviewer requests, merge/auto-merge attempts subject to GitHub governance, and issue updates where exposed.

Known limitations must be stated precisely. The connector does not itself provide a literal screenshot of the GitHub Settings UI. A screenshot is therefore not the default evidence source: use API-observable effects first. Independent-review requirements cannot be truthfully satisfied by self-approval. Operations blocked by GitHub rulesets, missing permissions, or external identity must remain blocked rather than bypassed.

## 4. No fake capability testing

Never weaken a ruleset, force-push protected refs, expose a secret, rotate a token, deploy, enable LIVE, place/modify/cancel an order, delete authoritative data, or perform another material/destructive action only to test whether access exists.

For those capabilities use read-only permission/config evidence, dry-run/preflight when available, or mark `UNTESTED_RISKY`/`PROVEN_BLOCKED`.

## 5. Alternative ladder on every blocker

Before saying `USER_ACTION_REQUIRED`, publish:

- `BLOCKED_OPERATION`
- `DIRECT_PATH_RESULT`
- `ALTERNATIVE_1`
- `ALTERNATIVE_2`
- `OTHER_AGENT_OPTION`
- `LAPTOP_AGENT_OPTION`
- `OWNER_ONLY_OPTION`
- `BEST_FASTEST_RECOMMENDATION`
- `WHY_BEST`
- `PARALLEL_WORK_CONTINUING`

Rank alternatives by: safety/governance first, then fastest time-to-proof, then least owner effort, then reversibility, then operational cost.

## 6. Exact kid-level user/laptop handoff

When external action is genuinely required, never give a vague request. Provide only the smallest remaining correction with:

- `WHY`
- `WHERE`
- `CLICK` for UI, or exact `RUN_FROM` directory for terminal;
- exact `SET` value or exact `COMMAND`/runnable `.ps1`, `.bat`, `.sh`, or repo script;
- `DO_NOT` safety boundary;
- `EXPECTED_RESULT`;
- `RETURN_THIS_EVIDENCE` with secrets redacted;
- `URGENCY`;
- `WHAT_AGENT_DOES_IMMEDIATELY_AFTER`.

If five checks exist and four are proven, ask only for the fifth. Never make the owner repeat already-proven steps without a material reason.

## 7. Verify-correct-reverify loop

After owner/laptop/other-agent evidence returns:

1. independently cross-verify using authoritative cloud/GitHub/API evidence when possible;
2. classify every requested item PASS/PARTIAL/FAIL/UNPROVEN;
3. if anything remains, return only the minimum correction;
4. reverify that correction;
5. immediately continue agent-owned implementation/proof work.

Do not convert supplied terminal text or a screenshot into production acceptance when stronger authoritative evidence exists.

## 8. Best recommendation is mandatory

Do not merely list choices. State `BEST_FASTEST_RECOMMENDATION` and why it wins for the current constraints. Mention a faster safe resource/agent/tool when known instead of hiding it or defaulting to a slower manual path.

## 9. Screenshot law

Use screenshots when visual state itself is the evidence or when an owner-only setting is not API-observable. Before requesting a screenshot, attempt available read-only API/config/effect checks. If a screenshot is needed, request the exact page/region and explain what single fact it must prove. For production UI acceptance, exact-serving browser screenshot/video evidence remains required by the parent RUHI rule.

## 10. Multi-agent propagation

ChatGPT, Cursor, Claude, Codex, laptop agents and future agents must receive the same `#RUHI #RUHI2` execution law through canonical repo documentation and Issue #188 coordination. Other-agent output is evidence to cross-check, not authority to accept blindly.

## 11. Core System3 result focus

Capability MRI exists to accelerate, not replace, product delivery. Continue to prioritize truthful 22-tab UI, Dhan-sourced option-chain/market truth, broker truth, backend/API/database architecture, persisted PAPER lifecycle and P&L, models/signals/risk/scheduler/alerts/gates, exact-main deployment, and same-session API↔UI proof while LIVE/orders remain disabled unless separately authorized.

## 12. RUHI2 failure capture

Every newly observed repeated failure becomes a prevention check:

`WHAT_BROKE -> ROOT_CAUSE -> FASTEST_SAFE_FIX -> PREVENTION_CHECK -> PROOF`.

Examples include: asking the owner for work the agent can do; declaring no user action without checking acceleration options; stopping all work on one merge/review blocker; treating CI as production proof; treating render success as semantic success; forgetting known tool access without rechecking; and failing to give an exact runnable handoff when external action is truly needed.
