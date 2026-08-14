import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { useStore } from '../store'
import { API_BASE, API_HEADERS } from '../config'
import { PriceCell } from './ui/PriceCell'
import { fmt, cn } from '../lib/utils'

const CORE_INDICES = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX', 'BANKEX']

interface Contract {
  strike: number
  option_type: 'CE' | 'PE'
  ltp: number
  oi: number
  dOI?: number
  oi_change?: number
  change_in_oi?: number
  volume: number
  iv: number
  top_bid_price?: number
  top_ask_price?: number
  bid?: number
  ask?: number
  bid_price?: number
  ask_price?: number
}
interface UnderlyingDiscovery {
  underlyings?: string[]
  indices?: string[]
  equity_options?: string[]
  counts?: { total?: number; indices?: number; equity_options?: number; option_contracts?: number }
  source?: string
  broker?: string
}

const apiBase = () => API_BASE || window.location.origin
async function apiJSON(path: string, timeoutMs = 12000) {
  const ctrl = new AbortController()
  const timer = window.setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const response = await fetch(`${apiBase()}${path}`, {
      credentials: 'include',
      headers: { Accept: 'application/json', ...API_HEADERS },
      signal: ctrl.signal,
    })
    if (!response.ok) throw new Error(`HTTP_${response.status}`)
    return await response.json()
  } finally {
    window.clearTimeout(timer)
  }
}
function quotePrice(c: Contract | undefined, side: 'bid' | 'ask') {
  if (!c) return null
  const anyC = c as any
  const v = side === 'bid' ? (anyC.top_bid_price ?? anyC.bid ?? anyC.bid_price) : (anyC.top_ask_price ?? anyC.ask ?? anyC.ask_price)
  return v == null || Number(v) <= 0 ? null : Number(v)
}
function oiChange(c: Contract | undefined) {
  if (!c) return null
  const raw = c.dOI ?? c.oi_change ?? c.change_in_oi
  return raw == null ? null : Number(raw)
}
function formatOI(value: number | null | undefined) {
  const val = Number(value ?? 0)
  if (!Number.isFinite(val)) return '--'
  if (Math.abs(val) >= 1e6) return `${(val / 1e6).toFixed(1)}M`
  if (Math.abs(val) >= 1e3) return `${(val / 1e3).toFixed(1)}K`
  return String(Math.trunc(val))
}
function oiBar(val: number, max: number, type: 'CE' | 'PE') {
  const pct = max > 0 ? Math.min((val / max) * 100, 100) : 0
  return <div className="flex items-center gap-1 w-20">
    {type === 'CE' && <div className="flex-1 h-1.5 bg-surface-3 rounded overflow-hidden"><div className="h-full bg-up/50 rounded" style={{ width: `${pct}%` }} /></div>}
    <span className="num text-[11px] text-text-secondary whitespace-nowrap">{formatOI(val)}</span>
    {type === 'PE' && <div className="flex-1 h-1.5 bg-surface-3 rounded overflow-hidden"><div className="h-full bg-down/50 rounded ml-auto" style={{ width: `${pct}%` }} /></div>}
  </div>
}

