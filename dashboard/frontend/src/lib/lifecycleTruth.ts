/** Shared read-only trade-permission labels. Checklist pass/fail stays on the API payload. */

export const REQUIRED_CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'] as const

export const PENDING_LIFECYCLE_BANNER =
  'PENDING PROOF - REAL_PAPER_LIFECYCLE_NOT_PROVEN - scripts/run_paper_validation.py is missing'

export function isDhanChainReady(value: any): boolean {
  if (!value || typeof value !== 'object') return false
  const source = String(value.data_source || value.source || '').toLowerCase()
  const priority = String(value.source_priority || '').toLowerCase()
  const status = String(value.status || '').toUpperCase()
  const contracts = Number(value.total_contracts || (Array.isArray(value.contracts) ? value.contracts.length : 0))
  const spot = Number(value.spot || 0)
  const dhanish = source === 'dhan' || source.startsWith('dhan_') || priority.startsWith('dhan') || priority.includes('worker_push')
  if (!dhanish || value.pendingProof || spot <= 0 || contracts <= 0) return false
  if (['MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT', 'MARKET_CLOSED'].includes(status)) return true
  if (value.snapshot === true && /DHAN|SNAPSHOT/.test(`${source} ${priority} ${status}`.toUpperCase())) return true
  return ['OK', 'MARKET_OPEN'].includes(status) && value.stale !== true
}

export function isSafeNoTradeChain(value: any): boolean {
  if (!value || typeof value !== 'object') return false
  return String(value.data_source || value.source || '').toLowerCase().startsWith('dhan')
    && String(value.status || '').toUpperCase() === 'NO_DHAN_DATA'
}

export function requiredChainCounts(chain: Record<string, any> | null | undefined) {
  const rows = REQUIRED_CHAIN_SYMBOLS.map((symbol) => chain?.[symbol])
  return {
    requiredReady: rows.filter(isDhanChainReady).length,
    safeNoTrade: rows.filter(isSafeNoTradeChain).length,
    total: REQUIRED_CHAIN_SYMBOLS.length,
    tradableLabel: 'PENDING' as const,
  }
}

export function availableBalance(funds: any): number | null {
  const raw = funds?.available_balance ?? funds?.normalized?.available_balance
  if (raw == null || raw === '') return null
  const n = Number(raw)
  return Number.isFinite(n) ? n : null
}

export function orderAllowedValue(state: any, brokerStatus: any): boolean | null {
  if (state?.order_placement_allowed === true || brokerStatus?.order_placement_allowed === true) return true
  if (state?.order_placement_allowed === false || brokerStatus?.order_placement_allowed === false) return false
  return null
}

export function liveTradingValue(state: any, brokerStatus: any, health: any): boolean | string | null {
  const raw = state?.live_trading_enabled ?? brokerStatus?.live_trading_enabled ?? health?.live_trading_enabled ?? health?.live_allowed
  if (raw == null || raw === '') return null
  return raw
}

export function liveTradingOn(state: any, brokerStatus: any, health: any): boolean {
  const raw = liveTradingValue(state, brokerStatus, health)
  return raw === true || raw === 1 || raw === '1'
}

export function brokerPermissionLabel(input: {
  brokerConnected?: boolean
  brokerStatus?: any
  health?: any
  state?: any
  brokerFunds?: any
}): string {
  const connected = input.brokerConnected === true
    || input.brokerStatus?.connected === true
    || input.health?.broker?.connected === true
  const allowed = orderAllowedValue(input.state, input.brokerStatus)
  const liveOn = liveTradingOn(input.state, input.brokerStatus, input.health)
  if (connected && allowed !== true && !liveOn) return 'PAPER LOCKED'
  if (connected && (allowed === true || liveOn)) return 'ORDER FLAG REVIEW'
  if (input.brokerStatus?.connected === false || input.health?.broker?.connected === false) return 'NOT CONNECTED'
  return 'PENDING PROOF'
}
