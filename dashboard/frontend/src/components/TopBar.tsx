import { useState, useEffect, useRef } from 'react'
import { useStore } from '../store'
import { fmt, cn } from '../lib/utils'

function Clock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const tick = () => {
      setTime(new Date().toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata', hour12: false,
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      }))
    }
    tick()
    const t = setInterval(tick, 1000)
    return () => clearInterval(t)
  }, [])
  return <span className="num" style={{ color: 'var(--accent)', fontSize: '1rem', fontWeight: 600, letterSpacing: '.05em' }}>{time} IST</span>
}

function IndexChip({ symbol, spot, chg }: { symbol: string; spot?: number; chg?: number }) {
  const isUp  = (chg ?? 0) >= 0
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '3px 10px',
                  background: 'var(--surface-2)', borderRadius: '6px', border: '1px solid var(--border)' }}>
      <span style={{ fontSize: '.65rem', color: 'var(--text-mut)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{symbol}</span>
      <span className="num" style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-pri)' }}>
        {spot ? fmt(spot, 0) : '--'}
      </span>
      {chg != null && (
        <span className="num" style={{ fontSize: '.6rem', color: isUp ? 'var(--up)' : 'var(--down)' }}>
          {isUp ? '▲' : '▼'} {Math.abs(chg).toFixed(1)}%
        </span>
      )}
    </div>
  )
}

// Fetch NSE spot prices via backend (works market closed)
async function fetchSpots(): Promise<Record<string, { spot: number; chg: number }>> {
  try {
    const r = await fetch('/api/underlyings')
    if (!r.ok) return {}
    const data = await r.json()
    const result: Record<string, { spot: number; chg: number }> = {}
    const items = data?.underlyings ?? data ?? []
    for (const item of items) {
      if (item.underlying && item.spot_price) {
        result[item.underlying] = {
          spot: item.spot_price,
          chg: item.change_pct ?? 0
        }
      }
    }
    return result
  } catch { return {} }
}

