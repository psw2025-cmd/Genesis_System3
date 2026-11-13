# System3 User-Selectable Solution Matrix

**Purpose:** Persistent decision register for major data, model, automation and
dashboard choices. This is not permission to enable LIVE trading or real orders.

## Current recommended sequence

| Domain | Recommended default | Faster/lower-cost option | Higher-capability challenger | Promotion gate |
|---|---|---|---|---|
| Historical lake | Incremental Dhan instrument/candle/chain-snapshot lake with immutable raw data, manifests and resume | Daily candles + selected liquid F&O universe | Licensed tick/depth and full-chain snapshot lake | coverage, gap, checksum, lineage and replay proof |
| CE/PE prediction | Tree/tabular baseline using point-in-time chain/candle features and calibrated abstention | Rules/logistic baseline | Temporal/foundation or LOB model only after sufficient history | same-window costed OOS win by CE/PE, expiry and regime |
| Equity ranking | Linear + boosted-tree cross-sectional baselines | Existing heuristic with calibrated uncertainty | TSFM/temporal ensemble challenger | survivorship-safe OOS net ranking value |
| Multibagger | Long-horizon cross-sectional fundamentals + price/quality/momentum baseline | Transparent factor score | multimodal/foundation challenger with licensed point-in-time data | multi-year walk-forward, drawdown, calibration and sector/regime robustness |
| Retraining | Scheduled bounded challenger evaluation; manual/PAPER promotion gates | Recalibration only | Automated registry promotion with rollback after long PAPER proof | drift trigger, reproducibility, champion delta and rollback test |
| Dashboard | Truth-first dense 2D desktop workspace derived from user references | Improve existing tabs incrementally | Optional 3D IV surface and advanced linked views | accessibility, performance and same-session UI/API proof |
| Operations | GitHub PR/CI -> guarded Cloud Run candidate -> exact-SHA proof | Manual read-only audit | Expanded observability/traces/SLO automation | preflight, exact-head CI, revision/traffic/log and browser trace proof |

## Laptop-to-cloud operating decision

| Concern | Selected default |
|---|---|
| Laptop role | Read-only inventory and authorized upload/intake only |
| Raw data | Preserve original bytes in governed cloud object storage |
| Analytical format | Parquet for large typed tables; CSV for compact interchange |
| Git repository | Code, schemas, manifests, hashes and compact proofs only |
| Compute | Reproducible cloud jobs for parsing, features, training and backtests |
| PAPER start | Begin forward observation immediately after historical gates; no arbitrary idle wait |
| Promotion | Historical plus required forward PAPER evidence; never time-window relabeling |
| Learning | Immutable challenger retraining/recalibration; no in-place champion weight mutation |
| Safety | ANALYZE/PAPER only; LIVE and real orders remain disabled |
| MRI scan | DATA -> MODEL -> VALIDATION -> PAPER -> IMPROVEMENT plus lineage/API/UI/governance nodes |

## Data and compute failover decisions

| Concern | Recommended default | Fail-closed rule |
|---|---|---|
| Live Indian market authority | Dhan API/WebSocket | Alternative sources never masquerade as Dhan/live broker truth |
| Dhan unavailable | Classify/recover Dhan, preserve last verified snapshot as labeled historical/replay | No synthetic or unlabeled provider substitution |
| Research backfill | Evaluate licensed Kaggle, Yahoo Finance or Nasdaq Data Link datasets separately | Recheck availability/license/lineage and Indian-market coverage at use time |
| Training compute | CPU baseline first; GCP GPU when profiling proves value; TPU only when compatible and beneficial | Quota, cost ceiling, deterministic data/checkpoints and cleanup required |
| Cloud failure | Cloud retry/failover, then smaller cloud CPU | Laptop CPU is bounded last resort, never production/PAPER serving |
| Artifact synchronization | Immutable cloud object/model versions plus hashes | No blind two-way sync or in-place champion overwrite |
| PAPER latency | Measure p50/p95/p99; target p95 tick-to-observation under 1s for supported WebSocket feed | Option-chain REST cadence is separate; no HFT/real-order inference |

