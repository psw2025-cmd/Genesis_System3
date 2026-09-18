/** Central source-quality arbitration for dashboard truth surfaces.
 *
 * Rank authentic local API payloads. Never invent prices, gate PASSes, or LIVE.
 * Stale/after-hours snapshots remain visible as SNAPSHOT, not as zeros.
 */

export type EvidenceClass = 'LIVE' | 'SNAPSHOT' | 'STALE' | 'PENDING' | 'UNAVAILABLE'

export type Ranked<T> = {
  value: T
  source: string
  quality: number
  evidenceClass: EvidenceClass
  reason: string
}

const FAKE_RE = /(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock)/i

function blob(payload: unknown): string {
  if (!payload || typeof payload !== 'object') return ''
  const row = payload as Record<string, unknown>
  return [
    row.data_source,
    row.source,
    row.source_priority,
    row.status,
    row.pending_reason,
    row.message,
  ].map((part) => String(part ?? '')).join(' ')
}

export function isFabricatedSource(payload: unknown): boolean {
  return FAKE_RE.test(blob(payload))
}

export function brokerConnectedFromPayloads(health: any, brokerStatus: any, storeConnected: boolean): Ranked<boolean> {
  const healthOn = health?.broker?.connected === true
    || String(health?.broker_status || health?.broker?.status || '').toLowerCase() === 'connected'
  const statusOn = brokerStatus?.connected === true
    || String(brokerStatus?.status || '').toLowerCase() === 'connected'
  if (healthOn) {
    return {
      value: true,
      source: '/api/health',
      quality: 100,
      evidenceClass: 'LIVE',
      reason: 'Canonical health reports Dhan connected. Connected is not market-data PASS.',
    }
  }
  if (statusOn) {
    return {
      value: true,
      source: '/api/broker/status',
      quality: 90,
      evidenceClass: 'LIVE',
      reason: 'Authoritative broker status reports connected. Connected is not market-data PASS.',
    }
  }
  if (storeConnected === true) {
    return {
      value: true,
      source: 'store',
      quality: 40,
      evidenceClass: 'STALE',
      reason: 'Last store truth was connected; awaiting canonical health.',
    }
  }
  if (health && (health?.broker?.connected === false || String(health?.broker_status || '').toLowerCase() === 'disconnected')) {
    return {
      value: false,
      source: '/api/health',
      quality: 80,
      evidenceClass: 'UNAVAILABLE',
      reason: 'Canonical health reports Dhan disconnected.',
    }
  }
  return {
    value: false,
    source: 'unproven',
    quality: 0,
    evidenceClass: 'PENDING',
    reason: 'Broker connectivity is not proven yet.',
  }
}

export function gatesDisplay(autoGates: any): {
  passCount: number
  total: number
  stale: boolean
  tradeReady: boolean
  liveTradingEnabled: boolean
  spearmanFail: boolean
  latestRho: number | null
  evidenceClass: EvidenceClass
  reason: string
} {
  const proof = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const total = Number(autoGates?.gates_total) > 0 ? Number(autoGates.gates_total) : (proof.length || 7)
  const passFromProof = proof.filter((gate: any) => gate?.pass === true).length
  const passReported = Number(autoGates?.gates_passing)
  const passCount = Number.isFinite(passReported) ? passReported : passFromProof
  const stale = autoGates?.stale === true
  const spearman = proof.find((gate: any) => String(gate?.gate_id || '').includes('SPEARMAN'))
    || (autoGates?.gates && autoGates.gates.ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS)
  const latestRho = spearman && Number.isFinite(Number(spearman.latest_rho)) ? Number(spearman.latest_rho) : null
  const spearmanFail = spearman ? spearman.pass !== true : false
  if (!autoGates) {
    return {
      passCount: 0,
      total,
      stale: true,
      tradeReady: false,
      liveTradingEnabled: false,
      spearmanFail: true,
      latestRho,
      evidenceClass: 'PENDING',
      reason: 'Canonical /api/auto_gates has not arrived.',
    }
  }
  return {
    passCount,
    total,
    stale,
    tradeReady: autoGates?.trade_ready === true,
    liveTradingEnabled: autoGates?.live_trading_enabled === true,
    spearmanFail,
    latestRho,
    evidenceClass: stale ? 'STALE' : 'SNAPSHOT',
    reason: stale
      ? `Evaluator returned ${passCount}/${total}; snapshot is stale/after-hours. Do not paint 0.`
      : `Evaluator returned ${passCount}/${total}.`,
  }
}

export function isAcceptableDhanChain(data: any): boolean {
  if (!data || typeof data !== 'object') return false
  if (isFabricatedSource(data)) return false
  const status = String(data.status || '').toUpperCase()
  const source = String(data.data_source || data.source || '').toLowerCase()
  const priority = String(data.source_priority || '').toLowerCase()
  const contracts = Number(data.total_contracts || (Array.isArray(data.contracts) ? data.contracts.length : 0))
  const spot = Number(data.spot || 0)
  if (!(spot > 0 && contracts > 0)) return false
  const closedSnapshot = /MARKET_CLOSED|SNAPSHOT|DHAN_SNAPSHOT/i.test(status) || data.snapshot === true || data.live === false
  const dhanish = source === 'dhan' || priority.startsWith('dhan') || priority.includes('worker_push') || closedSnapshot
  return dhanish
}

export function rankMultibagger(workspace: any, research: any): Ranked<any> {
  const workspaceCount = Array.isArray(workspace?.candidates) ? workspace.candidates.length : 0
  const researchCount = Array.isArray(research?.candidates) ? research.candidates.length : 0
  if (workspaceCount > 0) {
    return {
      value: {
        ...workspace,
        research_label: 'RESEARCH_CANDIDATE',
        not_investment_advice: true,
        not_proven_alpha: true,
      },
      source: '/api/multibagger',
      quality: 80,
      evidenceClass: String(workspace.status || '').toUpperCase() === 'READY' ? 'SNAPSHOT' : 'STALE',
      reason: `${workspaceCount} workspace candidates. Not verified alpha. Not a LIVE order list.`,
    }
  }
  if (researchCount > 0) {
    return {
      value: {
        ...research,
        research_label: 'RESEARCH_CANDIDATE',
        not_investment_advice: true,
        not_proven_alpha: true,
      },
      source: '/api/research/multibagger',
      quality: 50,
      evidenceClass: 'SNAPSHOT',
      reason: `${researchCount} research-contract candidates.`,
    }
  }
  const pending = research && (research.status === 'pending' || research.reason === 'NO_VERIFIED_EVIDENCE')
  return {
    value: pending ? research : (workspace || research || { candidates: [], status: 'pending' }),
    source: pending ? '/api/research/multibagger' : '/api/multibagger',
    quality: 10,
    evidenceClass: 'PENDING',
    reason: pending
      ? 'Research contract is NO_VERIFIED_EVIDENCE; do not fabricate names.'
      : 'No multibagger candidates are proven.',
  }
}
