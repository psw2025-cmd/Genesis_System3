#!/usr/bin/env python3
"""Build the initial evidence-first System3 mission package. LOCAL/GitHub ONLY.

Run once on an isolated branch. Refuses to overwrite existing master/evidence.
The diagram images are architectural representations, NOT screenshots of GCP.
No network, broker, secrets, orders, or cloud mutation.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HOME=ROOT/"SYSTEM3"
BASE="1dbae834605b7cbabd57eda82a9db182deb0822c"
NOW=datetime.now(timezone.utc).isoformat()
ISSUE="https://github.com/psw2025-cmd/Genesis_System3/issues/480"
def put(path,contents):
    target=HOME/path
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        raise FileExistsError("INITIALIZE_ONLY_REFUSE_OVERWRITE:"+str(target))
    target.write_text(contents,encoding="utf-8",newline="\n")
    print("CREATED",target.relative_to(ROOT))

master={
 "schema":"system3-master-state-v1","updated_at_utc":NOW,
 "repo":"psw2025-cmd/Genesis_System3","baseline_main_sha":BASE,
 "working_branch":"fix/system3-phase02-production-ui-truth-20261018",
 "main_merge_verification":"PENDING",
 "current_phase":"0.2_GITHUB_REPAIR",
 "phase_status":{"0":"PASS","0.1":"PASS","0.2":"UNKNOWN","0.3":"UNKNOWN",
 "0.4":"PASS","0.5":"UNKNOWN","1":"UNKNOWN","2":"UNKNOWN","3":"PASS",
 "4":"UNKNOWN","5":"UNKNOWN","6":"BLOCKED","8":"BLOCKED","9":"UNKNOWN",
 "10":"UNKNOWN","11":"UNKNOWN","12":"UNKNOWN","13":"UNKNOWN","14":"UNKNOWN"},
 "overall":"BLOCKED","production":"UNKNOWN",
 "source_truth":{"main_baseline":BASE,"phase0_1_root_cause":"PASS",
 "last_cloud_inventory":{"project":"system3-openalgo-safe",
 "observation_time_utc":"2026-10-18T03:22:00Z",
 "cloud_run_service":"MISSING","cloud_run_jobs":"MISSING","mumbai_scheduler":"MISSING",
 "refresh_required":True}},
 "blocker_ids":["B-001","B-002","B-003","B-004","B-005","B-006","B-007"],
 "evidence":[{"type":"GITHUB_COMMIT","url":"https://github.com/psw2025-cmd/Genesis_System3/commit/"+BASE},
 {"type":"GITHUB_ISSUE","url":ISSUE},
 {"type":"GITHUB_RUN","url":"https://github.com/psw2025-cmd/Genesis_System3/actions/runs/39093854945"}],
 "architecture_state":{"production_image":"UNKNOWN",
 "canonical_candidate_dockerfile":"dashboard/backend/Dockerfile",
 "legacy_root_dockerfile":"NONPRODUCTION",
 "deployment_workflow":"MISSING","approved_deployment_lineage":"MISSING",
 "broker_worker":"UNKNOWN","tracing":"UNKNOWN","observability":"PARTIAL_CODE"},
 "decisions":["ADR-001","ADR-002","ADR-003","ADR-004"],
 "owner_action_required":"NONE_NOW",
 "approval_boundary":"Explicit separate bounded consent before billable GCP changes",
 "safety":{"ANALYZE_MODE":"1","PAPER_MODE":"1","LIVE_TRADING_ENABLED":"0",
 "SYSTEM3_LIVE_TRADING_ALLOWED":"0","AUTO_EXECUTE_TRADES":"0",
 "LIVE_ORDER_AUTHORITY":"0","ORDER_PLACEMENT_ALLOWED":"false",
 "real_orders":"UNKNOWN_NO_INDEPENDENT_BROKER_HISTORY"},
 "next_actions":["Run exact-head PR CI for restored verifier",
 "Implement manually gated deployment candidate without executing it",
 "Add independent runtime and broker verification after owner approval"]
}
put(Path("01_MASTER_STATE/SYSTEM3_MASTER_STATE.json"),json.dumps(master,indent=2,sort_keys=True)+"\n")
events=[
 ("phase0","PASS","Current main branch SHA matched branch and Git ref; merged PRs 479,477,481 verified",
  "https://github.com/psw2025-cmd/Genesis_System3/commit/"+BASE),
 ("phase0.1","PASS","Historical source removed by commit 60034500 on 2026-09-05; retained workflow caused ENOENT",
  "https://github.com/psw2025-cmd/Genesis_System3/commit/60034500b52ba7a7ff8a12eb10cf99e3dd6a10aa"),
 ("main-security","PASS","Security Audit Evidence concluded success with npm 0 reported in log",
  "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/39093854999"),
 ("main-local-22-tabs","PASS","Local Chrome 22 canonical tabs/screenshots and Global Safety CI passed",
  "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/39093854982"),
 ("main-live-ui","FAIL","Actual CI exit 2 due missing scripts/gcp_live_ui_snapshot.py; not a runtime HTTP proof",
  "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/39093854945"),
 ("cloud-production","UNKNOWN","Historical read-only inventory saw zero Cloud Run services/jobs/scheduler; independent fresh deployment proof missing",
  ISSUE),
 ("order-safety","UNKNOWN","Application policy locks checked in code; broker order history not independently queried",ISSUE),
 ("phase0.2","UNKNOWN","Historical proof restored with expected blob before modernization; exact-head CI has not yet completed",ISSUE)]
with (HOME/"02_EVIDENCE/EVIDENCE.ndjson").open("x",encoding="utf-8",newline="\n") as out:
    for id,status,claim,url in events:
        out.write(json.dumps({"schema":"system3-evidence-v1","id":id,
         "recorded_at_utc":NOW,"status":status,"claim":claim,
         "evidence_url":url,"source_sha":BASE},sort_keys=True)+"\n")
print("CREATED SYSTEM3/02_EVIDENCE/EVIDENCE.ndjson APPEND_ONLY")
put(Path("04_OWNER/OWNER_STATUS.md"),f"""# System3 owner status
Updated: {NOW}
**Current Status:** Phase 0.2 repair in GitHub; production still BLOCKED.
**Overall Health:** GitHub security/governance PASS; existing main-only production proof FAIL.
**Owner Action Required:** NONE NOW. No console, terminal or troubleshooting action.
**Next Step:** Agent validates restored proof and prepares a manual-only, tested release candidate. Later request separate approval for potentially billable cloud operations.
**Safety:** PAPER/ANALYZE only. Application policy denies LIVE; actual broker-side count of real orders is UNKNOWN, not falsely certified zero.
Tracked blocker: {ISSUE}
""")
put(Path("05_AGENT_MEMORY/AGENT_MEMORY.md"),f"""# Agent memory — read before each action
1. Scope ONLY psw2025-cmd/Genesis_System3 / GCP system3-openalgo-safe; never mix Angel F&O.
2. Phase 0 repository and 0.1 root cause were independently verified; do not repeat absent new contradictory evidence.
3. PR #462 merge 60034500b52ba7a7ff8a12eb10cf99e3dd6a10aa deleted the original GCP proof; frontend workflow still referenced deleted file. Textual presence tests did not check file existence.
4. PRs #479, #477 and #481 were merged. Baseline main SHA {BASE}.
5. Current main frontend job 39093854945 local 22 tabs PASS, live proof failed ENOENT before sending a request.
6. Previous auto-deploy workflow was purged; never restore its automatic push-to-production behavior. Root Dockerfile legacy NONPRODUCTION; canonical candidate dashboard/backend/Dockerfile, repository-root context.
7. Do NOT infer production health from CI, historical artifacts, GitHub source or WIF provider presence.
8. Retain historical snapshot read-only exact SHA, 22 UI tabs, Dhan NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY subview checks, and independent beginning/end API provenance. Never substitute local/mock.
9. Broker order-count zero is UNKNOWN absent independent broker history. Application LIVE switches are documented locks only.
10. OWNER is nontechnical: do all permitted GitHub engineering. Ask only explicit legal/credential/budget/approval necessities.
11. Source snapshots, output hashes and UTC timestamps must be named; NDJSON evidence is append-only.
12. Owner approval never inferred from repository files. Billable GCP deployments/configuration require separate explicit consent.
""")
put(Path("06_BLOCKERS/BLOCKERS.yaml"),"""schema: system3-blockers-v1
updated_at_utc: '"""+NOW+"""'
blockers:
  - id: B-001
    severity: P0
    owner: agent
    status: UNKNOWN
    root_cause: Deleted production UI proof referenced by active workflow
    fix_strategy: Restore historical script, enforce exact SHA, add lineage gate and missing-target tests
    verification: Exact-head GitHub CI and missing-receipt negative tests
  - id: B-002
    severity: P0
    owner: agent
    status: BLOCKED
    root_cause: Manual-only deployment implementation absent since historical GCP purge
    fix_strategy: Build isolated workflow, candidate/rollback package and static no-mutation tests
    verification: Zero deployment triggers on push; canonical Dockerfile and deny-by-default tested
  - id: B-003
    severity: P0
    owner: owner
    status: BLOCKED
    root_cause: Billable cloud mutation consent not granted
    fix_strategy: Seek one bounded owner approval only after deployment candidate independently PASS
    verification: Explicit separate authority receipt
  - id: B-004
    severity: P0
    owner: agent_after_approval
    status: UNKNOWN
    root_cause: Serving System3 Cloud Run resource not independently proven
    fix_strategy: Approved zero-traffic candidate then exact revision/digest/health and rollback proof
    verification: Fresh project-scoped cloud inventory and same-revision API receipts
  - id: B-005
    severity: P0
    owner: agent_after_approval
    status: UNKNOWN
    root_cause: Broker, scheduler, worker, heartbeat and PAPER lifecycle lack current runtime proof
    fix_strategy: Verify read-only broker, market freshness, fenced worker and durable ledger during market session
    verification: UTC receipts and independent reconciliation
  - id: B-006
    severity: P0
    owner: agent_after_approval
    status: UNKNOWN
    root_cause: Independent broker-side order history not inspected
    fix_strategy: Obtain authorized read-only broker order-history evidence without any order creation
    verification: Independent actual-order reconciliation
  - id: B-007
    severity: P1
    owner: agent
    status: UNKNOWN
    root_cause: Full telemetry/FinOps/failure injection and paper prediction statistics not verified
    fix_strategy: Tests and independently measured runtime evidence; no synthetic production claims
    verification: Traces, SLO, cost, walk-forward and chaos receipts
