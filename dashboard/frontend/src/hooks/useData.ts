import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'
import { API_BASE, API_HEADERS } from '../config'

const BASE = API_BASE || window.location.origin
const TRANSIENT_STATUS = new Set([0, 502, 503, 504, 520, 521, 522, 523, 524])
const isTransient = (status?: number) => TRANSIENT_STATUS.has(Number(status ?? -1))

class ApiRequestError extends Error {
  status: number
  path: string

  constructor(path: string, status: number) {
    super(`${status}`)
    this.name = 'ApiRequestError'
    this.path = path
    this.status = status
  }
}

async function fetchJSON(path: string) {
  try {
    const r = await fetch(BASE + path, { credentials: 'include', headers: { Accept: 'application/json', ...API_HEADERS } })
    if (!r.ok) throw new ApiRequestError(path, r.status)
    return r.json()
  } catch (err: any) {
    if (err instanceof ApiRequestError) throw err
    throw new ApiRequestError(path, 0)
  }
}

const authStatus = (path: string, status: number) => ({
  status: status === 401 ? 'API_AUTH_REQUIRED' : isTransient(status) ? (status === 0 ? 'NETWORK_ERROR' : 'RENDER_UNAVAILABLE') : 'API_ERROR',
  code: status,
  path,
  severity: status === 401 ? 'locked' : isTransient(status) ? 'transient' : 'error',
  message: status === 401
    ? 'Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.'
    : isTransient(status)
      ? (status === 0 ? `Network/DNS could not reach Render for ${path}. Real data is blocked until live API returns.` : `Render/backend returned ${status} for ${path}. Real data is blocked until live API returns.`)
      : `Backend API returned ${status}`,
})

const fallbackHealth = (apiStatus: any) => ({
  mode: 'PAPER',
  data_source: apiStatus?.status || 'API_LOCKED',
  qc_status: apiStatus?.status || 'API_LOCKED',
  live_allowed: false,
  broker: { connected: false, status: apiStatus?.status || 'API_LOCKED' },
  market: { is_open: false, reason: apiStatus?.message || 'API locked/unavailable', next_open: '--' },
  live_blockers: [apiStatus?.message || 'Backend API unavailable'],
})

const blockedPaper = (apiStatus: any) => ({
  positions: { open_count: 0, open_positions: [] },
  pnl: { summary: { total_pnl: 0, win_rate: 0, total_trades: 0, closed_positions: [] } },
  status: apiStatus?.status || 'NO_REAL_PAPER_DATA',
  blocked: true,
  blocked_reason: apiStatus?.message || 'Paper data unavailable from live backend',
})

const blockedGainRank = (apiStatus: any) => ({
  rankings: [],
  latest: { predictions: [] },
  status: apiStatus?.status || 'NO_REAL_RANK_DATA',
  blocked: true,
  stale: false,
  message: apiStatus?.message || 'Backend API unavailable',
})

const blockedGates = (apiStatus: any) => ({
  proof_gates: [
    {
      gate_id: 'api_access',
      name: 'Dashboard API Access',
      status: 'FAIL',
      note: apiStatus?.message || 'Backend API unavailable',
    },
  ],
})

const blockedBrokerStatus = (apiStatus: any) => ({
  success: false,
  connected: false,
  status: apiStatus?.status || 'API_LOCKED',
  token_status: apiStatus?.status || 'API_LOCKED',
  message: apiStatus?.message || 'Broker API unavailable',
  error: apiStatus?.message || 'Broker API unavailable',
})

const blockedRows = (apiStatus: any, label: string) => ({
  success: false,
  rows: [],
  count: 0,
  status: apiStatus?.status || 'API_LOCKED',
  blocked: true,
  message: `${label}: ${apiStatus?.message || 'API unavailable'}`,
  error: apiStatus?.message || 'API unavailable',
})

const blockedFunds = (apiStatus: any) => ({
  success: false,
  normalized: {
    available_balance: null,
    utilized_amount: null,
    total_limit: null,
    raw: {
      status: 'failure',
      remarks: {
        error_code: apiStatus?.code || 'API_LOCKED',
        error_type: apiStatus?.status || 'API_ERROR',
        error_message: apiStatus?.message || 'Funds API unavailable',
      },
    },
  },
  message: apiStatus?.message || 'Funds API unavailable',
  error: apiStatus?.message || 'Funds API unavailable',
})

const blockedChain = (sym: string, apiStatus: any) => ({
  underlying: sym,
  contracts: [],
  spot: 0,
  pcr: '--',
  status: 'NO_DHAN_DATA',
  blocked: true,
  blocked_reason: apiStatus?.message || 'Dhan live option chain unavailable',
  data_source: 'dhan',
  source_priority: 'blocked_until_real_dhan_stream',
  stale: false,
  message: apiStatus?.message || 'Dhan live option chain unavailable',
})

