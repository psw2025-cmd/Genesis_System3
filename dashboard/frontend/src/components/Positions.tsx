import { useStore } from '../store'
import { PriceCell } from './ui/PriceCell'
import { fmtCr, fmt, signClass, cn } from '../lib/utils'

export function Positions() {
  const { paper } = useStore()

  const positions: any[] = paper?.positions?.open_positions ?? []
  const closed:   any[] = paper?.pnl?.summary?.closed_positions ?? []
  const summary          = paper?.pnl?.summary ?? {}

  const totalPnl  = summary.total_pnl ?? 0
  const winRate   = summary.win_rate ?? 0
  const totalTrades = summary.total_trades ?? 0

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* P&L summary bar */}
      <div className="bg-surface-1 border-b border-border px-6 py-3 flex items-center gap-8 flex-shrink-0">
        <div>
          <span className="text-xs text-text-muted">NET P&L</span>
          <div className={cn('num text-xl font-bold', signClass(totalPnl))}>
            {fmtCr(totalPnl)}
          </div>
        </div>
        <div>
          <span className="text-xs text-text-muted">WIN RATE</span>
          <div className={cn('num text-xl font-bold', winRate >= 50 ? 'text-up' : 'text-down')}>
            {winRate.toFixed(1)}%
          </div>
        </div>
        <div>
          <span className="text-xs text-text-muted">TRADES</span>
          <div className="num text-xl font-bold text-text-primary">{totalTrades}</div>
        </div>
        <div>
          <span className="text-xs text-text-muted">OPEN</span>
          <div className="num text-xl font-bold text-text-primary">{positions.length}</div>
        </div>
        <div className="ml-auto">
          <span className="text-xs text-down font-mono font-semibold">PAPER ONLY — NO REAL MONEY</span>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-6">
        {/* Open positions */}
        <div className="card overflow-hidden">
          <div className="px-4 py-2.5 border-b border-border bg-surface-2">
            <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">
              Open Positions ({positions.length})
            </h3>
          </div>
          {positions.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-text-muted text-sm">No open positions</p>
              <p className="text-text-muted text-xs mt-1">Paper engine generates positions during market hours</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  {['Symbol','Type','Entry','LTP','P&L','P&L%','Qty','Reason'].map(h => (
                    <th key={h} className="thead">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {positions.map((p: any, i: number) => (
                  <tr key={i} className="trow">
                    <td className="tcell font-semibold">{p.underlying}</td>
                    <td className="tcell">
                      <span className={cn('pill text-[10px]',
                        p.option_type === 'CE' ? 'bg-up/10 text-up border border-up/20' :
                                                  'bg-down/10 text-down border border-down/20'
                      )}>{p.option_type}</span>
                    </td>
                    <td className="tcell"><PriceCell value={p.entry_price} /></td>
                    <td className="tcell"><PriceCell value={p.current_price} /></td>
                    <td className={cn('tcell', signClass(p.unrealized_pnl))}>
                      {fmtCr(p.unrealized_pnl)}
                    </td>
                    <td className={cn('tcell', signClass(p.unrealized_pnl))}>
                      {p.entry_price > 0 ? fmtCr(((p.current_price - p.entry_price)/p.entry_price)*100) : '--'}
                    </td>
                    <td className="tcell">{p.qty}</td>
                    <td className="tcell text-text-muted">{p.strategy ?? '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Closed trades */}
        {closed.length > 0 && (
          <div className="card overflow-hidden">
            <div className="px-4 py-2.5 border-b border-border bg-surface-2">
              <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">
                Closed Trades ({closed.length})
              </h3>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  {['Symbol','Type','Entry','Exit','P&L','Exit Reason','Time'].map(h => (
                    <th key={h} className="thead">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {closed.slice(0,20).map((p: any, i: number) => (
                  <tr key={i} className="trow">
                    <td className="tcell font-semibold">{p.underlying}</td>
                    <td className="tcell">
                      <span className={cn('pill text-[10px]',
                        p.option_type === 'CE' ? 'bg-up/10 text-up border border-up/20'
                                               : 'bg-down/10 text-down border border-down/20'
                      )}>{p.option_type}</span>
                    </td>
                    <td className="tcell">{fmt(p.entry_price)}</td>
                    <td className="tcell">{fmt(p.exit_price)}</td>
                    <td className={cn('tcell font-semibold', signClass(p.realized_pnl))}>
                      {fmtCr(p.realized_pnl)}
                    </td>
                    <td className="tcell">
                      <span className={cn('pill text-[10px]',
                        p.exit_reason === 'TARGET' ? 'bg-up/10 text-up border border-up/20' :
                        p.exit_reason === 'STOP_LOSS' ? 'bg-down/10 text-down border border-down/20' :
                                                         'bg-surface-2 text-text-muted border border-border'
                      )}>{p.exit_reason}</span>
                    </td>
                    <td className="tcell text-text-muted text-[11px]">{p.time_ist}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
