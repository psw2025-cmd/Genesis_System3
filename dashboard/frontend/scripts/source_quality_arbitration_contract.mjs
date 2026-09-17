import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import ts from 'typescript'

const root = path.resolve(import.meta.dirname, '..')
const helperPath = path.join(root, 'src', 'lib', 'sourceQuality.ts')
const bannerPath = path.join(root, 'src', 'components', 'AutonomousLoopBanner.tsx')
const hookPath = path.join(root, 'src', 'hooks', 'useData.ts')

const source = fs.readFileSync(helperPath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2020, target: ts.ScriptTarget.ES2020 },
}).outputText
const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`
const {
  brokerConnectedFromPayloads,
  gatesDisplay,
  isAcceptableDhanChain,
  rankMultibagger,
  isFabricatedSource,
} = await import(moduleUrl)

const health = { broker: { connected: true }, broker_status: 'connected', mode: 'PAPER', live_allowed: false }
const broker = brokerConnectedFromPayloads(health, { connected: false }, false)
assert.equal(broker.value, true, 'canonical health connected must beat a disconnected batch')
assert.equal(broker.source, '/api/health')

const staleGates = {
  stale: true,
  snapshot_id: 'abc',
  gates_passing: 6,
  gates_total: 7,
  trade_ready: false,
  live_trading_enabled: false,
  proof_gates: [
    { gate_id: 'ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS', pass: false, latest_rho: 0.1377 },
    { gate_id: 'A', pass: true },
    { gate_id: 'B', pass: true },
    { gate_id: 'C', pass: true },
    { gate_id: 'D', pass: true },
    { gate_id: 'E', pass: true },
    { gate_id: 'F', pass: true },
  ],
}
const gates = gatesDisplay(staleGates)
assert.equal(gates.passCount, 6, 'stale evaluator must not paint 0/7')
assert.equal(gates.total, 7)
assert.equal(gates.stale, true)
assert.equal(gates.tradeReady, false)
assert.equal(gates.liveTradingEnabled, false)
assert.equal(gates.spearmanFail, true)
assert.equal(gates.latestRho, 0.1377)

const snapshot = {
  underlying: 'NIFTY',
  spot: 23118.6,
  total_contracts: 184,
  contracts: new Array(184).fill({ option_type: 'CE' }),
  status: 'MARKET_CLOSED_DHAN_SNAPSHOT',
  data_source: 'dhan',
}
assert.equal(isAcceptableDhanChain(snapshot), true, 'after-hours Dhan snapshot with rows is acceptable')
assert.equal(isAcceptableDhanChain({ ...snapshot, data_source: 'synthetic', status: 'OK' }), false)
assert.equal(isFabricatedSource({ data_source: 'csv_fallback' }), true)

const ranked = rankMultibagger(
  { status: 'READY', candidates: [{ symbol: 'KALYANKJIL' }] },
  { status: 'pending', reason: 'NO_VERIFIED_EVIDENCE', candidates: [] },
)
assert.equal(ranked.value.candidates[0].symbol, 'KALYANKJIL')
assert.equal(ranked.source, '/api/multibagger')
assert.equal(ranked.value.not_proven_alpha, true)

const emptyWinsNothing = rankMultibagger({ candidates: [] }, { status: 'pending', reason: 'NO_VERIFIED_EVIDENCE', candidates: [] })
assert.equal(emptyWinsNothing.evidenceClass, 'PENDING')

const banner = fs.readFileSync(bannerPath, 'utf8')
assert.match(banner, /gatesDisplay/)
assert.doesNotMatch(banner, /snapshotVerified \? proof\.filter/)

const hook = fs.readFileSync(hookPath, 'utf8')
assert.match(hook, /isAcceptableDhanChain/)
assert.match(hook, /rankMultibagger/)
assert.match(hook, /fetchJSON\('\/api\/health'/)
assert.match(hook, /pollChain\(sym\)/)

console.log('SOURCE_QUALITY_ARBITRATION_CONTRACT=PASS')
