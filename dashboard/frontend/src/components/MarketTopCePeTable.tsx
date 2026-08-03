import { useEffect, useMemo, useState } from 'react'
import { API_BASE, API_HEADERS } from '../config'
import { useStore } from '../store'
import { fmt, cn } from '../lib/utils'
import { AuthUnlock } from './AuthUnlock'

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

type BoardKind = 'moneycontrol' | 'dhan'

type Props = {
  onSelectUnderlying?: (symbol: string) => void
  compact?: boolean
  pollMs?: number
}

function fmtExpiry(raw?: string): string {
  if (!raw) return '—'
  const s = String(raw).trim()
  // Already Moneycontrol-like: 25-Aug-26
  if (/^\d{1,2}-[A-Za-z]{3}-\d{2}$/.test(s)) return s
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!m) return s
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const dd = String(Number(m[3]))
  const mon = months[Number(m[2]) - 1] || m[2]
  const yy = m[1].slice(2)
  return `${dd}-${mon}-${yy}`
}

function fmtInt(n: number): string {
  if (!Number.isFinite(n)) return '—'
  return Math.round(n).toLocaleString('en-IN')
}

export function MarketTopCePeTable({ onSelectUnderlying, compact = false, pollMs = 15000 }: Props) {
  const { marketTop, wsStatus, setMarketTop, apiStatus } = useStore()
  const [board, setBoard] = useState<BoardKind>('moneycontrol')
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(true)
  const [mcRows, setMcRows] = useState<MarketTopRow[]>([])
  const [mcMeta, setMcMeta] = useState<{ status?: string; refreshed_at?: string; note?: string; error?: string }>({})
  const [pollRows, setPollRows] = useState<MarketTopRow[]>([])
  const [pollMeta, setPollMeta] = useState<{ status?: string; refreshed_at?: string; scored?: number; note?: string; error?: string }>({})

  const wsRows: MarketTopRow[] = Array.isArray(marketTop?.market_top_table) ? marketTop.market_top_table : []

  useEffect(() => {
    let alive = true
    const fetchJson = async (path: string, timeoutMs = 12000) => {
      const ctrl = new AbortController()
      const timer = window.setTimeout(() => ctrl.abort(), timeoutMs)
      try {
        const r = await fetch(`${BASE}${path}`, {
          credentials: 'include',
          headers: { Accept: 'application/json', ...API_HEADERS },
          signal: ctrl.signal,
        })
        let body: any = null
        try { body = await r.json() } catch { body = null }
        return { ok: r.ok, status: r.status, body }
      } finally {
        window.clearTimeout(timer)
      }
    }

    const load = async () => {
      try {
        const [r, mc] = await Promise.allSettled([
          fetchJson('/api/scanner/top_contract_gainers?top_n=5&market_top_n=25&include_equity=true', 14000),
          fetchJson('/api/scanner/moneycontrol_gainers?top_n=25', 12000),
        ])
        if (!alive) return

        if (r.status === 'fulfilled') {
          if (r.value.ok) {
            const data = r.value.body || {}
            const table: MarketTopRow[] = data?.market_top_table || data?.market_wide?.top_combined_list || []
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
          } else if (r.value.status === 401) {
            setErr('API authentication required')
            setPollMeta({ status: 'auth_required', error: 'Unlock dashboard API session to load Dhan Market Top' })
          } else {
            setErr(`Dhan board HTTP ${r.value.status}`)
          }
        } else {
          setErr('Dhan board request timed out')
        }

        if (mc.status === 'fulfilled') {
          if (mc.value.ok) {
            const mcData = mc.value.body || {}
            setMcRows(Array.isArray(mcData?.market_top_table) ? mcData.market_top_table : [])
            setMcMeta({
              status: mcData?.status,
              refreshed_at: mcData?.refreshed_at,
              note: mcData?.note,
              error: mcData?.error,
            })
          } else if (mc.value.status === 401) {
            setMcMeta({ status: 'auth_required', error: 'Unlock dashboard API session to load Moneycontrol board' })
          } else {
            setMcMeta({ status: 'error', error: `Moneycontrol HTTP ${mc.value.status}` })
          }
        } else {
          setMcMeta({ status: 'timeout', error: 'Moneycontrol request timed out' })
        }
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

  const dhanRows = wsRows.length ? wsRows : pollRows
  const rows = board === 'moneycontrol' ? mcRows : dhanRows
  const refreshedAt = board === 'moneycontrol'
    ? (mcMeta.refreshed_at || rows?.[0]?.refreshed_at)
    : (marketTop?.refreshed_at || pollMeta.refreshed_at || rows?.[0]?.refreshed_at)
  const status = board === 'moneycontrol' ? mcMeta.status : (marketTop?.status || pollMeta.status)
  const streaming = wsStatus === 'live' && wsRows.length > 0
  const boardNote = board === 'moneycontrol'
    ? (mcMeta.error || mcMeta.note || 'Waiting for Moneycontrol All Options Top Gainers…')
    : (err || pollMeta.error || pollMeta.note || 'Waiting for Dhan option-chain gainers…')
  const authRequired = apiStatus?.status === 'API_AUTH_REQUIRED'
    || status === 'auth_required'
    || /auth|API authentication|Unlock dashboard/i.test(String(err || mcMeta.error || pollMeta.error || ''))
    || (!loading && rows.length === 0 && /timeout/i.test(String(boardNote)))
  const emptyNote = authRequired
    ? 'Dashboard API session required. Unlock once to load Market Top boards.'
    : boardNote

  const subtitle = useMemo(() => {
    if (board === 'moneycontrol') {
      return 'Reference board (LIVE_SCRAPED) · not used for live orders'
    }
    return streaming
      ? `Dhan live · ${marketTop?.stream_mode || 'ultra_micro'}`
      : 'Dhan live · trading truth for paper MTM'
  }, [board, streaming, marketTop?.stream_mode])

  return (
    <div className={cn('flex flex-col h-full min-h-0 overflow-hidden bg-surface', compact && 'text-[11px]')}>
      <div className="px-3 py-2 border-b border-border bg-surface-1 flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
        <div className="min-w-0">
          <div className="text-xs font-semibold text-text-primary uppercase tracking-wider">
            {board === 'moneycontrol' ? 'All-India Top Option Gainers' : 'Market Top CE / PE'}
          </div>
          <div className="text-[10px] text-text-muted font-mono truncate">
            {refreshedAt ? `Refreshed ${refreshedAt}` : loading ? 'Loading…' : 'Waiting'}
            {status ? ` · ${status}` : ''}
            {` · ${rows.length} rows`}
            {` · ${subtitle}`}
          </div>
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            type="button"
            className={cn(
              'pill border text-[10px]',
              board === 'moneycontrol'
                ? 'bg-amber/10 text-amber border-amber/30'
                : 'bg-surface-2 text-text-muted border-border',
            )}
            onClick={() => setBoard('moneycontrol')}
          >
            MONEYCONTROL
          </button>
          <button
            type="button"
            className={cn(
              'pill border text-[10px]',
              board === 'dhan'
                ? 'bg-up/10 text-up border-up/20'
                : 'bg-surface-2 text-text-muted border-border',
            )}
            onClick={() => setBoard('dhan')}
          >
            DHAN LIVE
          </button>
          <span className={cn(
            'pill text-[10px] border',
            streaming ? 'bg-up/10 text-up border-up/20' : 'bg-surface-2 text-text-muted border-border',
          )}>
            {streaming ? 'WS STREAM' : 'HTTP POLL'}
          </span>
          <span className="pill text-[10px] bg-down/10 text-down border border-down/20">
            LIVE OFF
          </span>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="flex-1 flex items-center justify-center p-6 text-center text-text-muted text-xs">
          <div className="max-w-md mx-auto space-y-3">
            <div className="font-semibold text-text-primary">
              {loading ? 'Loading market top…' : (authRequired ? 'API unlock required' : 'No gainer rows yet')}
            </div>
            <div>{emptyNote}</div>
            {authRequired && <AuthUnlock compact />}
          </div>
        </div>
      ) : (
        <div className="flex-1 min-h-0 overflow-auto">
          <table className="w-full min-w-[980px] text-left border-collapse">
            <thead className="sticky top-0 z-10">
              <tr style={{ background: '#065f46' }}>
                {['#', 'Symbol', 'Expiry', 'Type', 'Strike', 'LTP', 'Change', 'Gain %', 'Volume', 'OI', 'Source'].map((h) => (
                  <th
                    key={h}
                    className="px-2 py-2 text-[10px] font-semibold uppercase tracking-wider text-white whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => {
                const symbol = String(row.symbol || row.underlying || '').toUpperCase()
                const gain = Number(row.gain_pct || 0)
                const change = Number(row.change ?? row.change_rs ?? 0)
                const opt = String(row.option_type || '').toUpperCase()
                const prov = row.data_provenance || (board === 'moneycontrol' ? 'LIVE_SCRAPED' : 'DHAN_OPTION_CHAIN_LIVE')
                return (
                  <tr
                    key={`${board}-${symbol}-${opt}-${row.strike}-${i}`}
                    className={cn(
                      'border-b border-border text-xs font-mono cursor-pointer hover:bg-surface-2',
                      i % 2 === 0 ? 'bg-surface' : 'bg-surface-1',
                    )}
                    onClick={() => symbol && onSelectUnderlying?.(symbol)}
                    title={row.market_match_note || undefined}
                  >
                    <td className="px-2 py-1.5 text-text-muted">{row.rank ?? i + 1}</td>
                    <td className="px-2 py-1.5 font-semibold text-text-primary">{symbol}</td>
                    <td className="px-2 py-1.5 text-text-secondary whitespace-nowrap">{fmtExpiry(row.expiry_date)}</td>
                    <td className={cn('px-2 py-1.5 font-semibold', opt === 'CE' ? 'text-up' : 'text-down')}>{opt || '—'}</td>
                    <td className="px-2 py-1.5 num text-right">{fmtInt(Number(row.strike || 0))}</td>
                    <td className="px-2 py-1.5 num text-right">{fmt(Number(row.ltp || 0), 2)}</td>
                    <td className={cn('px-2 py-1.5 num text-right', change >= 0 ? 'text-up' : 'text-down')}>
                      {fmt(change, 2)}
                    </td>
                    <td className="px-2 py-1.5 num text-right font-semibold text-down">{fmt(gain, 2)}%</td>
                    <td className="px-2 py-1.5 num text-right">{fmtInt(Number(row.volume || 0))}</td>
                    <td className="px-2 py-1.5 num text-right">{fmtInt(Number(row.oi || 0))}</td>
                    <td className="px-2 py-1.5 text-[10px] text-text-muted whitespace-nowrap">{prov}</td>
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
