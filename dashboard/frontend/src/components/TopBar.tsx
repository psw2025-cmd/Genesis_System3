import { useStore } from '../store'
import { Pill } from './ui/Pill'
import { StatusDot } from './ui/StatusDot'
import { fmt } from '../lib/utils'

function IndexChip({ symbol, spot }: { symbol: string; spot?: number }) {
  return (
    <div className="flex items-center gap-2 px-3 py-1 bg-surface-2 rounded-lg border border-border">
      <span className="text-xs text-text-muted font-mono font-semibold">{symbol}</span>
      <span className="num text-sm font-semibold text-text-primary">
        {spot ? fmt(spot, 0) : '--'}
      </span>
    </div>
  )
}

function Clock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const tick = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata', hour12: false,
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      }))
    }
    tick()
    const t = setInterval(tick, 1000)
    return () => clearInterval(t)
  }, [])
  return (
    <span className="num text-accent text-lg font-semibold tabular-nums tracking-wide">
      {time}
    </span>
  )
}

import { useState, useEffect } from 'react'

export function TopBar() {
  const { health, wsStatus, brokerConnected, marketOpen } = useStore()
  const rho = health?.state?.signals?.spearman_rho ?? health?.rho ?? null

  const spot: Record<string, number> = {}
  const chain = useStore((s) => s.chain)
  for (const sym of ['NIFTY', 'BANKNIFTY', 'FINNIFTY']) {
    const c = chain[sym]
    if (c?.spot) spot[sym] = c.spot
  }

  return (
    <header className="h-14 bg-surface-1 border-b border-border flex items-center px-4 gap-4 flex-shrink-0 z-50">
      {/* Brand */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className="text-accent font-bold text-sm tracking-widest">SYSTEM3</span>
        <span className="text-text-muted text-xs">PSW</span>
      </div>

      {/* Divider */}
      <div className="w-px h-8 bg-border" />

      {/* Clock */}
      <Clock />

      {/* Index strip */}
      <div className="flex items-center gap-2 flex-1 overflow-x-auto scrollbar-hide">
        {['NIFTY','BANKNIFTY','FINNIFTY'].map(sym => (
          <IndexChip key={sym} symbol={sym} spot={spot[sym]} />
        ))}
      </div>

      {/* Status pills */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <Pill
          label={marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}
          variant={marketOpen ? 'green' : 'red'}
          pulse={marketOpen}
        />
        <Pill
          label={brokerConnected ? 'DHAN ✓' : 'DHAN ✗'}
          variant={brokerConnected ? 'green' : 'red'}
        />
        <Pill label="PAPER" variant="amber" />
        <Pill label="LIVE OFF" variant="red" dot={false} />

        {/* WS status */}
        <div className="flex items-center gap-1.5 px-2 py-1 bg-surface-2 rounded border border-border"
          title={`WebSocket: ${wsStatus}`}>
          <StatusDot
            status={wsStatus === 'live' ? 'live' : wsStatus === 'connecting' ? 'warn' : 'dead'}
            pulse={wsStatus === 'live'}
          />
          <span className="text-[10px] font-mono text-text-muted">WS</span>
        </div>

        {/* ρ badge */}
        {rho != null && (
          <div className="px-2 py-1 bg-surface-2 rounded border border-border">
            <span className="text-[10px] text-text-muted font-mono">ρ </span>
            <span className={`num text-xs font-semibold ${rho >= 0.7 ? 'text-up' : rho >= 0.4 ? 'text-amber' : 'text-down'}`}>
              {rho.toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </header>
  )
}
