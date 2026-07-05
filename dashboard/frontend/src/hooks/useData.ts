import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'

const BASE = window.location.origin
const REQUEST_TIMEOUT_MS = 8000

const inFlight = new Map<string, Promise<any>>()
const failCounts = new Map<string, number>()
const blockedUntil = new Map<string, number>()

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function backoffMs(path: string) {
  const failures = failCounts.get(path) ?? 0
  return Math.min(120000, 5000 * Math.pow(2, Math.min(failures, 4)))
}

async function fetchJSON(path: string) {
  const now = Date.now()
  const blocked = blockedUntil.get(path) ?? 0
  if (blocked > now) {
    throw new Error(`backoff:${path}`)
  }

  const existing = inFlight.get(path)
  if (existing) return existing

  const request = (async () => {
    const controller = new AbortController()
    const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
    try {
      const r = await fetch(BASE + path, {
        headers: { Accept: 'application/json' },
        cache: 'no-store',
        signal: controller.signal,
      })
      if (!r.ok) throw new Error(`${r.status}`)
      const data = await r.json()
      failCounts.delete(path)
      blockedUntil.delete(path)
      return data
    } catch (err) {
      const nextFails = (failCounts.get(path) ?? 0) + 1
      failCounts.set(path, nextFails)
      blockedUntil.set(path, Date.now() + backoffMs(path))
      throw err
    } finally {
      window.clearTimeout(timer)
      inFlight.delete(path)
    }
  })()

  inFlight.set(path, request)
  return request
}

export function useData() {
  const {
    setHealth, setState, setPaper, setGainRank,
    setAlerts, setAutoGates, setWsStatus, chainSymbol, setChain,
    setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions,
    setPnl,
  } = useStore()

  const wsRef = useRef<WebSocket | null>(null)
  const mountedRef = useRef(true)
  const brokerRunningRef = useRef(false)

  // ── BROKER status — lightweight and safe for regular polling ───────────────
  const pollBrokerStatus = useCallback(async () => {
    try {
      const status = await fetchJSON('/api/broker/dhan/status')
      setBrokerStatus(status)
    } catch { /* keep previous known status */ }
  }, [setBrokerStatus])

  // ── BROKER details — slower cadence and sequential to protect Render/Dhan ──
  // Guard against overlapping runs: if a previous run is still in progress, skip.
  const pollBrokerDetails = useCallback(async () => {
    if (brokerRunningRef.current) return
    brokerRunningRef.current = true
    try {
      try {
        const holdings = await fetchJSON('/api/broker/holdings')
        setBrokerHoldings(holdings)
        await sleep(500)
      } catch { /* keep previous holdings */ }

      try {
        const funds = await fetchJSON('/api/broker/funds')
        setBrokerFunds(funds)
        await sleep(500)
      } catch { /* keep previous funds */ }

      try {
        const positions = await fetchJSON('/api/broker/positions/live')
        setBrokerPositions(positions)
      } catch { /* keep previous positions */ }
    } finally {
      brokerRunningRef.current = false
    }
  }, [setBrokerHoldings, setBrokerFunds, setBrokerPositions])

  // ── Core REST poll ────────────────────────────────────────────────────────
  const poll = useCallback(async () => {
    const [health, state, paper, gainRank, pnl] = await Promise.allSettled([
      fetchJSON('/api/health'),
      fetchJSON('/api/state'),
      fetchJSON('/api/paper'),
      fetchJSON('/api/gain_rank'),
      fetchJSON('/api/pnl'),
    ])
    if (health.status === 'fulfilled') setHealth(health.value)
    if (state.status === 'fulfilled') setState(state.value)
    if (paper.status === 'fulfilled') setPaper(paper.value)
    if (gainRank.status === 'fulfilled') setGainRank(gainRank.value)
    if (pnl.status === 'fulfilled') setPnl(pnl.value)
  }, [setHealth, setState, setPaper, setGainRank, setPnl])

  // ── Chain poll ────────────────────────────────────────────────────────────
  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`)
      setChain(sym, data)
    } catch { /* keep previous chain */ }
  }, [setChain])

  // ── Secondary data ────────────────────────────────────────────────────────
  const pollSecondary = useCallback(async () => {
    const [alerts, gates] = await Promise.allSettled([
      fetchJSON('/api/alerts/recent?limit=30'),
      fetchJSON('/api/auto_gates'),
    ])
    if (alerts.status === 'fulfilled') setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
    if (gates.status === 'fulfilled') setAutoGates(gates.value)
  }, [setAlerts, setAutoGates])

  // ── WebSocket ─────────────────────────────────────────────────────────────
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
      // Only reconnect if the hook is still mounted
      if (mountedRef.current) setTimeout(wsConnect, 10000)
    }
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data)
        if (m.type === 'health_update' && m.data) setHealth(m.data)
      } catch { /* ignore */ }
    }
  }, [setHealth, setWsStatus])

  useEffect(() => {
    mountedRef.current = true

    poll()
    pollBrokerStatus()
    pollBrokerDetails()
    pollSecondary()
    wsConnect()

    const coreTimer = setInterval(poll, 30000)
    const brokerStatusTimer = setInterval(pollBrokerStatus, 60000)
    const brokerDetailsTimer = setInterval(pollBrokerDetails, 120000)
    const secTimer = setInterval(pollSecondary, 90000)

    return () => {
      mountedRef.current = false
      clearInterval(coreTimer)
      clearInterval(brokerStatusTimer)
      clearInterval(brokerDetailsTimer)
      clearInterval(secTimer)
      wsRef.current?.close()
    }
  }, [poll, pollBrokerStatus, pollBrokerDetails, pollSecondary, wsConnect])

  // Chain poll — selected symbol at controlled cadence + staggered TopBar symbols.
  useEffect(() => {
    const TOP_BAR_SYMS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']

    pollChain(chainSymbol)
    const selectedTimer = setInterval(() => pollChain(chainSymbol), 15000)

    const runTopBarPoll = () => {
      TOP_BAR_SYMS.forEach((sym, idx) => {
        if (sym !== chainSymbol) {
          window.setTimeout(() => pollChain(sym), idx * 2000)
        }
      })
    }
    runTopBarPoll()
    const topBarTimer = setInterval(runTopBarPoll, 60000)

    return () => {
      clearInterval(selectedTimer)
      clearInterval(topBarTimer)
    }
  }, [chainSymbol, pollChain])
}
