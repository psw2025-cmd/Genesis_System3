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
  message: status === 401 ? 'Backend API requires X-API-Key; dashboard is in read-only locked view.' : `Backend API returned ${status}`,
})

const fallbackHealth = (apiStatus: any) => ({
  mode: 'PAPER',
  data_source: apiStatus?.status || 'API_LOCKED',
  qc_status: apiStatus?.status || 'API_LOCKED',
  live_allowed: false,
  broker: { connected: false, status: apiStatus?.status || 'API_LOCKED' },
  market: { is_open: false },
  live_blockers: [apiStatus?.message || 'Backend API unavailable'],
})

const fallbackPaper = { positions: { open_count: 0, open_positions: [] }, pnl: { summary: { total_pnl: 0, win_rate: 0, total_trades: 0, closed_positions: [] } } }
const fallbackGainRank = (apiStatus: any) => ({ rankings: [], status: apiStatus?.status || 'API_LOCKED', message: apiStatus?.message || 'Backend API unavailable' })
const fallbackGates = (apiStatus: any) => ({ gates: { api_access: { status: 'BLOCKED', note: apiStatus?.message || 'Backend API unavailable' } } })

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

  const wsRef   = useRef<WebSocket | null>(null)

  // ── BROKER data — works even when market closed ───────────────────────────
  const pollBroker = useCallback(async () => {
    const [status, holdings, funds, positions] = await Promise.allSettled([
      fetchJSON('/api/broker/dhan/status'),
      fetchJSON('/api/broker/holdings'),
      fetchJSON('/api/broker/funds'),
      fetchJSON('/api/broker/positions/live'),
    ])
    const err = apiError(status, '/api/broker/dhan/status') || apiError(holdings, '/api/broker/holdings') || apiError(funds, '/api/broker/funds') || apiError(positions, '/api/broker/positions/live')
    if (err) setApiStatus(err)
    if (status.status   === 'fulfilled') setBrokerStatus(status.value)
    if (holdings.status === 'fulfilled') setBrokerHoldings(holdings.value)
    if (funds.status    === 'fulfilled') setBrokerFunds(funds.value)
    if (positions.status=== 'fulfilled') setBrokerPositions(positions.value)
  }, [setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions, setApiStatus])

  // ── Core REST poll ────────────────────────────────────────────────────────
  const poll = useCallback(async () => {
    const [health, state, paper, gainRank, pnl] = await Promise.allSettled([
      fetchJSON('/api/health'),
      fetchJSON('/api/state'),
      fetchJSON('/api/paper'),
      fetchJSON('/api/gain_rank'),
      fetchJSON('/api/pnl'),
    ])
    const err = apiError(health, '/api/health') || apiError(state, '/api/state') || apiError(paper, '/api/paper') || apiError(gainRank, '/api/gain_rank')
    if (err) {
      setApiStatus(err)
      setHealth(fallbackHealth(err))
      setPaper(fallbackPaper)
      setGainRank(fallbackGainRank(err))
    }
    if (health.status   === 'fulfilled') setHealth(health.value)
    if (state.status    === 'fulfilled') setState(state.value)
    if (paper.status    === 'fulfilled') setPaper(paper.value)
    if (gainRank.status === 'fulfilled') setGainRank(gainRank.value)
    if (pnl.status      === 'fulfilled') setPnl(pnl.value)
  }, [setHealth, setState, setPaper, setGainRank, setPnl, setApiStatus])

  // ── Chain poll ────────────────────────────────────────────────────────────
  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`)
      setChain(sym, data)
    } catch (err: any) {
      if (err instanceof ApiRequestError) setApiStatus(authStatus(`/api/chain/${sym}`, err.status))
    }
  }, [setChain, setApiStatus])

  // ── Secondary data ────────────────────────────────────────────────────────
  const pollSecondary = useCallback(async () => {
    const [alerts, gates] = await Promise.allSettled([
      fetchJSON('/api/alerts/recent?limit=30'),
      fetchJSON('/api/auto_gates'),
    ])
    const err = apiError(alerts, '/api/alerts/recent') || apiError(gates, '/api/auto_gates')
    if (err) {
      setApiStatus(err)
      setAutoGates(fallbackGates(err))
    }
    if (alerts.status === 'fulfilled') setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
    if (gates.status  === 'fulfilled') setAutoGates(gates.value)
  }, [setAlerts, setAutoGates, setApiStatus])

  // ── WebSocket ─────────────────────────────────────────────────────────────
  const wsConnect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url   = `${proto}//${location.host}/ws/stream`
    const ws    = new WebSocket(url)
    wsRef.current = ws
    setWsStatus('connecting')

    ws.onopen  = () => setWsStatus('live')
    ws.onerror = () => setWsStatus('error')
    ws.onclose = () => {
      setWsStatus('off')
      setTimeout(wsConnect, 5000)  // auto-reconnect 5s
    }
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data)
        if (m.type === 'health_update' && m.data) setHealth(m.data)
      } catch { /* ignore */ }
    }
  }, [setHealth, setWsStatus])

  useEffect(() => {
    // Load everything immediately on mount
    poll()
    pollBroker()     // broker data — market-independent
    pollSecondary()
    wsConnect()

    // Core: every 20s
    const coreTimer = setInterval(poll, 20000)
    // Broker: every 30s (rate-limited by backend TTL cache)
    const brokerTimer = setInterval(pollBroker, 30000)
    // Secondary: every 60s
    const secTimer = setInterval(pollSecondary, 60000)

    return () => {
      clearInterval(coreTimer)
      clearInterval(brokerTimer)
      clearInterval(secTimer)
      wsRef.current?.close()
    }
  }, [poll, pollBroker, pollSecondary, wsConnect])

  // Chain poll — selected symbol every 5s + TopBar symbols every 30s
  useEffect(() => {
    const TOP_BAR_SYMS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']

    // Poll selected chain symbol fast (5s) for option chain tab
    pollChain(chainSymbol)
    const fastTimer = setInterval(() => pollChain(chainSymbol), 5000)

    // Poll all TopBar symbols at startup for spot prices
    TOP_BAR_SYMS.forEach(sym => { if (sym !== chainSymbol) pollChain(sym) })
    // Refresh TopBar spots every 30s (just need spot price, not full chain)
    const topBarTimer = setInterval(() => {
      TOP_BAR_SYMS.forEach(sym => { if (sym !== chainSymbol) pollChain(sym) })
    }, 30000)

    return () => {
      clearInterval(fastTimer)
      clearInterval(topBarTimer)
    }
  }, [chainSymbol, pollChain])
}
