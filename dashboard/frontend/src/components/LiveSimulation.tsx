import { useEffect, useMemo, useState } from 'react'

type BackendPosition = {
  position_id: string
  symbol: string
  side: 'CE' | 'PE'
  strike: number
  expiry: string
  entry_price: number
  ltp: number
  qty: number
  pnl: number
  status: 'OPEN' | 'CLOSED'
  source: string
}

type BackendSimState = {
  status: string
  mode: string
  scenario: string
  generated_utc: string
  broker?: { connected?: boolean; status?: string; heartbeat_age_sec?: number; source?: string }
  market?: { is_open?: boolean; state?: string; source?: string }
  risk?: { live_trading_enabled?: boolean; order_placement_allowed?: boolean; real_broker_routes_called?: boolean }
  option_chain?: Array<Record<string, any>>
  signals?: Array<Record<string, any>>
  positions?: BackendPosition[]
  paper?: { total_pnl?: number; currency?: string; source?: string }
  gates?: Record<string, boolean>
  safety_banner?: string
}

function cardStyle(border = 'rgba(148,163,184,.18)') {
  return {
    background: 'rgba(15,23,42,.72)',
    border: `1px solid ${border}`,
    borderRadius: '14px',
    padding: '14px',
    boxShadow: '0 0 18px rgba(0,0,0,.16)',
  } as const
}

function Pill({ label, ok = true }: { label: string; ok?: boolean }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '6px',
      borderRadius: '999px', padding: '5px 9px', fontSize: '11px', fontWeight: 900,
      letterSpacing: '.04em', color: ok ? 'var(--up)' : 'var(--amber)',
      border: ok ? '1px solid rgba(0,232,122,.35)' : '1px solid rgba(245,158,11,.45)',
      background: ok ? 'rgba(0,232,122,.08)' : 'rgba(245,158,11,.10)',
    }}>
      {ok ? '✓' : 'SIM'} {label}
    </span>
  )
}

async function fetchSimulation(scenario: string): Promise<BackendSimState> {
  const res = await fetch(`/api/simulation/live/state?scenario=${encodeURIComponent(scenario)}`, { credentials: 'include' })
  if (!res.ok) throw new Error(`backend simulation API failed: ${res.status}`)
  return res.json()
}

