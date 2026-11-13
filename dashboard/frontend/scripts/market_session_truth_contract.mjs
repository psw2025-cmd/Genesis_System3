import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const require = createRequire(import.meta.url)
function load(relative) {
  const source = fs.readFileSync(path.join(root, relative), 'utf8')
  const code = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const exports = {}
  vm.runInNewContext(code, { exports, require, Date, console })
  return exports
}
const { useStore, marketOpenFromHealth } = load('src/store.ts')
assert.equal(useStore.getState().marketOpen, null, 'clock/calendar must not determine initial session')
for (const payload of [null, {}, { market: { is_open: null } }, { market: { is_open: 'false' } }]) {
  assert.equal(marketOpenFromHealth(payload), null)
}
assert.equal(marketOpenFromHealth({ market: { is_open: true } }), true)
assert.equal(marketOpenFromHealth({ market: { is_open: false } }), false)
useStore.getState().setHealth({ market: { is_open: true } })
assert.equal(useStore.getState().marketOpen, true)
useStore.getState().setState({ market: { is_open: null } })
assert.equal(useStore.getState().marketOpen, null, 'absent state cannot retain an old OPEN claim')

const { resolveFeedQuality } = load('src/lib/feedQuality.ts')
const input = { marketOpen: true, wsStatus: 'live', dataSource: 'dhan', brokerConnected: true }
assert.equal(resolveFeedQuality({ ...input, tickAgeSec: 59.9 }).label, 'Live')
for (const age of [60, 61, 120]) {
  const result = resolveFeedQuality({ ...input, tickAgeSec: age })
  assert.equal(result.label, 'Stale')
  assert.match(result.detail, /market OPEN/)
}
const unknown = resolveFeedQuality({ ...input, marketOpen: null, tickAgeSec: 1 })
assert.equal(unknown.label, 'Delayed')
assert.match(unknown.detail, /UNKNOWN/)
assert.doesNotMatch(unknown.detail, /closed/i)
console.log('Market source truth: unknown startup, no stale OPEN carry-over, 60-second freshness boundary verified.')
