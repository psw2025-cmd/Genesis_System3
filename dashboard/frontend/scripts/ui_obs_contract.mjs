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

for (const tab of expectedTabs) {
  assert.match(sidebar, new RegExp(`id:\\s*'${tab}'`), `Sidebar must expose ${tab}`)
  assert.match(app, new RegExp(`case\\s+'${tab}'`), `App must render ${tab}`)
}
assert.equal((sidebar.match(/\{\s*id:\s*'/g) || []).length, 22, 'canonical tab count must remain 22')

assert.match(dataIntegrity, /<SystemProgressPanel\s*\/>/, 'Data Integrity must render progress truth')
for (const path of [
  '/api/instruments/health',
  '/api/accuracy_trend',
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
assert.doesNotMatch(progress, /CURRENT WAVE UI-OBS-1/, 'active coordination must not be hard-coded in the frontend')

assert.match(prediction, /Sample size/, 'Prediction Audit must show sample size')
assert.match(prediction, /Average Spearman ρ/, 'Prediction Audit must show rank correlation')
assert.match(prediction, /Latest hit rate/, 'Prediction Audit must show latest hit rate')
assert.match(prediction, /minimum proof gate: 5 days/, 'Prediction Audit must state the sample gate')
assert.match(prediction, /canonicalGates/, 'Prediction Audit must prefer canonical gate verdicts')
assert.match(prediction, /DATA_CONTRACT_CONFLICT/, 'Prediction Audit must expose cross-contract disagreement')
assert.match(prediction, /summary row disagrees with canonical gate/, 'Prediction Audit must not silently render contradictory PASS rows')

assert.match(performance, /PIPELINE_PROOF_ONLY/, 'Performance must distinguish pipeline from strategy proof')
assert.match(performance, /Promotion remains blocked/, 'Performance must retain the promotion block')
assert.match(performance, /costs_slippage_included_proven/, 'Performance must expose cost/slippage proof')
assert.match(performance, /winRatePct/, 'Performance must normalize 0–1 win-rate ratios before percent display')

console.log(`UI-OBS contract PASS: ${expectedTabs.length} tabs and truth semantics verified`)