""")
put(Path("07_DECISIONS/DECISIONS.md"),f"""# Architecture decision log (append new numbered ADRs, never delete history)
**ADR-001 — 2026-10-18 — Cloud-only runtime.** System3 GCP { 'system3-openalgo-safe' } is target; desktop only transient engineering control. Supersedes laptop-only historical #462.
**ADR-002 — 2026-10-18 — Owner deployment boundary.** GitHub coding/testing/read-only GCP permitted; billable infrastructure and production mutations require separate scoped approval. No push-to-deploy.
**ADR-003 — 2026-10-18 — Proof identity.** A committed receipt is only an expected-source hint; production PASS requires independently retrieved start/end actual serving SHA, immutable digest and live UI/API semantics. Never assume current main equals deployed SHA.
**ADR-004 — 2026-10-18 — Evidence truth.** Four verdicts PASS/FAIL/BLOCKED/UNKNOWN. Code flags cannot establish independent broker real_orders=0. Historical evidence stays historical. EVIDENCE.ndjson append-only.
""")
put(Path("03_ARCHITECTURE/DEPLOYMENT_ARCHITECTURE.md"),"""# Deployment architecture — proposed, not deployed
Owner-approved source SHA -> manual workflow_dispatch (NO push/schedule) -> OIDC/WIF -> Cloud Build canonical dashboard/backend/Dockerfile -> Artifact Registry digest -> zero-traffic Cloud Run candidate -> independent proof -> owner-bounded traffic promotion -> rollback to prior known-good revision. Current deploy implementation: MISSING. No cloud commands authorized.
""")
put(Path("03_ARCHITECTURE/RUNTIME_ARCHITECTURE.md"),"""# Runtime architecture — candidate, NOT LIVE
Cloud Run secure_app read-only web/API + separately owned fenced PAPER worker + scheduler + Firestore state/append-only evidence + Dhan read-only API. Heartbeat/cache/SLO/telemetry must be proved after approved deployment; no current deployed health claim.
""")
put(Path("03_ARCHITECTURE/CICD_ARCHITECTURE.md"),"""# CI/CD
PR -> compile/negative tests/security/CodeQL/22 local browser tabs -> governed merge -> separately owner-authorized manual candidate build. Main-only production proof must stay FAIL/BLOCKED if no source-lineage receipt or serving service. A workflow that returns success after only writing a BLOCKED report must never be named production PASS.
""")
put(Path("03_ARCHITECTURE/ROLLBACK_ARCHITECTURE.md"),"""# Rollback architecture
Before future approved promotion: capture currently serving revision + immutable image digest and traffic splits, or explicitly record no baseline. Deploy candidate with zero traffic. Independently verify. On failure: do not promote; if promoted and failed, revert to actual recorded previous healthy revision (never invent one). All cloud actions require separate scoped approval.
""")
put(Path("08_REPORTS/GITHUB_REPAIR_REPORT.md"),f"""# Phase 0.2 GitHub repair report
Root cause Phase 0.1 PASS: removed at commit 60034500; retained workflow referenced deleted verifier.
Historical script restored from Git blob b3d15032363892c27603c853da3a55fc44a6ff27 to isolated branch, with strict 40-hex SHA comparison.
Added scripts/system3_release_proof_gate.py; absent approved DEPLOYMENT_LINEAGE.json must emit BLOCKED immediately; a receipt never constitutes proof of current serving production.
Workflow now compiles restored script and tests missing-reference conditions. Phase 0.2 exact-head GitHub CI: **UNKNOWN until actual run completes**. No GCP mutation.
""")
put(Path("08_REPORTS/ARCHITECTURE_DISCOVERY_REPORT.md"),"""# Phase 0.3 architecture discovery
Observed: dashboard/backend/Dockerfile candidate, scripts/start_cloud_run.py, secure_app, Firestore state backend and tests. Removed auto-deploy workflow/impl and gcp_live_ui_snapshot in #462. Root Dockerfile marked nonproduction in #481. Canonical build, owner-gated manual deploy, rollback and production runtime integration still require tests. Runtime topology remains UNKNOWN/NOT DEPLOYED, not PASS.
""")
put(Path("08_REPORTS/EVIDENCE_MATRIX.md"),"""# Phase 0.4 evidence inventory
| Evidence | Classification | Status |
|---|---|---|
| GitHub repo/main SHA/merged PRs | VERIFIED | PASS |
| Main CI code/security/22 local tabs | VERIFIED | PASS |
| Historical snapshot deletion + workflow dangling reference | VERIFIED | PASS |
| Existing snapshot on original main | MISSING | FAIL |
| New Phase 0.2 exact-head CI | UNKNOWN | UNKNOWN |
| Manual-only deployment implementation | MISSING | BLOCKED |
| Approval for GCP mutation | BLOCKED | BLOCKED |
| Actual serving image/worker/scheduler/broker health | UNKNOWN | UNKNOWN |
| Broker-side real-order history | UNKNOWN | UNKNOWN |
| Complete live 22-tab/GCP proof | BLOCKED | BLOCKED |
""")
put(Path("08_REPORTS/RECOVERY_BLUEPRINT.md"),"""# Phase 0.5 recovery blueprint
| Blocker | Root cause | Fix | Verification | Expected result |
|---|---|---|---|---|
| B-001 | Deleted verifier/dangling workflow | Restore+modernize script, gate and tests | Exact-head CI + negative test | Code proof PASS, live proof BLOCKED pending deploy |
| B-002 | Removed auto-deploy path | Implement manual-only candidate with immutable digest + rollback | Static CI cannot execute without approval | Candidate reviewed |
| B-003 | Owner consent absent | Separate scoped approval after candidate PASS | Explicit receipt | Authorized bounded change only |
| B-004 | No serving service | Future approved candidate | Serving SHA/digest/revision | Real runtime proof |
| B-005 | No broker/worker proof | Read-only market-session verifier, lease, heartbeat, ledger | Independent UTC reconciliation | PAPER runtime proof |
| B-006 | No independent broker history | Authorized read-only order-history inspection | Broker-side reconciliation | Actual-order verdict |
| B-007 | Insufficient reliability/analytics | OTel/SLO/FinOps/walk-forward/failure injection | Measured source-backed receipts | Reliable phase gates |
""")
put(Path("08_REPORTS/SAFETY_CERTIFICATION_REPORT.md"),"""# Phase 1 safety verification
Policy targets: ANALYZE_MODE=1, PAPER_MODE=1, LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0, AUTO_EXECUTE_TRADES=0, LIVE_ORDER_AUTHORITY=0, ORDER_PLACEMENT_ALLOWED=false.
Source policy and GitHub safety tests at baseline main: PASS. Current candidate retest: UNKNOWN.
Actual deployed environment: UNKNOWN (no current running service receipt).
Independent broker-side real_orders=0: UNKNOWN, MUST NEVER mark PASS from source flags or absence of a deployed service.
Overall phase-1 production safety certification: UNKNOWN until runtime and independent broker data.
""")
put(Path("08_REPORTS/FOUNDATION_AUDIT.md"),"""# Phase 2 foundation audit
Source security audit on baseline main: PASS, npm vulnerabilities reported 0 (run 39093854999); CodeQL PASS (39093854938).
Dependencies/lockfile: source present; canonical candidate image has NOT been built/tested as approved release. Workflow safety: global CI PASS baseline. GCP WIF metadata historical read-only observed, not successful exchange proof. Secret **values** not inspected; validity UNKNOWN. Containers/policies static only. Overall deploy foundation: BLOCKED by manual-only workflow, lineage and consent.
""")
put(Path("08_REPORTS/DIGITAL_TWIN_REPORT.md"),"""# Phase 3 digital twin
Ten diagram PNGs in 09_DIAGRAMS are explicitly conceptual/source-grounded, NOT screenshots or production deployment evidence. Graph nodes label unverified Cloud Run/worker/telemetry as UNKNOWN/BLOCKED. Maps: Architecture, DependencyGraph, RiskHeatmap, RootCauseGraph, DeploymentGraph, DigitalTwin, DataLineage, ServiceMap, APIMap.
""")
put(Path("08_REPORTS/DEPENDENCY_INTELLIGENCE_REPORT.md"),"""# Phase 4 dependency intelligence
Upstream: owner bounded authority -> exact merged SHA -> CI -> approved build -> immutable digest -> Cloud Run & job/scheduler -> Dhan session and exchange data. Downstream: worker -> Firestore artifacts/lease -> read-only API -> 22-tab UI -> independent evidence.
Failure cascade: missing verifier -> main workflow exits 2 before HTTP; missing approval -> no candidate build; absent worker -> stale/absent broker & paper records; mismatched SHA -> no production proof; stale lease/duplicate owner -> quarantine.
Blast radius: CI-only negative tests cannot mutate cloud. LIVE/order route remains separately denied; no broker-side zero-order evidence.
""")
put(Path("08_REPORTS/OBSERVABILITY_PACKAGE.md"),"""# Phase 5 observability status
Spider Web (OpenTelemetry): end-to-end trace UNKNOWN. Heartbeat: source loop exists; cloud pulse UNKNOWN. Blood Pressure: broker latency source exists; unified queue/SLO UNKNOWN. Synapse: Firestore schema and route capability checks CODE_PRESENT; deployed consumer parity UNKNOWN. Immune System: local-oriented self-heal handlers CODE_PRESENT; cloud watchdog UNKNOWN. No fabricated measurements. Cloud deployment needed for runtime validation.
""")
put(Path("08_REPORTS/DEPLOYMENT_CANDIDATE_REPORT.md"),"""# Phase 6 release candidate — BLOCKED
Historical auto deploy was intentionally removed. Manual-only workflow/implementation currently MISSING; image build and rollback package not independently tested. Do not claim candidate PASS; do not request GCP deployment approval yet. No billable GCP build or resource change executed.
Required gate: complete GitHub PR tests, manual-only/no-push/no-order contract, canonical Dockerfile build, rollback check, code/security scan and full evidence pack. If and only if candidate independently PASS, STOP and request OWNER APPROVAL REQUIRED with change/cost/safety/rollback evidence.
""")
put(Path("10_HANDOVER/HANDOVER.md"),"""# Handover / read-first
Before work read, in order: ../01_MASTER_STATE/SYSTEM3_MASTER_STATE.json; ../05_AGENT_MEMORY/AGENT_MEMORY.md; ../06_BLOCKERS/BLOCKERS.yaml; ../07_DECISIONS/DECISIONS.md; then append new verified receipts to ../02_EVIDENCE/EVIDENCE.ndjson. Never overwrite that ledger; update master/owner report only after evidence.
Scope GitHub-only and read-only GCP; owner handles approval/credentials/legal/budget. No one can claim production PASS because this repository contains conceptual images. Issue #480 remains open. Full cloud acceptance follows separate owner consent.
""")
# Diagrams generated from code/source descriptions, not screenshots or traced live topology.
from PIL import Image, ImageDraw, ImageFont
diagrams={
 "Architecture.png":(["Owner consent","GitHub main","CI / security","Manual release (MISSING)","Cloud Run (UNKNOWN)","Read-only broker","PAPER ledger / UI"],[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6)]),
 "DependencyGraph.png":(["Bounded approval","Exact Git SHA","Security & tests","Dockerfile candidate","Image digest (UNKNOWN)","Serving revision (UNKNOWN)","22-tab truth"],[(0,3),(1,2),(2,3),(3,4),(4,5),(5,6)]),
 "RiskHeatmap.png":(["P0: deploy workflow MISSING","P0: live proof FAILED","P0: cloud service UNKNOWN","P0: broker order count UNKNOWN","P1: traces UNKNOWN","P1: costs UNKNOWN"],[(0,1),(1,2),(2,3),(3,4),(4,5)]),
 "RootCauseGraph.png":(["#462 GCP purge","snapshot.py DELETED","workflow call RETAINED","text-only test passed","main CI exits ENOENT","repair + regression tests"],[(0,1),(1,2),(2,3),(3,4),(4,5)]),
 "DeploymentGraph.png":(["PR CI","Owner approval PENDING","Manual workflow MISSING","Canonical Dockerfile","Digest + zero traffic","Verify + rollback","Promote (NOT AUTHORIZED)"],[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6)]),
 "DigitalTwin.png":(["GitHub source: VERIFIED","GCP project: INVENTORY ONLY","Service: MISSING","Worker: MISSING","Scheduler: MISSING","API/UI: NOT PROVEN"],[(0,1),(1,2),(2,3),(3,4),(4,5)]),
 "DataLineage.png":(["Dhan real feed (UNKNOWN)","Bounded reader (UNKNOWN)","Fenced worker (UNKNOWN)","Firestore artifact (UNKNOWN)","Read-only API (UNKNOWN)","22 production tabs (UNKNOWN)"],[(0,1),(1,2),(2,3),(3,4),(4,5)]),
 "ServiceMap.png":(["GCP: system3-openalgo-safe","Artifact Registry: EXISTS","Cloud Run web: MISSING","Cloud Run job: MISSING","Mumbai scheduler: MISSING","WIF metadata: EXISTS"],[(0,1),(0,2),(0,3),(0,4),(0,5)]),
 "APIMap.png":(["/api/deploy/info","/api/health","/api/broker/status","/api/market/live_board","/ui/ 22 tabs","independent UI proof"],[(0,5),(1,5),(2,5),(3,5),(4,5)]),
 "FailureCascade.png":(["No approved deploy","No serving revision","No runtime heartbeat","No broker evidence","No PAPER ledger","No production UI proof"],[(0,1),(1,2),(2,3),(3,4),(4,5)])
}
palette={"bg":(245,248,252),"ink":(22,36,56),"line":(68,94,122),"box":(227,237,248),"warning":(248,231,211)}
for name,(nodes,edges) in diagrams.items():
    im=Image.new("RGB",(1450,850),palette["bg"])
    dr=ImageDraw.Draw(im)
    title=name.replace(".png","").replace("Graph"," Graph").replace("Map"," Map")
    dr.text((55,30),"SYSTEM3 / "+title,fill=palette["ink"])
    dr.text((55,60),"SOURCE-GROUNDED ARCHITECTURE | NOT A LIVE DEPLOYMENT SCREENSHOT",fill=(139,58,40))
    pos={}
    for i,node in enumerate(nodes):
        col=i%2; row=i//2
        x=65+col*725; y=115+row*205
        pos[i]=(x,y)
    for a,b in edges:
        x,y=pos[a];X,Y=pos[b]
        dr.line((x+555,y+55,X+10,Y+55),fill=palette["line"],width=4)
    for i,node in enumerate(nodes):
        x,y=pos[i]; warn=any(word in node for word in ("MISSING","UNKNOWN","FAILED","PENDING","NOT PROVEN","NOT AUTHORIZED"))
        dr.rounded_rectangle((x,y,x+570,y+102),radius=14,fill=palette["warning"] if warn else palette["box"],outline=palette["line"],width=2)
        dr.text((x+15,y+37),node,fill=palette["ink"])
    dr.text((55,808),"Baseline main: "+BASE[:12]+" | Bounded GCP authority not granted | full proof via Issue #480",fill=palette["ink"])
    target=HOME/"09_DIAGRAMS"/name;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():raise FileExistsError(str(target))
    im.save(target,format="PNG")
    print("CREATED",target.relative_to(ROOT))
print("SYSTEM3_INITIALIZATION_DONE; NO GCP CALLS; NO BROKER CALLS; NO ORDERS")
