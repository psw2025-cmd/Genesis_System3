# Genesis System3 User-Action, Autonomy, and Speed Policy

**Authority marker:** `SYSTEM3_USER_ACTION_AUTONOMY_SPEED_V1`

This policy exists because agents previously made a harmful reasoning error: they treated `HUMAN_ACTION_REQUIRED=NO` as if it also meant `USER_ACTION=NONE` and as if no user-side setup could materially accelerate safe autonomous execution. For a non-coder owner, that behavior is misleading. It hides leverage that the agent is responsible for discovering and explaining.

## Core law

Every agent must distinguish three different questions on every material System3 task:

1. **Can the agent continue safely without the user?**
2. **Is there any user-side account/settings/access action that would materially speed up, unblock, or improve the quality of autonomous work?**
3. **Is a true human-only/break-glass action mandatory before progress can continue?**

These answers are independent.

Therefore:

- `HUMAN_ACTION_REQUIRED=NO` does **not** permit `USER_ACTION=NONE` unless the agent has actively checked for useful user-side setup actions.
- If a safe user-side setting would materially reduce delays, retries, stale PRs, merge blocks, connector limitations, or proof gaps, the agent must surface it immediately in kid-level instructions.
- The agent must continue all safe autonomous work in parallel while the user performs any optional acceleration step.
- The user must never be asked to run technical commands that the connected agent can safely execute itself.

## Mandatory 19-point self-MRI before saying USER_ACTION=NONE

Before any agent reports `USER_ACTION=NONE`, `HUMAN_ACTION_REQUIRED=NO`, or equivalent, it must check all 19 items below and record the result in the active task ledger or Issue #188 when material:

1. GitHub repository access is connected and current.
2. Current `main` can be read remotely.
3. Agent can create/update a branch when implementation is needed.
4. Agent can create/update PRs.
5. Agent can read exact-head CI checks and failed logs.
6. Agent can review/comment on PRs.
7. Merge is permitted by current repository governance after checks/review.
8. Branch/ruleset protection does not accidentally block intended safe automation.
9. Bypass permissions are no broader than necessary and do not weaken safety.
10. Required status checks are correctly configured and actually emitted by relevant PRs.
11. Required review settings are compatible with the available independent reviewer model.
12. GitHub environment/deployment protection is configured so approved autonomous deployment is not silently blocked.
13. GCP WIF/deploy identity is usable without service-account keys.
14. GCP runtime/proof access is available to the responsible cloud agent.
15. Browser/URL proof tooling can reach the canonical production URL.
16. Broker recovery authority, if ever needed, is cloud-only and separately delegated.
17. External account/provider actions that cannot be delegated are identified early.
18. Another active agent/PR does not already own the same write surface.
19. The fastest safe primary path and at least one safe alternative have been compared, with expected time/benefit explained to the user.

If any item is `NO`, `PARTIAL`, or `UNKNOWN`, the agent must not hide it behind `USER_ACTION=NONE`.

## Kid-level user guidance contract

When a user action is useful or required, every agent must provide:

- **WHY:** one sentence describing the concrete blocker or speed benefit.
- **WHERE:** exact product/page path, for example `GitHub > Repository > Settings > Rules > Rulesets`.
- **CLICK:** the exact control to click or toggle.
- **SET:** the exact value to select.
- **DO NOT:** the nearby setting that must remain unchanged for safety.
- **RESULT:** what becomes faster or unblocked after the change.
- **PROOF:** what screenshot, URL, or fresh API evidence the agent will verify afterwards.
- **URGENCY:** `NOW`, `TODAY`, or `OPTIONAL`.

Do not dump raw logs or assume coding knowledge when a graphical click path can be given.

## Speed-first autonomous execution law

For every open blocker, the agent must choose the fastest safe path that preserves production truth and safety. The operating order is:

`fresh authority -> ownership -> user/setup leverage check -> parallel safe work -> root cause -> smallest systemic fix -> tests -> PR -> exact-head CI -> review -> merge -> deploy -> exact-serving URL/UI proof -> next blocker`

Rules:

- Never remain in chat/reporting mode when a safe executable repo/cloud action exists.
- Never wait for the user on routine engineering that the agent can perform.
- Never hide a useful user setup action merely because work can technically continue without it.
- Never ask the user to weaken safety, enable LIVE, expose secrets, create service-account JSON keys, or bypass failed checks.
- Prefer visual/kid-level guidance for account settings, permissions, connectors, billing, organization settings, and external provider setup.
- Give an expected speed benefit in plain language, for example: `This removes repeated manual merge blocks and lets green PRs move automatically after required review.`

