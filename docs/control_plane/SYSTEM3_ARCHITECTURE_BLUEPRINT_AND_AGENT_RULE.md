# Genesis System3 — Architecture Blueprint + Blueprint-First Agent Rule

AGENT_NAME=ChatGPT  
AGENT_LANE=D  
AGENT_ROLE=Controller  
CREATED_BY=ChatGPT  
LAST_EDITED_BY=ChatGPT  

## Canonical sources

- Machine-readable registry: `config/system3_architecture_registry.yaml`
- Human visual/data blueprint: Google Drive `SYSTEM3_ARCHITECTURE_BLUEPRINT_SSOT`
- Code authority: GitHub `main`
- Runtime authority: local laptop
- Evidence authority: sanitized bounded evidence in Google Drive

## Hard rule

No agent may implement a new persistent component, DB/table/column, data path, feature, model, scanner, strategy, scheduler, API field, UI widget, evidence path or recovery mechanism unless it already exists in the architecture blueprint, or the agent first adds a `NEW/AUDIT_REQUIRED` blueprint entry describing its upstream/downstream dependency and acceptance criteria.

The blueprint is an advance engineering design, not a post-hoc tracker.

## Pixel-level lineage

Every meaningful field must be traceable through:

`SOURCE → SOURCE FIELD → PATH → PRODUCER → STORE → DB/DATASET → TABLE → COLUMN/HEADER → TYPE → UNIT → PK/FK/JOIN → TIMESTAMP/FRESHNESS → FORMULA → FEATURE → MODEL → SCANNER → STRATEGY → RANKER → SIGNAL → RISK → PAPER → API → JSON FIELD → UI → EVIDENCE → BACKUP/RETENTION → FAILURE/RECOVERY`.

If any required upstream dependency is not proven, dependent downstream blocks are not PASS.

## Discovery / implementation loop

1. Read blueprint + machine registry.
2. Inspect current GitHub + local runtime.
3. If discovery is absent from blueprint, add the blueprint row first.
4. Reproduce the defect/gap.
5. Trace root upstream dependency.
6. Add meaningful failing regression.
7. Implement root fix.
8. Restart/recover runtime.
9. Verify store/DB/API/UI and exact SHA.
10. Rerun the same daily BAT output.
11. Update the same blueprint row.
12. Publish sanitized evidence.
13. Continue the highest upstream unresolved dependency.

## Retention

- `PERMANENT`: core code/config/schema/migration/controller SSOT/current model metadata.
- `LATEST_REPLACE`: current status; overwrite same canonical filename.
- `DAILY_7D`: one `DAY_YYYY-MM-DD`; same-day reruns replace; latest seven days only.
- `TEMP_DELETE`: scratch/test output removed after proof summary.
- `MILESTONE_KEEP`: explicitly accepted high-value proof.

Do not create timestamp-per-run evidence explosion. Do not commit raw DB/log/browser/cache/audit output to GitHub.

## Current P0 foundation examples

Historical data, canonical PAPER storage, holdings, multibagger, news/catalyst, feature/model training lineage and 22-tab field mapping are first-class architecture blocks. A downstream failure such as “model not trained” must be traced backward to whether the historical dataset/storage/writer/scheduler/schema existed and was populated correctly, rather than being treated as an isolated UI/model defect.

## Safety

PAPER/ANALYZER only. LIVE OFF. Order placement disabled. `REAL_BROKER_ORDER_COUNT=0`. No active GCP runtime dependency. Never expose secrets in GitHub, Drive or audit output.

## Self-correction

ChatGPT and every agent may be wrong. Agents must independently verify the blueprint against current GitHub and runtime evidence. A better architecture may replace a weaker one only by updating the canonical blueprint/registry first with rationale and impact; parallel undocumented architectures are forbidden.
