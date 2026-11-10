import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const srcRoot = path.join(root, 'src')

const verdictFiles = [
  'components/workspaces/DecisionIntelligence.tsx',
  'components/GenesisTab.tsx',
  'components/BrokerProofPanel.tsx',
  'components/SystemTruthControl.tsx',
  'components/EndToEndProof.tsx',
  'components/PerformanceTab.tsx',
  'components/MLPerformance.tsx',
  'components/LiveTradingGate.tsx',
]

const forbidden = [
  { name: 'mock 88 fallback', re: /(?:\?\?|\|\|)\s*88(?:\.0)?\b/ },
  { name: 'mock 74 fallback', re: /(?:\?\?|\|\|)\s*74(?:\.0)?\b/ },
  { name: 'mock 68 fallback', re: /(?:\?\?|\|\|)\s*68(?:\.0)?\b/ },
  { name: 'mock 1.85 fallback', re: /(?:\?\?|\|\|)\s*1\.85\b/ },
  { name: 'hardcoded 88.0', re: /\b88\.0\b/ },
  { name: 'hardcoded 74.0', re: /\b74\.0\b/ },
  { name: 'hardcoded 68.0', re: /\b68\.0\b/ },
  { name: 'hardcoded 1.85', re: /\b1\.85\b/ },
  { name: 'fake spearman 0.74', re: /ρ\s*=\s*0\.74\b/ },
  { name: 'fake sub-15ms latency', re: /<15ms/ },
  { name: 'fresh chain tradable badge', re: /4-of-4 FRESH/ },
  { name: 'ready_for_live literal true', re: /ready_for_live\s*:\s*true\b/ },
  { name: 'assigned ready_for_live true', re: /(?<![=!])ready_for_live\s*=\s*true(?!=)/ },
  { name: 'hardcoded model ACTIVE', re: /value="ACTIVE"|Model Ensemble" value="ACTIVE"/ },
]

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, out)
    else if (/\.(tsx|ts)$/.test(entry.name)) out.push(full)
  }
  return out
}

const files = walk(srcRoot)
const hits = []
for (const file of files) {
  const text = fs.readFileSync(file, 'utf8')
  const rel = path.relative(root, file).replaceAll('\\', '/')
  for (const rule of forbidden) {
    if (rule.re.test(text)) hits.push(`${rel}: ${rule.name}`)
  }
}
assert.deepEqual(hits, [], `lifecycle display contract failed:\n${hits.join('\n')}`)

for (const rel of verdictFiles) {
  const text = fs.readFileSync(path.join(srcRoot, rel), 'utf8')
  assert.match(text, /PendingLifecycleBanner/, `${rel} must render the shared lifecycle banner`)
  assert.doesNotMatch(text, /FULL E2E/, `${rel} must not claim a full E2E trade pass`)
}

const banner = fs.readFileSync(path.join(srcRoot, 'components', 'PendingLifecycleBanner.tsx'), 'utf8')
const truth = fs.readFileSync(path.join(srcRoot, 'lib', 'lifecycleTruth.ts'), 'utf8')
assert.match(banner, /ValidationChecklist/)
assert.match(truth, /REAL_PAPER_LIFECYCLE_NOT_PROVEN/)
assert.match(truth, /scripts\/run_paper_validation\.py is missing/)
assert.match(banner, /PENDING_LIFECYCLE_BANNER/)
assert.doesNotMatch(banner, /ready_for_live\s*:\s*true/)

const poller = fs.readFileSync(path.join(srcRoot, 'hooks', 'useData.ts'), 'utf8')
assert.match(poller, /\/api\/ml\/performance/)
assert.match(poller, /setMlPerformance/)

console.log('lifecycle_display_contract: PASS')
