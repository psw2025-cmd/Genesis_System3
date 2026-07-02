import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'

const BASE = window.location.origin

async function fetchJSON(path: string) {
  const r = await fetch(BASE + path, { headers: { Accept: 'application/json' } })
  if (!r.ok) throw new Error(`${r.status}`)
  return r.json()
}

export function useData() {
  const {
    setHealth, setState, setPaper, setGainRank,
    setAlerts, setAutoGates, setWsStatus, chainSymbol, setChain,
    setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions,
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
    if (status.status   === 'fulfilled') setBrokerStatus(status.value)
    if (holdings.status === 'fulfilled') setBrokerHoldings(holdings.value)
    if (funds.status    === 'fulfilled') setBrokerFunds(funds.value)
    if (positions.status=== 'fulfilled') setBrokerPositions(positions.value)
  }, [setBrokerStatus, setBrokerHoldings, setBrokerFunds, setBrokerPositions])

  // ── Core REST poll ────────────────────────────────────────────────────────
  const poll = useCallback(async () => {
    const [health, state, paper, gainRank] = await Promise.allSettled([
      fetchJSON('/api/health'),
      fetchJSON('/api/state'),
      fetchJSON('/api/paper'),
      fetchJSON('/api/gain_rank'),
    ])
    if (health.status   === 'fulfilled') setHealth(health.value)
    if (state.status    === 'fulfilled') setState(state.value)
    if (paper.status    === 'fulfilled') setPaper(paper.value)
    if (gainRank.status === 'fulfilled') setGainRank(gainRank.value)
  }, [setHealth, setState, setPaper, setGainRank])

  // ── Chain poll ────────────────────────────────────────────────────────────
  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`)
      setChain(sym, data)
    } catch { /* ignore */ }
  }, [setChain])

  // ── Secondary data ────────────────────────────────────────────────────────
  const pollSecondary = useCallback(async () => {
    const [alerts, gates] = await Promise.allSettled([
      fetchJSON('/api/alerts/recent?limit=30'),
      fetchJSON('/api/auto_gates'),
    ])
    if (alerts.status === 'fulfilled') setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
    if (gates.status  === 'fulfilled') setAutoGates(gates.value)
  }, [setAlerts, setAutoGates])

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
