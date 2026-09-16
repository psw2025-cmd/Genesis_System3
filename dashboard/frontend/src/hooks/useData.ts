import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'
import { API_BASE, API_HEADERS } from '../config'
import { mergeAuthoritativeBrokerStatus } from '../lib/brokerStatus'

const BASE = API_BASE || window.location.origin

// Cloud Run / dashboard can return 429/5xx during bursts. These are transient; keep last
// good values instead of flashing the whole UI red.
const TRANSIENT_STATUS = new Set([0, 429, 502, 503, 504, 520, 521, 522, 523, 524])
const isTransient = (status?: number) => TRANSIENT_STATUS.has(Number(status ?? -1))

const ENABLED_CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
const OPTIONAL_CHAIN_SYMBOLS = ['SENSEX', 'RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK']
const isOptionalChain = (sym: string) => OPTIONAL_CHAIN_SYMBOLS.includes(String(sym || '').toUpperCase())

// HTTP is backup only. Live market-hours ticks must come from WS cache pushes.
// Fast HTTP chain polls during market hours were stampeding Dhan (~1 OC / 3s).
const CORE_POLL_MS_OPEN = 20000
const CORE_POLL_MS_CLOSED = 60000
const BROKER_POLL_MS = 30000
const SECONDARY_POLL_MS = 180000
const ACTIVE_CHAIN_POLL_MS_OPEN = 30000
const ACTIVE_CHAIN_POLL_MS_CLOSED = 60000
const TOPBAR_CHAIN_POLL_MS_OPEN = 60000
const TOPBAR_CHAIN_POLL_MS_CLOSED = 180000
const LIVE_BOARD_POLL_MS_OPEN = 5000
const LIVE_BOARD_POLL_MS_CLOSED = 30000

type ApiErrorKind = 'http' | 'timeout' | 'network'

class ApiRequestError extends Error {
  status: number
  path: string
  kind: ApiErrorKind

  constructor(path: string, status: number, kind: ApiErrorKind = 'http') {
    super(`${kind}:${status}`)
    this.name = 'ApiRequestError'
    this.path = path
    this.status = status
    this.kind = kind
  }
}

async function fetchJSON(path: string, timeoutMs = 20000) {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const r = await fetch(BASE + path, {
      credentials: 'include',
      headers: { Accept: 'application/json', ...API_HEADERS },
      signal: ctrl.signal,
    })
    if (!r.ok) throw new ApiRequestError(path, r.status)
    return r.json()
  } catch (err: any) {
    if (err instanceof ApiRequestError) throw err
    if (err?.name === 'AbortError') throw new ApiRequestError(path, 0, 'timeout')
    throw new ApiRequestError(path, 0, 'network')
  } finally {
    clearTimeout(timer)
  }
}

const authStatus = (path: string, status: number, kind: ApiErrorKind = 'http') => ({
  status: status === 401
    ? 'API_AUTH_REQUIRED'
    : kind === 'timeout'
      ? 'REQUEST_TIMEOUT'
      : kind === 'network'
        ? 'NETWORK_ERROR'
        : isTransient(status)
          ? (status === 429 ? 'RATE_LIMITED' : 'CLOUD_DEGRADED')
          : 'API_ERROR',
  code: status,
  path,
  error_kind: kind,
  severity: status === 401 ? 'locked' : isTransient(status) ? 'transient' : 'error',
  message: status === 401
    ? 'Dashboard authentication is required. Read-only data remains locked until a valid session is established.'
    : kind === 'timeout'
      ? `Request to ${path} timed out. Keeping last good data while the backend or cache recovers.`
      : kind === 'network'
        ? `The browser could not reach ${path}. Check connectivity or service availability; keeping last good data.`
        : status === 429
          ? `Backend rate-limited ${path}. Keeping last good data and using slower polling.`
          : isTransient(status)
            ? `Cloud Run/backend returned ${status} for ${path}. Keeping last good data where available.`
            : `Backend API returned ${status}`,
})

