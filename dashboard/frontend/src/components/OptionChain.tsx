import { useEffect, useRef, useState } from 'react'
import { useStore } from '../store'
import { PriceCell } from './ui/PriceCell'
import { fmt, cn } from '../lib/utils'

const SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

interface Contract {
  strike: number
  option_type: 'CE' | 'PE'
  ltp: number
  oi: number
  dOI: number
  volume: number
  iv: number
  delta: number
  theta: number
}

function oiBar(val: number, max: number, type: 'CE' | 'PE') {
  const pct = max > 0 ? Math.min((val / max) * 100, 100) : 0
  return (
    <div className="flex items-center gap-1 w-20">
      {type === 'CE' && <div className="flex-1 h-1.5 bg-surface-3 rounded overflow-hidden">
        <div className="h-full bg-up/50 rounded" style={{ width: `${pct}%` }} />
      </div>}
      <span className="num text-[11px] text-text-secondary whitespace-nowrap">
        {val >= 1e6 ? (val/1e6).toFixed(1)+'M' : val >= 1e3 ? (val/1e3).toFixed(0)+'K' : val}
      </span>
      {type === 'PE' && <div className="flex-1 h-1.5 bg-surface-3 rounded overflow-hidden">
        <div className="h-full bg-down/50 rounded ml-auto" style={{ width: `${pct}%` }} />
      </div>}
    </div>
  )
}

function StatusRow({ label, value, tone }: { label: string; value: string | number; tone?: 'ok' | 'warn' | 'bad' }) {
  const color = tone === 'ok' ? 'text-up' : tone === 'bad' ? 'text-down' : tone === 'warn' ? 'text-amber' : 'text-text-primary'
  return (
    <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
      <span className="text-text-muted text-xs">{label}</span>
      <span className={cn('num text-xs font-semibold text-right', color)}>{value}</span>
    </div>
  )
}

