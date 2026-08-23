import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const read = (relative) => readFileSync(resolve(root, relative), 'utf8')

const expectedTabs = [
  'decision-intel',
  'truth',
  'genesis',
  'e2e-proof',
  'overview',
  'sim-live',
  'options-intel',
  'chain',
  'signals',
  'trade',
  'paper',
  'positions',
  'risk-scenarios',
  'multibagger',
  'prediction-audit',
  'performance',
  'ml',
  'data-integrity',
  'broker',
  'alerts',
  'system',
  'gates',
]

const sidebar = read('src/components/Sidebar.tsx')
const app = read('src/App.tsx')
const dataIntegrity = read('src/components/workspaces/DataIntegrity.tsx')
const progress = read('src/components/SystemProgressPanel.tsx')
const prediction = read('src/components/workspaces/PredictionAudit.tsx')
const performance = read('src/components/PerformanceTab.tsx')
const alerts = read('src/components/AlertsTab.tsx')
const store = read('src/store.ts')
const useData = read('src/hooks/useData.ts')
const styles = read('src/index.css')
const mobileHub = read('src/components/MobileTradingHub.tsx')
const riskDashboard = read('src/components/RiskDashboard.tsx')
const riskWorkspace = read('src/components/workspaces/RiskAndScenarios.tsx')