## Indian catalyst-source decisions

| Source/category | Recommended role | Exclusion/gate |
|---|---|---|
| NSE/BSE/SEBI/RBI releases | Official event/corporate-action/policy truth with dissemination-time lineage | Use sanctioned access and preserve revisions/document hashes |
| Moneycontrol/ET Markets | Licensed editorial catalyst context | No scraping/paywall bypass; exclude when ML/non-display rights are unclear |
| TradingView India | Manual display/community research only by default | Published terms prohibit automated collection/non-display algorithmic use without separate license |
| Finshots/Zerodha Varsity | Educational macro/event taxonomy | Not automatically a live catalyst feed or model label |
| Unusual volume/OI/volatility | Compute from Dhan timestamps | Label as derived technical catalyst, not news |
| Catalyst model | Separate volatility and directional-bias challengers with abstention | Point-in-time leakage tests and price-only ablation required |

## Paid data and AI connector decisions

| Requested connector | Safe supported interpretation | Activation gate |
|---|---|---|
| Bloomberg | Exact licensed enterprise data product and fields | Contract, entitlement, delivery method and non-display/ML rights proven |
| TradingView | Manual/display research by default | Automated model ingestion disabled without a separate written license |
| Nasdaq Data Link/Quandl | Dataset-specific research benchmark | Dataset entitlement, point-in-time lineage and Indian coverage proven |
| OpenAI / “ChatGPT Finance” | Official API NLP extraction/research challenger | Backend-only secret, pinned model, citations and same-input evaluation; never market authority |
| Gemini | Official Gemini API or Vertex AI NLP challenger | Backend identity, region/privacy review and pinned evaluation |
| Claude | Official API or authorized cloud NLP challenger | Backend identity, retention/privacy review and pinned evaluation |
| Perplexity | Official API research/search challenger | Independently verify cited primary sources |
| DeepSeek | Official API NLP challenger | Current terms, region, privacy, retention and security review |
| GitHub Copilot / “Copilot Finance” | Engineering orchestration and diagnostics | Not a finance feed, broker authority or prediction benchmark |
| Google Finance | No general API assumed | Remains `CONNECTOR_NOT_PROVEN` until a suitable official API is documented |

The public dashboard shows read-only connector state and sanitized health. Raw
credentials are configured only through an authenticated admin path backed by
Google Secret Manager or OAuth/WIF. Connector activation stays PAPER-only and
uses normal branch/PR/CI/deployment proof; it cannot hot-patch production or
enable LIVE trading/orders.

An authenticated admin view may offer `Connect with OAuth` only for an exact
provider/product with a documented authorization-code flow. The backend uses
PKCE, single-use state/nonce, exact scopes, allowlisted HTTPS callbacks and
server-side token exchange; the browser receives only an opaque connection ID
and sanitized status. API-key-only products route setup directly to Secret
Manager. Unsupported OAuth is displayed as unavailable, never emulated.

## MRI concern-list contract

Before its first commit, every MRI execution publishes Markdown and JSON concern
lists under `reports/latest/mri/`. Material concerns include reason, impact,
evidence, recommended fix, alternatives, acceptance test, owner and next action.
The agent continues safe routine work after reporting and waits only for a real
account, authorization, licensing, billing, destructive or LIVE/order decision.

Unresolved concerns are re-reported at transitions or material state changes,
not duplicated on a timer. Every genuine user-owned blocker receives a
secret-safe Next Action Plan with exact environment, command when applicable,
expected output, verification and rollback.

## Reference-folder findings (2026-08-24)

The user folder contains 13 PNG files, representing 10 unique hashes and three
byte-identical duplicate pairs. Useful design themes:

- persistent single-truth/deployment/broker/feed/freshness strip;
- four-index summary cards;
- complete option table with OI, IV, Greeks, PCR and max pain;
- IV/Greeks surfaces, heatmaps and model/accuracy monitoring;
- explicit layered data/orchestration/model/visualization architecture;
- side-by-side engineering console and dashboard proof.

