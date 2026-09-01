// CREATED_BY=Codex | LAST_EDITED_BY=Codex | TASK_OR_ISSUE=#442 | CHANGE_NOTE=Regression contract for local-only dashboard semantics
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import ts from 'typescript'

const root = path.resolve(import.meta.dirname, '..')
const helperPath = path.join(root, 'src', 'lib', 'dashboardTruth.ts')
const compiled = ts.transpileModule(fs.readFileSync(helperPath, 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.ES2020, target: ts.ScriptTarget.ES2020 },
}).outputText
const truth = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)

assert.deepEqual(truth.chainReadiness({}), { ready: 0, total: 4, complete: false })
assert.deepEqual(truth.chainReadiness({
  NIFTY: { spot: 25000, total_contracts: 40 },
  BANKNIFTY: { spot: 54000, contracts: [{}] },
  FINNIFTY: { spot: 26000, total_contracts: 2, pendingProof: true },
  MIDCPNIFTY: { spot: 13000, total_contracts: 0 },
}), { ready: 2, total: 4, complete: false })
assert.equal(truth.safeDeployTruth({}).shortSha, 'UNPROVEN')
assert.equal(truth.safeDeployTruth({}).target, 'local-laptop-unproven')
assert.equal(truth.brokerTokenSourceIsLocal('GCP_SECRET_MANAGER_DYNAMIC'), false)
assert.equal(truth.brokerTokenSourceIsLocal('WINDOWS_DPAPI_VAULT'), true)
assert.equal(truth.chartEvidenceReady({ strikes: [], expiries: [], spot: 0 }, 'surface'), false)
assert.equal(truth.chartEvidenceReady({ strikes: [1], expiries: ['x'], spot: 100 }, 'surface'), true)

const truthStrip = fs.readFileSync(path.join(root, 'src', 'components', 'TruthStrip.tsx'), 'utf8')
const banner = fs.readFileSync(path.join(root, 'src', 'components', 'AutonomousLoopBanner.tsx'), 'utf8')
const footer = fs.readFileSync(path.join(root, 'src', 'components', 'DeploymentTruthFooter.tsx'), 'utf8')
assert.doesNotMatch(truthStrip, /4-of-4 FRESH|7b26b87/)
assert.doesNotMatch(banner, /WEEKEND STANDBY|2026-08-31|7b26b87/)
assert.doesNotMatch(footer, /\|\| 'gcp-cloud-run'|\|\| 'asia-south1'/)

console.log('LOCAL_DASHBOARD_TRUTH_CONTRACT=PASS')