function isRealDhanChainPayload(data: any) {
  if (!data || typeof data !== 'object') return false
  const source = String(data.data_source || data.source || '').toLowerCase()
  const priority = String(data.source_priority || '').toLowerCase()
  const status = String(data.status || '').toUpperCase()
  const combined = `${source} ${priority} ${status}`
  if (data.stale === true) return false
  if (/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock|stale)/i.test(combined)) return false
  const contracts = Number(data.total_contracts || (Array.isArray(data.contracts) ? data.contracts.length : 0))
  const spot = Number(data.spot || 0)
  return source === 'dhan' && spot > 0 && contracts > 0
}

function keepLastGood(previous: any, apiStatus: any, label: string) {
  if (!previous) return null
  return {
    ...previous,
    stale: true,
    transient_error: true,
    degraded_at: new Date().toISOString(),
    last_warning: `${label}: ${apiStatus?.message || 'temporary API failure'}`,
    status: previous.status || 'STALE_LAST_GOOD',
  }
}

function withFailureCount(apiStatus: any, group: string, count: number) {
  return {
    ...apiStatus,
    group,
    consecutive_failures: count,
    message: count < 3 ? `${apiStatus.message} Retrying; live data remains blocked where truth cannot be proven.` : apiStatus.message,
  }
}

function apiError(result: PromiseSettledResult<any>, path: string) {
  if (result.status === 'rejected' && result.reason instanceof ApiRequestError) return authStatus(path, result.reason.status)
  if (result.status === 'rejected') return { status: 'API_ERROR', code: 0, path, message: String(result.reason?.message || result.reason) }
  return null
}

