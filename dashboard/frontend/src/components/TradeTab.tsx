import { useEffect, useState } from 'react'
import { OptionChain } from './OptionChain'
import { MarketTopCePeTable } from './MarketTopCePeTable'
import { useStore } from '../store'
import { API_BASE, API_HEADERS } from '../config'
import { fmt, cn } from '../lib/utils'

const BASE = API_BASE || (typeof window !== 'undefined' ? window.location.origin : '')

function ScannerRow({ row }: { row: any }) {
  const isUp = row.direction === 'UP'
  return (
    <div className={cn(
      'flex items-center justify-between px-4 py-2.5 border-b border-border',
      'hover:bg-surface-2 transition-colors'
    )}>
      <div className="flex items-center gap-3 min-w-0">
        <span className="text-[10px] text-text-muted w-5">{row.rank ?? ''}</span>
        <span className="text-xs font-mono font-semibold text-text-secondary truncate w-20">{row.underlying}</span>
        <span className={cn('pill text-[10px]',
          isUp ? 'bg-up/10 text-up border border-up/20' : 'bg-down/10 text-down border border-down/20'
        )}>{row.option_type || row.direction}</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right">
          <div className="text-[10px] text-text-muted">GAIN %</div>
          <div className={cn('num text-sm font-semibold',
            (row.gain_pct ?? row.gain_rank ?? 0) > 0 ? 'text-red-500' : 'text-text-muted'
          )}>{fmt(row.gain_pct ?? row.gain_rank ?? 0, 1)}%</div>
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

function EquityRow({ row }: { row: any }) {
  return (
    <div className="flex items-center justify-between px-4 py-2.5 border-b border-border hover:bg-surface-2">
      <div className="min-w-0">
        <div className="text-xs font-mono font-semibold text-text-primary truncate">{row.underlying}</div>
        <div className="text-[10px] text-text-muted font-mono">
          {row.option_type} {row.strike} · OI {fmt(row.oi ?? 0, 0)}
        </div>
      </div>
      <div className="text-right">
        <div className="text-[10px] text-text-muted">LTP</div>
        <div className="num text-sm font-semibold text-text-primary">{fmt(row.ltp ?? 0, 2)}</div>
      </div>
    </div>
  )
}

export function TradeTab() {
  const { gainRank, apiStatus, setChainSymbol, marketTop } = useStore()
  const rankings: any[] = gainRank?.rankings ?? []
  const [equity, setEquity] = useState<unknown>(null)
  const [equityErr, setEquityErr] = useState('')
  const [seedRows, setSeedRows] = useState<any[]>([])

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const r = await fetch(`${BASE}/api/scanner/equity_options?top_n=8`, {
          credentials: 'include',
          headers: { Accept: 'application/json', ...API_HEADERS },
        })
        if (!r.ok) throw new Error(String(r.status))
        const data = await r.json()
        if (alive) {
          setEquity(data)
          setEquityErr('')
        }
      } catch (e: any) {
        if (alive) setEquityErr(String(e?.message || e))
      }
    }
    load()
    const t = setInterval(load, 180000)
    return () => {
      alive = false
      clearInterval(t)
    }
  }, [])

  useEffect(() => {
    let alive = true
    const seeds = ['RELIANCE', 'HDFCBANK', 'POWERGRID']
    const loadSeeds = async () => {
      const rows: any[] = []
      await Promise.all(seeds.map(async (sym) => {
        try {
          const r = await fetch(`${BASE}/api/chain/${sym}`, {
            credentials: 'include',
            headers: { Accept: 'application/json', ...API_HEADERS },
          })
          if (!r.ok) return
          const data = await r.json()
          const contracts = Array.isArray(data?.contracts) ? data.contracts : []
          const ce = contracts.filter((c: any) => String(c?.option_type || '').toUpperCase() === 'CE' && Number(c?.ltp) > 0)
            .sort((a: any, b: any) => Number(b.oi || 0) - Number(a.oi || 0))[0]
          const pe = contracts.filter((c: any) => String(c?.option_type || '').toUpperCase() === 'PE' && Number(c?.ltp) > 0)
            .sort((a: any, b: any) => Number(b.oi || 0) - Number(a.oi || 0))[0]
          if (ce) rows.push({ underlying: sym, option_type: 'CE', strike: ce.strike, ltp: ce.ltp, oi: ce.oi })
          if (pe) rows.push({ underlying: sym, option_type: 'PE', strike: pe.strike, ltp: pe.ltp, oi: pe.oi })
        } catch {
          // keep last-good seeds
        }
      }))
      if (alive) setSeedRows(rows)
    }
    loadSeeds()
    return () => { alive = false }
  }, [])

  const scannerRows: any[] = [
    ...(equity?.scanner?.top_ce_list || []),
    ...(equity?.scanner?.top_pe_list || []),
  ]
  const marketEquity = Array.isArray(marketTop?.market_top_table)
    ? marketTop.market_top_table.filter((row: any) => {
        const u = String(row?.underlying || row?.symbol || '').toUpperCase()
        return u && !['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX', 'BANKEX'].includes(u)
      })
    : []
  const equityRows: any[] = (scannerRows.length ? scannerRows : (seedRows.length ? seedRows : marketEquity)).slice(0, 12)
  const liveOk = Number(equity?.segments?.equity_options?.live_chains_ok || seedRows.length || 0)

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden">
      <div className="h-[46%] min-h-[240px] border-b border-border flex-shrink-0 overflow-hidden">
        <MarketTopCePeTable onSelectUnderlying={(sym) => setChainSymbol(sym)} />
      </div>

      <div className="flex flex-1 min-h-0 overflow-hidden">
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden border-r border-border">
          <div className="px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
            <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Option Chain</h2>
          </div>
          <div className="flex-1 min-h-0 overflow-hidden">
            <OptionChain />
          </div>
        </div>

        <div className="w-72 flex flex-col flex-shrink-0 min-h-0 overflow-hidden bg-surface">
          <div className="px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
            <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Index / Rank Feed</h2>
          </div>
          <div className="flex-1 min-h-0 overflow-y-auto border-b border-border">
            {rankings.length === 0 ? (
              <div className="p-4 text-center text-text-muted text-xs space-y-2">
                <div className="font-semibold text-text-primary">{apiStatus?.status === 'API_AUTH_REQUIRED' ? 'API authentication required' : 'No rankings available'}</div>
                <div>{apiStatus?.message || gainRank?.message || 'Scanner has no current ranking rows.'}</div>
              </div>
            ) : (
              rankings.slice(0, 12).map((row, i) => <ScannerRow key={i} row={row} />)
            )}
          </div>

          <div className="px-4 py-2 border-b border-border bg-surface-1 flex items-center justify-between flex-shrink-0">
            <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Equity Options</h2>
            <span className="text-[10px] font-mono text-text-muted">{liveOk > 0 ? `${liveOk} live` : 'EOD/live'}</span>
          </div>
          <div className="flex-1 min-h-0 overflow-y-auto">
            {equityRows.length === 0 ? (
              <div className="p-4 text-center text-text-muted text-xs space-y-2">
                <div className="font-semibold text-text-primary">No equity option rows</div>
                <div>{equityErr || equity?.scanner?.gain_metric_note || equity?.message || 'Waiting for Dhan equity option chain snapshot.'}</div>
              </div>
            ) : (
              equityRows.map((row, i) => (
                <button
                  key={`${row.underlying}-${row.option_type}-${row.strike}-${i}`}
                  className="w-full text-left"
                  onClick={() => row?.underlying && setChainSymbol(String(row.underlying).toUpperCase())}
                >
                  <EquityRow row={row} />
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