Rejected as technical authority:

- “quantum,” “beyond quantum,” “MRI,” “entanglement” and HFT claims without a
  real implemented method and measured incremental evidence;
- “99.9%,” “100% confidence,” “world highest,” guaranteed multibagger, or maximum
  success language;
- generated prices, model outputs, broker states and pipeline-complete badges;
- LIVE/automatic execution implied by artwork.

The text reference `FOR_INFO_FOR_IMPROMENT.txt` is 20,120 bytes, SHA-256
`C70E3604A18F7EFE5A72A2CC3E686B17E09FDDC17EE35ED31E1D15CBD6203B31`, and
ends mid-URL. It is retained as an incomplete advisory input. Adopted controls
include a fail-closed readiness dependency DAG, a non-mutating production
sentinel, WIF-only deployment provenance, sole-deployer/split-brain detection,
artifact-digest-to-revision mapping, data-integrity semantics and immutable
PAPER lifecycle reconciliation. Its issue statuses, priorities, automation
percentages and example deployment narratives require fresh verification.

## Decision-record template

| Field | Value |
|---|---|
| Decision ID/date/owner | |
| Current proven state | |
| Gap and user outcome | |
| Recommended option | |
| Alternatives | |
| Data/license/account dependencies | |
| Engineering/cloud cost | |
| Risk and rollback | |
| Acceptance metrics | |
| Evidence links and observation time | |
| User decision genuinely required | YES/NO + reason |
| Status | PROPOSED/SELECTED/IMPLEMENTING/PAPER_PROVEN/REJECTED |

## Runbook governance recommendation ledger

Verdicts are refreshed from authoritative evidence and include an evidence UTC;
stored rows are historical after capture. `PASS`, `FAIL`, `PARTIAL`, and
`BLOCKED` are the only allowed states.

| ID | Recommended primary solution | Alternative | Current implementation verdict |
|---|---|---|---|
| R01 | Full GitHub Actions-to-Artifact Registry-to-Cloud Run digest chain | Cloud Build ID/source checksum/artifact chain | PARTIAL pending per-transition evidence |
| R02 | Versioned 12-row evidence ledger | Deduplicated blocker cards | PASS contract implemented |
| R03 | One WIF GitHub production writer | One governed Cloud Build writer | PARTIAL until all triggers are freshly inventoried |
| R04 | Branch + environment protection and least-privilege WIF | Exact workflow/ref-bound WIF where environment controls are unavailable | PARTIAL; account configuration requires live proof |
| R05 | Read-only schema-versioned dashboard backed by immutable Cloud Storage | BigQuery append-only audit tables plus versioned Cloud Storage | PASS contract; runtime implementation separately gated |
| R06 | Dedicated Dhan rotator/scheduler with metadata-only audit | Bounded authenticated recovery authority | PASS contract; never invent refresh-token behavior |
| R07 | Four-timestamp immutable PAPER reconciliation | Offline versioned-export audit | PASS contract; PAPER is not real execution |
| R08 | p50/p95/p99/max plus drop/reconnect/stale metrics | Bounded replay/load measurement | PASS contract |
| R09 | pytest property/state-machine/fault injection first | Locust bounded load; Chaos Mesh only for governed Kubernetes | PASS contract |
| R10 | JSON Schema v4 with migrations and compatibility gates | Bounded compatibility reader | PASS contract |
| R11 | Observer detects/freezes; separate guarded IAM workflow repairs | Audit-log function detects/queues only | PASS contract |
| R12 | Full-SHA-pinned actions and minimum workflow permissions | First-party pinned scripts/toolchain | PARTIAL until every workflow is scanned |

Each execution replaces the final column with evidence-backed status,
`evidence_time_utc`, source identities, owner, blocker and next action. Contract
implementation does not by itself prove GitHub/GCP/runtime configuration.
