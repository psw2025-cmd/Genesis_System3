# System3 V5 Consolidation Specification

## Objective

Consolidate the existing production React dashboard with all capabilities from:

- Existing 41 React components
- Institutional Command Centre V2
- Options Intelligence V3
- Multibagger Research V4
- Decision Intelligence V5
- Repository/API/security audit findings

Do not remove or silently replace existing functionality.

## Global truth and safety rules

- PAPER and LIVE OFF must remain globally visible.
- Authentication-disabled state must be critical and visible.
- Broker token failures must not appear healthy.
- Do not invent live prices, positions, model performance or predictions.
- Illustrative values must say MOCK or FICTIONAL.
- Empty HTTP 200 data must appear unavailable, not successful.
- Predictions require probability, uncertainty, evidence, counter-evidence,
  invalidation, model version and data cutoff.
- No order, cancel, close, approval, upgrade, rollback or runner controls.
- No new direct fetch or Axios calls; use existing Zustand store data.
- Preserve all existing tabs and components.
- Keep current error boundaries and production proof controls.

## New first-class workspaces

### 1. Decision Intelligence

Unified command view containing:

- Operating mode
- Data truth
- Broker health
- Prediction-source health
- Scanner/API health
- System blockers
- Existing market/portfolio summaries when genuinely available
- AI decision brief contract
- Links into existing detailed tabs

### 2. Options Intelligence

Use existing store/chain/marketTop/gainRank data for:

- Underlying and chain status
- PCR, IV, OI, volume and Greeks when available
- Market leaders versus System3 comparison
- Abnormal activity
- Forecast status
- Dhan position context
- Strategy/risk status

Missing catalysts, sentiment, validated forecasts or prediction ledger must
show BLOCKED or NOT IMPLEMENTED—not mock production data.

### 3. Multibagger Research

Production service does not yet exist. Create a truthful research workspace
showing:

- Required candidate ranking
- Horizon forecast matrix
- 2x–100x probability ladder
- Fundamentals
- Governance
- Catalysts
- Ownership/flows
- Valuation
- Explainability
- Actual-versus-predicted ledger
- Exit/thesis monitor

All sections must show DATA SERVICE NOT IMPLEMENTED unless real store data
exists. Fictional UI examples may appear only if unmistakably labelled.

### 4. Risk and Scenarios

Reuse existing RiskDashboard where possible and expose:

- Portfolio/factor-risk status
- Scenario-analysis availability
- Pre-trade security requirements
- Live gate state
- No executable controls

### 5. Data Integrity

Show:

- Authentication state
- Dhan/broker status
- Option-chain truth
- API error kind
- Data freshness
- Model/prediction availability
- Existing audit blockers
- Clear timeout versus network distinction

### 6. Prediction Audit

Show the required immutable ledger schema:

- Prediction timestamp
- Target and horizon
- Probability and interval
- Model/data version
- Frozen data cutoff
- Actual outcome
- Calibration/error score

If no ledger exists, display NOT IMPLEMENTED.

## UX requirements

- Material Design 3-inspired semantic surfaces and status chips
- Dense institutional desktop layout
- Responsive tablet/mobile layout
- Visible keyboard focus
- Semantic headings, navigation, tables and status labels
- Reduced-motion support
- Color must not be the only status signal
- Reuse current CSS variables and extend them carefully
- Avoid external UI dependencies

## Required source behavior

- Add new tabs without deleting existing tabs.
- Keep existing active-tab/store architecture.
- Create small reusable truth-first components rather than one giant file.
- New components must compile under existing TypeScript/Vite configuration.
- Add data-testid attributes for new workspace roots.
- Do not edit backend, deployment, authentication middleware or tests.
- Do not modify useData.ts, config.ts or generated dist assets.
