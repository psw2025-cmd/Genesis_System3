import { useEffect, useState } from 'react'
import { useStore } from '../store'
import { fmt, fmtCr, signClass, cn } from '../lib/utils'

interface PnlData {
  summary?: {
    total_trades?: number
    winning_trades?: number
    losing_trades?: number
    win_rate?: number
    total_realized_pnl?: number
    total_unrealized_pnl?: number
    total_pnl?: number
  }
  history?: any[]
}

function StatCard({ label, value, color, sub }: { label: string; value: string; color?: string; sub?: string }) {
  return (
    <div className="card p-4">
      <span style={{ fontSize: '.65rem', color: 'var(--text-mut)', textTransform: 'uppercase', letterSpacing: '.05em' }}>{label}</span>
      <div className={cn('num', color)} style={{ fontSize: '1.4rem', fontWeight: 700, marginTop: '4px' }}>{value}</div>
      {sub && <span style={{ fontSize: '.65rem', color: 'var(--text-mut)' }}>{sub}</span>}
    </div>
  )
}

async function fetchJSON(path: string) {
  const r = await fetch(path, { headers: { Accept: 'application/json' } })
  if (!r.ok) throw new Error(`${r.status}`)
  return r.json()
}

export function PerformanceTab() {
  const { gainRank, paper } = useStore()
  const [pnl, setPnl] = useState<PnlData | null>(null)
  const [pnlError, setPnlError] = useState<string | null>(null)
  const [lastChecked, setLastChecked] = useState<string>('')

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const data = await fetchJSON('/api/pnl')
        if (mounted) { setPnl(data); setPnlError(null) }
      } catch (e: any) {
        if (mounted) setPnlError(e.message ?? 'fetch failed')
      } finally {
        if (mounted) setLastChecked(new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour12: false }))
      }
    }
    load()
    const t = setInterval(load, 30000)
    return () => { mounted = false; clearInterval(t) }
  }, [])

  const summary = pnl?.summary ?? paper?.pnl?.summary ?? {}
  const totalPnl    = summary.total_pnl ?? 0
  const winRate     = summary.win_rate ?? 0
  const totalTrades = summary.total_trades ?? 0
  const winning     = summary.winning_trades ?? 0
  const losing      = summary.losing_trades ?? 0

  // ρ history from gain_rank (file-based, always available)
  const rankHistory: any[] = gainRank?.history ?? []
  const hasData = totalTrades > 0 || rankHistory.length > 0

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ color: 'var(--text-pri)', fontWeight: 600, fontSize: '.95rem' }}>Performance</h2>
        <span style={{ fontSize: '.65rem', color: 'var(--text-mut)', fontFamily: 'var(--font-mono)' }}>
          last checked {lastChecked || '--'} IST
        </span>
      </div>

      {pnlError && (
        <div className="card p-4" style={{ borderColor: 'var(--down)' }}>
          <p style={{ color: 'var(--down)', fontSize: '.8rem' }}>
            Failed to load performance data: {pnlError}
          </p>
        </div>
      )}

      {!pnlError && !hasData && (
        <div className="card p-4">
          <p style={{ color: 'var(--text-mut)', fontSize: '.85rem' }}>
            No performance data yet — paper engine has not closed any trades.
          </p>
          <p style={{ color: 'var(--text-mut)', fontSize: '.75rem', marginTop: '6px' }}>
            API status: /api/pnl {pnl ? 'responded OK, 0 trades' : 'loading'} · checked {lastChecked || '--'} IST
          </p>
        </div>
      )}

      {hasData && (
        <>
          {/* KPI row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total P&L" value={fmtCr(totalPnl)} color={signClass(totalPnl)} sub="Realized + Unrealized" />
            <StatCard label="Win Rate"  value={`${(winRate ?? 0).toFixed(1)}%`} color={winRate >= 50 ? 'tx-up' : 'tx-down'} />
            <StatCard label="Total Trades" value={String(totalTrades)} sub={`${winning}W / ${losing}L`} />
            <StatCard label="Expectancy" value={totalTrades > 0 ? fmtCr(totalPnl / totalTrades) : '--'} color={signClass(totalPnl)} />
          </div>

          {/* ML accuracy / ρ history */}
          <div className="card p-4">
            <h3 style={{ fontSize: '.75rem', fontWeight: 700, color: 'var(--text-pri)', textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: '10px' }}>
              ML Accuracy (Spearman ρ) — {rankHistory.length} day history
            </h3>
            {rankHistory.length === 0 ? (
              <p style={{ color: 'var(--text-mut)', fontSize: '.8rem' }}>No ρ history recorded yet</p>
            ) : (
              <div style={{ display: 'flex', gap: '4px', alignItems: 'flex-end', height: '60px', marginTop: '8px' }}>
                {rankHistory.slice(-14).map((d: any, i: number) => {
                  const rho = d.spearman_rho ?? d.rho ?? 0
                  const h = Math.max(4, Math.min(60, rho * 60))
                  return (
                    <div key={i} title={`${d.date}: ρ=${rho.toFixed(2)}`}
                         style={{
                           flex: 1, height: `${h}px`, borderRadius: '2px 2px 0 0',
                           background: rho >= 0.7 ? 'var(--up)' : rho >= 0.4 ? 'var(--amber)' : 'var(--down)',
                           opacity: 0.85,
                         }} />
                  )
                })}
              </div>
            )}
          </div>

          {/* Recent closed trades */}
          {(pnl?.history?.length ?? 0) > 0 && (
            <div className="card" style={{ overflow: 'hidden' }}>
              <div style={{ padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
                <h3 style={{ fontSize: '.75rem', fontWeight: 700, color: 'var(--text-pri)', textTransform: 'uppercase' }}>
                  Recent Sessions
                </h3>
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {['Date', 'Trades', 'Win Rate', 'P&L'].map(h => (
                      <th key={h} className="thead">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(pnl?.history ?? []).slice(-10).reverse().map((row: any, i: number) => (
                    <tr key={i} className="trow">
                      <td className="tcell">{row.date ?? row.timestamp ?? '--'}</td>
                      <td className="tcell">{row.total_trades ?? '--'}</td>
                      <td className="tcell">{row.win_rate != null ? `${row.win_rate.toFixed(1)}%` : '--'}</td>
                      <td className={cn('tcell', signClass(row.total_pnl ?? 0))}>{fmtCr(row.total_pnl ?? 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
