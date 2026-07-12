import { useMemo, useState } from 'react'

type SimRow = {
  id: string
  time: string
  symbol: string
  side: 'CE' | 'PE'
  strike: number
  expiry: string
  entry: number
  ltp: number
  qty: number
  pnl: number
  status: 'OPEN' | 'CLOSED'
  reason: string
}

const baseRows: SimRow[] = [
  { id: 'SIM-001', time: '09:20:05', symbol: 'NIFTY', side: 'CE', strike: 24550, expiry: 'SIM-WEEKLY', entry: 112.4, ltp: 118.2, qty: 75, pnl: 435, status: 'OPEN', reason: 'virtual momentum + tick heartbeat' },
  { id: 'SIM-002', time: '09:22:18', symbol: 'BANKNIFTY', side: 'PE', strike: 52300, expiry: 'SIM-WEEKLY', entry: 184.5, ltp: 176.8, qty: 30, pnl: 231, status: 'OPEN', reason: 'virtual reversal + spread ok' },
  { id: 'SIM-003', time: '09:29:41', symbol: 'FINNIFTY', side: 'CE', strike: 23600, expiry: 'SIM-WEEKLY', entry: 62.2, ltp: 66.1, qty: 65, pnl: 253.5, status: 'CLOSED', reason: 'virtual target hit' },
]

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

export function LiveSimulation() {
  const [running, setRunning] = useState(true)
  const [scenario, setScenario] = useState<'trend' | 'range' | 'volatile'>('trend')
  const [step, setStep] = useState(7)

  const rows = useMemo(() => {
    const factor = scenario === 'trend' ? 1.0 : scenario === 'range' ? 0.52 : 1.74
    return baseRows.map((r, i) => {
      const delta = running ? (step + i * 2) * factor * (r.side === 'CE' ? 0.32 : -0.28) : 0
      const ltp = Number((r.ltp + delta).toFixed(2))
      const pnl = Number(((ltp - r.entry) * r.qty * (r.side === 'PE' ? -1 : 1)).toFixed(2))
      return { ...r, ltp, pnl }
    })
  }, [running, scenario, step])

  const totalPnl = rows.reduce((a, r) => a + r.pnl, 0)
  const gateItems = [
    'virtual broker heartbeat',
    'virtual tick stream',
    'virtual option chain',
    'virtual CE/PE signal',
    'virtual paper order path',
    'virtual risk guard',
    'virtual dashboard refresh',
  ]

  return (
    <section style={{ height: '100%', overflow: 'auto', padding: '18px 18px 110px' }} data-testid="live-simulation-tab">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '14px', alignItems: 'flex-start', marginBottom: '14px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 950 }}>Virtual Live Trading Simulation</h1>
          <p style={{ margin: '6px 0 0', color: 'var(--text-mut)', maxWidth: '880px', lineHeight: 1.45 }}>
            This tab simulates live market conditions for dashboard testing only. It does not call broker order APIs,
            does not change real gates, does not enable live trading, and must be removed or disabled before real execution approval.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <Pill label="SIMULATION ONLY" />
          <Pill label="NO REAL ORDERS" />
          <Pill label="LIVE OFF" />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '12px', marginBottom: '14px' }}>
        <div style={cardStyle('rgba(0,232,122,.28)')}>
          <div style={{ color: 'var(--text-mut)', fontSize: '11px', fontWeight: 800 }}>VIRTUAL MODE</div>
          <div style={{ fontSize: '22px', fontWeight: 950, color: 'var(--up)' }}>{running ? 'RUNNING' : 'PAUSED'}</div>
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
          <div style={{ color: 'var(--text-mut)', fontSize: '11px', fontWeight: 800 }}>SCENARIO</div>
          <div style={{ fontSize: '22px', fontWeight: 950, textTransform: 'uppercase' }}>{scenario}</div>
        </div>
      </div>

      <div style={{ ...cardStyle(), marginBottom: '14px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <button onClick={() => setRunning(v => !v)} style={{ padding: '9px 12px', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-3)', color: 'var(--text-primary)', fontWeight: 900, cursor: 'pointer' }}>
            {running ? 'Pause virtual stream' : 'Start virtual stream'}
          </button>
          <button onClick={() => setStep(v => v + 1)} style={{ padding: '9px 12px', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface-3)', color: 'var(--text-primary)', fontWeight: 900, cursor: 'pointer' }}>
            Advance virtual tick
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
          <h2 style={{ marginTop: 0 }}>Virtual paper order tape</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ color: 'var(--text-mut)', textAlign: 'left' }}>
                  <th style={{ padding: '8px' }}>ID</th><th>Time</th><th>Symbol</th><th>Side</th><th>Strike</th><th>LTP</th><th>P&L</th><th>Status</th><th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.id} style={{ borderTop: '1px solid var(--border)' }}>
                    <td style={{ padding: '8px', fontFamily: 'var(--font-mono)' }}>{r.id}</td>
                    <td>{r.time}</td><td>{r.symbol}</td><td>{r.side}</td><td>{r.strike}</td><td>{r.ltp}</td>
                    <td style={{ color: r.pnl >= 0 ? 'var(--up)' : 'var(--down)', fontWeight: 900 }}>₹{r.pnl.toFixed(2)}</td>
                    <td>{r.status}</td><td style={{ color: 'var(--text-mut)' }}>{r.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={cardStyle()}>
          <h2 style={{ marginTop: 0 }}>Virtual live checklist</h2>
          <div style={{ display: 'grid', gap: '8px' }}>
            {gateItems.map(item => (
              <div key={item} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid rgba(0,232,122,.20)', borderRadius: '10px', padding: '9px 10px', background: 'rgba(0,232,122,.06)' }}>
                <span style={{ fontWeight: 800 }}>{item}</span>
                <span style={{ color: 'var(--up)', fontWeight: 950 }}>✓ SIM OK</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '12px', padding: '10px', borderRadius: '10px', background: 'rgba(245,158,11,.10)', border: '1px solid rgba(245,158,11,.35)', color: 'var(--amber)', fontWeight: 850 }}>
            Real Live Gate remains separate. Simulation green checks must never be counted as real production readiness.
          </div>
        </div>
      </div>
    </section>
  )
}
