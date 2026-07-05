import { OptionChain } from './OptionChain'
import { useStore } from '../store'
import { fmt, cn } from '../lib/utils'

function ScannerRow({ row }: { row: any }) {
  const isUp = row.direction === 'UP'
  return (
    <div className={cn(
      'flex items-center justify-between px-4 py-2.5 border-b border-border',
      'hover:bg-surface-2 transition-colors'
    )}>
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono font-semibold text-text-secondary w-24">{row.underlying}</span>
        <span className={cn('pill text-[10px]',
          isUp ? 'bg-up/10 text-up border border-up/20' : 'bg-down/10 text-down border border-down/20'
        )}>{row.direction}</span>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <div className="text-[10px] text-text-muted">SCORE</div>
          <div className={cn('num text-sm font-semibold',
            (row.gain_rank ?? 0) > 60 ? 'text-up' : (row.gain_rank ?? 0) > 40 ? 'text-amber' : 'text-down'
          )}>{fmt(row.gain_rank ?? 0, 1)}</div>
        </div>
        <span className={cn('pill text-[10px]',
          row.option_eligible ? 'bg-up/10 text-up border border-up/20' : 'bg-surface-2 text-text-muted border border-border'
        )}>
          {row.option_eligible ? 'ELIGIBLE' : 'WATCH'}
        </span>
      </div>
    </div>
  )
}

export function TradeTab() {
  const { gainRank } = useStore()
  const rankings: any[] = gainRank?.rankings ?? []

  return (
    <div className="flex h-full overflow-hidden">
      {/* Option Chain — main panel */}
      <div className="flex-1 flex flex-col overflow-hidden border-r border-border">
        <div className="px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
          <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Option Chain</h2>
        </div>
        <OptionChain />
      </div>

      {/* Scanner — right panel */}
      <div className="w-64 flex flex-col flex-shrink-0 overflow-hidden">
        <div className="px-4 py-2 border-b border-border bg-surface-1">
          <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Index Scanner</h2>
        </div>
        <div className="flex-1 overflow-y-auto">
          {rankings.length === 0 ? (
            <div className="p-6 text-center text-text-muted text-sm">
              Loading rankings…
            </div>
          ) : (
            rankings.map((row, i) => <ScannerRow key={i} row={row} />)
          )}
        </div>
      </div>
    </div>
  )
}
