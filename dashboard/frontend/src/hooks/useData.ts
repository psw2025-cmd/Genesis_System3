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
    setAlerts, setAutoGates, setWsStatus, chainSymbol, setChain
  } = useStore()

  const wsRef   = useRef<WebSocket | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // ── REST poll (core data) ─────────────────────────────────────────────
  const poll = useCallback(async () => {
    try {
      const [health, state, paper, gainRank] = await Promise.allSettled([
        fetchJSON('/api/health'),
        fetchJSON('/api/state'),
        fetchJSON('/api/paper'),
        fetchJSON('/api/gain_rank'),
      ])
      if (health.status === 'fulfilled')   setHealth(health.value)
      if (state.status === 'fulfilled')    setState(state.value)
      if (paper.status === 'fulfilled')    setPaper(paper.value)
      if (gainRank.status === 'fulfilled') setGainRank(gainRank.value)
    } catch { /* ignore individual failures */ }
  }, [setHealth, setState, setPaper, setGainRank])

  // ── Chain poll (separate — only when tab active) ──────────────────────
  const pollChain = useCallback(async (sym: string) => {
    try {
      const data = await fetchJSON(`/api/chain/${sym}`)
      setChain(sym, data)
    } catch { /* ignore */ }
  }, [setChain])

  // ── Secondary data ────────────────────────────────────────────────────
  const pollSecondary = useCallback(async () => {
    try {
      const [alerts, gates] = await Promise.allSettled([
        fetchJSON('/api/alerts/recent?limit=30'),
        fetchJSON('/api/auto_gates'),
      ])
      if (alerts.status === 'fulfilled') setAlerts(Array.isArray(alerts.value?.alerts) ? alerts.value.alerts : [])
      if (gates.status === 'fulfilled')  setAutoGates(gates.value)
    } catch { /* ignore */ }
  }, [setAlerts, setAutoGates])

  // ── WebSocket ─────────────────────────────────────────────────────────
  const wsConnect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url   = `${proto}//${location.host}/ws/stream`
    const ws    = new WebSocket(url)
    wsRef.current = ws
    setWsStatus('connecting')

    ws.onopen  = () => setWsStatus('live')
    ws.onerror = () => setWsStatus('error')
    ws.onclose = (e) => {
      setWsStatus('off')
      // Auto-reconnect after 5s (3s if market closed)
      setTimeout(wsConnect, e.code === 1008 ? 300000 : 5000)
    }
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data)
        switch (m.type) {
          case 'health_update':    if (m.data) setHealth(m.data);   break
          case 'positions_update': break  // handled via REST
          case 'pnl_update':       break  // handled via REST
        }
      } catch { /* ignore */ }
    }
  }, [setHealth, setWsStatus])

  useEffect(() => {
    // Initial load
    poll()
    pollSecondary()
    wsConnect()

    // REST: 20s market, 30s closed
    pollRef.current = setInterval(() => {
      poll()
    }, 20000)

    // Secondary every 60s
    const secInterval = setInterval(pollSecondary, 60000)

    return () => {
      clearInterval(pollRef.current!)
      clearInterval(secInterval)
      wsRef.current?.close()
    }
  }, [poll, pollSecondary, wsConnect])

  // Chain poll when symbol changes
  useEffect(() => {
    pollChain(chainSymbol)
    const t = setInterval(() => pollChain(chainSymbol), 5000)
    return () => clearInterval(t)
  }, [chainSymbol, pollChain])
}
