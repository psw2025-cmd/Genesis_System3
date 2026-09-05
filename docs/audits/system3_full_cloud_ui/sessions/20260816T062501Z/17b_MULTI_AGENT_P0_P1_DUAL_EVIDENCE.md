# Multi-agent dual evidence (P0/P1)

| Finding | Lane1 | Lane2 | Evidence1 | Evidence2 | Agreement | Final |
|---------|-------|-------|-----------|-----------|-----------|-------|
| F-001 SHA drift | Live API | GCP describe | deploy/info | revision image tag | AGREE | CONFIRMED |
| F-002 #188 incomplete | D market | B wiring | hardcoded stream | discovery vs stream | AGREE | CONFIRMED_MISSING |
| F-003 OC timeout | Live API | D code | summary_compact | paced 3.4s lock | AGREE | DEGRADED |
| F-004 PCR | B wiring | Live UI options-intel short text | miswirings.csv | scorecard | AGREE | MISWIRING |
| F-005 Pred Audit | B | Live UI | code auto_gates | tab text short | AGREE | MISWIRING |
| F-006 accuracy_trend | B | Live API | no FE call | endpoint 200 | SINGLE_LANE_ONLY+API | MISSING UI |
| F-007 OC durable | D | E | ephemeral cache | lineage | AGREE | MISSING |
| F-008 ML registry | F | blueprint doc | MISSING labels | — | SINGLE_LANE_ONLY | MISSING |
| F-012 CI fail | GitHub Actions | — | run IDs | — | SINGLE_LANE_ONLY | CONFIRMED |
| F-013 source= | A UI | B code | chain.txt | OptionChain.tsx | AGREE | CORRECT |
| F-014 safety | A+API | manifest | live=false | — | AGREE | CORRECT |
| F-015 connected | API | UI | broker status | Broker Connected | AGREE | CORRECT |
| F-016 TOTP DESTROYED | C GCP | jobs JSON | 25szr message | FORENSIC_SUMMARY | AGREE | CONFIRMED |