for (const tab of expectedTabs) {
  assert.match(sidebar, new RegExp(`id:\\s*'${tab}'`), `Sidebar must expose ${tab}`)
  assert.match(app, new RegExp(`case\\s+'${tab}'`), `App must render ${tab}`)
}
assert.equal((sidebar.match(/\{\s*id:\s*'/g) || []).length, 22, 'canonical tab count must remain 22')

assert.match(dataIntegrity, /<SystemProgressPanel\s*\/>/, 'Data Integrity must render progress truth')
for (const path of [
  '/api/instruments/health',
  '/api/accuracy_trend',
  '/api/auto_gates',
  '/api/backtest/results',
  '/api/ml/performance',
  '/api/agent/status',
]) {
  assert.match(progress, new RegExp(path.replaceAll('/', '\\/')), `progress panel must use ${path}`)
}
for (const state of ['PASS', 'PARTIAL', 'BLOCKED', 'NOT_PROVEN', 'ERROR']) {
  assert.match(progress, new RegExp(`'${state}'`), `progress panel must support ${state}`)
}
assert.match(progress, /BACKEND_PROGRESS_CONTRACT_REQUIRED/, 'missing wave/owner contract must remain explicit')
assert.match(progress, /costs_slippage_included_proven/, 'progress costed lane must require proven costs/slippage')
assert.match(progress, /DATA_CONTRACT_CONFLICT/, 'progress prediction lane must surface contract conflicts')
assert.match(progress, /Broker authentication\/session/, 'broker lane must mean auth/session, not end-to-end reliability')
assert.match(progress, /Broker market-data reliability/, 'market-data reliability must be a separate lane')
assert.match(progress, /BACKEND_DEPENDENCY/, 'market-data reliability must fail closed without a health contract')
assert.doesNotMatch(progress, /name: 'Broker reliability'/, 'connected=true must not be labeled Broker reliability PASS')
assert.doesNotMatch(progress, /CURRENT WAVE UI-OBS-1/, 'active coordination must not be hard-coded in the frontend')

assert.match(prediction, /Sample size/, 'Prediction Audit must show sample size')
assert.match(prediction, /Average Spearman ρ/, 'Prediction Audit must show rank correlation')
assert.match(prediction, /Latest hit rate/, 'Prediction Audit must show latest hit rate')
assert.match(prediction, /minimum proof gate: 5 days/, 'Prediction Audit must state the sample gate')
assert.match(prediction, /canonicalGates/, 'Prediction Audit must prefer canonical gate verdicts')
assert.match(prediction, /hasCanonicalGates/, 'Prediction Audit must require canonical gates before PASS')
assert.match(prediction, /DATA_CONTRACT_CONFLICT/, 'Prediction Audit must expose cross-contract disagreement')
assert.match(prediction, /summary row disagrees with canonical gate/, 'Prediction Audit must not silently render contradictory PASS rows')
assert.match(prediction, /gatesError/, 'Prediction Audit must surface auto_gates fetch failure')
assert.match(prediction, /AUTO_GATES CONTRACT ERROR/, 'Prediction Audit must fail closed when auto_gates rejects')
assert.doesNotMatch(prediction, /gateContract \|\| autoGates/, 'Prediction Audit must not fall back to slim-store autoGates for PASS')

assert.match(performance, /PIPELINE_PROOF_ONLY/, 'Performance must distinguish pipeline from strategy proof')
assert.match(performance, /Promotion remains blocked/, 'Performance must retain the promotion block')
assert.match(performance, /costs_slippage_included_proven/, 'Performance must expose cost/slippage proof')
assert.match(performance, /winRatePct/, 'Performance must normalize 0–1 win-rate ratios before percent display')

assert.match(alerts, /alertFeedStatus/, 'Alerts must consume explicit feed truth')
assert.match(alerts, /feedReady/, 'Alerts must distinguish a successful empty feed from an unavailable feed')
assert.match(alerts, /Alert feed unavailable/, 'Alerts must expose a finite degraded state')
assert.match(alerts, /WebSocket transport/, 'Alerts must label WS as transport state')
assert.match(alerts, /alerts-message/, 'Alerts must use tested wrapping hooks for long content')
assert.doesNotMatch(alerts, /repeat\(6, minmax\(0, 1fr\)\)/, 'Alerts must not hard-code six inline metric columns')
assert.match(store, /alertFeedStatus/, 'Store must retain alert-feed provenance state')
assert.match(useData, /state: 'ready'.*source: '\/api\/alerts\/recent'/s, 'Successful alert reads must mark the feed ready')
assert.match(useData, /state: 'degraded'.*Alert feed request failed/s, 'Failed alert reads must mark the feed degraded')
assert.match(styles, /\.alerts-metrics-grid/, 'Alerts metrics must have responsive CSS')
assert.match(styles, /@media \(max-width: 600px\)[\s\S]*?\.alerts-metrics-grid \{ grid-template-columns: repeat\(2/, 'Phone metrics must reflow to two columns')
assert.match(styles, /@media \(max-width: 900px\)[\s\S]*?\.alerts-content-grid \{ grid-template-columns: minmax\(0, 1fr\)/, 'Phone/tablet alert content must become one column')
assert.match(styles, /overflow-wrap: anywhere/, 'Long alert content must wrap intentionally')

assert.match(riskDashboard, /axios\.get\(\x60\$\{API_BASE\}\/api\/risk\/portfolio/, 'Risk dashboard must use authoritative read-only GET portfolio risk')
assert.doesNotMatch(riskDashboard, /axios\.post|\/api\/risk\/check-limits/, 'Public risk dashboard must require no mutation-shaped POST')
for (const state of ['loading', 'ready', 'degraded', 'no-data', 'error']) {
  assert.match(riskDashboard, new RegExp(`'${state}'`), `Risk dashboard must support finite ${state} state`)
}
assert.match(riskDashboard, /timeout: 15000/, 'Risk read must be bounded by a timeout')
assert.match(riskDashboard, /error\?\.name === 'NO_DATA'/, 'Successful empty risk payloads must become explicit no-data truth')
assert.match(riskDashboard, /loadState !== 'ready' && fallback/, 'Late state snapshot must recover a failed or empty API read')
assert.match(riskDashboard, /raw\.var_95 \?\? raw\.var/, 'Empty-book VaR aliases must normalize')
assert.match(riskDashboard, /raw\.expected_shortfall_95 \?\? raw\.expected_shortfall/, 'Empty-book ES aliases must normalize')
assert.match(riskDashboard, /emptyBook \? 0/, 'Verified empty books must render truthful zeroes instead of dashes')
for (const fixed of ['Delta 0.35', 'Vega 0.12', 'Theta -0.08', 'Beta 1.02', 'Bullish +15%', 'Bearish -12%']) {
  assert.equal(riskWorkspace.includes(fixed), false, `Risk workspace must not hard-code ${fixed}`)
}
assert.match(riskWorkspace, /NO VERIFIED SCENARIO MODEL OUTPUT AVAILABLE/, 'Missing scenario proof must remain explicit')

for (const label of ['Options Chain', 'Equity Feed', 'Prediction Charts', 'Backtest', 'Portfolio']) {
  assert.match(mobileHub, new RegExp(label), `Mobile hub must expose ${label}`)
}
for (const reused of ['OptionChain', 'Signals', 'PredictionAudit', 'Backtest', 'Positions']) {
  assert.match(mobileHub, new RegExp(`<${reused} \/>`), `Mobile hub must reuse ${reused}`)
}
assert.match(app, /view.*mobile-trader/, 'App must expose the explicit mobile-trader route')
assert.match(mobileHub, /max-width: 820px/, 'Mobile hub must render feature content only at phone widths')
assert.match(mobileHub, /SYSTEM3_STREAM_PROOF/, 'Mobile hub must publish F12 streaming proof')
assert.match(mobileHub, /PAPER · LIVE OFF/, 'Mobile hub must retain the safe trading authority label')
assert.doesNotMatch(mobileHub, /fetch\(|axios|POST|placeOrder|executeOrder/, 'Mobile orchestration must add no duplicate API or mutation logic')
assert.match(styles, /\.mobile-hub-tabs/, 'Mobile hub tabs require production CSS')
assert.match(styles, /@media \(min-width: 821px\)[\s\S]*?\.mobile-hub-shell \{ display: none; \}/, 'Mobile feature shell must not render on desktop')

console.log(`UI-OBS contract PASS: ${expectedTabs.length} tabs and truth semantics verified`)