const fallbackHealth = (apiStatus: any) => ({
  mode: 'PAPER',
  data_source: apiStatus?.status || 'API_LOCKED',
  qc_status: apiStatus?.status || 'API_LOCKED',
  live_allowed: false,
  broker: { connected: false, status: apiStatus?.status || 'API_LOCKED' },
  market: { is_open: false, reason: apiStatus?.message || 'API temporarily offline', next_open: '--' },
  live_blockers: [apiStatus?.message || 'API temporarily offline'],
})

const pendingPaper = (apiStatus: any) => ({
  positions: { open_count: 0, open_positions: [] },
  pnl: { summary: { total_pnl: 0, win_rate: 0, total_trades: 0, closed_positions: [] } },
  status: apiStatus?.status || 'NO_REAL_PAPER_DATA',
  pendingProof: true,
  pending_reason: apiStatus?.message || 'Paper data pending',
})

const pendingGainRank = (apiStatus: any) => ({
  rankings: [],
  latest: { predictions: [] },
  status: apiStatus?.status || 'NO_REAL_RANK_DATA',
  pendingProof: true,
  stale: false,
  message: apiStatus?.message || 'API temporarily offline',
})

const pendingGates = (apiStatus: any) => ({
  proof_gates: [
    { gate_id: 'api_access', name: 'Dashboard API Access', status: 'FAIL', note: apiStatus?.message || 'API temporarily offline' },
  ],
})

const pendingBrokerStatus = (apiStatus: any) => ({
  success: false,
  connected: false,
  status: apiStatus?.status || 'API_LOCKED',
  token_status: apiStatus?.status || 'API_LOCKED',
  message: apiStatus?.message || 'Broker API pending',
  error: apiStatus?.message || 'Broker API pending',
})

const pendingRows = (apiStatus: any, label: string) => ({
  success: false,
  rows: [],
  count: 0,
  status: apiStatus?.status || 'API_LOCKED',
  pendingProof: true,
  message: `${label}: ${apiStatus?.message || 'API pending'}`,
  error: apiStatus?.message || 'API pending',
})

const pendingFunds = (apiStatus: any) => ({
  success: false,
  normalized: {
    available_balance: null,
    utilized_amount: null,
    total_limit: null,
    raw: { status: 'failure', remarks: { error_code: apiStatus?.code || 'API_LOCKED', error_type: apiStatus?.status || 'API_ERROR', error_message: apiStatus?.message || 'Funds data pending' } },
  },
  message: apiStatus?.message || 'Funds data pending',
  error: apiStatus?.message || 'Funds data pending',
})

const pendingChain = (sym: string, apiStatus: any) => ({
  underlying: sym,
  contracts: [],
  spot: 0,
  pcr: '--',
  status: 'NO_DHAN_DATA',
  pendingProof: true,
  pending_reason: apiStatus?.message || 'Option chain pending',
  data_source: 'dhan',
  source_priority: isOptionalChain(sym) ? 'optional_symbol_pending' : 'pending_real_dhan_stream',
  stale: false,
  optional: isOptionalChain(sym),
  message: apiStatus?.message || 'Option chain pending',
})

function isRealDhanChainPayload(data: any) {
  if (!data || typeof data !== 'object') return false
  const source = String(data.data_source || data.source || '').toLowerCase()
  const priority = String(data.source_priority || '').toLowerCase()
  const status = String(data.status || '').toUpperCase()
  const combined = `${source} ${priority} ${status}`
  // Reject fake/non-Dhan sources. Allow market-closed verified Dhan snapshots.
  if (/(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock)/i.test(combined)) return false
  if (data.stale === true && !/MARKET_CLOSED|SNAPSHOT/i.test(status) && data.snapshot !== true && data.live !== false) {
    return false
  }
  const contracts = Number(data.total_contracts || (Array.isArray(data.contracts) ? data.contracts.length : 0))
  const spot = Number(data.spot || 0)
  const dhanish = source === 'dhan' || priority.startsWith('dhan') || priority.includes('worker_push')
  return dhanish && spot > 0 && contracts > 0
}

