import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'
import { API_BASE, API_HEADERS } from '../config'

const BASE = API_BASE || window.location.origin

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
  const r = await fetch(BASE + path, { credentials: 'include', headers: { Accept: 'application/json', ...API_HEADERS } })
  if (!r.ok) throw new ApiRequestError(path, r.status)
  return r.json()
}

const authStatus = (path: string, status: number) => ({
  status: status === 401 ? 'API_AUTH_REQUIRED' : 'API_ERROR',
  code: status,
  path,
  message: status === 401 ? 'Dashboard API auth required. Read-only data is locked until API key/session unlock succeeds.' : `Backend API returned ${status}`,
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

const fallbackPaper = {
  positions: { open_count: 0, open_positions: [] },
  pnl: { summary: { total_pnl: 0, win_rate: 0, total_trades: 0, closed_positions: [] } },
}

const fallbackGainRank = (apiStatus: any) => ({
  rankings: [],
  latest: { predictions: [] },
  status: apiStatus?.status || 'API_LOCKED',
  stale: true,
  message: apiStatus?.message || 'Backend API unavailable',
})

const fallbackGates = (apiStatus: any) => ({
  proof_gates: [
    {
      gate_id: 'api_access',
      name: 'Dashboard API Access',
      status: 'FAIL',
      note: apiStatus?.message || 'Backend API unavailable',
    },
  ],
})

const fallbackBrokerStatus = (apiStatus: any) => ({
  success: false,
  connected: false,
  status: apiStatus?.status || 'API_LOCKED',
  token_status: apiStatus?.status || 'API_LOCKED',
  message: apiStatus?.message || 'Broker API unavailable',
  error: apiStatus?.message || 'Broker API unavailable',
})

const fallbackRows = (apiStatus: any, label: string) => ({
  success: false,
  rows: [],
  count: 0,
  status: apiStatus?.status || 'API_LOCKED',
  message: `${label}: ${apiStatus?.message || 'API unavailable'}`,
  error: apiStatus?.message || 'API unavailable',
})

const fallbackFunds = (apiStatus: any) => ({
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

const fallbackChain = (sym: string, apiStatus: any) => ({
  underlying: sym,
  contracts: [],
  spot: 0,
  pcr: '--',
  status: apiStatus?.status || 'API_LOCKED',
  data_source: apiStatus?.status || 'API_LOCKED',
  message: apiStatus?.message || 'Option chain unavailable',
})

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

    if (err) setApiStatus(err)

    setBrokerStatus(status.status === 'fulfilled' ? status.value : fallbackBrokerStatus(statusErr || err))
    setBrokerHoldings(holdings.status === 'fulfilled' ? holdings.value : fallbackRows(holdingsErr || err, 'Holdings'))
    setBrokerFunds(funds.status === 'fulfilled' ? funds.value : fallbackFunds(fundsErr || err))
    setBrokerPositions(positions.status === 'fulfilled' ? positions.value : fallbackRows(positionsErr || err, 'Positions'))
  }, [setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions, setApiStatus])

  const poll = useCallback(async () => {
    const [health, state, paper, gainRank, pnl] = await Promise.allSettled([
      fetchJSON('/api/health'),
      fetchJSON('/api/state'),
      fetchJSON('/api/paper'),
      fetchJSON('/api/gain_rank'),
      fetchJSON('/api/pnl'),
    ])

    const err = apiError(health, '/api/health') || apiError(state, '/api/state') || apiError(paper, '/api/paper') || apiError(gainRank, '/api/gain_rank') || apiError(pnl, '/api/pnl')

    if (err) {
      setApiStatus(err)
      if (health.status !== 'fulfilled') setHealth(fallbackHealth(err))
      if (paper.status !== 'fulfilled') setPaper(fallbackPaper)
      if (gainRank.status !== 'fulfilled') setGainRank(fallbackGainRank(err))
      if (pnl.status !== 'fulfilled') setPnl({ history: [], summary: { total_pnl: 0, total_trades: 0 }, status: err.status, message: err.message })
    }

    if (health.status === 'fulfilled') setHealth(health.value)
    if (state.status === 'fulfilled') setState(state.value)
    if (paper.status === 'fulfilled') setPaper(paper.value)
    if (gainRank.status === 'fulfilled') setGainRank(gainRank.value)
    if (pnl.status === 'fulfilled') setPnl(pnl.value)
  }, [setHealth, setState, setPaper, setGainRank, setPnl, setApiStatus])

  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`)
      setChain(sym, data)
    } catch (err: any) {
      const apiStatus = err instanceof ApiRequestError ? authStatus(`/api/chain/${sym}`, err.status) : { status: 'API_ERROR', code: 0, path: `/api/chain/${sym}`, message: String(err?.message || err) }
      setApiStatus(apiStatus)
      setChain(sym, fallbackChain(sym, apiStatus))
    }
  }, [setChain, setApiStatus])

  const pollSecondary = useCallback(async () => {
    const [alerts, gates] = await Promise.allSettled([
      fetchJSON('/api/alerts/recent?limit=30'),
      fetchJSON('/api/auto_gates'),
    ])

    const err = apiError(alerts, '/api/alerts/recent') || apiError(gates, '/api/auto_gates')
    if (err) {
      setApiStatus(err)
      if (alerts.status !== 'fulfilled') setAlerts([])
      if (gates.status !== 'fulfilled') setAutoGates(fallbackGates(err))
    }

    if (alerts.status === 'fulfilled') setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
    if (gates.status === 'fulfilled') setAutoGates(gates.value)
  }, [setAlerts, setAutoGates, setApiStatus])

  const wsConnect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${proto}//${location.host}/ws/stream`
    const ws = new WebSocket(url)
    wsRef.current = ws
    setWsStatus('connecting')

    ws.onopen = () => setWsStatus('live')
    ws.onerror = () => setWsStatus('error')
    ws.onclose = () => {
      setWsStatus('off')
      setTimeout(wsConnect, 5000)
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
    poll()
    pollBroker()
    pollSecondary()
    wsConnect()

    const coreTimer = setInterval(poll, 20000)
    const brokerTimer = setInterval(pollBroker, 30000)
    const secTimer = setInterval(pollSecondary, 60000)

    return () => {
      clearInterval(coreTimer)
      clearInterval(brokerTimer)
      clearInterval(secTimer)
      wsRef.current?.close()
    }
  }, [poll, pollBroker, pollSecondary, wsConnect])

  useEffect(() => {
    const TOP_BAR_SYMS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']

    pollChain(chainSymbol)
    const fastTimer = setInterval(() => pollChain(chainSymbol), 5000)

    TOP_BAR_SYMS.forEach(sym => { if (sym !== chainSymbol) pollChain(sym) })
    const topBarTimer = setInterval(() => {
      TOP_BAR_SYMS.forEach(sym => { if (sym !== chainSymbol) pollChain(sym) })
    }, 30000)

    return () => {
      clearInterval(fastTimer)
      clearInterval(topBarTimer)
    }
  }, [chainSymbol, pollChain])
}

