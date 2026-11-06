/** Shared read-only trade-permission labels. Checklist pass/fail stays on the API payload. */

export const REQUIRED_CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'] as const

export const PENDING_LIFECYCLE_BANNER =
  'PENDING PROOF - REAL_PAPER_LIFECYCLE_NOT_PROVEN - run scripts/run_paper_validation.py to generate fresh state/paper_validations proof'

import { asRecord, isLiveFlagOn } from './strictFlags';

export function isDhanChainReady(value: unknown): boolean {
  if (!value || typeof value !== 'object') return false
  const v = asRecord(value)
  const source = String(v['data_source'] ?? v['source'] ?? '').toLowerCase()
  const priority = String(v['source_priority'] ?? '').toLowerCase()
  const status = String(v['status'] ?? '').toUpperCase()
  const contractsRaw = v['total_contracts'] ?? (Array.isArray(v['contracts']) ? (v['contracts'] as unknown[]).length : 0)
  const contracts = Number(contractsRaw)
  const spot = Number(v['spot'] ?? 0)
  const dhanish = source === 'dhan' || source.startsWith('dhan_') || priority.startsWith('dhan') || priority.includes('worker_push')
  if (!dhanish || v['pendingProof'] || spot <= 0 || contracts <= 0) return false
  if (['MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT', 'MARKET_CLOSED'].includes(status)) return true
  if (v['snapshot'] === true && /DHAN|SNAPSHOT/.test(`${source} ${priority} ${status}`.toUpperCase())) return true
  return ['OK', 'MARKET_OPEN'].includes(status) && v['stale'] !== true
}

export function isSafeNoTradeChain(value: unknown): boolean {
  if (!value || typeof value !== 'object') return false
  const v = asRecord(value)
  return String(v['data_source'] ?? v['source'] ?? '').toLowerCase().startsWith('dhan')
    && String(v['status'] ?? '').toUpperCase() === 'NO_DHAN_DATA'
}

export function requiredChainCounts(chain: Record<string, unknown> | null | undefined) {
  const rows = REQUIRED_CHAIN_SYMBOLS.map((symbol) => chain?.[symbol])
  return {
    requiredReady: rows.filter(isDhanChainReady).length,
    safeNoTrade: rows.filter(isSafeNoTradeChain).length,
    total: REQUIRED_CHAIN_SYMBOLS.length,
    tradableLabel: 'PENDING' as const,
  }
}

export function availableBalance(funds: unknown): number | null {
  const f = asRecord(funds)
  const normalized = asRecord(f['normalized'])
  const raw = f['available_balance'] ?? normalized['available_balance']
  if (raw == null || raw === '') return null
  const n = Number(raw)
  return Number.isFinite(n) ? n : null
}

export function orderAllowedValue(state: unknown, brokerStatus: unknown): boolean | null {
  const s = asRecord(state)
  const b = asRecord(brokerStatus)
  if (s['order_placement_allowed'] === true || b['order_placement_allowed'] === true) return true
  if (s['order_placement_allowed'] === false || b['order_placement_allowed'] === false) return false
  return null
}

export function liveTradingValue(state: unknown, brokerStatus: unknown, health: unknown): boolean | number | string | null {
  const s = asRecord(state)
  const b = asRecord(brokerStatus)
  const h = asRecord(health)
  const raw = s['live_trading_enabled'] ?? b['live_trading_enabled'] ?? h['live_trading_enabled'] ?? h['live_allowed']
  if (raw == null || raw === '') return null
  if (typeof raw === 'boolean' || typeof raw === 'number' || typeof raw === 'string') return raw
  return null
}

export function liveTradingOn(state: unknown, brokerStatus: unknown, health: unknown): boolean {
  const raw = liveTradingValue(state, brokerStatus, health)
  return isLiveFlagOn(raw)
}

export function brokerPermissionLabel(input: {
  brokerConnected?: boolean
  brokerStatus?: unknown
  health?: unknown
  state?: unknown
  brokerFunds?: unknown
}): string {
  const b = asRecord(input.brokerStatus)
  const h = asRecord(input.health)
  const hb = asRecord(h['broker'])
  const connected = input.brokerConnected === true
    || b['connected'] === true
    || hb['connected'] === true
  const allowed = orderAllowedValue(input.state, input.brokerStatus)
  const liveOn = liveTradingOn(input.state, input.brokerStatus, input.health)
  if (connected && allowed !== true && !liveOn) return 'PAPER LOCKED'
  if (connected && (allowed === true || liveOn)) return 'ORDER FLAG REVIEW'
  if (b['connected'] === false || hb['connected'] === false) return 'NOT CONNECTED'
  return 'PENDING PROOF'
}
