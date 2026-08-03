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

function GainersTable({
  title,
  badge,
  badgeClass,
  rows,
  refreshedAt,
  scored,
  status,
  streamLabel,
  emptyNote,
  onSelectUnderlying,
  loading,
  err,
}: {
  title: string
  badge: string
  badgeClass: string
  rows: MarketTopRow[]
  refreshedAt?: string
  scored?: number
  status?: string
  streamLabel: string
  emptyNote: string
  onSelectUnderlying?: (symbol: string) => void
  loading?: boolean
  err?: string
}) {
  return (
    <div className="flex flex-col overflow-hidden h-full min-h-[280px] border border-border rounded-md bg-surface">
      <div className="px-4 py-2 border-b border-border bg-surface-1 flex items-center justify-between gap-3 flex-shrink-0">
        <div>
          <h2 className="text-xs font-semibold text-text-primary uppercase tracking-wider">{title}</h2>
          <div className="text-[10px] text-text-muted font-mono">
            {refreshedAt ? `Refreshed ${refreshedAt}` : loading ? 'Loading…' : 'Waiting'}
            {scored != null ? ` · ${scored} scored` : ''}
            {status ? ` · ${status}` : ''}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn('pill text-[10px] border', badgeClass)}>{badge}</span>
          <span className="pill text-[10px] bg-surface-2 text-text-muted border border-border">{streamLabel}</span>
        </div>
      </div>

      {err && rows.length === 0 ? (
        <div className="p-4 text-center text-text-muted text-xs space-y-1">
          <div className="font-semibold text-text-primary">{loading ? 'Scanning…' : 'No rows yet'}</div>
          <div>{err}</div>
        </div>
      ) : rows.length === 0 ? (
        <div className="p-4 text-center text-text-muted text-xs space-y-1">
          <div className="font-semibold text-text-primary">{loading ? 'Scanning…' : 'No rows yet'}</div>
          <div>{emptyNote}</div>
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
                      {row.market_match_note || `GAINER (+${fmt(gain, 2)}%)`}
                    </td>
                    <td className="px-2 py-1.5 text-[10px] text-text-muted whitespace-nowrap">
                      {row.refreshed_at || refreshedAt || '—'}
                    </td>
                    <td className="px-2 py-1.5 text-[10px] text-text-muted">{row.data_provenance || '—'}</td>
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

export function MarketTopCePeTable({ onSelectUnderlying, compact = false, pollMs = 15000 }: Props) {
  const { marketTop, wsStatus, setMarketTop } = useStore()
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(true)
  const [mcRows, setMcRows] = useState<MarketTopRow[]>([])
  const [mcMeta, setMcMeta] = useState<{ status?: string; refreshed_at?: string; note?: string; error?: string }>({})
  const [diag, setDiag] = useState<string>('')

  const wsRows: MarketTopRow[] = Array.isArray(marketTop?.market_top_table) ? marketTop.market_top_table : []
  const [pollRows, setPollRows] = useState<MarketTopRow[]>([])
  const [pollMeta, setPollMeta] = useState<{ status?: string; refreshed_at?: string; scored?: number; note?: string; error?: string }>({})

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const [r, mc, dg] = await Promise.all([
          fetch(`${BASE}/api/scanner/top_contract_gainers?top_n=5&market_top_n=25&include_equity=true`, {
            credentials: 'include', headers: { Accept: 'application/json', ...API_HEADERS },
          }),
          fetch(`${BASE}/api/scanner/moneycontrol_gainers?top_n=25`, {
            credentials: 'include', headers: { Accept: 'application/json', ...API_HEADERS },
          }),
          fetch(`${BASE}/api/scanner/market_top_diagnose`, {
            credentials: 'include', headers: { Accept: 'application/json', ...API_HEADERS },
          }),
        ])
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const data = await r.json()
        const table: MarketTopRow[] = data?.market_top_table || data?.market_wide?.top_combined_list || []
        if (!alive) return
        setPollRows(Array.isArray(table) ? table : [])
        setPollMeta({
          status: data?.status,
          refreshed_at: data?.refreshed_at || table?.[0]?.refreshed_at,
          scored: data?.contracts_scored_total,
          note: data?.diagnose?.why_not_moneycontrol_parity || data?.note,
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
        if (mc.ok) {
          const mcData = await mc.json()
          setMcRows(Array.isArray(mcData?.market_top_table) ? mcData.market_top_table : [])
          setMcMeta({
            status: mcData?.status,
            refreshed_at: mcData?.refreshed_at,
            note: mcData?.note,
            error: mcData?.error,
          })
        }
        if (dg.ok) {
          const d = await dg.json()
          const missing = (d?.not_in_priority_head16 || []).slice(0, 6).join(',')
          setDiag(missing ? `Rotate pending for: ${missing}` : (d?.root_cause_if_absent_on_board || ''))
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
    <div className={cn('flex flex-col gap-3 overflow-hidden', compact ? 'h-full' : '')}>
      <div className="text-[10px] text-text-muted px-1">
        Why Moneycontrol parity lagged: Dhan board previously scanned only 4 priority equities.
        Now rotates OPTSTK shards + Moneycontrol LIVE_SCRAPED reference. Paper may seed high-risers; live money stays OFF.
        {diag ? ` · ${diag}` : ''}
      </div>
      <div className={cn('grid gap-3', compact ? 'grid-cols-1' : 'grid-cols-1 xl:grid-cols-2')}>
        <GainersTable
          title="Moneycontrol All-India Top Option Gainers [% Gain]"
          badge="LIVE SCRAPED"
          badgeClass="bg-amber/10 text-amber border-amber/30"
          rows={mcRows}
          refreshedAt={mcMeta.refreshed_at}
          scored={mcRows.length}
          status={mcMeta.status}
          streamLabel="REFERENCE ONLY"
          emptyNote={mcMeta.error || mcMeta.note || 'Waiting for Moneycontrol scrape…'}
          onSelectUnderlying={onSelectUnderlying}
          loading={loading && mcRows.length === 0}
          err={mcMeta.error}
        />
        <GainersTable
          title="Market Top CE / PE (Dhan Live)"
          badge="DHAN LIVE"
          badgeClass="bg-up/10 text-up border-up/20"
          rows={rows}
          refreshedAt={refreshedAt}
          scored={scored}
          status={status}
          streamLabel={streamLabel}
          emptyNote={pollMeta.note || 'Waiting for live Dhan option-chain gainers.'}
          onSelectUnderlying={onSelectUnderlying}
          loading={loading && rows.length === 0}
          err={err || pollMeta.error}
        />
      </div>
    </div>
  )
}

export default MarketTopCePeTable
