# ISSUES MERMAID (overwrite)

Serving `01a4592f4c68c120a26b4fd955d1aff655b82e33` · gates 3/7

## P0 dependency micro-network

```mermaid
flowchart LR
    PEND_001["PEND-001"]
    PEND_004["PEND-004"]
    PEND_005["PEND-005"]
    PEND_006["PEND-006"]
    PEND_007["PEND-007"]
    PEND_008["PEND-008"]
    PEND_009["PEND-009"]
    PEND_014["PEND-014"]
    PEND_015["PEND-015"]
    PEND_016["PEND-016"]
    PEND_017["PEND-017"]
    PEND_018["PEND-018"]
    PEND_001 --> PEND_004
    PEND_014 --> PEND_017
    PEND_014 --> PEND_018
```

## Full control loop

```mermaid
flowchart TD
  CC[command_center_refresh] --> T[TRACKING_CHECKLIST overwrite]
  CC --> X[AGENT_OPERATING_OPTIONS.xlsx]
  CC --> I[ISSUES_ONLY.md]
  CC --> M[ISSUES_MERMAID.md]
  T --> A[Agent picks highest P0]
  A --> E[Edit primary clone]
  E --> CC2[AUTO trigger command_center again]
  CC2 --> P[PR merge deploy]
  P --> S[Serving SHA proof]
  S --> B[Browser re-snap]
  B --> D{Match?}
  D -->|No| A
  D -->|Yes| DONE[Mark DONE on checklist]
```

## Advanced solution order (agent-first)

1. OPT-A1 deploy chain+API aliases  
2. OPT-A10 keep command_center as only probe source  
3. OPT-A3 deploy lag  
4. OPT-A4 scheduler  
5. OPT-A5 paper persistence  
6. OPT-A6 signals  
7. OPT-A7 ML gates (long)