export function OptionChain() {
  const { chainSymbol, setChainSymbol, chain, marketOpen, state, gainRank } = useStore()
  const data      = chain[chainSymbol]
  const atmRef    = useRef<HTMLTableRowElement>(null)
  const [filter, setFilter] = useState(10)

  useEffect(() => {
    if (atmRef.current) {
      atmRef.current.scrollIntoView({ block: 'center', behavior: 'smooth' })
    }
  }, [data?.spot, chainSymbol])

  const contracts: Contract[] = data?.contracts ?? []
  const spot = data?.spot ?? 0
  const pcr  = data?.pcr ?? '--'
  const status = data?.status ?? 'LOADING'
  const dataSource = data?.data_source ?? state?.data_source ?? '--'
  const marketReason = String(state?.market?.reason ?? data?.message ?? (marketOpen ? 'Market open' : 'Market closed'))
  const nextOpen = String(state?.market?.next_open ?? '--')
  const latestSignals = gainRank?.latest?.predictions ?? gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
  const latestSignal = Array.isArray(latestSignals)
    ? latestSignals.find((r: any) => r?.underlying === chainSymbol)
    : null

  const strikeMap = new Map<number, { CE?: Contract; PE?: Contract }>()
  for (const c of contracts) {
    if (!strikeMap.has(c.strike)) strikeMap.set(c.strike, {})
    strikeMap.get(c.strike)![c.option_type] = c
  }

  const strikes = Array.from(strikeMap.keys()).sort((a, b) => a - b)
  const atmIdx  = strikes.length > 0
    ? strikes.reduce((best, s, i) => Math.abs(s - spot) < Math.abs(strikes[best] - spot) ? i : best, 0)
    : 0

  const visible = strikes.slice(
    Math.max(0, atmIdx - filter),
    Math.min(strikes.length, atmIdx + filter + 1)
  )

  const maxOI = Math.max(...contracts.map(c => c.oi ?? 0), 1)

  if (contracts.length === 0 && !marketOpen) {
    return (
      <div className="p-6 space-y-4 overflow-y-auto h-full">
        <div className="flex items-center gap-2 flex-wrap">
          {SYMBOLS.map(sym => (
            <button key={sym}
              onClick={() => setChainSymbol(sym)}
              className={cn(
                'px-3 py-1 rounded text-xs font-mono font-semibold transition-colors',
                chainSymbol === sym
                  ? 'bg-accent text-white'
                  : 'bg-surface-2 text-text-secondary hover:text-text-primary border border-border'
              )}
            >{sym}</button>
          ))}
        </div>

        <div className="card p-4 border border-amber/30 bg-amber/5">
          <div className="flex items-center justify-between gap-4 mb-3">
            <div>
              <div className="text-xs text-text-muted uppercase tracking-wider">Option Chain - {chainSymbol}</div>
              <div className="text-sm text-text-primary font-semibold">Market closed: live option-chain rows are session-dependent only.</div>
            </div>
            <span className="pill text-[10px] bg-amber/10 text-amber border border-amber/20">{status}</span>
          </div>
          <p className="text-xs text-text-muted leading-5">
            Broker, paper P&amp;L, scanner snapshots, gates, alerts, and health/state data must remain visible. Market close is not a reason for an empty dashboard.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card p-4">
            <h3 className="text-sm font-semibold text-text-primary mb-3">Chain Status</h3>
            <StatusRow label="Market" value={marketOpen ? 'OPEN' : 'CLOSED'} tone={marketOpen ? 'ok' : 'warn'} />
            <StatusRow label="Reason" value={marketReason} />
            <StatusRow label="Next Open" value={nextOpen} />
            <StatusRow label="Data Source" value={String(dataSource)} />
            <StatusRow label="Contracts" value={contracts.length} tone="warn" />
            <StatusRow label="Spot" value={spot ? fmt(spot, 0) : '--'} />
            <StatusRow label="PCR" value={typeof pcr === 'number' ? pcr.toFixed(2) : String(pcr)} />
          </div>

          <div className="card p-4">
            <h3 className="text-sm font-semibold text-text-primary mb-3">Last Scanner Snapshot</h3>
            <StatusRow label="Latest Date" value={String(gainRank?.latest_date ?? gainRank?.latest?.date ?? '--')} tone={gainRank?.stale ? 'warn' : 'ok'} />
            <StatusRow label="Stale" value={String(gainRank?.stale ?? '--')} tone={gainRank?.stale ? 'warn' : 'ok'} />
            <StatusRow label="Rank" value={String(latestSignal?.rank ?? '--')} />
            <StatusRow label="Gain Score" value={latestSignal?.gain_score != null ? `${latestSignal.gain_score}%` : '--'} />
            <StatusRow label="Expected Move" value={latestSignal?.expected_move_pct != null ? `${latestSignal.expected_move_pct}%` : '--'} />
            <StatusRow label="Recommendation" value={String(latestSignal?.recommendation ?? '--')} tone={latestSignal?.recommendation === 'TRADE' ? 'ok' : undefined} />
          </div>
        </div>

        {data?.message && (
          <div className="card p-4">
            <h3 className="text-sm font-semibold text-text-primary mb-2">Backend Message</h3>
            <p className="text-xs text-text-muted font-mono">{data.message}</p>
          </div>
        )}
      </div>
    )
  }

  if (status === 'NOT_READY' || (contracts.length === 0 && marketOpen)) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="w-12 h-12 rounded-full bg-amber/10 border border-amber/30 flex items-center justify-center text-2xl">!</div>
        <p className="text-amber font-semibold">Broker Not Ready</p>
        <p className="text-text-muted text-sm">{data?.message || 'Waiting for Dhan connection...'}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
        <div className="flex gap-1">
          {SYMBOLS.map(sym => (
            <button key={sym}
              onClick={() => setChainSymbol(sym)}
              className={cn(
                'px-3 py-1 rounded text-xs font-mono font-semibold transition-colors',
                chainSymbol === sym
                  ? 'bg-accent text-white'
                  : 'bg-surface-2 text-text-secondary hover:text-text-primary border border-border'
              )}
            >{sym}</button>
          ))}
        </div>

        <div className="flex items-center gap-4 ml-auto">
          <div className="flex items-center gap-1.5">
            <span className="text-text-muted text-xs">SPOT</span>
            <span className="num text-sm font-semibold text-text-primary">{spot ? fmt(spot, 0) : '--'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-text-muted text-xs">PCR</span>
            <span className={cn('num text-sm font-semibold',
              typeof pcr === 'number' && pcr > 1 ? 'text-up' : 'text-down'
            )}>{typeof pcr === 'number' ? pcr.toFixed(2) : pcr}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-text-muted text-xs">CONTRACTS</span>
            <span className="num text-xs text-text-secondary">{contracts.length}</span>
          </div>

          <select
            value={filter}
            onChange={e => setFilter(+e.target.value)}
            className="bg-surface-2 border border-border rounded px-2 py-0.5 text-xs text-text-secondary"
          >
            {[5,10,15,20].map(n => <option key={n} value={n}>+/-{n} ATM</option>)}
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-xs">
          <thead className="sticky top-0 z-10 bg-surface-1">
            <tr>
              <th className="thead text-right border-b border-border">OI</th>
              <th className="thead text-right border-b border-border">ChgOI</th>
              <th className="thead text-right border-b border-border">Vol</th>
              <th className="thead text-right border-b border-border">IV</th>
              <th className="thead text-right border-b border-border">LTP</th>
              <th className="thead text-right border-b border-border">Bid</th>
              <th className="thead text-center border-b border-border bg-surface-2 px-4 py-2 text-text-primary font-bold">STRIKE</th>
              <th className="thead text-left border-b border-border">Ask</th>
              <th className="thead text-left border-b border-border">LTP</th>
              <th className="thead text-left border-b border-border">IV</th>
              <th className="thead text-left border-b border-border">Vol</th>
              <th className="thead text-left border-b border-border">ChgOI</th>
              <th className="thead text-left border-b border-border">OI</th>
            </tr>
          </thead>
          <tbody>
            {visible.map(strike => {
              const row   = strikeMap.get(strike)!
              const ce    = row.CE
              const pe    = row.PE
              const step  = strikes.length > 1 ? strikes[1] - strikes[0] : 0
              const isATM = step > 0 && Math.abs(strike - spot) < step / 2

              return (
                <tr
                  key={strike}
                  ref={isATM ? atmRef : undefined}
                  className={cn('trow', isATM && 'atm-row')}
                >
                  <td className="tcell text-right">{ce ? oiBar(ce.oi, maxOI, 'CE') : '--'}</td>
                  <td className={cn('tcell text-right num', ce?.dOI != null && ce.dOI > 0 ? 'text-up' : 'text-down')}>
                    {ce?.dOI != null ? (ce.dOI >= 0 ? '+' : '') + (ce.dOI >= 1000 ? (ce.dOI/1000).toFixed(1)+'K' : ce.dOI) : '--'}
                  </td>
                  <td className="tcell text-right">{ce?.volume != null ? (ce.volume >= 1000 ? (ce.volume/1000).toFixed(0)+'K' : ce.volume) : '--'}</td>
                  <td className="tcell text-right text-amber">{ce?.iv != null ? (ce.iv * 100).toFixed(1) + '%' : '--'}</td>
                  <td className="tcell text-right">
                    {ce ? <PriceCell value={ce.ltp} /> : '--'}
                  </td>
                  <td className="tcell text-right text-text-muted">{ce?.ltp != null ? fmt(ce.ltp * 0.998, 1) : '--'}</td>

                  <td className={cn(
                    'tcell text-center font-bold text-sm px-4',
                    isATM ? 'text-accent bg-surface-2' : 'text-text-primary bg-surface-1'
                  )}>
                    {fmt(strike, 0)}
                    {isATM && <span className="ml-1 text-[9px] text-accent font-mono">ATM</span>}
                  </td>

                  <td className="tcell text-left text-text-muted">{pe?.ltp != null ? fmt(pe.ltp * 1.002, 1) : '--'}</td>
                  <td className="tcell text-left">
                    {pe ? <PriceCell value={pe.ltp} /> : '--'}
                  </td>
                  <td className="tcell text-left text-amber">{pe?.iv != null ? (pe.iv * 100).toFixed(1) + '%' : '--'}</td>
                  <td className="tcell text-left">{pe?.volume != null ? (pe.volume >= 1000 ? (pe.volume/1000).toFixed(0)+'K' : pe.volume) : '--'}</td>
                  <td className={cn('tcell text-left num', pe?.dOI != null && pe.dOI > 0 ? 'text-up' : 'text-down')}>
                    {pe?.dOI != null ? (pe.dOI >= 0 ? '+' : '') + (pe.dOI >= 1000 ? (pe.dOI/1000).toFixed(1)+'K' : pe.dOI) : '--'}
                  </td>
                  <td className="tcell text-left">{pe ? oiBar(pe.oi, maxOI, 'PE') : '--'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