export function LiveSimulation() {
  const [running, setRunning] = useState(true)
  const [scenario, setScenario] = useState<'trend' | 'range' | 'volatile'>('trend')
  const [tick, setTick] = useState(0)
  const [data, setData] = useState<BackendSimState | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let stop = false
    async function load() {
      try {
        const payload = await fetchSimulation(scenario)
        if (!stop) {
          setData(payload)
          setError(null)
        }
      } catch (err: any) {
        if (!stop) setError(err?.message || String(err))
      }
    }
    load()
    if (!running) return () => { stop = true }
    const id = window.setInterval(() => {
      setTick(v => v + 1)
      load()
    }, 2500)
    return () => { stop = true; window.clearInterval(id) }
  }, [running, scenario])

  const rows = data?.positions || []
  const totalPnl = Number(data?.paper?.total_pnl || rows.reduce((a, r) => a + Number(r.pnl || 0), 0))
  const gateItems = useMemo(() => Object.entries(data?.gates || {}).filter(([k]) => k !== 'real_live_gate_credit'), [data])

  return (
    <section style={{ height: '100%', overflow: 'auto', padding: '18px 18px 110px' }} data-testid="live-simulation-tab">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '14px', alignItems: 'flex-start', marginBottom: '14px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 950 }}>Backend Virtual Live Trading Simulation</h1>
          <p style={{ margin: '6px 0 0', color: 'var(--text-mut)', maxWidth: '920px', lineHeight: 1.45 }}>
            This tab consumes backend API route <b>/api/simulation/live/state</b> like a live feed. It is simulation only:
            no broker order APIs, no real live gate credit, no live trading enablement.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <Pill label="BACKEND FEED" />
          <Pill label="SIMULATION ONLY" />
          <Pill label="NO REAL ORDERS" />
          <Pill label="LIVE OFF" />
        </div>
      </div>

      {error && (
        <div style={{ ...cardStyle('rgba(239,68,68,.35)'), marginBottom: '14px', color: 'var(--down)', fontWeight: 900 }}>
          Backend simulation API not available yet: {error}. After Render deploy, this should come from /api/simulation/live/state.
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '12px', marginBottom: '14px' }}>
        <div style={cardStyle('rgba(0,232,122,.28)')}>
          <div style={{ color: 'var(--text-mut)', fontSize: '11px', fontWeight: 800 }}>BACKEND SIM MODE</div>
          <div style={{ fontSize: '22px', fontWeight: 950, color: 'var(--up)' }}>{running ? 'STREAMING' : 'PAUSED'}</div>
        </div>
        <div style={cardStyle('rgba(59,130,246,.28)')}>
          <div style={{ color: 'var(--text-mut)', fontSize: '11px', fontWeight: 800 }}>VIRTUAL P&L</div>
          <div style={{ fontSize: '22px', fontWeight: 950, color: totalPnl >= 0 ? 'var(--up)' : 'var(--down)' }}>₹{totalPnl.toFixed(2)}</div>
        </div>
        <div style={cardStyle('rgba(245,158,11,.28)')}>
          <div style={{ color: 'var(--text-mut)', fontSize: '11px', fontWeight: 800 }}>REAL LIVE STATUS</div>
          <div style={{ fontSize: '22px', fontWeight: 950, color: 'var(--amber)' }}>OFF / LOCKED</div>
        </div>
        <div style={cardStyle('rgba(148,163,184,.25)')}>
          <div style={{ color: 'var(--text-mut)', fontSize: '11px', fontWeight: 800 }}>SOURCE</div>
          <div style={{ fontSize: '18px', fontWeight: 950 }}>{data?.status || 'WAITING'}</div>
        </div>
      </div>

      <div style={{ ...cardStyle(), marginBottom: '14px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <button onClick={() => setRunning(v => !v)} style={{ padding: '9px 12px', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-3)', color: 'var(--text-primary)', fontWeight: 900, cursor: 'pointer' }}>
            {running ? 'Pause backend stream' : 'Start backend stream'}
          </button>
          <button onClick={() => setTick(v => v + 1)} style={{ padding: '9px 12px', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-3)', color: 'var(--text-primary)', fontWeight: 900, cursor: 'pointer' }}>
            Refresh backend tick #{tick}
          </button>
          {(['trend', 'range', 'volatile'] as const).map(s => (
            <button key={s} onClick={() => setScenario(s)} style={{ padding: '9px 12px', borderRadius: '10px', border: scenario === s ? '1px solid var(--accent)' : '1px solid var(--border)', background: scenario === s ? 'rgba(0,232,122,.10)' : 'var(--surface-3)', color: 'var(--text-primary)', fontWeight: 900, cursor: 'pointer', textTransform: 'uppercase' }}>
              {s}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(280px, .8fr)', gap: '14px' }}>
        <div style={cardStyle()}>
          <h2 style={{ marginTop: 0 }}>Backend virtual paper order tape</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ color: 'var(--text-mut)', textAlign: 'left' }}>
                  <th style={{ padding: '8px' }}>ID</th><th>Symbol</th><th>Side</th><th>Strike</th><th>Expiry</th><th>LTP</th><th>P&L</th><th>Status</th><th>Source</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.position_id} style={{ borderTop: '1px solid var(--border)' }}>
                    <td style={{ padding: '8px', fontFamily: 'var(--font-mono)' }}>{r.position_id}</td>
                    <td>{r.symbol}</td><td>{r.side}</td><td>{r.strike}</td><td>{r.expiry}</td><td>{r.ltp}</td>
                    <td style={{ color: Number(r.pnl) >= 0 ? 'var(--up)' : 'var(--down)', fontWeight: 900 }}>₹{Number(r.pnl).toFixed(2)}</td>
                    <td>{r.status}</td><td style={{ color: 'var(--text-mut)' }}>{r.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={cardStyle()}>
          <h2 style={{ marginTop: 0 }}>Backend virtual checklist</h2>
          <div style={{ display: 'grid', gap: '8px' }}>
            {gateItems.map(([item, ok]) => (
              <div key={item} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid rgba(0,232,122,.20)', borderRadius: '10px', padding: '9px 10px', background: 'rgba(0,232,122,.06)' }}>
                <span style={{ fontWeight: 800 }}>{item.replaceAll('_', ' ')}</span>
                <span style={{ color: ok ? 'var(--up)' : 'var(--amber)', fontWeight: 950 }}>{ok ? '✓ SIM OK' : 'SIM ONLY'}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '12px', padding: '10px', borderRadius: '10px', background: 'rgba(245,158,11,.10)', border: '1px solid rgba(245,158,11,.35)', color: 'var(--amber)', fontWeight: 850 }}>
            {data?.safety_banner || 'Simulation green checks must never be counted as real production readiness.'}
          </div>
        </div>
      </div>
    </section>
  )
}
