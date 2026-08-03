import { useEffect, useState } from 'react'
import { API_BASE, API_HEADERS } from '../config'
import { useStore } from '../store'
import { fmt, cn } from '../lib/utils'

const BASE = API_BASE || (typeof window !== 'undefined' ? window.location.origin : '')

type MarketTopRow = {
  rank?: number
  symbol?: string
  underlying?: string
  expiry_date?: string
  option_type?: string
  strike?: number | string
  ltp?: number
  change?: number
  change_rs?: number
  gain_pct?: number
  volume?: number
  oi?: number
  market_match_note?: string
  refreshed_at?: string
  data_provenance?: string
}

type Props = {
  onSelectUnderlying?: (symbol: string) => void
  compact?: boolean
  pollMs?: number
}

export function MarketTopCePeTable({ onSelectUnderlying, compact = false, pollMs = 15000 }: Props) {
  const { marketTop, wsStatus, setMarketTop } = useStore()
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(true)

  const wsRows: MarketTopRow[] = Array.isArray(marketTop?.market_top_table) ? marketTop.market_top_table : []
  const [pollRows, setPollRows] = useState<MarketTopRow[]>([])
  const [pollMeta, setPollMeta] = useState<{ status?: string; refreshed_at?: string; scored?: number; note?: string; error?: string }>({})

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const r = await fetch(
          `${BASE}/api/scanner/top_contract_gainers?top_n=5&market_top_n=25&include_equity=true`,
          { credentials: 'include', headers: { Accept: 'application/json', ...API_HEADERS } },
        )
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const data = await r.json()
        const table: MarketTopRow[] =
          data?.market_top_table ||
          data?.market_wide?.top_combined_list ||
          []
        if (!alive) return
        setPollRows(Array.isArray(table) ? table : [])
        setPollMeta({
          status: data?.status,
          refreshed_at: data?.refreshed_at || table?.[0]?.refreshed_at,
          scored: data?.contracts_scored_total,
          note: data?.note,
          error: data?.error,
        })
        if (Array.isArray(table) && table.length) {
          setMarketTop({
            market_top_table: table,
            refreshed_at: data?.refreshed_at || table?.[0]?.refreshed_at,
            contracts_scored_total: data?.contracts_scored_total,
            status: data?.status,
            stream_mode: data?.stream_mode || 'http_poll',
          })
        }
        setErr('')
      } catch (e: any) {
        if (alive) setErr(String(e?.message || e))
      } finally {
        if (alive) setLoading(false)
      }
    }
    load()
    const t = setInterval(load, pollMs)
    return () => {
      alive = false
      clearInterval(t)
    }
  }, [pollMs, setMarketTop])

  const rows = wsRows.length ? wsRows : pollRows
  const refreshedAt = marketTop?.refreshed_at || pollMeta.refreshed_at || rows?.[0]?.refreshed_at
  const scored = marketTop?.contracts_scored_total ?? pollMeta.scored
  const status = marketTop?.status || pollMeta.status
  const streaming = wsStatus === 'live' && wsRows.length > 0
  const streamLabel = streaming
    ? `ULTRA MICRO · ${marketTop?.stream_mode || 'ws'}`
    : wsStatus === 'live'
      ? 'WS LIVE · waiting table'
      : 'HTTP POLL'

  return (
    <div className={cn('flex flex-col overflow-hidden h-full', compact ? '' : '')}>
      <div className="px-4 py-2 border-b border-border bg-surface-1 flex items-center justify-between gap-3 flex-shrink-0">
        <div>
          <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">
            Market Top CE / PE
          </h2>
          <div className="text-[10px] text-text-muted font-mono">
            {refreshedAt ? `Refreshed ${refreshedAt}` : loading ? 'Loading…' : 'Waiting for Dhan chain'}
            {scored != null ? ` · ${scored} contracts scored` : ''}
            {status ? ` · ${status}` : ''}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn(
            'pill text-[10px] border',
            streaming ? 'bg-up/10 text-up border-up/20' : 'bg-surface-2 text-text-muted border-border',
          )}>{streamLabel}</span>
          <span className="pill text-[10px] bg-up/10 text-up border border-up/20">DHAN LIVE</span>
        </div>
      </div>

      {err && rows.length === 0 ? (
        <div className="p-4 text-center text-text-muted text-xs space-y-1">
          <div className="font-semibold text-text-primary">
            {loading ? 'Scanning market top CE/PE…' : 'No market top rows yet'}
          </div>
          <div>{err || pollMeta.error || pollMeta.note || 'Waiting for live Dhan option-chain gainers.'}</div>
        </div>
      ) : rows.length === 0 ? (
        <div className="p-4 text-center text-text-muted text-xs space-y-1">
          <div className="font-semibold text-text-primary">
            {loading ? 'Scanning market top CE/PE…' : 'No market top rows yet'}
          </div>
          <div>{pollMeta.note || 'Waiting for live Dhan option-chain gainers.'}</div>
        </div>
      ) : (
        <div className="overflow-auto flex-1">
          <table className="w-full min-w-[1100px] text-left">
            <thead className="sticky top-0 z-10">
              <tr className="bg-emerald-800 text-white text-[10px] uppercase tracking-wider">
                {[
                  'Rank', 'Symbol', 'Expiry', 'CE/PE', 'Strike', 'LTP', 'Change', 'Gain %',
                  'Volume', 'OI', 'Note', 'Refreshed', 'Provenance',
                ].map((h) => (
                  <th key={h} className="px-2 py-2 font-semibold whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => {
                const symbol = String(row.symbol || row.underlying || '').toUpperCase()
                const gain = Number(row.gain_pct || 0)
                const change = Number(row.change ?? row.change_rs ?? 0)
                const opt = String(row.option_type || '').toUpperCase()
                return (
                  <tr
                    key={`${symbol}-${opt}-${row.strike}-${i}`}
                    className={cn(
                      'border-b border-border text-xs font-mono cursor-pointer hover:bg-surface-2',
                      i % 2 === 0 ? 'bg-emerald-50/5' : 'bg-transparent',
                    )}
                    onClick={() => symbol && onSelectUnderlying?.(symbol)}
                  >
                    <td className="px-2 py-1.5 text-text-muted">{row.rank ?? i + 1}</td>
                    <td className="px-2 py-1.5 font-semibold text-text-primary">{symbol}</td>
                    <td className="px-2 py-1.5 text-text-secondary">{row.expiry_date || '—'}</td>
                    <td className={cn('px-2 py-1.5 font-semibold', opt === 'CE' ? 'text-up' : 'text-down')}>{opt || '—'}</td>
                    <td className="px-2 py-1.5 num">{fmt(Number(row.strike || 0), 0)}</td>
                    <td className="px-2 py-1.5 num">{fmt(Number(row.ltp || 0), 2)}</td>
                    <td className={cn('px-2 py-1.5 num', change >= 0 ? 'text-up' : 'text-down')}>{fmt(change, 2)}</td>
                    <td className="px-2 py-1.5 num font-semibold text-red-500">{fmt(gain, 2)}%</td>
                    <td className="px-2 py-1.5 num">{fmt(Number(row.volume || 0), 0)}</td>
                    <td className="px-2 py-1.5 num">{fmt(Number(row.oi || 0), 0)}</td>
                    <td className="px-2 py-1.5 text-[10px] text-text-muted max-w-[180px] truncate">
                      {row.market_match_note || `LIVE DHAN GAINER (+${fmt(gain, 2)}%)`}
                    </td>
                    <td className="px-2 py-1.5 text-[10px] text-text-muted whitespace-nowrap">
                      {row.refreshed_at || refreshedAt || '—'}
                    </td>
                    <td className="px-2 py-1.5 text-[10px] text-text-muted">{row.data_provenance || 'DHAN_OPTION_CHAIN_LIVE'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default MarketTopCePeTable