## Exact user-run command/file + cross-verification loop

When the fastest safe path requires the user or the user's laptop agent to perform an action that this agent cannot execute directly, the agent must not respond with vague prose such as `run some checks`, `open settings`, or `ask your agent to verify`.

The agent must provide the smallest exact runnable artifact available:

1. Prefer one ready-to-run file (`.bat`, `.ps1`, `.sh`, or repository script) when several commands are needed.
2. Otherwise provide one exact copy/paste command.
3. State the exact directory/context from which to run it.
4. State what output/evidence must be returned.
5. Never request secret values; commands must redact token/secret payloads by default.
6. After the user returns the output, the agent must independently cross-check every relevant capability/settings item it can verify from GitHub/GCP/current remote evidence.
7. If anything remains missing, ambiguous, or misconfigured, report **only the smallest remaining correction** the user must make, using `WHY / WHERE / CLICK or RUN / SET / DO NOT / RESULT / PROOF / URGENCY`.
8. Repeat this verify-correct-reverify loop until the required capability is proven or a genuine external blocker is reached.
9. Agents do not make the user rerun already-PASS checks unless fresh evidence shows they may have changed.
10. Once the required access/capability is proven, immediately continue the agent-owned implementation work; do not stop at the access audit.

Required output fields for this loop:

- `USER_RUN_FILE_OR_COMMAND=` exact artifact or `NONE`
- `RETURN_THIS_EVIDENCE=` exact output needed
- `CROSS_VERIFY_RESULT=` `PASS / PARTIAL / FAIL / UNPROVEN`
- `ONLY_REMAINING_USER_CORRECTION=` exact smallest correction or `NONE`
- `AGENT_CONTINUES_WITH=` next agent-owned executable action

This rule applies especially to GitHub permissions/rulesets/actions, GCP/WIF/deploy visibility, canonical URL reachability, broker-cloud recovery authority, and any other setup that materially affects autonomous delivery speed.

## RUHI start-of-work recall marker

For Genesis System3 material work, `#RUHI #RUHI2` is a visible execution marker, not decoration. When used at task start or transition, it requires the agent to recall and apply this policy before acting or reporting.

At minimum it means:

- use already-verified access first;
- do not forget or re-ask settled capability facts without cause;
- surface the fastest safe user leverage immediately;
- provide exact runnable commands/files instead of vague instructions when user execution is needed;
- cross-verify returned evidence;
- correct only what is still missing;
- continue until the practical product result is proven;
- treat live dashboard/UI + backend/API/data/model/paper-trade truth as the acceptance surface, not chat, plans, code existence, or render-only success.
- immediately tell the user when a material run stalls, fails, times out, is interrupted, or loses promised evidence; do not wait for the user to discover or ask about it;
- state what failed, the impact, what remains proven, what became unproven, and the recovery action already being taken.

## False-NO prevention

The following statements are prohibited unless the 19-point self-MRI has been completed for the current material task:

- `No action required from user.`
- `HUMAN_ACTION_REQUIRED=NO` when a useful account/settings action exists but is merely optional.
- `Everything is autonomous` when merge/review/deploy/account configuration is actually preventing autonomy.
- `Waiting` when another safe non-overlapping lane is executable.

Instead use two explicit fields:

- `MANDATORY_USER_ACTION=` `NONE` or the true blocker.
- `OPTIONAL_ACCELERATION_ACTION=` `NONE` or the fastest safe user-side setup improvement.

A task may correctly have `MANDATORY_USER_ACTION=NONE` and simultaneously have a non-empty `OPTIONAL_ACCELERATION_ACTION`.

## User-behavior adaptation

System3 agents must assume the owner may be non-technical unless the current task proves otherwise. The agent must therefore:

- explain settings visually and sequentially;
- use screenshots as confirmation when available;
- avoid jargon without a plain-language translation;
- tell the user before an account-level setup becomes a blocker, not after hours of failed automation;
- present the shortest safe path first and alternatives second;
- explicitly state what the agent will do automatically after the user's click;
- never make the user repeatedly rediscover the same setup requirement across agents.

## Multi-agent propagation

Every agent must read this policy before:

- saying no user action is needed;
- asking for user action;
- recommending GitHub/GCP/account settings;
- merge/deploy governance changes;
- final status that claims autonomous progress.

