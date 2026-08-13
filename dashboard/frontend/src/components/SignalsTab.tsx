import { useStore } from '../store'
import { cn, fmt } from '../lib/utils'
import { TrendingUp, TrendingDown } from 'lucide-react'

export function SignalsTab() {
  const { state, gainRank } = useStore()
  const signals = state?.signals ?? {}
  const forecast: any[] = gainRank?.rankings ?? []

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Top signal */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-text-primary">Top Signal</h3>
          <span className="text-xs text-text-muted font-mono">PATH A — FORECAST</span>
        </div>
        <div className="flex items-center gap-4">
          <div className={cn(
            'w-16 h-16 rounded-xl flex items-center justify-center text-2xl border',
            signals.status === 'BUY' ? 'bg-up/10 border-up/30' :
            signals.status === 'SELL' ? 'bg-down/10 border-down/30' :
                                        'bg-surface-2 border-border'
          )}>
            {signals.status === 'BUY' ? <TrendingUp className="text-up" size={28} /> :
             signals.status === 'SELL' ? <TrendingDown className="text-down" size={28} /> :
             '—'}
          </div>
          <div>
            <div className={cn('text-xl font-bold num',
              signals.status === 'BUY' ? 'text-up' :
              signals.status === 'SELL' ? 'text-down' : 'text-text-muted'
            )}>
              {signals.status ?? 'AWAITING'}
            </div>
            <div className="text-sm text-text-secondary">{signals.underlying ?? 'No signal'}</div>
            <div className="text-xs text-text-muted">{signals.reason ?? 'Waiting for market data'}</div>
          </div>
          {signals.confidence != null && (
            <div className="ml-auto text-right">
              <div className="text-xs text-text-muted">CONFIDENCE</div>
              <div className="num text-2xl font-bold text-accent">{(signals.confidence).toFixed(0)}%</div>
            </div>
          )}
        </div>
      </div>

      {/* Index Forecast */}
      <div className="card overflow-hidden">
        <div className="px-4 py-2.5 border-b border-border bg-surface-2">
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Index Forecast</h3>
        </div>
        {forecast.length === 0 ? (
          <div className="p-6 text-center text-text-muted text-sm">
            Gain rank data loading…
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                {['Index','Score','Direction','Status'].map(h => (
                  <th key={h} className="thead">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {forecast.map((row: any, i: number) => (
                <tr key={i} className="trow">
                  <td className="tcell font-semibold">{row.underlying}</td>
                  <td className="tcell">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-surface-3 rounded overflow-hidden">
                        <div
                          className={cn('h-full rounded', row.gain_rank > 60 ? 'bg-up' : row.gain_rank > 40 ? 'bg-amber' : 'bg-down')}
                          style={{ width: `${row.gain_rank}%` }}
                        />
                      </div>
                      <span className={cn('num text-xs font-semibold',
                        row.gain_rank > 60 ? 'text-up' : row.gain_rank > 40 ? 'text-amber' : 'text-down'
                      )}>{fmt(row.gain_rank, 1)}</span>
                    </div>
                  </td>
                  <td className="tcell">
                    <span className={cn('flex items-center gap-1 font-semibold',
                      row.direction === 'UP' ? 'text-up' : 'text-down'
                    )}>
                      {row.direction === 'UP' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      {row.direction}
                    </span>
                  </td>
                  <td className="tcell">
                    <span className={cn('pill text-[10px]',
                      row.option_eligible
                        ? 'bg-up/10 text-up border border-up/20'
                        : 'bg-surface-2 text-text-muted border border-border'
                    )}>
                      {row.option_eligible ? 'OPTION ELIGIBLE' : 'WATCH'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
