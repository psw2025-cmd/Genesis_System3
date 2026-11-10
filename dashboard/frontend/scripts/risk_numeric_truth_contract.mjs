import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const source = readFileSync(resolve(root, 'src/lib/riskNumericTruth.ts'), 'utf8')
const transpiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText
const mod = await import('data:text/javascript;base64,' + Buffer.from(transpiled).toString('base64'))
const { numberOrUndefined } = mod

for (const unavailable of [null, undefined, '', ' ', false, true, [], {}, 'N/A', 'NaN', 'Infinity', '0x10', '1,200', '12x', NaN, Infinity, -Infinity]) {
  assert.equal(numberOrUndefined(unavailable), undefined, 'missing/invalid field must never become a real zero')
}
for (const [input, expected] of [[0, 0], [-0, -0], ['0', 0], [' 42.75 ', 42.75], ['-0.7', -0.7], ['1e3', 1000], [17, 17]]) {
  assert.equal(numberOrUndefined(input), expected)
}
const dashboard = readFileSync(resolve(root, 'src/components/RiskDashboard.tsx'), 'utf8')
const workspace = readFileSync(resolve(root, 'src/components/workspaces/RiskAndScenarios.tsx'), 'utf8')
assert.match(dashboard, /import \{ numberOrUndefined \} from '\.\.\/lib\/riskNumericTruth'/)
assert.match(workspace, /marketStatus === 'OPEN' \? 'ok'/)
assert.match(workspace, /liveOrdersStatus === 'ENABLED'/)
assert.match(workspace, /'UNVERIFIED'/)
console.log('PASS: unavailable risk numbers and unknown control states never masquerade as zero or locked')