Issue #188 remains the coordination bus. A material autonomy/access/settings discovery must be posted once as a deduplicated transition so all agents inherit it.

## Safety invariants remain unchanged

This speed policy never authorizes:

- LIVE trading;
- real order placement/modification/cancellation;
- secret/token/PIN/TOTP exposure;
- service-account JSON keys;
- bypassing failed mandatory checks;
- destructive data deletion;
- privilege expansion without governed approval.

Faster means fewer avoidable coordination and permissions delays, not weaker safety.

## Dashboard-impact priority and dual-channel owner escalation

**Authority extension:** `SYSTEM3_USER_ACTION_ESCALATION_V2`

A blocker is owner-escalation priority when a safe user-side action can directly
or indirectly accelerate, unblock, or improve any of these surfaces:

- production dashboard content, cards, tables, charts, tabs, or status truth;
- market-data coverage, instrument master, broker/option-chain/quote/candle
  freshness, source labeling, or API↔UI parity;
- scanner, prediction, ML, PAPER lifecycle, P&L, risk, or proof visibility;
- CI, review, merge, deployment, GCP evidence, browser capture, or agent access;
- multi-agent ownership, handoff, or any dependency feeding the dashboard.

The agent must prioritize the least-privilege action that unlocks the greatest
number of downstream tasks. It must not pause unblocked work while escalation is
pending.

### Required option matrix

For every useful owner action, list all materially different **safe** options.
Put the fastest safe option first and label it
`FASTEST_SAFE_RECOMMENDED`. For each option state:

- expected time to enable;
- tasks/surfaces unblocked;
- permission or account scope;
- risk and rollback;
- evidence that will prove it worked.

Do not pad the list with cosmetic variants, and never offer an unsafe option
such as bypassing failed checks, sharing secrets, weakening IAM/WIF, or enabling
LIVE/orders.

### Immediate chat and mail action card

Create one stable `USER_ACTION_ID` and deliver the same concise action card:

1. immediately in the active ChatGPT/Work chat;
2. immediately through the verified connected owner mail identity;
3. once in Issue #188 when material, so every agent inherits the state.

The action card must contain:

- `USER_ACTION_ID`, detection time, owner, blocked task IDs, and dashboard
  impact;
- `MANDATORY_USER_ACTION` and `OPTIONAL_ACCELERATION_ACTION` as separate
  fields;
- `FASTEST_SAFE_RECOMMENDED` plus alternatives;
- `WHY / WHERE / CLICK or RUN / SET / DO NOT / RESULT / PROOF / URGENCY`;
- `AGENT_CONTINUES_WITH` for parallel autonomous work;
- `STATUS` and `NEXT_REMINDER_AT`.

Recipient identity must be resolved from the connected provider. Never guess or
commit the owner's private address. If mail access or sending fails, notify in
chat, record `MAIL_DELIVERY_BLOCKED`, give the smallest connection correction,
and continue chat/Issue delivery.

### Repeat-until-proven tracker

Statuses are:

`DISCOVERED -> NOTIFIED -> ACKNOWLEDGED -> IN_PROGRESS -> PROVEN_COMPLETE`

or `SUPERSEDED` with a replacement ID.

Acknowledgement or a claimed click is not completion. Close only after fresh
screenshot, provider/API state, repository setting, workflow result, or other
appropriate practical proof verifies the intended capability.

Reminder rules:

- notify immediately on discovery or material change;
- while owner-blocking and unresolved, repeat the smallest remaining action at
  least every 6 hours;
- for an active P0 market-session/dashboard incident, a one-hour reminder is
  allowed when the user can still act and the reminder contains new status or
  the exact outstanding step;
- do not send identical mail every automation tick; deduplicate by
  `USER_ACTION_ID + action revision`;
- stop reminders immediately when `PROVEN_COMPLETE` or `SUPERSEDED`;
- never remove an unresolved action from the ledger because another task moved.

Each reminder must show
`PREVIOUS_REMINDER -> USER_EVIDENCE_RECEIVED -> CROSS_VERIFY_RESULT ->
ONLY_REMAINING_USER_CORRECTION -> AGENT_CONTINUES_WITH`.

This delivery rule complements ChatGPT task notifications. Account-level task
notification channels are controlled by the owner's ChatGPT notification
settings; direct connected-mail delivery must be reported as successful only
when the mail action itself confirms success.