export function useData() {
  const {
    setHealth, setState, setPaper, setGainRank,
    setAlerts, setAutoGates, setWsStatus, chainSymbol, setChain,
    setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions,
    setPnl, setApiStatus,
  } = useStore()

  const wsRef = useRef<WebSocket | null>(null)
  const wsReconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const wsReconnectAttemptsRef = useRef(0)
  const unmountedRef = useRef(false)
  const failureCountRef = useRef<Record<string, number>>({})

  const markFailure = useCallback((group: string, apiStatus: any) => {
    const count = (failureCountRef.current[group] || 0) + 1
    failureCountRef.current[group] = count
    setApiStatus(withFailureCount(apiStatus, group, count))
    return count
  }, [setApiStatus])

  const markSuccess = useCallback((group: string) => {
    failureCountRef.current[group] = 0
  }, [])

  const pollBroker = useCallback(async () => {
    const [status, holdings, funds, positions] = await Promise.allSettled([
      fetchJSON('/api/broker/dhan/status'),
      fetchJSON('/api/broker/holdings'),
      fetchJSON('/api/broker/funds'),
      fetchJSON('/api/broker/positions/live'),
    ])

    const statusErr = apiError(status, '/api/broker/dhan/status')
    const holdingsErr = apiError(holdings, '/api/broker/holdings')
    const fundsErr = apiError(funds, '/api/broker/funds')
    const positionsErr = apiError(positions, '/api/broker/positions/live')
    const err = statusErr || holdingsErr || fundsErr || positionsErr

    const prev = useStore.getState()
    const retainTransient = err && isTransient(err.code)
    if (err) markFailure('broker', err)
    else markSuccess('broker')

    setBrokerStatus(status.status === 'fulfilled' ? status.value : retainTransient ? (keepLastGood(prev.brokerStatus, err, 'Broker status') || blockedBrokerStatus(statusErr || err)) : blockedBrokerStatus(statusErr || err))
    setBrokerHoldings(holdings.status === 'fulfilled' ? holdings.value : retainTransient ? (keepLastGood(prev.brokerHoldings, err, 'Holdings') || blockedRows(holdingsErr || err, 'Holdings')) : blockedRows(holdingsErr || err, 'Holdings'))
    setBrokerFunds(funds.status === 'fulfilled' ? funds.value : retainTransient ? (keepLastGood(prev.brokerFunds, err, 'Funds') || blockedFunds(fundsErr || err)) : blockedFunds(fundsErr || err))
    setBrokerPositions(positions.status === 'fulfilled' ? positions.value : retainTransient ? (keepLastGood(prev.brokerPositions, err, 'Positions') || blockedRows(positionsErr || err, 'Positions')) : blockedRows(positionsErr || err, 'Positions'))
  }, [setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions, markFailure, markSuccess])

  const poll = useCallback(async () => {
    const [health, state, paper, gainRank, pnl] = await Promise.allSettled([
      fetchJSON('/api/health'),
      fetchJSON('/api/state'),
      fetchJSON('/api/paper'),
      fetchJSON('/api/gain_rank'),
      fetchJSON('/api/pnl'),
    ])

    const err = apiError(health, '/api/health') || apiError(state, '/api/state') || apiError(paper, '/api/paper') || apiError(gainRank, '/api/gain_rank') || apiError(pnl, '/api/pnl')

    const prev = useStore.getState()
    const retainTransient = err && isTransient(err.code)
    if (err) markFailure('core', err)
    else markSuccess('core')

    if (health.status === 'fulfilled') setHealth(health.value)
    else if (!retainTransient || !prev.health) setHealth(fallbackHealth(err))

    if (state.status === 'fulfilled') setState(state.value)
    if (paper.status === 'fulfilled') setPaper(paper.value)
    else if (!retainTransient || !prev.paper) setPaper(blockedPaper(err))

    if (gainRank.status === 'fulfilled') setGainRank(gainRank.value)
    else if (!retainTransient || !prev.gainRank) setGainRank(blockedGainRank(err))

    if (pnl.status === 'fulfilled') setPnl(pnl.value)
    else if (!retainTransient || !prev.pnl) setPnl({ history: [], summary: { total_pnl: 0, total_trades: 0 }, status: err?.status, message: err?.message, blocked: true })
  }, [setHealth, setState, setPaper, setGainRank, setPnl, markFailure, markSuccess])

  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`)
      if (!isRealDhanChainPayload(data)) {
        const blocked = blockedChain(sym, { message: data?.blocked_reason || data?.message || data?.status || 'Option chain response is not proven live Dhan data' })
        markFailure(`chain_${sym}`, { status: 'NO_DHAN_DATA', code: 200, path: `/api/chain/${sym}`, message: blocked.blocked_reason })
        setChain(sym, blocked)
        return
      }
      markSuccess(`chain_${sym}`)
      setChain(sym, { ...data, stale: false, blocked: false, verified_live_dhan: true })
    } catch (err: any) {
      const apiStatus = err instanceof ApiRequestError ? authStatus(`/api/chain/${sym}`, err.status) : { status: 'API_ERROR', code: 0, path: `/api/chain/${sym}`, message: String(err?.message || err) }
      markFailure(`chain_${sym}`, apiStatus)
      setChain(sym, blockedChain(sym, apiStatus))
    }
  }, [setChain, markFailure, markSuccess])

  const pollSecondary = useCallback(async () => {
    const [alerts, gates] = await Promise.allSettled([
      fetchJSON('/api/alerts/recent?limit=30'),
      fetchJSON('/api/auto_gates'),
    ])

    const err = apiError(alerts, '/api/alerts/recent') || apiError(gates, '/api/auto_gates')
    const prev = useStore.getState()
    const retainTransient = err && isTransient(err.code)
    if (err) markFailure('secondary', err)
    else markSuccess('secondary')

    if (alerts.status === 'fulfilled') setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
    else if (!retainTransient || !prev.alerts?.length) setAlerts([])

    if (gates.status === 'fulfilled') setAutoGates(gates.value)
    else if (!retainTransient || !prev.autoGates) setAutoGates(blockedGates(err))
  }, [setAlerts, setAutoGates, markFailure, markSuccess])

  const wsConnect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${proto}//${location.host}/ws/stream`
    const ws = new WebSocket(url)
    wsRef.current = ws
    setWsStatus('connecting')

    ws.onopen = () => {
      wsReconnectAttemptsRef.current = 0
      setWsStatus('live')
    }
    ws.onerror = () => setWsStatus('error')
    ws.onclose = () => {
      setWsStatus('off')
      if (unmountedRef.current) return
      const attempt = wsReconnectAttemptsRef.current
      wsReconnectAttemptsRef.current = attempt + 1
      const baseDelay = Math.min(5000 * 2 ** attempt, 60000)
      const jitter = Math.round(baseDelay * 0.25 * Math.random())
      if (wsReconnectTimerRef.current) clearTimeout(wsReconnectTimerRef.current)
      wsReconnectTimerRef.current = setTimeout(wsConnect, baseDelay + jitter)
    }
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data)
        if (m.type === 'health_update' && m.data) setHealth(m.data)
      } catch {
        // ignore malformed websocket message
      }
    }
  }, [setHealth, setWsStatus])

  useEffect(() => {
    unmountedRef.current = false
    poll()
    pollBroker()
    pollSecondary()
    wsConnect()

    const coreTimer = setInterval(poll, 45000)
    const brokerTimer = setInterval(pollBroker, 60000)
    const secTimer = setInterval(pollSecondary, 120000)

    return () => {
      unmountedRef.current = true
      clearInterval(coreTimer)
      clearInterval(brokerTimer)
      clearInterval(secTimer)
      if (wsReconnectTimerRef.current) clearTimeout(wsReconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [poll, pollBroker, pollSecondary, wsConnect])

  useEffect(() => {
    const TOP_BAR_SYMS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

    pollChain(chainSymbol)
    const fastTimer = setInterval(() => pollChain(chainSymbol), 30000)

    TOP_BAR_SYMS.forEach(sym => { if (sym !== chainSymbol) pollChain(sym) })
    const topBarTimer = setInterval(() => {
      TOP_BAR_SYMS.forEach(sym => { if (sym !== chainSymbol) pollChain(sym) })
    }, 90000)

    return () => {
      clearInterval(fastTimer)
      clearInterval(topBarTimer)
    }
  }, [chainSymbol, pollChain])
}