export function TopBar() {
  const { health, wsStatus, brokerConnected, marketOpen, brokerStatus, setActiveTab } = useStore()
  const [spots, setSpots] = useState<Record<string, { spot: number; chg: number }>>({})
  const rho = health?.state?.signals?.spearman_rho ?? null

  // Also try to get spots from gain_rank / state
  const gainRank = useStore(s => s.gainRank)
  const state    = useStore(s => s.state)

  useEffect(() => {
    // Fetch spots from underlyings API (works anytime)
    fetchSpots().then(s => { if (Object.keys(s).length) setSpots(s) })
    const t = setInterval(() => fetchSpots().then(s => { if (Object.keys(s).length) setSpots(s) }), 30000)
    return () => clearInterval(t)
  }, [])

  // Fallback: extract spots from gain_rank data
  const getSpot = (sym: string) => {
    if (spots[sym]?.spot) return spots[sym]
    const entry = gainRank?.rankings?.find((r: any) => r.underlying === sym)
    if (entry?.spot_price) return { spot: entry.spot_price, chg: entry.change_pct ?? 0 }
    const stateEntry = state?.signals?.underlyings?.[sym]
    if (stateEntry?.spot) return { spot: stateEntry.spot, chg: 0 }
    return null
  }

  const nifty   = getSpot('NIFTY')
  const bnfty   = getSpot('BANKNIFTY')
  const finnifty = getSpot('FINNIFTY')

  return (
    <header style={{
      height: '52px', background: 'var(--surface-1)', borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', padding: '0 12px', gap: '10px',
      flexShrink: 0, zIndex: 50, overflow: 'hidden'
    }}>
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
        <span style={{ color: 'var(--accent)', fontWeight: 800, fontSize: '.8rem', letterSpacing: '.1em' }}>SYSTEM3</span>
        <span style={{ color: 'var(--text-mut)', fontSize: '.6rem' }}>PSW</span>
      </div>
      <div style={{ width: '1px', height: '28px', background: 'var(--border)' }} />

      {/* Clock */}
      <Clock />
      <div style={{ width: '1px', height: '28px', background: 'var(--border)' }} />

      {/* Index strip — ALWAYS visible, uses last known data */}
      <div style={{ display: 'flex', gap: '6px', overflow: 'hidden', flex: 1 }}>
        <IndexChip symbol="NIFTY"    spot={nifty?.spot}    chg={nifty?.chg} />
        <IndexChip symbol="BNFTY"    spot={bnfty?.spot}    chg={bnfty?.chg} />
        <IndexChip symbol="FINNIFTY" spot={finnifty?.spot} chg={finnifty?.chg} />
      </div>

      {/* Status pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
        {/* Market */}
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '3px 8px',
          borderRadius: '6px', fontSize: '.65rem', fontWeight: 700, fontFamily: 'var(--font-mono)',
          background: marketOpen ? 'rgba(0,232,122,.1)' : 'rgba(255,77,106,.1)',
          color: marketOpen ? 'var(--up)' : 'var(--down)',
          border: `1px solid ${marketOpen ? 'rgba(0,232,122,.25)' : 'rgba(255,77,106,.25)'}`,
        }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%',
                         background: marketOpen ? 'var(--up)' : 'var(--down)',
                         animation: marketOpen ? 'pulseDot 1.5s infinite' : 'none' }} />
          {marketOpen ? 'OPEN' : 'CLOSED'}
        </span>

        {/* Dhan — clickable → broker tab */}
        <span
          onClick={() => setActiveTab('broker')}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '3px 8px',
            borderRadius: '6px', fontSize: '.65rem', fontWeight: 700, fontFamily: 'var(--font-mono)',
            cursor: 'pointer',
            background: brokerConnected ? 'rgba(0,232,122,.1)' : 'rgba(255,77,106,.1)',
            color: brokerConnected ? 'var(--up)' : 'var(--down)',
            border: `1px solid ${brokerConnected ? 'rgba(0,232,122,.25)' : 'rgba(255,77,106,.25)'}`,
          }}
          title="Click to see broker data"
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%',
                         background: brokerConnected ? 'var(--up)' : 'var(--down)' }} />
          DHAN {brokerConnected ? '✓' : '✗'}
        </span>

        <span style={{
          padding: '3px 8px', borderRadius: '6px', fontSize: '.65rem', fontWeight: 700,
          background: 'rgba(245,158,11,.1)', color: 'var(--amber)',
          border: '1px solid rgba(245,158,11,.25)', fontFamily: 'var(--font-mono)',
        }}>PAPER</span>

        <span style={{
          padding: '3px 8px', borderRadius: '6px', fontSize: '.65rem', fontWeight: 700,
          background: 'rgba(255,77,106,.08)', color: 'var(--down)',
          border: '1px solid rgba(255,77,106,.2)', fontFamily: 'var(--font-mono)',
        }}>LIVE OFF</span>

        {/* WS */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '4px', padding: '3px 7px',
          background: 'var(--surface-2)', borderRadius: '5px', border: '1px solid var(--border)',
          cursor: 'default',
        }} title={`WebSocket: ${wsStatus}`}>
          <span style={{
            width: '6px', height: '6px', borderRadius: '50%',
            background: wsStatus === 'live' ? 'var(--up)' : wsStatus === 'connecting' ? 'var(--amber)' : 'var(--down)',
            animation: wsStatus === 'live' ? 'pulseDot 1.5s infinite' : 'none'
          }} />
          <span style={{ fontSize: '.55rem', fontFamily: 'var(--font-mono)', color: 'var(--text-mut)' }}>WS</span>
          <span style={{ fontSize: '.55rem', fontFamily: 'var(--font-mono)',
                         color: wsStatus === 'live' ? 'var(--up)' : 'var(--text-mut)' }}>
            {wsStatus.toUpperCase()}
          </span>
        </div>

        {/* ρ badge */}
        {rho != null && (
          <div style={{ padding: '3px 7px', background: 'var(--surface-2)', borderRadius: '5px',
                        border: '1px solid var(--border)' }}>
            <span style={{ fontSize: '.55rem', color: 'var(--text-mut)', fontFamily: 'var(--font-mono)' }}>ρ </span>
            <span className="num" style={{ fontSize: '.75rem', fontWeight: 700,
                                           color: rho >= 0.7 ? 'var(--up)' : rho >= 0.4 ? 'var(--amber)' : 'var(--down)' }}>
              {rho.toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </header>
  )
}
