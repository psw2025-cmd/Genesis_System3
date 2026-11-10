import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import ts from 'typescript'

const root = path.resolve(import.meta.dirname, '..')
const helperPath = path.join(root, 'src', 'lib', 'brokerStatus.ts')
const hookPath = path.join(root, 'src', 'hooks', 'useData.ts')

const source = fs.readFileSync(helperPath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2020, target: ts.ScriptTarget.ES2020 },
}).outputText
const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`
const { mergeAuthoritativeBrokerStatus } = await import(moduleUrl)

const staleBatch = {
  connected: false,
  status: 'AUTH_REJECTED',
  error: 'stale batch error',
  token_proof: { source: 'GCP_SECRET_MANAGER_DYNAMIC', secret_version: '317' },
  batch_only_marker: true,
}
const freshFull = {
  connected: true,
  status: 'CONNECTED',
  error: '',
  latency_ms: 41,
  token_proof: { source: 'GCP_SECRET_MANAGER_DYNAMIC', secret_version: '318' },
  live_trading_enabled: false,
  order_placement_allowed: false,
}

const merged = mergeAuthoritativeBrokerStatus(staleBatch, freshFull)
assert.equal(merged.connected, true, 'fresh authoritative connectivity must override stale batch state')
assert.equal(merged.status, 'CONNECTED')
assert.equal(merged.error, '')
assert.equal(merged.token_proof.secret_version, '318')
assert.equal(merged.batch_only_marker, true, 'non-conflicting batch context remains available')
assert.equal(merged.live_trading_enabled, false)
assert.equal(merged.order_placement_allowed, false)
assert.deepEqual(
  mergeAuthoritativeBrokerStatus(staleBatch, null),
  staleBatch,
  'a failed/missing full-status response must retain last batch truth',
)

const hook = fs.readFileSync(hookPath, 'utf8')
assert.match(hook, /fetchJSON\('\/api\/broker\/status', 12000\)/)
assert.doesNotMatch(
  hook,
  /if\s*\(brokerStatus\s*&&\s*!\(brokerStatus as any\)\.token_proof\)/,
  'token_proof presence must never suppress the fresh authoritative request',
)
assert.match(hook, /mergeAuthoritativeBrokerStatus\(brokerStatus, full\)/)

console.log('BROKER_STATUS_FRESHNESS_CONTRACT=PASS')
