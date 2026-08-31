import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const sourcePath = path.resolve(here, '../src/components/workspaces/DataIntegrity.tsx')
const source = fs.readFileSync(sourcePath, 'utf8')

const required = [
  "'NIFTY'",
  "'BANKNIFTY'",
  "'FINNIFTY'",
  "'MIDCPNIFTY'",
  'verifiedDhanContracts(chain)',
  'payload.total_contracts',
  'payload.contracts.length',
  "source.includes('dhan')",
  "priority.includes('worker_push')",
  'payload.stale === true',
  'verifiedContractsTotal',
]

for (const marker of required) {
  if (!source.includes(marker)) {
    throw new Error(`Data Integrity chain-truth contract missing: ${marker}`)
  }
}

const legacyOnly = /if\s*\(contractsRaw\s*==\s*null[^)]*contractsTotal\s*<=\s*0\)/s
if (legacyOnly.test(source)) {
  throw new Error('Data Integrity regressed to legacy state.qc.contracts_total-only truth')
}

if (!source.includes("derivedBlockers.push('No verified option contracts')")) {
  throw new Error('Fail-closed zero-contract blocker must remain present')
}

console.log('DATA_INTEGRITY_CHAIN_TRUTH_CONTRACT PASS')
