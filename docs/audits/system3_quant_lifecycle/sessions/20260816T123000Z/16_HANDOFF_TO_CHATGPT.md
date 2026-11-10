# HANDOFF TO CHATGPT — Quant Lifecycle Q (20260816T123000Z)

**Read this first**, then matrices in the same folder.

## 0. Instruction source
`docs/chatgpt_instruction_for_cursar_2.md` (also copied as `00_INSTRUCTION_SOURCE.md`)

Contains:
1. **Part 1** — Broker permanent fix executor tasks (4:53 PM IST) → **PASS / re-verified**
2. **Part 2** — Mandatory Q1–Q27 quant lifecycle audit → **this package** (Q27 text truncated in source)

## 1. Production pins (live at capture)
| Pin | Value |
|-----|-------|
| URL | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui |
| Broker | **connected=true** |
| Secret | `dhan-access-token` **v259** |
| LIVE / orders | **false / false** |
| Serving SHA | `997daef4cfb3322e317da69b5cbb5b69950dab26` |
| Region | asia-south1 |
| Operator | Mumbai IST |

## 2. Executive verdict
Broker reliability ≠ System3 complete. Quant loop is **PARTIAL / NOT_PROVEN** with **UI_OBSERVABILITY_GAP**s. Promotion to live money correctly **BLOCKED**.

## 3. File map
| File | Content |
|------|---------|
| `00_MANIFEST.json` | Session pins |
| `00_EXECUTIVE_VERDICT.md` | Stage scoreboard |
| `01_BROKER_PART1_REPROOF.md` | Part 1 PASS evidence |
| `Q1_DATA_FETCH_MASTER.md` | Data acquisition |
| `Q2_Q10_FEATURES_MODELS.md` | Quality→models |
| `Q11_Q20_STRATEGY_PAPER.md` | Strategy→promotion |
| `Q21_Q26_UI_TRUTH.md` | URL-first gaps |
| `STAGE_STATUS_SCORECARD.csv` | Machine-readable stages |
| `supporting/*.json` | Live API captures |

## 4. Related prior evidence
- PR #242 full cloud UI forensic session
- PR #244 broker auto-heal
- PR #245 IST auth incident + Storage Insights unrelated
- `docs/incidents/BROKER_AUTH_20260816_IST.md`
- `docs/BROKER_SETUP.md`

## 5. What NOT to do next
- Do not enable LIVE
- Do not treat Storage Insights NHLVNDD as broker/quant root cause
- Do not invent “best strategy” without OOS tournament
- Do not call heuristics “AI”

## 6. Recommended remediation waves (for ChatGPT design)
1. Durable market history + labeled sources  
2. Feature/label contracts + leakage tests  
3. Champion/challenger registry  
4. Costed walk-forward backtest gate  
5. Paper lifecycle continuous proof  
6. URL truth surfaces for Q22  
7. Only then discuss LIVE

## 7. Handoff status
`READY_FOR_CHATGPT_REVIEW`
