# 20 — Next Action Dependency and Handoff Map

QC: 2026-08-16T06:45:28Z  
PR: https://github.com/psw2025-cmd/Genesis_System3/pull/242  
Audit main pin: `c763ecf048478842688373cf674eb56a7dc04aa9` · Current main: `41f7a80cf0c31711f4c26d46fdc0e3f26fc6a311` · Serving: `a48e7b3c7c086a21352f718355d1c12d4a48955b`

## P0

| ID | Finding | Owner | Deps | User? | Parallel? |
|----|---------|-------|------|-------|-----------|
| F-001 | Serving≠main drift | CURSOR→GCP_AUTOMATION | classify runtime vs proof commits; deploy if needed | NO | NO (before live proofs) |
| F-002 / #188 | Universe parity incomplete | CHATGPT design → CURSOR | master counts, coverage API | NO | After F-001 |
| R25.1 | IAM vs baseline not completed in audit | CURSOR | read-only IAM dump | NO | YES with F-002 prep |
| Equity OC live | NOT_PROVEN | MARKET_SESSION_AUTOMATION | MH | NO | After Wave1 OC |

## P1

| ID | Finding | Owner | Deps | User? |
|----|---------|-------|------|-------|
| F-016 | TOTP secret v8 DESTROYED | USER_BREAK_GLASS then CURSOR verify | Secret Manager | **YES** (secret) |
| F-003 | Chain stampede timeouts | CHATGPT→CURSOR | Wave1 single-flight | NO |
| F-004 | PCR schema | CURSOR | DTO | NO |
| F-005 | Prediction Audit miswire | CHATGPT→CURSOR | ledger design | NO |
| F-006 | accuracy_trend orphan | CURSOR | FE chart | NO |
| F-007 | OC lake missing | CHATGPT→GCP | storage design | NO |
| F-008 | ML registry missing | CHATGPT | blueprint | NO |
| F-012 | CI failures on main | CURSOR | triage runs | NO |
| R13.2 | Dhan 429 RCA | MARKET_SESSION_AUTOMATION | MH soak | NO |
| R14/R11 | Index/BSE counts | CURSOR | master | NO |

## P2 / P3

Mobile UI, visual defect gallery, Monitoring policies, deep journey script, chart category expansion → CURSOR/CHATGPT; no user.

## MARKET_HOURS

Owner: MARKET_SESSION_AUTOMATION (+ CURSOR scripts). Plan: `13_`.

## MANUAL_BREAK_GLASS

Only **M-001** TOTP secret ENABLED/`latest` repair (see `18_`).

## Optimal sequence

1. **USER** fix TOTP secret latest (M-001) if mint must be reliable  
2. **CURSOR** read-only IAM baseline compare (close R25.1 gap)  
3. **CHATGPT** authorize Wave 0–1 (SHA lock + OC single-flight)  
4. Deploy/converge serving SHA if runtime commits pending  
5. UI wiring Wave 3 (PCR, Prediction Audit, accuracy_trend)  
6. Market-hours proof pack (#188 sample + 4 indices + VIX + 429)  
7. Data lake + ML registry waves  
8. IAM least-privilege closure after deny proofs  

## ChatGPT-owned next

- Remediation wave sequencing & PR designs from findings  
- Decide whether current main `41f7a80cf0c31711f4c26d46fdc0e3f26fc6a311` requires new forensic delta vs audit pin  
- Prediction ledger / ML honesty UX copy  

## Cursor-owned next (after authorization)

- IAM forensic completion  
- Wiring fixes Wave 3  
- OC coalescing Wave 1  
- Market-hours automation scripts  
- CI failure triage  

## Top 10 remaining dependencies

1. TOTP secret health (F-016)  
2. Serving SHA convergence (F-001)  
3. Current-main delta since `c763ecf048478842688373cf674eb56a7dc04aa9`  
4. IAM baseline compare  
5. OC single-flight (F-003)  
6. Issue #188 count matrix  
7. Market-hours window  
8. PCR/Prediction Audit/accuracy_trend wiring  
9. OC durable lake  
10. CI red workflows on main  