function isChainWarmingPayload(data: any) {
  if (!data || typeof data !== 'object') return false
  const status = String(data.status || '').toUpperCase()
  return status === 'CHAIN_CACHE_WARMING' || status === 'NO_DHAN_DATA'
}

function keepLastGood(previous: any, apiStatus: any, label: string) {
  if (!previous) return null
  return {
    ...previous,
    stale: true,
    transient_error: true,
    degraded_at: new Date().toISOString(),
    last_warning: `${label}: ${apiStatus?.message || 'temporary API failure'}`,
    status: previous.status || 'TRANSIENT_CACHE',
  }
}

function withFailureCount(apiStatus: any, group: string, count: number) {
  return {
    ...apiStatus,
    group,
    consecutive_failures: count,
    message: count < 3 ? `${apiStatus.message} Retrying slowly; last good truth remains visible where available.` : apiStatus.message,
  }
}

function apiError(result: PromiseSettledResult<any>, path: string) {
  if (result.status === 'rejected' && result.reason instanceof ApiRequestError) return authStatus(path, result.reason.status, result.reason.kind)
  if (result.status === 'rejected') return { status: 'API_ERROR', code: 0, path, message: String(result.reason?.message || result.reason) }
  return null
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function useData() {
  const {
    setHealth, setState, setPaper, setGainRank, setMarketTop,
    setAlerts, setAlertFeedStatus, setAutoGates, setWsStatus, chainSymbol, setChain,
    setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions,
    setLiveBoard, setPnl, setApiStatus, setDeployInfo, setResearch,
  } = useStore()

  const wsRef = useRef<WebSocket | null>(null)
  const wsReconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const wsReconnectAttemptsRef = useRef(0)
  const unmountedRef = useRef(false)
  const failureCountRef = useRef<Record<string, number>>({})

  const markFailure = useCallback((group: string, apiStatus: any) => {
    if (group.startsWith('chain_') && isOptionalChain(group.replace('chain_', ''))) return 0
    const count = (failureCountRef.current[group] || 0) + 1
    failureCountRef.current[group] = count
    setApiStatus(withFailureCount(apiStatus, group, count))
    return count
  }, [setApiStatus])

  const markSuccess = useCallback((group: string) => {
    failureCountRef.current[group] = 0
    // Clear sticky NETWORK_ERROR / CLOUD_DEGRADED once a group recovers,
    // otherwise TopBar stays DHAN DEGRADED forever after one failed poll.
    const remaining = Object.values(failureCountRef.current).some((n) => Number(n) > 0)
    if (!remaining) setApiStatus(null as any)
  }, [setApiStatus])

  const pollBroker = useCallback(async () => {
    try {
      const batch = await fetchJSON('/api/batch/positions-holdings')
      markSuccess('broker')
      let brokerStatus = batch?.broker_status || pendingBrokerStatus({ message: 'batch missing broker_status' })
      // Batch broker state can lag; always converge it with the authoritative endpoint.
      try {
        const full = await fetchJSON('/api/broker/status', 12000)
        brokerStatus = mergeAuthoritativeBrokerStatus(brokerStatus, full)
      } catch {
        // Keep batch status and its last-known-safe metadata when full status is unavailable.
      }
      setBrokerStatus(brokerStatus)
      setBrokerHoldings(batch?.holdings || pendingRows({ message: 'batch missing holdings' }, 'Holdings'))
      setBrokerFunds(batch?.funds || pendingFunds({ message: 'batch missing funds' }))
      setBrokerPositions(batch?.positions || pendingRows({ message: 'batch missing positions' }, 'Positions'))
    } catch (err: any) {
      const apiStatus = err instanceof ApiRequestError
        ? authStatus('/api/batch/positions-holdings', err.status, err.kind)
        : { status: 'API_ERROR', code: 0, path: '/api/batch/positions-holdings', message: String(err?.message || err) }
      const prev = useStore.getState()
      const retainTransient = isTransient(apiStatus.code)
      markFailure('broker', apiStatus)
      if (retainTransient) {
        if (prev.brokerStatus) setBrokerStatus(keepLastGood(prev.brokerStatus, apiStatus, 'Broker status') || prev.brokerStatus)
        if (prev.brokerHoldings) setBrokerHoldings(keepLastGood(prev.brokerHoldings, apiStatus, 'Holdings') || prev.brokerHoldings)
        if (prev.brokerFunds) setBrokerFunds(keepLastGood(prev.brokerFunds, apiStatus, 'Funds') || prev.brokerFunds)
        if (prev.brokerPositions) setBrokerPositions(keepLastGood(prev.brokerPositions, apiStatus, 'Positions') || prev.brokerPositions)
      } else {
        setBrokerStatus(pendingBrokerStatus(apiStatus))
        setBrokerHoldings(pendingRows(apiStatus, 'Holdings'))
        setBrokerFunds(pendingFunds(apiStatus))
        setBrokerPositions(pendingRows(apiStatus, 'Positions'))
      }
    }
  }, [setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions, markFailure, markSuccess])

  const pollLiveBoard = useCallback(async () => {
    try {
      const board = await fetchJSON('/api/market/live_board', 12000)
      if (board && typeof board === 'object') {
        setLiveBoard(board)
        markSuccess('live_board')
        // Merge index spots into chain so TopBar stays continuous even between OC polls.
        for (const row of board.indices || []) {
          const sym = String(row?.symbol || '').toUpperCase()
          if (!sym || !(Number(row?.ltp) > 0)) continue
          const prev = useStore.getState().chain?.[sym] || {}
          setChain(sym, {
            ...prev,
            spot: Number(row.ltp),
            change_pct: row.change_pct == null ? prev.change_pct : Number(row.change_pct),
            pct_change: row.change_pct == null ? prev.pct_change : Number(row.change_pct),
            live_board: true,
            source: 'dhan_live_board',
          })
        }
      }
    } catch {
      // Keep last-good board; TopBar falls back to chain spots.
    }
  }, [setLiveBoard, setChain, markSuccess])

  const poll = useCallback(async () => {
    try {
      const [batchResult, stateResult] = await Promise.allSettled([
        fetchJSON('/api/batch/market-data', 25000),
        fetchJSON('/api/state', 20000),
      ])
      if (batchResult.status !== 'fulfilled') throw batchResult.reason
      const batch = batchResult.value
      markSuccess('core')
      if (batch?.health) setHealth(batch.health)
      // Batch state is a slim health-shaped snapshot. Prefer /api/state for live risk/PnL/cycle.
      if (stateResult.status === 'fulfilled' && stateResult.value && typeof stateResult.value === 'object') {
        setState(stateResult.value)
      } else if (batch?.state) {
        setState(batch.state)
      }
      if (batch?.paper) setPaper(batch.paper)
      else setPaper(pendingPaper({ message: 'batch missing paper' }))
      if (batch?.gain_rank) setGainRank(batch.gain_rank)
      else setGainRank(pendingGainRank({ message: 'batch missing gain_rank' }))
      if (batch?.pnl) setPnl(batch.pnl)
      else setPnl({ history: [], summary: { total_pnl: 0, total_trades: 0 }, status: 'NO_DATA', pendingProof: true })
      // Secondary alerts/gates also arrive in market-data batch (one round-trip).
      if (Array.isArray(batch?.alerts?.alerts)) {
        setAlerts(batch.alerts.alerts)
        setAlertFeedStatus({ state: 'ready', source: '/api/batch/market-data', updatedAt: new Date().toISOString() })
      } else {
        setAlertFeedStatus({ state: 'degraded', source: '/api/batch/market-data', message: 'Market-data batch did not include an authoritative alert feed.' })
      }
      if (batch?.auto_gates) setAutoGates(batch.auto_gates)
    } catch (err: any) {
      const apiStatus = err instanceof ApiRequestError
        ? authStatus('/api/batch/market-data', err.status, err.kind)
        : { status: 'API_ERROR', code: 0, path: '/api/batch/market-data', message: String(err?.message || err) }
      const prev = useStore.getState()
      const retainTransient = isTransient(apiStatus.code)
      markFailure('core', apiStatus)
      setAlertFeedStatus({ state: 'degraded', source: '/api/batch/market-data', message: apiStatus.message })
      if (!retainTransient || !prev.health) setHealth(fallbackHealth(apiStatus))
      if (!retainTransient || !prev.paper) setPaper(pendingPaper(apiStatus))
      if (!retainTransient || !prev.gainRank) setGainRank(pendingGainRank(apiStatus))
      if (!retainTransient || !prev.pnl) {
        setPnl({ history: [], summary: { total_pnl: 0, total_trades: 0 }, status: apiStatus.status, message: apiStatus.message, pendingProof: true })
      }
    }
  }, [setHealth, setState, setPaper, setGainRank, setPnl, setAlerts, setAlertFeedStatus, setAutoGates, markFailure, markSuccess])

  const applyChainPayload = useCallback((sym: string, data: any) => {
    if (!isRealDhanChainPayload(data)) {
      const prev = useStore.getState().chain?.[sym]
      // Never wipe a previously good chain for empty/rate-limited/closed payloads.
      if (prev && (isRealDhanChainPayload(prev) || (Array.isArray(prev.contracts) && prev.contracts.length > 0 && Number(prev.spot || 0) > 0))) {
        setChain(sym, {
          ...prev,
          snapshot: true,
          live: false,
          verified_live_dhan: false,
          stale: true,
          status: prev.status || 'DHAN_LAST_GOOD',
          message: data?.message || data?.pending_reason || 'Keeping last good Dhan chain (live refresh pending)',
        })
        return
      }
      // After-hours / cold-cache warm is expected — never paint sticky NETWORK_ERROR.
      if (isChainWarmingPayload(data)) {
        setChain(sym, {
          underlying: sym,
          contracts: [],
          spot: 0,
          pcr: 1,
          total_contracts: 0,
          data_source: 'dhan',
          status: String(data.status || 'CHAIN_CACHE_WARMING'),
          stale: true,
          snapshot: true,
          live: false,
          pendingProof: false,
          optional: isOptionalChain(sym),
          message: data.message || 'Index chain warming from Dhan cache',
        })
        return
      }
      const pendingItem = pendingChain(sym, { message: data?.pending_reason || data?.message || data?.status || 'Option chain response is not proven Dhan data' })
      if (!isOptionalChain(sym)) markFailure(`chain_${sym}`, { status: 'NO_DHAN_DATA', code: 200, path: `/api/batch/chains`, message: pendingItem.pending_reason })
      setChain(sym, pendingItem)
      return
    }
    markSuccess(`chain_${sym}`)
    const isSnapshot = data?.snapshot === true || data?.live === false || /MARKET_CLOSED/i.test(String(data?.status || ''))
    setChain(sym, {
      ...data,
      stale: Boolean(isSnapshot || data?.stale),
      pendingProof: false,
      verified_live_dhan: !isSnapshot,
      verified_dhan_snapshot: Boolean(isSnapshot),
      optional: isOptionalChain(sym),
      stream_tick_at: new Date().toISOString(),
    })
  }, [setChain, markFailure, markSuccess])

  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`, 12000)
      applyChainPayload(sym, data)
    } catch (err: any) {
      const apiStatus = err instanceof ApiRequestError ? authStatus(`/api/chain/${sym}`, err.status, err.kind) : { status: 'API_ERROR', code: 0, path: `/api/chain/${sym}`, message: String(err?.message || err) }
      const prev = useStore.getState().chain?.[sym]
      const retain = isTransient(apiStatus.code) || apiStatus.status === 'API_AUTH_REQUIRED' || Boolean(prev?.contracts?.length)
      // Soft-fail individual chain: do not overwrite Overview with NETWORK_ERROR when
      // batch path is the primary source of truth (especially after hours).
      if (!isOptionalChain(sym) && apiStatus.status === 'API_AUTH_REQUIRED') markFailure(`chain_${sym}`, apiStatus)
      if (retain && prev) setChain(sym, keepLastGood(prev, apiStatus, `${sym} chain`) || pendingChain(sym, apiStatus))
      else setChain(sym, {
        ...pendingChain(sym, apiStatus),
        status: 'CHAIN_CACHE_WARMING',
        pendingProof: false,
        message: apiStatus.message || 'Waiting for Dhan chain cache',
      })
    }
  }, [applyChainPayload, setChain, markFailure])

  const pollAllChains = useCallback(async () => {
    try {
      const batch = await fetchJSON('/api/batch/chains', 15000)
      const chains = batch?.chains && typeof batch.chains === 'object' ? batch.chains : {}
      ENABLED_CHAIN_SYMBOLS.forEach((sym) => {
        if (chains[sym]) applyChainPayload(sym, chains[sym])
        else applyChainPayload(sym, { status: 'CHAIN_CACHE_WARMING', data_source: 'dhan', message: 'Missing from batch chains' })
      })
      // Batch OK clears sticky chain_* NETWORK_ERROR leftovers.
      ENABLED_CHAIN_SYMBOLS.forEach((sym) => { failureCountRef.current[`chain_${sym}`] = 0 })
      markSuccess('chains_batch')
    } catch (err: any) {
      const apiStatus = err instanceof ApiRequestError
        ? authStatus('/api/batch/chains', err.status, err.kind)
        : { status: 'API_ERROR', code: 0, path: '/api/batch/chains', message: String(err?.message || err) }
      markFailure('chains_batch', apiStatus)
      // Soft fallback only when market likely open; after-hours keep warming placeholders.
      const marketOpen = Boolean(useStore.getState().marketOpen)
      if (marketOpen) {
        ENABLED_CHAIN_SYMBOLS.forEach((sym, idx) => {
          setTimeout(() => { if (!unmountedRef.current) void pollChain(sym) }, 250 * (idx + 1))
        })
      } else {
        ENABLED_CHAIN_SYMBOLS.forEach((sym) => {
          applyChainPayload(sym, { status: 'CHAIN_CACHE_WARMING', data_source: 'dhan', message: 'Batch chains timeout — waiting for cache warm' })
        })
      }
    }
  }, [applyChainPayload, pollChain, markFailure, markSuccess])

  const pollRuntimeFacts = useCallback(async () => {
    console.log('[pollRuntimeFacts] starting')
    const [deploy, research, workspace] = await Promise.allSettled([
      fetchJSON('/api/deploy/info', 12000),
      fetchJSON('/api/research/multibagger', 15000),
      fetchJSON('/api/multibagger', 12000),
    ])
    console.log('[pollRuntimeFacts] deploy:', deploy.status, 'research:', research.status, 'workspace:', workspace.status, 'candidates:', workspace.status === 'fulfilled' ? workspace.value?.candidates?.length : null)
    if (deploy.status === 'fulfilled') setDeployInfo(deploy.value)
    if (workspace.status === 'fulfilled' && workspace.value?.candidates?.length > 0) {
      console.log('[pollRuntimeFacts] setting research to workspace:', workspace.value)
      setResearch(workspace.value)
    } else if (research.status === 'fulfilled') {
      console.log('[pollRuntimeFacts] setting research to research:', research.value)
      setResearch(research.value)
    }
  }, [setDeployInfo, setResearch])

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

    if (alerts.status === 'fulfilled') {
      setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
      setAlertFeedStatus({ state: 'ready', source: '/api/alerts/recent', updatedAt: new Date().toISOString() })
    } else {
      setAlertFeedStatus({ state: 'degraded', source: '/api/alerts/recent', message: apiError(alerts, '/api/alerts/recent')?.message || 'Alert feed request failed.' })
    }

    if (gates.status === 'fulfilled') setAutoGates(gates.value)
    else if (!retainTransient || !prev.autoGates) setAutoGates(pendingGates(err))
  }, [setAlerts, setAlertFeedStatus, setAutoGates, markFailure, markSuccess])

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
      const baseDelay = Math.min(10000 * 2 ** attempt, 120000)
      const jitter = Math.round(baseDelay * 0.25 * Math.random())
      if (wsReconnectTimerRef.current) clearTimeout(wsReconnectTimerRef.current)
      wsReconnectTimerRef.current = setTimeout(wsConnect, baseDelay + jitter)
    }
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data)
        if (m.type === 'market_status') {
          if (typeof m.market_open === 'boolean') {
            useStore.setState({ marketOpen: m.market_open })
          }
        }
        if (m.type === 'health_update' && m.data) setHealth(m.data)
        if (m.type === 'paper_update' && m.data) setPaper(m.data)
        if (m.type === 'positions_update' && m.data) {
          const prev = useStore.getState().paper || {}
          setPaper({
            ...prev,
            positions: m.data,
          })
        }
        if (m.type === 'pnl_update' && m.data) {
          setPnl(m.data)
          const prev = useStore.getState().paper || {}
          setPaper({
            ...prev,
            pnl: m.data?.summary ? m.data : { summary: m.data, history: m.data?.history || [] },
          })
        }
        if (m.type === 'chain_spots_update' && m.data && typeof m.data === 'object') {
          Object.entries(m.data).forEach(([sym, info]: [string, any]) => {
            const key = String(sym || '').toUpperCase()
            if (!key || !info) return
            const prev = useStore.getState().chain?.[key] || { underlying: key, contracts: [] }
            setChain(key, {
              ...prev,
              underlying: key,
              spot: Number(info.spot || prev.spot || 0),
              total_contracts: info.n ?? prev.total_contracts,
              status: info.status || prev.status,
              data_source: info.src || prev.data_source || 'dhan',
              stream_tick_at: m.timestamp || new Date().toISOString(),
              live: Boolean(useStore.getState().marketOpen),
            })
          })
        }
        if (m.type === 'chain_update' && m.data) {
          const sym = String(m.data.underlying || m.symbol || '').toUpperCase()
          if (sym && isRealDhanChainPayload(m.data)) {
            const isSnapshot = m.data?.snapshot === true || m.data?.live === false || /MARKET_CLOSED/i.test(String(m.data?.status || ''))
            setChain(sym, {
              ...m.data,
              stale: Boolean(isSnapshot || m.data?.stale),
              pendingProof: false,
              verified_live_dhan: !isSnapshot,
              verified_dhan_snapshot: Boolean(isSnapshot),
              optional: isOptionalChain(sym),
              stream_tick_at: m.timestamp || new Date().toISOString(),
            })
          }
        }
        if (m.type === 'market_top_update' && m.data) {
          setMarketTop({
            ...m.data,
            stream_mode: m.data.stream_mode || 'ultra_micro',
            ws_timestamp: m.timestamp,
          })
          const table = m.data.market_top_table || []
          if (Array.isArray(table) && table.length) {
            const rankings = table.slice(0, 25).map((row: any) => {
              const opt = String(row.option_type || '').toUpperCase()
              return {
                rank: row.rank,
                underlying: String(row.underlying || row.symbol || '').toUpperCase(),
                direction: opt === 'CE' ? 'UP' : 'DOWN',
                option_type: opt,
                strike: row.strike,
                expiry_date: row.expiry_date,
                ltp: row.ltp,
                change: row.change ?? row.change_rs,
                volume: row.volume,
                oi: row.oi,
                gain_rank: Number(row.gain_pct || 0),
                gain_pct: Number(row.gain_pct || 0),
                option_eligible: true,
                recommendation: 'WATCH',
                market_match_note: row.market_match_note,
                data_provenance: row.data_provenance,
                refreshed_at: row.refreshed_at || m.data.refreshed_at,
                source: 'ws_market_top_micro',
              }
            })
            setGainRank({
              status: 'ok',
              rankings,
              latest: { date: new Date().toISOString().slice(0, 10), rankings, source: 'ws_market_top_micro' },
              source: 'ws_market_top_micro',
              refreshed_at: m.data.refreshed_at,
            })
          }
        }
        if (m.type === 'heartbeat') {
          // WS transport is healthy if the socket is open. Cache-age stream_ok=false
          // means paced Dhan refresh is catching up — keep LIVE, not a false
          // "WebSocket error / Disconnected" top-bar state.
          const socketOpen = wsRef.current?.readyState === WebSocket.OPEN
          if (socketOpen) setWsStatus('live')
          else if (m.market_open && m.stream_ok === false) setWsStatus('error')
          else setWsStatus('live')
          if (typeof m.market_open === 'boolean') {
            useStore.setState({ marketOpen: m.market_open })
          }
        }
      } catch {
        // ignore malformed websocket message
      }
    }
  }, [setHealth, setWsStatus, setPaper, setPnl, setMarketTop, setGainRank, setChain])

  useEffect(() => {
    unmountedRef.current = false
    // Boot with market-data, broker batch, live board, and deploy/research facts.
    void Promise.all([poll(), pollBroker(), pollLiveBoard(), pollRuntimeFacts()])
    wsConnect()

    let coreTimer: ReturnType<typeof setInterval> | null = null
    let brokerTimer: ReturnType<typeof setInterval> | null = null
    let liveBoardTimer: ReturnType<typeof setInterval> | null = null
    let secTimer: ReturnType<typeof setInterval> | null = null

    const armTimers = () => {
      if (coreTimer) clearInterval(coreTimer)
      if (brokerTimer) clearInterval(brokerTimer)
      if (liveBoardTimer) clearInterval(liveBoardTimer)
      if (secTimer) clearInterval(secTimer)
      const open = useStore.getState().marketOpen
      coreTimer = setInterval(poll, open ? CORE_POLL_MS_OPEN : CORE_POLL_MS_CLOSED)
      brokerTimer = setInterval(pollBroker, BROKER_POLL_MS)
      liveBoardTimer = setInterval(pollLiveBoard, open ? LIVE_BOARD_POLL_MS_OPEN : LIVE_BOARD_POLL_MS_CLOSED)
      // alerts/gates already included in market-data batch; keep rare secondary refresh as safety net
      secTimer = setInterval(pollSecondary, SECONDARY_POLL_MS)
    }
    armTimers()
    const runtimeTimer = setInterval(pollRuntimeFacts, SECONDARY_POLL_MS)
    const modeTimer = setInterval(armTimers, 30000)

    return () => {
      unmountedRef.current = true
      if (coreTimer) clearInterval(coreTimer)
      if (brokerTimer) clearInterval(brokerTimer)
      if (liveBoardTimer) clearInterval(liveBoardTimer)
      if (secTimer) clearInterval(secTimer)
      clearInterval(runtimeTimer)
      clearInterval(modeTimer)
      if (wsReconnectTimerRef.current) clearTimeout(wsReconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [poll, pollBroker, pollLiveBoard, pollSecondary, pollRuntimeFacts, wsConnect])

  useEffect(() => {
    const active = String(chainSymbol || 'NIFTY').toUpperCase()
    // One cache-only batch for all index chains (TopBar) + short active-chain refresh.
    void pollAllChains()
    void pollChain(active)

    let activeTimer: ReturnType<typeof setInterval> | null = null
    let topBarTimer: ReturnType<typeof setInterval> | null = null

    const armChainTimers = () => {
      if (activeTimer) clearInterval(activeTimer)
      if (topBarTimer) clearInterval(topBarTimer)
      const open = useStore.getState().marketOpen
      activeTimer = setInterval(() => pollChain(active), open ? ACTIVE_CHAIN_POLL_MS_OPEN : ACTIVE_CHAIN_POLL_MS_CLOSED)
      topBarTimer = setInterval(() => { void pollAllChains() }, open ? TOPBAR_CHAIN_POLL_MS_OPEN : TOPBAR_CHAIN_POLL_MS_CLOSED)
    }

    armChainTimers()
    const modeTimer = setInterval(armChainTimers, 30000)

    return () => {
      if (activeTimer) clearInterval(activeTimer)
      if (topBarTimer) clearInterval(topBarTimer)
      clearInterval(modeTimer)
    }
  }, [chainSymbol, pollChain, pollAllChains])
}