function SymbolControls({ chainSymbol, setChainSymbol, universe, discovery, discoveryError }: {
  chainSymbol: string; setChainSymbol: (symbol: string) => void; universe: string[]; discovery: UnderlyingDiscovery | null; discoveryError: string
}) {
  const [query, setQuery] = useState(chainSymbol)
  const indexSymbols = discovery?.indices?.length ? discovery.indices : CORE_INDICES
  useEffect(() => setQuery(chainSymbol), [chainSymbol])
  const choose = (symbol: string) => {
    const next = String(symbol || '').trim().toUpperCase()
    if (!next) return
    setQuery(next)
    setChainSymbol(next)
  }
  const submit = (event: FormEvent) => {
    event.preventDefault()
    const next = query.trim().toUpperCase()
    if (!next || (universe.length > 0 && !universe.includes(next))) return
    choose(next)
  }
  return <div className="flex flex-wrap items-center gap-2 px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
    <div className="flex flex-wrap gap-1">{indexSymbols.map(sym => <button key={sym} onClick={() => choose(sym)} className={cn('px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors', chainSymbol === sym ? 'bg-accent text-white' : 'bg-surface-2 text-text-secondary hover:text-text-primary border border-border')}>{sym}</button>)}</div>
    <form onSubmit={submit} className="flex items-center gap-1 min-w-[260px] flex-1 max-w-xl">
      <input value={query} onChange={e => setQuery(e.target.value.toUpperCase())} list="option-underlying-universe" placeholder="Search any broker-supported equity/index option underlying" className="w-full bg-surface-2 border border-border rounded px-2.5 py-1 text-xs text-text-primary font-mono" aria-label="Search option underlying" />
      <datalist id="option-underlying-universe">{universe.map(sym => <option value={sym} key={sym} />)}</datalist>
      <button type="submit" className="soft-btn" style={{ minHeight: 28 }}>Load</button>
    </form>
    <div className="ml-auto flex items-center gap-2 text-[10px] font-mono text-text-muted">
      <span className="pill">DHAN UNIVERSE {discovery?.counts?.total ?? universe.length ?? '--'}</span>
      <span className="pill">EQ OPT {discovery?.counts?.equity_options ?? '--'}</span>
      {discoveryError && <span className="pill text-amber">DISCOVERY DEGRADED</span>}
    </div>
  </div>
}

