// CREATED_BY=Codex | LAST_EDITED_BY=Codex | TASK_OR_ISSUE=#442 | CHANGE_NOTE=Fail-closed laptop dashboard truth helpers
export type ChainMap = Record<string, any> | null | undefined

export const REQUIRED_INDEX_CHAINS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'] as const

export function chainReadiness(chain: ChainMap) {
  const ready = REQUIRED_INDEX_CHAINS.filter((symbol) => {
    const row = chain?.[symbol]
    const count = Number(row?.total_contracts ?? row?.contracts?.length ?? 0)
    const spot = Number(row?.spot ?? 0)
    return count > 0 && spot > 0 && row?.pendingProof !== true
  }).length
  return { ready, total: REQUIRED_INDEX_CHAINS.length, complete: ready === REQUIRED_INDEX_CHAINS.length }
}

export function safeDeployTruth(deployInfo: any) {
  const sha = String(deployInfo?.git_sha || '').trim()
  const target = String(deployInfo?.deploy_target || '').trim()
  const region = String(deployInfo?.region || '').trim()
  return {
    sha,
    shortSha: sha ? sha.slice(0, 7) : 'UNPROVEN',
    target: target || 'local-laptop-unproven',
    region: region || 'LOCAL',
    proven: Boolean(sha && target),
  }
}

export function brokerTokenSourceIsLocal(source: unknown) {
  return /^(WINDOWS_|LOCAL_|DPAPI|CREDENTIAL_MANAGER)/i.test(String(source || ''))
}

export function chartEvidenceReady(payload: any, kind: 'surface' | 'greeks' | 'pcr') {
  const strikes = Array.isArray(payload?.strikes) ? payload.strikes.length : 0
  const spot = Number(payload?.spot || 0)
  if (strikes === 0 || spot <= 0) return false
  if (kind === 'surface') return Array.isArray(payload?.expiries) && payload.expiries.length > 0
  if (kind === 'greeks') return Array.isArray(payload?.values) && payload.values.length > 0
  return Number.isFinite(Number(payload?.overall_pcr))
}
