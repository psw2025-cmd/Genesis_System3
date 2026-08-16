# 18 — Blocked / Not Proven / Manual Action Register
QC: 2026-08-16T06:45:28Z
Lists every requirement with status BLOCKED, NOT_PROVEN, NOT_DONE, or DONE_PARTIAL.
## R1.17 — DONE_PARTIAL
- **Requirement:** Do not begin with SYSTEM_STATE/CHANGE_LOG/reports as authority
- **Reason code:** STALE_EVIDENCE_REJECTED
- **Plain reason:** TEMPORAL process slip then corrected
- **Evidence attempted:** Authority docs + live first; SYSTEM_STATE peeked early then marked historical
- **Location:** 01_EXECUTIVE_VERDICT.md
- **Missing:** Early session peek before full authority read
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Keep historical labels
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R3.5 — DONE_PARTIAL
- **Requirement:** Never promote reports/latest as current
- **Reason code:** STALE_EVIDENCE_REJECTED
- **Plain reason:** Some prior session handoff mentioned as HISTORICAL
- **Evidence attempted:** used scratch+live; handoff referenced historical handoff file carefully
- **Location:** 01_EXECUTIVE
- **Missing:** Some prior session handoff mentioned as HISTORICAL
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** 
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R5.2 — DONE_PARTIAL
- **Requirement:** Two evidence classes for important findings
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** many P0/P1 dual-classed; not all
- **Location:** 14_MULTI_AGENT; 00_MASTER
- **Missing:** Some findings SINGLE_LANE_ONLY
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Re-observe single-lane items
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.semantic_state — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.api_compare — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.network_errors — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.freshness — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.provenance — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.empty_loading — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.visual_defect — NOT_DONE
- **Requirement:** Tab decision-intel: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab decision-intel: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.decision-intel.mobile_responsive — NOT_DONE
- **Requirement:** Tab decision-intel: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.semantic_state — DONE_PARTIAL
- **Requirement:** Tab truth: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.api_compare — DONE_PARTIAL
- **Requirement:** Tab truth: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.network_errors — DONE_PARTIAL
- **Requirement:** Tab truth: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.freshness — DONE_PARTIAL
- **Requirement:** Tab truth: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.provenance — DONE_PARTIAL
- **Requirement:** Tab truth: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.empty_loading — DONE_PARTIAL
- **Requirement:** Tab truth: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.visual_defect — NOT_DONE
- **Requirement:** Tab truth: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab truth: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab truth: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab truth: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.truth.mobile_responsive — NOT_DONE
- **Requirement:** Tab truth: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.semantic_state — DONE_PARTIAL
- **Requirement:** Tab genesis: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.api_compare — DONE_PARTIAL
- **Requirement:** Tab genesis: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.network_errors — DONE_PARTIAL
- **Requirement:** Tab genesis: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.freshness — DONE_PARTIAL
- **Requirement:** Tab genesis: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.provenance — DONE_PARTIAL
- **Requirement:** Tab genesis: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.empty_loading — DONE_PARTIAL
- **Requirement:** Tab genesis: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.visual_defect — NOT_DONE
- **Requirement:** Tab genesis: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab genesis: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab genesis: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab genesis: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.genesis.mobile_responsive — NOT_DONE
- **Requirement:** Tab genesis: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.semantic_state — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.api_compare — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.network_errors — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.freshness — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.provenance — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.empty_loading — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.visual_defect — NOT_DONE
- **Requirement:** Tab e2e-proof: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab e2e-proof: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.e2e-proof.mobile_responsive — NOT_DONE
- **Requirement:** Tab e2e-proof: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.semantic_state — DONE_PARTIAL
- **Requirement:** Tab overview: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.api_compare — DONE_PARTIAL
- **Requirement:** Tab overview: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.network_errors — DONE_PARTIAL
- **Requirement:** Tab overview: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.freshness — DONE_PARTIAL
- **Requirement:** Tab overview: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.provenance — DONE_PARTIAL
- **Requirement:** Tab overview: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.empty_loading — DONE_PARTIAL
- **Requirement:** Tab overview: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.visual_defect — NOT_DONE
- **Requirement:** Tab overview: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab overview: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab overview: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab overview: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.overview.mobile_responsive — NOT_DONE
- **Requirement:** Tab overview: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.semantic_state — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.api_compare — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.network_errors — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.freshness — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.provenance — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.empty_loading — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.visual_defect — NOT_DONE
- **Requirement:** Tab sim-live: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab sim-live: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.sim-live.mobile_responsive — NOT_DONE
- **Requirement:** Tab sim-live: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.semantic_state — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.api_compare — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.network_errors — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.freshness — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.provenance — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.empty_loading — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.visual_defect — NOT_DONE
- **Requirement:** Tab options-intel: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab options-intel: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.options-intel.mobile_responsive — NOT_DONE
- **Requirement:** Tab options-intel: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.semantic_state — DONE_PARTIAL
- **Requirement:** Tab chain: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.api_compare — DONE_PARTIAL
- **Requirement:** Tab chain: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.network_errors — DONE_PARTIAL
- **Requirement:** Tab chain: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.freshness — DONE_PARTIAL
- **Requirement:** Tab chain: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.provenance — DONE_PARTIAL
- **Requirement:** Tab chain: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.empty_loading — DONE_PARTIAL
- **Requirement:** Tab chain: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.visual_defect — NOT_DONE
- **Requirement:** Tab chain: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab chain: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab chain: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab chain: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.chain.mobile_responsive — NOT_DONE
- **Requirement:** Tab chain: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.semantic_state — DONE_PARTIAL
- **Requirement:** Tab signals: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.api_compare — DONE_PARTIAL
- **Requirement:** Tab signals: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.network_errors — DONE_PARTIAL
- **Requirement:** Tab signals: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.freshness — DONE_PARTIAL
- **Requirement:** Tab signals: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.provenance — DONE_PARTIAL
- **Requirement:** Tab signals: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.empty_loading — DONE_PARTIAL
- **Requirement:** Tab signals: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.visual_defect — NOT_DONE
- **Requirement:** Tab signals: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab signals: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab signals: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab signals: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.signals.mobile_responsive — NOT_DONE
- **Requirement:** Tab signals: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.semantic_state — DONE_PARTIAL
- **Requirement:** Tab trade: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.api_compare — DONE_PARTIAL
- **Requirement:** Tab trade: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.network_errors — DONE_PARTIAL
- **Requirement:** Tab trade: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.freshness — DONE_PARTIAL
- **Requirement:** Tab trade: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.provenance — DONE_PARTIAL
- **Requirement:** Tab trade: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.empty_loading — DONE_PARTIAL
- **Requirement:** Tab trade: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.visual_defect — NOT_DONE
- **Requirement:** Tab trade: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab trade: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab trade: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab trade: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.trade.mobile_responsive — NOT_DONE
- **Requirement:** Tab trade: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.semantic_state — DONE_PARTIAL
- **Requirement:** Tab paper: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.api_compare — DONE_PARTIAL
- **Requirement:** Tab paper: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.network_errors — DONE_PARTIAL
- **Requirement:** Tab paper: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.freshness — DONE_PARTIAL
- **Requirement:** Tab paper: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.provenance — DONE_PARTIAL
- **Requirement:** Tab paper: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.empty_loading — DONE_PARTIAL
- **Requirement:** Tab paper: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.visual_defect — NOT_DONE
- **Requirement:** Tab paper: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab paper: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab paper: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab paper: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.paper.mobile_responsive — NOT_DONE
- **Requirement:** Tab paper: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.semantic_state — DONE_PARTIAL
- **Requirement:** Tab positions: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.api_compare — DONE_PARTIAL
- **Requirement:** Tab positions: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.network_errors — DONE_PARTIAL
- **Requirement:** Tab positions: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.freshness — DONE_PARTIAL
- **Requirement:** Tab positions: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.provenance — DONE_PARTIAL
- **Requirement:** Tab positions: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.empty_loading — DONE_PARTIAL
- **Requirement:** Tab positions: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.visual_defect — NOT_DONE
- **Requirement:** Tab positions: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab positions: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab positions: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab positions: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.positions.mobile_responsive — NOT_DONE
- **Requirement:** Tab positions: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.semantic_state — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.api_compare — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.network_errors — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.freshness — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.provenance — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.empty_loading — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.visual_defect — NOT_DONE
- **Requirement:** Tab risk-scenarios: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab risk-scenarios: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.risk-scenarios.mobile_responsive — NOT_DONE
- **Requirement:** Tab risk-scenarios: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.semantic_state — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.api_compare — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.network_errors — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.freshness — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.provenance — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.empty_loading — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.visual_defect — NOT_DONE
- **Requirement:** Tab multibagger: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab multibagger: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.multibagger.mobile_responsive — NOT_DONE
- **Requirement:** Tab multibagger: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.semantic_state — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.api_compare — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.network_errors — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.freshness — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.provenance — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.empty_loading — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.visual_defect — NOT_DONE
- **Requirement:** Tab prediction-audit: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab prediction-audit: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.prediction-audit.mobile_responsive — NOT_DONE
- **Requirement:** Tab prediction-audit: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.semantic_state — DONE_PARTIAL
- **Requirement:** Tab performance: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.api_compare — DONE_PARTIAL
- **Requirement:** Tab performance: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.network_errors — DONE_PARTIAL
- **Requirement:** Tab performance: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.freshness — DONE_PARTIAL
- **Requirement:** Tab performance: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.provenance — DONE_PARTIAL
- **Requirement:** Tab performance: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.empty_loading — DONE_PARTIAL
- **Requirement:** Tab performance: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.visual_defect — NOT_DONE
- **Requirement:** Tab performance: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab performance: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab performance: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab performance: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.performance.mobile_responsive — NOT_DONE
- **Requirement:** Tab performance: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.semantic_state — DONE_PARTIAL
- **Requirement:** Tab ml: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.api_compare — DONE_PARTIAL
- **Requirement:** Tab ml: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.network_errors — DONE_PARTIAL
- **Requirement:** Tab ml: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.freshness — DONE_PARTIAL
- **Requirement:** Tab ml: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.provenance — DONE_PARTIAL
- **Requirement:** Tab ml: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.empty_loading — DONE_PARTIAL
- **Requirement:** Tab ml: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.visual_defect — NOT_DONE
- **Requirement:** Tab ml: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab ml: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab ml: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab ml: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.ml.mobile_responsive — NOT_DONE
- **Requirement:** Tab ml: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.semantic_state — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.api_compare — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.network_errors — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.freshness — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.provenance — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.empty_loading — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.visual_defect — NOT_DONE
- **Requirement:** Tab data-integrity: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab data-integrity: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.data-integrity.mobile_responsive — NOT_DONE
- **Requirement:** Tab data-integrity: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.semantic_state — DONE_PARTIAL
- **Requirement:** Tab broker: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.api_compare — DONE_PARTIAL
- **Requirement:** Tab broker: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.network_errors — DONE_PARTIAL
- **Requirement:** Tab broker: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.freshness — DONE_PARTIAL
- **Requirement:** Tab broker: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.provenance — DONE_PARTIAL
- **Requirement:** Tab broker: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.empty_loading — DONE_PARTIAL
- **Requirement:** Tab broker: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.visual_defect — NOT_DONE
- **Requirement:** Tab broker: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab broker: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab broker: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab broker: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.broker.mobile_responsive — NOT_DONE
- **Requirement:** Tab broker: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.semantic_state — DONE_PARTIAL
- **Requirement:** Tab alerts: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.api_compare — DONE_PARTIAL
- **Requirement:** Tab alerts: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.network_errors — DONE_PARTIAL
- **Requirement:** Tab alerts: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.freshness — DONE_PARTIAL
- **Requirement:** Tab alerts: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.provenance — DONE_PARTIAL
- **Requirement:** Tab alerts: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.empty_loading — DONE_PARTIAL
- **Requirement:** Tab alerts: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.visual_defect — NOT_DONE
- **Requirement:** Tab alerts: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab alerts: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab alerts: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab alerts: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.alerts.mobile_responsive — NOT_DONE
- **Requirement:** Tab alerts: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.semantic_state — DONE_PARTIAL
- **Requirement:** Tab system: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.api_compare — DONE_PARTIAL
- **Requirement:** Tab system: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.network_errors — DONE_PARTIAL
- **Requirement:** Tab system: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.freshness — DONE_PARTIAL
- **Requirement:** Tab system: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.provenance — DONE_PARTIAL
- **Requirement:** Tab system: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.empty_loading — DONE_PARTIAL
- **Requirement:** Tab system: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.visual_defect — NOT_DONE
- **Requirement:** Tab system: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab system: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab system: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab system: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.system.mobile_responsive — NOT_DONE
- **Requirement:** Tab system: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.semantic_state — DONE_PARTIAL
- **Requirement:** Tab gates: capture semantic_state
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** markers only; not full taxonomy per card
- **Evidence attempted:** markers only; not full taxonomy per card
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** markers only; not full taxonomy per card
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.api_compare — DONE_PARTIAL
- **Requirement:** Tab gates: capture api_compare
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** global APIs; not per-tab deep diff
- **Evidence attempted:** global APIs; not per-tab deep diff
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** global APIs; not per-tab deep diff
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.network_errors — DONE_PARTIAL
- **Requirement:** Tab gates: capture network_errors
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** api_statuses sampled; not full HAR
- **Evidence attempted:** api_statuses sampled; not full HAR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** api_statuses sampled; not full HAR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.freshness — DONE_PARTIAL
- **Requirement:** Tab gates: capture freshness
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** chain age on chain tab; not all tabs
- **Evidence attempted:** chain age on chain tab; not all tabs
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** chain age on chain tab; not all tabs
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.provenance — DONE_PARTIAL
- **Requirement:** Tab gates: capture provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** proven on chain; not every tab
- **Evidence attempted:** proven on chain; not every tab
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** proven on chain; not every tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Re-capture during market hours if freshness claim
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.empty_loading — DONE_PARTIAL
- **Requirement:** Tab gates: capture empty_loading
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** WAITING markers; incomplete empty-state taxonomy
- **Evidence attempted:** WAITING markers; incomplete empty-state taxonomy
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** WAITING markers; incomplete empty-state taxonomy
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.visual_defect — NOT_DONE
- **Requirement:** Tab gates: capture visual_defect
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** no structured visual defect list with screenshots in PR
- **Evidence attempted:** no structured visual defect list with screenshots in PR
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** no structured visual defect list with screenshots in PR
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.wiring_trace — DONE_PARTIAL
- **Requirement:** Tab gates: capture wiring_trace
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** tab_api_map.csv covers major; not every widget
- **Evidence attempted:** tab_api_map.csv covers major; not every widget
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** tab_api_map.csv covers major; not every widget
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.backend_endpoint — DONE_PARTIAL
- **Requirement:** Tab gates: capture backend_endpoint
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** mapped in lane B
- **Evidence attempted:** mapped in lane B
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** mapped in lane B
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.recommended_correction — DONE_PARTIAL
- **Requirement:** Tab gates: capture recommended_correction
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** waves in 12_; not per-tab complete
- **Evidence attempted:** waves in 12_; not per-tab complete
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** waves in 12_; not per-tab complete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R6.gates.mobile_responsive — NOT_DONE
- **Requirement:** Tab gates: capture mobile_responsive
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** desktop 1440 only
- **Evidence attempted:** desktop 1440 only
- **Location:** 02_LIVE_UI_22_TAB_SCORECARD.csv; lane_a_ui
- **Missing:** desktop 1440 only
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete missing evidence category
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R7.1 — DONE_PARTIAL
- **Requirement:** Trace READ-ONLY user journeys end-to-end
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** tab sequence via Playwright; not continuous journey script
- **Location:** lane_a_ui scorecard
- **Missing:** Instrument→expiry→CE/PE→signal→paper continuous journey
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Scripted journey on market day
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.1 — DONE_PARTIAL
- **Requirement:** Complete UI→API→backend→storage→GCP trace for important components
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** lane B matrix major tabs
- **Location:** 03_; lane_b FINDINGS
- **Missing:** Not every widget field
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Expand matrix per wave
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.C — DONE_PARTIAL
- **Requirement:** Find wiring class C: wrong API
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.F — DONE_PARTIAL
- **Requirement:** Find wiring class F: backend data UI blank
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.G — DONE_PARTIAL
- **Requirement:** Find wiring class G: healthy vs degraded
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.H — DONE_PARTIAL
- **Requirement:** Find wiring class H: tabs disagree
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.I — DONE_PARTIAL
- **Requirement:** Find wiring class I: hardcoded/demo
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.J — DONE_PARTIAL
- **Requirement:** Find wiring class J: stale cache
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.K — DONE_PARTIAL
- **Requirement:** Find wiring class K: race/hydration
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.L — DONE_PARTIAL
- **Requirement:** Find wiring class L: timeout
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.M — DONE_PARTIAL
- **Requirement:** Find wiring class M: duplicate polling
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.N — DONE_PARTIAL
- **Requirement:** Find wiring class N: legacy route
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.O — DONE_PARTIAL
- **Requirement:** Find wiring class O: optional dep
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.P — DONE_PARTIAL
- **Requirement:** Find wiring class P: missing timestamp
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.Q — DONE_PARTIAL
- **Requirement:** Find wiring class Q: missing provenance
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.R — DONE_PARTIAL
- **Requirement:** Find wiring class R: incorrect fallback
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.S — DONE_PARTIAL
- **Requirement:** Find wiring class S: partial map
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R8.2.T — DONE_PARTIAL
- **Requirement:** Find wiring class T: backend lacks UI fields
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** miswirings.csv examples
- **Location:** lane_b_wiring/miswirings.csv
- **Missing:** Exhaustive search not claimed
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Continue during remediation
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.12 — DONE_PARTIAL
- **Requirement:** GCP inspect: Scheduler recent execution evidence
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** list present; not all last-run deep
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Scheduler recent execution evidence incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.13 — DONE_PARTIAL
- **Requirement:** GCP inspect: Cloud Logging audit window
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** ERROR/429/timeout samples
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Cloud Logging audit window incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.14 — NOT_PROVEN
- **Requirement:** GCP inspect: broker failure logs
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** not systematically queried
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** broker failure logs incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.15 — NOT_DONE
- **Requirement:** GCP inspect: Cloud Monitoring uptime/incidents/alerts
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** no monitoring policy inventory
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Cloud Monitoring uptime/incidents/alerts incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.16 — DONE_PARTIAL
- **Requirement:** GCP inspect: IAM project+SA bindings vs baseline
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** SA names; not full binding dump vs baseline
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** IAM project+SA bindings vs baseline incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.17 — NOT_PROVEN
- **Requirement:** GCP inspect: temporary run.admin debt verify
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** not re-proven this session
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** temporary run.admin debt verify incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.18 — DONE_PARTIAL
- **Requirement:** GCP inspect: Secret Manager names/versions/IAM meta
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** names+versions; IAM meta partial
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Secret Manager names/versions/IAM meta incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.20 — DONE_PARTIAL
- **Requirement:** GCP inspect: Firestore
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** env SYSTEM3_STATE_BACKEND; not full inventory
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Firestore incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.21 — NOT_DONE
- **Requirement:** GCP inspect: GCS
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** no authoritative list query
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** GCS incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.22 — NOT_DONE
- **Requirement:** GCP inspect: Cloud SQL
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Cloud SQL incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.23 — NOT_DONE
- **Requirement:** GCP inspect: BigQuery
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** BigQuery incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.24 — NOT_DONE
- **Requirement:** GCP inspect: Memorystore
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Memorystore incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.25 — NOT_DONE
- **Requirement:** GCP inspect: Pub/Sub
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Pub/Sub incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.26 — NOT_DONE
- **Requirement:** GCP inspect: Cloud Tasks
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Cloud Tasks incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.27 — NOT_DONE
- **Requirement:** GCP inspect: Workflows
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Workflows incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R9.28 — NOT_DONE
- **Requirement:** GCP inspect: Eventarc
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** Not fully inventoried in audit window
- **Evidence attempted:** 
- **Location:** 04_GCP; lane_c_gcp
- **Missing:** Eventarc incomplete
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Complete read-only inventory
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.1 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: instrument master
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.2 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: equity quotes
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.3 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: index quotes
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.4 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: futures
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.5 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: option chains
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.6 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: OHLCV
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.7 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: tick/quote
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.8 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: OI
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.9 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: volume
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.10 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: IV
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.11 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: Greeks
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.12 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: India VIX
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.13 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: signals
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.14 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: predictions
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.15 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: actual outcomes
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.16 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: paper trades
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.17 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: paper PnL
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.18 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: broker positions
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.19 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: risk events
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.20 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: model features
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.21 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: training data
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.22 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: backtest data
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.23 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: validation data
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R10.24 — DONE_PARTIAL
- **Requirement:** Lineage map dataset: model artifacts
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** lane_e FINDINGS
- **Location:** 05_DATA_LINEAGE
- **Missing:** Not all schema/retention/DQ/version fields filled
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Fill lineage cells per dataset
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.strikes — DONE_PARTIAL
- **Requirement:** Prove NIFTY strikes
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.LTP — DONE_PARTIAL
- **Requirement:** Prove NIFTY LTP
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.bid — DONE_PARTIAL
- **Requirement:** Prove NIFTY bid
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.ask — DONE_PARTIAL
- **Requirement:** Prove NIFTY ask
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.OI — DONE_PARTIAL
- **Requirement:** Prove NIFTY OI
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.OI_change — DONE_PARTIAL
- **Requirement:** Prove NIFTY OI_change
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.volume — DONE_PARTIAL
- **Requirement:** Prove NIFTY volume
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.IV — DONE_PARTIAL
- **Requirement:** Prove NIFTY IV
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.Greeks — DONE_PARTIAL
- **Requirement:** Prove NIFTY Greeks
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.NIFTY.security_id_map — DONE_PARTIAL
- **Requirement:** Prove NIFTY security_id_map
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** weekend snapshot; field-level not fully extracted
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** weekend snapshot; field-level not fully extracted
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.symbol — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY symbol
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.expiry — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY expiry
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.contracts — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY contracts
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.strikes — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY strikes
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.CE — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY CE
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.PE — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY PE
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.LTP — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY LTP
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.bid — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY bid
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.ask — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY ask
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.OI — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY OI
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.OI_change — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY OI_change
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.volume — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY volume
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.IV — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY IV
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.Greeks — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY Greeks
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.source — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY source
- **Reason code:** CONTRADICTORY_EVIDENCE
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.observed_time — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY observed_time
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.freshness — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY freshness
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.market_session — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY market_session
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.backend_endpoint — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY backend_endpoint
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.security_id_map — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY security_id_map
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.BANKNIFTY.frontend_visibility — NOT_PROVEN
- **Requirement:** Prove BANKNIFTY frontend_visibility
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.symbol — NOT_PROVEN
- **Requirement:** Prove FINNIFTY symbol
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.expiry — NOT_PROVEN
- **Requirement:** Prove FINNIFTY expiry
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.contracts — NOT_PROVEN
- **Requirement:** Prove FINNIFTY contracts
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.strikes — NOT_PROVEN
- **Requirement:** Prove FINNIFTY strikes
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.CE — NOT_PROVEN
- **Requirement:** Prove FINNIFTY CE
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.PE — NOT_PROVEN
- **Requirement:** Prove FINNIFTY PE
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.LTP — NOT_PROVEN
- **Requirement:** Prove FINNIFTY LTP
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.bid — NOT_PROVEN
- **Requirement:** Prove FINNIFTY bid
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.ask — NOT_PROVEN
- **Requirement:** Prove FINNIFTY ask
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.OI — NOT_PROVEN
- **Requirement:** Prove FINNIFTY OI
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.OI_change — NOT_PROVEN
- **Requirement:** Prove FINNIFTY OI_change
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.volume — NOT_PROVEN
- **Requirement:** Prove FINNIFTY volume
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.IV — NOT_PROVEN
- **Requirement:** Prove FINNIFTY IV
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.Greeks — NOT_PROVEN
- **Requirement:** Prove FINNIFTY Greeks
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.source — NOT_PROVEN
- **Requirement:** Prove FINNIFTY source
- **Reason code:** CONTRADICTORY_EVIDENCE
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.observed_time — NOT_PROVEN
- **Requirement:** Prove FINNIFTY observed_time
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.freshness — NOT_PROVEN
- **Requirement:** Prove FINNIFTY freshness
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.market_session — NOT_PROVEN
- **Requirement:** Prove FINNIFTY market_session
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.backend_endpoint — NOT_PROVEN
- **Requirement:** Prove FINNIFTY backend_endpoint
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.security_id_map — NOT_PROVEN
- **Requirement:** Prove FINNIFTY security_id_map
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.FINNIFTY.frontend_visibility — NOT_PROVEN
- **Requirement:** Prove FINNIFTY frontend_visibility
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.symbol — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY symbol
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.expiry — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY expiry
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.contracts — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY contracts
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.strikes — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY strikes
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.CE — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY CE
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.PE — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY PE
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.LTP — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY LTP
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.bid — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY bid
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.ask — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY ask
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.OI — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY OI
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.OI_change — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY OI_change
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.volume — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY volume
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.IV — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY IV
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.Greeks — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY Greeks
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.source — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY source
- **Reason code:** CONTRADICTORY_EVIDENCE
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.observed_time — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY observed_time
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.freshness — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY freshness
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.market_session — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY market_session
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.backend_endpoint — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY backend_endpoint
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.security_id_map — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY security_id_map
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.MIDCPNIFTY.frontend_visibility — NOT_PROVEN
- **Requirement:** Prove MIDCPNIFTY frontend_visibility
- **Reason code:** BROKER_MARKET_CLOSED_LIMITATION
- **Plain reason:** concurrent fetch timeouts / weekend
- **Evidence attempted:** chain summary / UI text
- **Location:** 06_OPTION; 07_chain.txt
- **Missing:** concurrent fetch timeouts / weekend
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours four-chain proof
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.equity_chains — DONE_PARTIAL
- **Requirement:** Investigate equity option chains
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** MARKET_HOURS_REQUIRED
- **Evidence attempted:** code discovery OPTSTK; no live equity OC sample matrix
- **Location:** lane_d
- **Missing:** Live equity OC UI/API counts
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Sample ≥10 equity OCs live
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R11.full_expiries_underlyings — NOT_PROVEN
- **Requirement:** Full supported expiries/underlyings
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** underlyings API exists; counts not completed
- **Location:** openapi paths
- **Missing:** Full count matrix
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Universe count job
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R13.1 — DONE_PARTIAL
- **Requirement:** Complete Dhan request graph
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** MARKET_HOURS_REQUIRED
- **Evidence attempted:** lane_d call-site map
- **Location:** lane_d_market FINDINGS
- **Missing:** calls/min measured live
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Instrument metrics under load
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R13.2 — NOT_PROVEN
- **Requirement:** Reverify HTTP 429 on OHLC/quote/LTP
- **Reason code:** NO_LIVE_EVENT_OCCURRED
- **Plain reason:** NO_LIVE_EVENT_OCCURRED
- **Evidence attempted:** GCP 429 were capacity; Dhan 429 not proven this window
- **Location:** 10_PERFORMANCE; lane_c logs
- **Missing:** Direct Dhan 429 evidence
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Market-hours soak
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R14.1 — DONE_PARTIAL
- **Requirement:** Trace India VIX UI→API→Dhan
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** MARKET_HOURS_REQUIRED
- **Evidence attempted:** live_board wiring code + TopBar
- **Location:** lane_b FINDINGS
- **Missing:** Live VIX value freshness weekend
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** Capture live_board VIX during session
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R14.2 — NOT_PROVEN
- **Requirement:** NSE/BSE index coverage inventory
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** hardcoded index IDs in code
- **Location:** lane_d
- **Missing:** Full index list counts
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Master vs API count
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R15.1 — DONE_PARTIAL
- **Requirement:** Trace every prediction UI surface to model/heuristic
- **Reason code:** FEATURE_NOT_IMPLEMENTED
- **Plain reason:** FEATURE_NOT_IMPLEMENTED
- **Evidence attempted:** lane_f; ml tab
- **Location:** 07_PREDICTION
- **Missing:** artifact hash/calibration/outcomes incomplete
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Prediction ledger design
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R17.1 — DONE_PARTIAL
- **Requirement:** Historical data inventory equities/indices/FO/options
- **Reason code:** INSUFFICIENT_HISTORY
- **Plain reason:** INSUFFICIENT_HISTORY
- **Evidence attempted:** bhavcopy/local paths noted
- **Location:** 05_;08_
- **Missing:** Date coverage/missing sessions matrix
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** History inventory job
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R17.2 — DONE_PARTIAL
- **Requirement:** Backtest pipeline leakage/costs/slippage
- **Reason code:** BACKTEST_PIPELINE_NOT_FOUND
- **Plain reason:** BACKTEST_PIPELINE_NOT_FOUND
- **Evidence attempted:** flags MISSING institutional gates
- **Location:** 08_
- **Missing:** Deep leakage proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Wave 6 design
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R18.1 — DONE_PARTIAL
- **Requirement:** Paper lifecycle trace + separate from broker positions
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** MARKET_HOURS_REQUIRED
- **Evidence attempted:** paper API + positions tab; labels exist
- **Location:** api/paper; positions txt
- **Missing:** Full entry→exit→ledger journey market day
- **Owner:** MARKET_SESSION_AUTOMATION
- **Manual?** NO
- **Market hours?** YES
- **Next:** Paper lifecycle proof market day
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.1 — DONE_PARTIAL
- **Requirement:** Per-tab visual-information matrix
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** 09_ matrix 22 rows
- **Location:** 09_CHART_GRAPH
- **Missing:** Not every candidate chart category scored
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Expand chart backlog
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.candlestick — NOT_DONE
- **Requirement:** Consider visualization category: candlestick
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.volume — NOT_DONE
- **Requirement:** Consider visualization category: volume
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.OI — NOT_DONE
- **Requirement:** Consider visualization category: OI
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.change_OI — NOT_DONE
- **Requirement:** Consider visualization category: change_OI
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.CE_PE_OI — NOT_DONE
- **Requirement:** Consider visualization category: CE_PE_OI
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.PCR — DONE_PARTIAL
- **Requirement:** Consider visualization category: PCR
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.IV_smile — NOT_DONE
- **Requirement:** Consider visualization category: IV_smile
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.IV_skew — NOT_DONE
- **Requirement:** Consider visualization category: IV_skew
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.term_structure — NOT_DONE
- **Requirement:** Consider visualization category: term_structure
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.Greeks — NOT_DONE
- **Requirement:** Consider visualization category: Greeks
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.OI_heatmap — DONE_PARTIAL
- **Requirement:** Consider visualization category: OI_heatmap
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.max_pain — NOT_DONE
- **Requirement:** Consider visualization category: max_pain
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.pred_vs_actual — DONE_PARTIAL
- **Requirement:** Consider visualization category: pred_vs_actual
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.calibration — NOT_DONE
- **Requirement:** Consider visualization category: calibration
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.confusion — NOT_DONE
- **Requirement:** Consider visualization category: confusion
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.hit_rate — NOT_DONE
- **Requirement:** Consider visualization category: hit_rate
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.feature_importance — NOT_DONE
- **Requirement:** Consider visualization category: feature_importance
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.regime — NOT_DONE
- **Requirement:** Consider visualization category: regime
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.equity_curve — DONE_PARTIAL
- **Requirement:** Consider visualization category: equity_curve
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.drawdown — NOT_DONE
- **Requirement:** Consider visualization category: drawdown
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.paper_pnl — NOT_DONE
- **Requirement:** Consider visualization category: paper_pnl
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.trade_dist — NOT_DONE
- **Requirement:** Consider visualization category: trade_dist
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.latency — NOT_DONE
- **Requirement:** Consider visualization category: latency
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.freshness — DONE_PARTIAL
- **Requirement:** Consider visualization category: freshness
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.scheduler — NOT_DONE
- **Requirement:** Consider visualization category: scheduler
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** not explicitly scored
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.dhan_429 — DONE_PARTIAL
- **Requirement:** Consider visualization category: dhan_429
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R19.2.coverage — DONE_PARTIAL
- **Requirement:** Consider visualization category: coverage
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** mentioned in 09_ or waves
- **Location:** 09_
- **Missing:** Full justification+data existence proof
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** Include in Wave 7
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R20.1 — DONE_PARTIAL
- **Requirement:** Page content completeness per tab
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** executive + scorecard markers
- **Location:** 01_;02_
- **Missing:** Full BROKEN/MISWIRED taxonomy per tab
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** 
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R21.1 — DONE_PARTIAL
- **Requirement:** Desktop+mobile UX audit with screenshots
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** desktop screenshots only
- **Location:** lane_a_ui png
- **Missing:** Mobile viewport captures
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Mobile Playwright pass
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R22.1 — DONE_PARTIAL
- **Requirement:** Perf/network major endpoints
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** openapi 182; poller list; capacity 429
- **Location:** 10_
- **Missing:** payload sizes/calls per minute
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** YES
- **Next:** HAR + metrics
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R23.1 — DONE_PARTIAL
- **Requirement:** Observability matrix events
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** GCP_RESOURCE_NOT_FOUND
- **Evidence attempted:** table in 10_
- **Location:** 10_
- **Missing:** Alert policies / notification proof
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Inventory Monitoring policies
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R24.2 — DONE_PARTIAL
- **Requirement:** Runtime-affecting vs proof-only SHA
- **Reason code:** INSUFFICIENT_EVIDENCE
- **Plain reason:** INSUFFICIENT_EVIDENCE
- **Evidence attempted:** drift noted; commit classified likely proof-oriented
- **Location:** 00_MANIFEST; F-001
- **Missing:** File-level runtime delta a48e7b3..c763ecf
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** git diff deploy paths
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R25.1 — NOT_DONE
- **Requirement:** Compare actual IAM to baseline+authority matrix
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** SA names only; no full binding compare
- **Location:** 04_; lane_c
- **Missing:** Full IAM dump vs system3_iam_baseline.json
- **Owner:** CURSOR
- **Manual?** NO
- **Market hours?** NO
- **Next:** Read-only IAM forensic pass
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R26.1 — NOT_PROVEN
- **Requirement:** Recheck hypothesis: Dhan 429 OHLC
- **Reason code:** NO_LIVE_EVENT_OCCURRED
- **Plain reason:** incomplete evidence
- **Evidence attempted:** 01 hypothesis table
- **Location:** 01_EXECUTIVE
- **Missing:** 
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** 
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R26.3 — NOT_PROVEN
- **Requirement:** Recheck hypothesis: India VIX unavailable
- **Reason code:** MARKET_HOURS_REQUIRED
- **Plain reason:** incomplete evidence
- **Evidence attempted:** 01 hypothesis table
- **Location:** 01_EXECUTIVE
- **Missing:** 
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** YES
- **Next:** 
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## R27.1 — DONE_PARTIAL
- **Requirement:** Root-cause loop for every material issue
- **Reason code:** TIME_BUDGET_LIMITATION
- **Plain reason:** TIME_BUDGET_LIMITATION
- **Evidence attempted:** master finding table fields
- **Location:** 00_MASTER_FINDING_TABLE
- **Missing:** Not every P2/P3 full 15-step loop
- **Owner:** CHATGPT
- **Manual?** NO
- **Market hours?** NO
- **Next:** 
- **Fresh proof after:** YES if status changes to DONE_AND_EVIDENCED claim

## Manual / break-glass candidates (conservative)

### M-001 — dhan-totp-secret DESTROYED v8 (F-016)
- **Why automation cannot (yet):** Secret payload recreation / linking `latest` to a valid ENABLED version may require owner access to Secret Manager or Dhan TOTP seed that agents must not print/chat.
- **Platform:** GCP Secret Manager `dhan-totp-secret` + Dhan authenticator
- **Screen/account:** GCP Console secrets / Dhan app TOTP
- **Risk if not done:** Next scheduled/manual token rotate fails even while current access-token v257 still works
- **Can System3 continue?** YES short-term (broker connected now); NO for reliable daily mint
- **Minimum user action:** Ensure an ENABLED TOTP secret version exists and `latest` alias points to it (do not paste secret in chat). Optionally confirm PIN still valid.
- **Responsible party:** USER_BREAK_GLASS_ACTION_REQUIRED (secret material) + CURSOR/GCP after for read-only verify
- **Afterward:** ONE guarded recovery/rotate proof; `/api/broker/status` connected; no LIVE

### M-002 — None other elevated to break-glass
Routine IAM inventory, Monitoring list, mobile screenshots, universe counts → **CURSOR/CHATGPT/automation**, not user.