export function OptionChain() {
  const { chainSymbol, setChainSymbol, chain, marketOpen, state } = useStore()
  const atmRef = useRef<HTMLTableRowElement>(null)
  const [range, setRange] = useState(0)
  const [discovery, setDiscovery] = useState<UnderlyingDiscovery | null>(null)
  const [discoveryError, setDiscoveryError] = useState('')
  const [expiries, setExpiries] = useState<string[]>([])
  const [selectedExpiry, setSelectedExpiry] = useState('')
  const [expiryData, setExpiryData] = useState<any>(null)
  const [expiryError, setExpiryError] = useState('')

  useEffect(() => {
    let cancelled = false
    apiJSON('/api/underlyings')
      .then(payload => {
        if (cancelled) return
        const all = Array.isArray(payload?.underlyings) ? payload.underlyings.map((s: any) => String(s).toUpperCase()).filter(Boolean) : []
        if (!all.length) throw new Error('EMPTY_BROKER_UNIVERSE')
        setDiscovery({ ...payload, underlyings: all })
        setDiscoveryError('')
      })
      .catch(err => {
        if (cancelled) return
        setDiscoveryError(String(err?.message || err))
        setDiscovery({ underlyings: CORE_INDICES, indices: CORE_INDICES, source: 'degraded_manual_index_fallback', broker: 'DHAN' })
      })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    let cancelled = false
    setSelectedExpiry('')
    setExpiryData(null)
    setExpiryError('')
    apiJSON(`/api/expiries/${encodeURIComponent(chainSymbol)}`)
      .then(payload => {
        if (cancelled) return
        const values = Array.isArray(payload?.expiries) ? payload.expiries.map((x: any) => String(x)).filter(Boolean) : []
        setExpiries(values)
        // Live chain can still be valid while master expiry lookup is catching up.
        if (!values.length) setExpiryError(String(payload?.status || 'NO_EXPIRIES_IN_BROKER_MASTER'))
      })
      .catch(err => {
        if (cancelled) return
        setExpiries([])
        setExpiryError(String(err?.message || err))
      })
    return () => { cancelled = true }
  }, [chainSymbol])

  useEffect(() => {
    if (!selectedExpiry) { setExpiryData(null); return }
    let cancelled = false
    setExpiryError('')
    apiJSON(`/api/chain-expiry/${encodeURIComponent(chainSymbol)}?expiry=${encodeURIComponent(selectedExpiry)}`, 20000)
      .then(payload => {
        if (cancelled) return
        setExpiryData(payload)
        if (!Array.isArray(payload?.contracts) || payload.contracts.length === 0) setExpiryError(String(payload?.status || 'NO_DHAN_DATA'))
      })
      .catch(err => { if (!cancelled) { setExpiryData(null); setExpiryError(String(err?.message || err)) } })
    return () => { cancelled = true }
  }, [chainSymbol, selectedExpiry])

  const universe = useMemo(() => {
    const all = discovery?.underlyings || CORE_INDICES
    return Array.from(new Set(all.map(s => String(s).toUpperCase()).filter(Boolean))).sort((a, b) => a.localeCompare(b))
  }, [discovery])
  const liveDefaultData = chain[chainSymbol]
  const harvestedExpiries = useMemo(() => {
    const fromLive = new Set<string>(expiries)
    const contracts = liveDefaultData?.contracts
    if (Array.isArray(contracts)) {
      for (const row of contracts) {
        const exp = String(row?.expiry_date || row?.expiry || '').slice(0, 10)
        if (/^\d{4}-\d{2}-\d{2}$/.test(exp)) fromLive.add(exp)
      }
    }
    return Array.from(fromLive).sort()
  }, [expiries, liveDefaultData])
  const data = selectedExpiry ? expiryData : liveDefaultData
  const expiryWarning = selectedExpiry ? expiryError : (harvestedExpiries.length ? '' : expiryError)

  useEffect(() => { if (atmRef.current) atmRef.current.scrollIntoView({ block: 'center', behavior: 'smooth' }) }, [data?.spot, chainSymbol, selectedExpiry, range])

  const chainMismatch = Boolean(data?.underlying && String(data.underlying).toUpperCase() !== chainSymbol)
  const contracts: Contract[] = chainMismatch ? [] : (data?.contracts ?? [])
  const spot = chainMismatch ? 0 : Number(data?.spot ?? 0)
  const pcr = chainMismatch ? '--' : (data?.pcr ?? '--')
  const status = chainMismatch ? 'CHAIN_SYMBOL_MISMATCH' : (data?.status ?? (selectedExpiry ? 'LOADING_EXPIRY' : 'LOADING'))
  const dataSource = data?.data_source ?? state?.data_source ?? '--'
  const sourcePriority = data?.source_priority ?? '--'
  const stale = Boolean(data?.stale) || String(status).toUpperCase().includes('STALE') || /(csv|synthetic|mock|fake)/i.test(String(sourcePriority))
  const snapshotAge = data?.snapshot_age_seconds
  const fetchedAt = data?.fetched_at_utc ?? data?.snapshot_time ?? data?.generated_at ?? data?.stream_tick_at ?? '--'
  const marketReason = String(state?.market?.reason ?? data?.message ?? (marketOpen ? 'Market open' : 'Market closed'))

  const strikeMap = new Map<number, { CE?: Contract; PE?: Contract }>()
  for (const contract of contracts) {
    const strike = Number(contract?.strike), side = String(contract?.option_type || '').toUpperCase()
    if (!Number.isFinite(strike) || !['CE', 'PE'].includes(side)) continue
    if (!strikeMap.has(strike)) strikeMap.set(strike, {})
    strikeMap.get(strike)![side as 'CE' | 'PE'] = contract
  }
  const strikes = Array.from(strikeMap.keys()).sort((a, b) => a - b)
  const atmIdx = strikes.length ? strikes.reduce((best, strike, index) => Math.abs(strike - spot) < Math.abs(strikes[best] - spot) ? index : best, 0) : 0
  const visible = range === 0 ? strikes : strikes.slice(Math.max(0, atmIdx - range), Math.min(strikes.length, atmIdx + range + 1))
  const maxOI = Math.max(...contracts.map(c => Number(c.oi ?? 0)), 1)
  const streamLive = Boolean(marketOpen && !selectedExpiry && (data?.verified_live_dhan || data?.live === true) && !stale)
  const streamLabel = selectedExpiry ? 'DHAN EXPIRY SNAPSHOT' : streamLive ? 'LIVE DHAN' : (marketOpen ? 'POLLING / DEGRADED' : 'SESSION SNAPSHOT')

  return <div className="flex flex-col h-full">
    <SymbolControls chainSymbol={chainSymbol} setChainSymbol={setChainSymbol} universe={universe} discovery={discovery} discoveryError={discoveryError} />
    <div className="flex flex-wrap items-center gap-3 px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
      <span className={cn('pill text-[10px] border', streamLive ? 'bg-up/10 text-up border-up/20' : 'bg-amber/10 text-amber border-amber/20')}>{streamLabel}</span>
      <label className="flex items-center gap-1.5"><span className="text-text-muted text-xs">EXPIRY</span><select aria-label="Option expiry" value={selectedExpiry} onChange={e => { setSelectedExpiry(e.target.value); setRange(0) }} className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-secondary"><option value="">AUTO / NEAREST</option>{harvestedExpiries.map(expiry => <option value={expiry} key={expiry}>{expiry}</option>)}</select></label>
      <span className="pill text-[10px]">EXPIRIES {harvestedExpiries.length}</span>
      {expiryWarning && <span className="pill text-amber text-[10px]">EXPIRY DATA {expiryWarning}</span>}
      <div><span className="text-text-muted text-xs"> SYMBOL </span><span className="num text-sm font-semibold">{chainSymbol}</span></div>
      <div><span className="text-text-muted text-xs"> SPOT </span><span className="num text-sm font-semibold">{spot ? fmt(spot, 2) : '--'}</span></div>
      <div><span className="text-text-muted text-xs"> PCR </span><span className="num text-sm font-semibold">{typeof pcr === 'number' ? pcr.toFixed(2) : pcr}</span></div>
      <div><span className="text-text-muted text-xs"> CONTRACTS </span><span className="num text-xs">{contracts.length}</span></div>
      <div><span className="text-text-muted text-xs"> STRIKES </span><span className="num text-xs">{strikes.length}</span></div>
      <div className="ml-auto flex items-center gap-2"><span className="text-text-muted text-[10px]">VISIBLE</span><select aria-label="Strike visibility" value={range} onChange={e => setRange(Number(e.target.value))} className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-secondary"><option value={0}>ALL STRIKES ({strikes.length})</option>{[5,10,20,40].map(n => <option key={n} value={n}>+/-{n} ATM</option>)}</select></div>
    </div>
    <div className={cn('px-4 py-2 border-b border-border text-[10px] font-mono', stale || !streamLive ? 'text-amber bg-amber/5' : 'text-text-muted')}>source={String(dataSource)} priority={String(sourcePriority)} status={String(status)}{selectedExpiry ? ` selected_expiry=${selectedExpiry}` : ''}{data?.complete_chain === true ? ' complete_chain=true' : ''}{snapshotAge != null ? ` age=${snapshotAge}s` : ''}{fetchedAt !== '--' ? ` fetched=${String(fetchedAt)}` : ''}{discovery?.source ? ` universe=${String(discovery.source)}` : ''}{data?.message ? ` - ${String(data.message)}` : ''}</div>
    {chainMismatch && <div className="px-4 py-2 bg-down/5 text-down text-xs border-b border-border">Backend returned {String(data?.underlying)} while UI selected {chainSymbol}. Wrong-symbol rows are hidden.</div>}
    {contracts.length === 0 ? <div className="flex-1 overflow-auto p-4"><div className="card p-4"><div className="panel-title">Option Chain</div><div className="mt-3 text-amber font-semibold">NO VERIFIED BROKER CHAIN ROWS</div><div className="mt-2 text-xs text-text-muted">{String(data?.message || marketReason || 'Waiting for a Dhan-backed option-chain snapshot.')}</div><div className="mt-3 grid gap-2 md:grid-cols-4 text-xs"><div><span className="text-text-muted">Selected:</span> {chainSymbol}</div><div><span className="text-text-muted">Expiry:</span> {selectedExpiry || 'AUTO'}</div><div><span className="text-text-muted">Universe:</span> {discovery?.counts?.total ?? universe.length}</div><div><span className="text-text-muted">Safety:</span> ANALYZER / PAPER · LIVE OFF</div></div></div></div> :
      <div className="flex-1 overflow-auto"><table className="w-full border-collapse text-xs"><thead className="sticky top-0 z-10 bg-surface-1"><tr>{['OI','ChgOI','Vol','IV','LTP','Bid','STRIKE','Ask','LTP','IV','Vol','ChgOI','OI'].map((h,i)=><th key={`${h}-${i}`} className={cn('thead border-b border-border', i<6?'text-right':i===6?'text-center bg-surface-2 px-4 py-2 text-text-primary font-bold':'text-left')}>{h}</th>)}</tr></thead><tbody>{visible.map(strike => {
        const row = strikeMap.get(strike)!, ce = row.CE, pe = row.PE
        const step = strikes.length > 1 ? Math.abs(strikes[1] - strikes[0]) : 0
        const isATM = step > 0 && Math.abs(strike - spot) < step / 2
        const ceChange = oiChange(ce), peChange = oiChange(pe)
        return <tr key={strike} ref={isATM ? atmRef : undefined} className={cn('trow', isATM && 'atm-row')}>
          <td className="tcell text-right">{ce ? oiBar(Number(ce.oi || 0), maxOI, 'CE') : '--'}</td><td className={cn('tcell text-right num', ceChange != null && ceChange > 0 ? 'text-up' : ceChange != null && ceChange < 0 ? 'text-down' : '')}>{ceChange == null ? '--' : `${ceChange >= 0 ? '+' : ''}${formatOI(ceChange)}`}</td><td className="tcell text-right">{ce ? formatOI(ce.volume) : '--'}</td><td className="tcell text-right text-amber">{ce?.iv != null ? Number(ce.iv).toFixed(2) : '--'}</td><td className="tcell text-right">{ce ? <PriceCell value={Number(ce.ltp || 0)} /> : '--'}</td><td className="tcell text-right text-text-muted">{quotePrice(ce,'bid') != null ? fmt(quotePrice(ce,'bid')!,2) : '--'}</td>
          <td className={cn('tcell text-center font-bold text-sm px-4', isATM ? 'text-accent bg-surface-2' : 'text-text-primary bg-surface-1')}>{fmt(strike,2)}{isATM && <span className="ml-1 text-[9px] text-accent font-mono">ATM</span>}</td>
          <td className="tcell text-left text-text-muted">{quotePrice(pe,'ask') != null ? fmt(quotePrice(pe,'ask')!,2) : '--'}</td><td className="tcell text-left">{pe ? <PriceCell value={Number(pe.ltp || 0)} /> : '--'}</td><td className="tcell text-left text-amber">{pe?.iv != null ? Number(pe.iv).toFixed(2) : '--'}</td><td className="tcell text-left">{pe ? formatOI(pe.volume) : '--'}</td><td className={cn('tcell text-left num', peChange != null && peChange > 0 ? 'text-up' : peChange != null && peChange < 0 ? 'text-down' : '')}>{peChange == null ? '--' : `${peChange >= 0 ? '+' : ''}${formatOI(peChange)}`}</td><td className="tcell text-left">{pe ? oiBar(Number(pe.oi || 0), maxOI, 'PE') : '--'}</td>
        </tr>
      })}</tbody></table></div>}
  </div>
}
