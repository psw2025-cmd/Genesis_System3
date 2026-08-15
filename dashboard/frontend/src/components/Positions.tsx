import { useStore } from '../store'
import { PriceCell } from './ui/PriceCell'
import { fmtCr, fmt, signClass, cn } from '../lib/utils'

function rowsOf(value: any): any[] {
  if (Array.isArray(value)) return value
  if (!value || typeof value !== 'object') return []
  for (const key of ['rows', 'positions', 'data', 'open_positions']) if (Array.isArray(value[key])) return value[key]
  return []
}

export function Positions() {
  const { paper, brokerPositions, setActiveTab } = useStore()

  const posBlock = paper?.positions
  const positions: any[] = Array.isArray(posBlock)
    ? posBlock
    : Array.isArray(posBlock?.positions)
      ? posBlock.positions
      : Array.isArray(posBlock?.open_positions)
        ? posBlock.open_positions
        : []
  const closed: any[] = Array.isArray(paper?.pnl?.summary?.closed_positions)
    ? paper.pnl.summary.closed_positions
    : Array.isArray(paper?.pnl?.closed_positions)
      ? paper.pnl.closed_positions
      : []
  const summary = paper?.pnl?.summary ?? paper?.pnl ?? {}
  const summaryAvailable = paper != null && (paper?.pnl != null || paper?.summary != null)
  const dhanPositions = rowsOf(brokerPositions)
  const dhanReadKnown = brokerPositions != null && brokerPositions?.success !== false && brokerPositions?.pendingProof !== true

  const totalPnl = Number(
    summary.total_pnl
    ?? ((Number(summary.total_unrealized_pnl ?? 0) + Number(summary.total_realized_pnl ?? 0)) || 0)
  )
  const winRate = Number(summary.win_rate ?? 0)
  const totalTrades = Number(summary.total_trades ?? closed.length ?? 0)

  return (
    <div className="flex flex-col h-full overflow-y-auto" data-testid="paper-positions-ledger">
      <div className="bg-surface-1 border-b border-border px-6 py-3 flex items-center gap-8 flex-shrink-0 flex-wrap">
        <div>
          <span className="text-xs text-text-muted">PAPER NET P&L</span>
          <div className={cn('num text-xl font-bold', signClass(totalPnl))}>
            {summaryAvailable ? fmtCr(totalPnl) : '--'}
          </div>
        </div>
        <div>
          <span className="text-xs text-text-muted">PAPER WIN RATE</span>
          <div className={cn('num text-xl font-bold', winRate >= 50 ? 'text-up' : 'text-down')}>
            {summaryAvailable ? `${winRate.toFixed(1)}%` : '--'}
          </div>
        </div>
        <div>
          <span className="text-xs text-text-muted">PAPER TRADES</span>
          <div className="num text-xl font-bold text-text-primary">{summaryAvailable ? totalTrades : '--'}</div>
        </div>
        <div>
          <span className="text-xs text-text-muted">PAPER OPEN</span>
          <div className="num text-xl font-bold text-text-primary">{positions.length}</div>
        </div>
        <div>
          <span className="text-xs text-text-muted">DHAN LIVE POSITIONS</span>
          <div className="num text-xl font-bold text-text-primary">{dhanReadKnown ? dhanPositions.length : '--'}</div>
        </div>
        <div className="ml-auto flex items-center gap-2 flex-wrap">
          <span className="text-xs text-up font-mono font-semibold">PAPER LEDGER — NO REAL ORDER ACTIONS</span>
          <button type="button" className="soft-btn" onClick={() => setActiveTab('broker')}>Open read-only Dhan broker truth</button>
        </div>
      </div>

      <div className="px-6 py-2 border-b border-border bg-surface-2 text-[11px] text-text-muted">
        This tab is intentionally the <b>PAPER positions ledger</b>. Real Dhan positions are read-only and shown separately on the Broker tab. A paper count of 0 does not mean Dhan has 0 broker positions.
      </div>

      <div className="flex-1 p-6 space-y-6">
        <div className="card overflow-hidden">
          <div className="px-4 py-2.5 border-b border-border bg-surface-2">
            <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">
              Paper Open Positions ({positions.length})
            </h3>
          </div>
          {positions.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-text-muted text-sm">No paper positions are open</p>
              <p className="text-text-muted text-xs mt-1">Paper engine positions are separate from the read-only Dhan broker ledger.</p>
              {dhanReadKnown && dhanPositions.length > 0 && (
                <p className="text-amber text-xs mt-3">Dhan currently reports {dhanPositions.length} broker position{dhanPositions.length === 1 ? '' : 's'}; open the Broker tab for read-only details.</p>
              )}
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
                    <td className={cn('tcell', signClass(p.unrealized_pnl))}>{fmtCr(p.unrealized_pnl)}</td>
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

        {closed.length > 0 && (
          <div className="card overflow-hidden">
            <div className="px-4 py-2.5 border-b border-border bg-surface-2">
              <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Paper Closed Trades ({closed.length})</h3>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  {['Symbol','Type','Entry','Exit','P&L','Exit Reason','Time'].map(h => <th key={h} className="thead">{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {closed.slice(0,20).map((p: any, i: number) => (
                  <tr className="trow" key={i}>
                    <td className="tcell font-semibold">{p.underlying}</td>
                    <td className="tcell"><span className={cn('pill text-[10px]', p.option_type === 'CE' ? 'bg-up/10 text-up border border-up/20' : 'bg-down/10 text-down border border-down/20')}>{p.option_type}</span></td>
                    <td className="tcell">{fmt(p.entry_price)}</td>
                    <td className="tcell">{fmt(p.exit_price)}</td>
                    <td className={cn('tcell font-semibold', signClass(p.realized_pnl))}>{fmtCr(p.realized_pnl)}</td>
                    <td className="tcell"><span className={cn('pill text-[10px]', p.exit_reason === 'TARGET' ? 'bg-up/10 text-up border border-up/20' : p.exit_reason === 'STOP_LOSS' ? 'bg-down/10 text-down border border-down/20' : 'bg-surface-2 text-text-muted border border-border')}>{p.exit_reason}</span></td>
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
