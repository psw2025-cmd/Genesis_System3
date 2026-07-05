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

export function OptionChain() {
  const { chainSymbol, setChainSymbol, chain, marketOpen } = useStore()
  const data      = chain[chainSymbol]
  const atmRef    = useRef<HTMLTableRowElement>(null)
  const [filter, setFilter] = useState(10) // strikes around ATM

  useEffect(() => {
    if (atmRef.current) {
      atmRef.current.scrollIntoView({ block: 'center', behavior: 'smooth' })
    }
  }, [data?.spot, chainSymbol])

  const contracts: Contract[] = data?.contracts ?? []
  const spot = data?.spot ?? 0
  const pcr  = data?.pcr ?? '--'
  const status = data?.status

  // Group by strike
  const strikeMap = new Map<number, { CE?: Contract; PE?: Contract }>()
  for (const c of contracts) {
    if (!strikeMap.has(c.strike)) strikeMap.set(c.strike, {})
    strikeMap.get(c.strike)![c.option_type] = c
  }

  // Sort strikes and find ATM
  const strikes = Array.from(strikeMap.keys()).sort((a, b) => a - b)
  const atmIdx  = strikes.reduce((best, s, i) =>
    Math.abs(s - spot) < Math.abs(strikes[best] - spot) ? i : best, 0)

  // Filter near ATM
  const visible = strikes.slice(
    Math.max(0, atmIdx - filter),
    Math.min(strikes.length, atmIdx + filter + 1)
  )

  const maxOI = Math.max(...contracts.map(c => c.oi ?? 0), 1)

  // Not ready state
  if (!marketOpen && (!data || contracts.length === 0)) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="w-12 h-12 rounded-full bg-surface-2 border border-border flex items-center justify-center text-2xl">🔒</div>
        <p className="text-text-secondary font-semibold">Market Closed</p>
        <p className="text-text-muted text-sm">Option chain unavailable outside trading hours</p>
        <p className="text-text-muted text-xs">Opens Mon–Fri 09:15 IST</p>
      </div>
    )
  }

  if (status === 'NOT_READY' || (contracts.length === 0 && marketOpen)) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="w-12 h-12 rounded-full bg-amber/10 border border-amber/30 flex items-center justify-center text-2xl">⚡</div>
        <p className="text-amber font-semibold">Broker Not Ready</p>
        <p className="text-text-muted text-sm">{data?.message || 'Waiting for Dhan connection…'}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header controls */}
      <div className="flex items-center gap-3 px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
        {/* Symbol selector */}
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

        {/* Spot + PCR */}
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

          {/* Strikes filter */}
          <select
            value={filter}
            onChange={e => setFilter(+e.target.value)}
            className="bg-surface-2 border border-border rounded px-2 py-0.5 text-xs text-text-secondary"
          >
            {[5,10,15,20].map(n => <option key={n} value={n}>±{n} ATM</option>)}
          </select>
        </div>
      </div>

      {/* Chain table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-xs">
          <thead className="sticky top-0 z-10 bg-surface-1">
            <tr>
              {/* CE headers */}
              <th className="thead text-right border-b border-border">OI</th>
              <th className="thead text-right border-b border-border">ChgOI</th>
              <th className="thead text-right border-b border-border">Vol</th>
              <th className="thead text-right border-b border-border">IV</th>
              <th className="thead text-right border-b border-border">LTP</th>
              <th className="thead text-right border-b border-border">Bid</th>
              {/* Strike */}
              <th className="thead text-center border-b border-border bg-surface-2 px-4 py-2 text-text-primary font-bold">STRIKE</th>
              {/* PE headers */}
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
              const isATM = Math.abs(strike - spot) < (strikes[1] - strikes[0]) / 2

              return (
                <tr
                  key={strike}
                  ref={isATM ? atmRef : undefined}
                  className={cn('trow', isATM && 'atm-row')}
                >
                  {/* CE side */}
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

                  {/* Strike column */}
                  <td className={cn(
                    'tcell text-center font-bold text-sm px-4',
                    isATM ? 'text-accent bg-surface-2' : 'text-text-primary bg-surface-1'
                  )}>
                    {fmt(strike, 0)}
                    {isATM && <span className="ml-1 text-[9px] text-accent font-mono">ATM</span>}
                  </td>

                  {/* PE side */}
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
