import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { useStore } from '../store'
import { API_BASE, API_HEADERS } from '../config'
import { PriceCell } from './ui/PriceCell'
import { fmt, cn } from '../lib/utils'

const CORE_INDICES = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX', 'BANKEX']

type Contract = {
  strike: number
  option_type: 'CE' | 'PE'
  ltp: number
  oi: number
  volume: number
  iv: number
  dOI?: number
  oi_change?: number
  change_in_oi?: number
  oi_change_percent?: number
  oi_chg_pct?: number
  volume_change?: number
  volume_change_percent?: number
  vol_chg_pct?: number
  change?: number
  change_percent?: number
  ltp_change_percent?: number
  buildup?: string
  delta?: number
  gamma?: number
  theta?: number
  vega?: number
  top_bid_price?: number
  top_ask_price?: number
  bid?: number
  ask?: number
  bid_price?: number
  ask_price?: number
}

type UnderlyingDiscovery = {
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

function num(v: unknown) {
  if (v == null || v === '') return null
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

function quotePrice(c: Contract | undefined, side: 'bid' | 'ask') {
  if (!c) return null
  const value = side === 'bid'
    ? (c.top_bid_price ?? c.bid ?? c.bid_price)
    : (c.top_ask_price ?? c.ask ?? c.ask_price)
  const n = num(value)
  return n != null && n > 0 ? n : null
}

function pct(v: number | null | undefined, digits = 1) {
  if (v == null || !Number.isFinite(v)) return '--'
  return `${v > 0 ? '+' : ''}${v.toFixed(digits)}%`
}

function oiChange(c: Contract | undefined) {
  return c ? num(c.dOI ?? c.oi_change ?? c.change_in_oi) : null
}

function oiChangePct(c: Contract | undefined) {
  if (!c) return null
  const direct = num(c.oi_change_percent ?? c.oi_chg_pct)
  if (direct != null) return direct
  const delta = oiChange(c)
  const oi = num(c.oi)
  if (delta == null || oi == null) return null
  const previous = oi - delta
  return Math.abs(previous) < 1e-9 ? null : (delta / Math.abs(previous)) * 100
}

function volumeChangePct(c: Contract | undefined) {
  if (!c) return null
  const direct = num(c.volume_change_percent ?? c.vol_chg_pct)
  if (direct != null) return direct
  const delta = num(c.volume_change)
  const volume = num(c.volume)
  if (delta == null || volume == null) return null
  const previous = volume - delta
  return Math.abs(previous) < 1e-9 ? null : (delta / Math.abs(previous)) * 100
}

function buildup(c: Contract | undefined) {
  if (!c) return '--'
  const explicit = String(c.buildup || '').trim()
  if (explicit) return explicit
  const dOi = oiChange(c)
  const dPx = num(c.change ?? c.change_percent ?? c.ltp_change_percent)
  if (dOi == null || dPx == null) return '--'
  if (dPx > 0 && dOi > 0) return 'Long Buildup'
  if (dPx < 0 && dOi > 0) return 'Short Buildup'
  if (dPx > 0 && dOi < 0) return 'Short Covering'
  if (dPx < 0 && dOi < 0) return 'Long Unwinding'
  return 'Neutral'
}

function formatOI(value: unknown) {
  const n = num(value)
  if (n == null) return '--'
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return String(Math.trunc(n))
}

function SymbolControls({ chainSymbol, setChainSymbol, universe, discovery, discoveryError }: {
  chainSymbol: string
  setChainSymbol: (symbol: string) => void
  universe: string[]
  discovery: UnderlyingDiscovery | null
  discoveryError: string
}) {
  const [query, setQuery] = useState(chainSymbol)
  useEffect(() => setQuery(chainSymbol), [chainSymbol])

  const indexSymbols = useMemo(() => Array.from(new Set([
    ...CORE_INDICES,
    ...(discovery?.indices || []),
  ].map(value => String(value).trim().toUpperCase()).filter(Boolean))), [discovery])

  const choose = (value: string) => {
    const symbol = String(value || '').trim().toUpperCase()
    if (!symbol) return
    setQuery(symbol)
    setChainSymbol(symbol)
  }

  const submit = (event: FormEvent) => {
    event.preventDefault()
    const symbol = query.trim().toUpperCase()
    if (!symbol || (universe.length > 0 && !universe.includes(symbol))) return
    choose(symbol)
  }

  return <div className="flex flex-wrap items-center gap-2 px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
    <div className="flex flex-wrap gap-1">
      {indexSymbols.map(symbol => <button
        key={symbol}
        data-chain-symbol={symbol}
        aria-label={`Option chain ${symbol}`}
        onClick={() => choose(symbol)}
        className={cn('px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors', chainSymbol === symbol ? 'bg-accent text-white' : 'bg-surface-2 text-text-secondary hover:text-text-primary border border-border')}
      >{symbol}</button>)}
    </div>
    <form onSubmit={submit} className="flex items-center gap-1 min-w-[260px] flex-1 max-w-xl">
      <input value={query} onChange={e => setQuery(e.target.value.toUpperCase())} list="option-underlying-universe" placeholder="Search broker-supported option underlying" className="w-full bg-surface-2 border border-border rounded px-2.5 py-1 text-xs text-text-primary font-mono" aria-label="Search option underlying" />
      <datalist id="option-underlying-universe">{universe.map(symbol => <option value={symbol} key={symbol} />)}</datalist>
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
  const [range, setRange] = useState(10)
  const [discovery, setDiscovery] = useState<UnderlyingDiscovery | null>(null)
  const [discoveryError, setDiscoveryError] = useState('')
  const [expiries, setExpiries] = useState<string[]>([])
  const [selectedExpiry, setSelectedExpiry] = useState('')
  const [expiryData, setExpiryData] = useState<any>(null)
  const [expiryError, setExpiryError] = useState('')

  useEffect(() => {
    let cancelled = false
    apiJSON('/api/underlyings').then(payload => {
      if (cancelled) return
      const underlyings = Array.isArray(payload?.underlyings) ? payload.underlyings.map((value: unknown) => String(value).trim().toUpperCase()).filter(Boolean) : []
      if (!underlyings.length) throw new Error('EMPTY_BROKER_UNIVERSE')
      setDiscovery({ ...payload, underlyings })
      setDiscoveryError('')
    }).catch(error => {
      if (cancelled) return
      setDiscoveryError(String(error?.message || error))
      setDiscovery({ underlyings: CORE_INDICES, indices: CORE_INDICES, source: 'degraded_manual_index_fallback', broker: 'DHAN' })
    })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    let cancelled = false
    setSelectedExpiry('')
    setExpiryData(null)
    setExpiryError('')
    apiJSON(`/api/expiries/${encodeURIComponent(chainSymbol)}`).then(payload => {
      if (cancelled) return
      const values = Array.isArray(payload?.expiries) ? payload.expiries.map((value: unknown) => String(value)).filter(Boolean) : []
      setExpiries(values)
      if (!values.length) setExpiryError(String(payload?.status || 'NO_EXPIRIES_IN_BROKER_MASTER'))
    }).catch(error => {
      if (cancelled) return
      setExpiries([])
      setExpiryError(String(error?.message || error))
    })
    return () => { cancelled = true }
  }, [chainSymbol])

  useEffect(() => {
    if (!selectedExpiry) {
      setExpiryData(null)
      return
    }
    let cancelled = false
    setExpiryError('')
    apiJSON(`/api/chain-expiry/${encodeURIComponent(chainSymbol)}?expiry=${encodeURIComponent(selectedExpiry)}`, 20000).then(payload => {
      if (cancelled) return
      setExpiryData(payload)
      if (!Array.isArray(payload?.contracts) || payload.contracts.length === 0) setExpiryError(String(payload?.status || 'NO_DHAN_DATA'))
    }).catch(error => {
      if (cancelled) return
      setExpiryData(null)
      setExpiryError(String(error?.message || error))
    })
    return () => { cancelled = true }
  }, [chainSymbol, selectedExpiry])

  const universe = useMemo(() => Array.from(new Set([
    ...CORE_INDICES,
    ...(discovery?.underlyings || []),
  ].map(value => String(value).trim().toUpperCase()).filter(Boolean))).sort((a, b) => a.localeCompare(b)), [discovery])

  const liveDefaultData: any = (chain as any)?.[chainSymbol]
  const data: any = selectedExpiry ? expiryData : liveDefaultData
  const mismatch = Boolean(data?.underlying && String(data.underlying).toUpperCase() !== chainSymbol)
  const contracts: Contract[] = !mismatch && Array.isArray(data?.contracts) ? data.contracts : []
  const spot = !mismatch && num(data?.spot) != null && Number(data.spot) > 0 ? Number(data.spot) : null
  const pcrValue = !mismatch ? num(data?.pcr) : null
  const status = mismatch ? 'CHAIN_SYMBOL_MISMATCH' : String(data?.status || (selectedExpiry ? 'LOADING_EXPIRY' : 'LOADING'))
  const sourceValue = String(data?.source ?? data?.source_priority ?? data?.data_source ?? discovery?.source ?? '--').trim().toLowerCase()
  const fetchedAt = data?.fetched_at_utc ?? data?.snapshot_time ?? data?.generated_at ?? data?.stream_tick_at ?? '--'
  const stale = Boolean(data?.stale) || /stale|synthetic|mock|fake/.test(`${status} ${sourceValue}`.toLowerCase())
  const completeChain = data?.complete_chain === true

  const harvestedExpiries = useMemo(() => {
    const set = new Set(expiries)
    const rows = Array.isArray(liveDefaultData?.contracts) ? liveDefaultData.contracts : []
    for (const row of rows) {
      const expiry = String(row?.expiry_date || row?.expiry || '').slice(0, 10)
      if (/^\d{4}-\d{2}-\d{2}$/.test(expiry)) set.add(expiry)
    }
    return Array.from(set).sort()
  }, [expiries, liveDefaultData])

  const strikeMap = new Map<number, { CE?: Contract; PE?: Contract }>()
  for (const contract of contracts) {
    const strike = num(contract?.strike)
    const side = String(contract?.option_type || '').toUpperCase()
    if (strike == null || (side !== 'CE' && side !== 'PE')) continue
    if (!strikeMap.has(strike)) strikeMap.set(strike, {})
    strikeMap.get(strike)![side] = contract
  }
  const strikes = Array.from(strikeMap.keys()).sort((a, b) => a - b)
  const atmIndex = spot != null && strikes.length ? strikes.reduce((best, strike, index) => Math.abs(strike - spot) < Math.abs(strikes[best] - spot) ? index : best, 0) : 0
  const visible = range === 0 ? strikes : strikes.slice(Math.max(0, atmIndex - range), Math.min(strikes.length, atmIndex + range + 1))

  useEffect(() => {
    if (atmRef.current) atmRef.current.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, [spot, chainSymbol, selectedExpiry, range])

  const noDataReason = String(data?.message || expiryError || state?.market?.reason || (marketOpen ? 'Waiting for verified Dhan option-chain rows.' : 'Market closed; no verified broker chain snapshot is available.'))

  return <div className="flex flex-col h-full">
    <SymbolControls chainSymbol={chainSymbol} setChainSymbol={setChainSymbol} universe={universe} discovery={discovery} discoveryError={discoveryError} />
    <div className="flex flex-wrap items-center gap-3 px-4 py-2 border-b border-border bg-surface-1 flex-shrink-0">
      <span className={cn('pill text-[10px] border', stale ? 'bg-amber/10 text-amber border-amber/20' : 'bg-surface-2 text-text-secondary border-border')}>{marketOpen ? (stale ? 'STALE / DEGRADED' : 'BROKER SESSION') : 'SESSION SNAPSHOT'}</span>
      <label className="flex items-center gap-1.5"><span className="text-text-muted text-xs">EXPIRY</span><select aria-label="Option expiry" value={selectedExpiry} onChange={event => { setSelectedExpiry(event.target.value); setRange(10) }} className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-secondary"><option value="">AUTO / NEAREST</option>{harvestedExpiries.map(expiry => <option value={expiry} key={expiry}>{expiry}</option>)}</select></label>
      <div><span className="text-text-muted text-xs"> SYMBOL </span><span className="num text-sm font-semibold">{chainSymbol}</span></div>
      <div><span className="text-text-muted text-xs"> SPOT </span><span className="num text-sm font-semibold">{spot != null ? fmt(spot, 2) : '--'}</span></div>
      <div><span className="text-text-muted text-xs"> PCR </span><span className="num text-sm font-semibold">{pcrValue != null ? pcrValue.toFixed(2) : '--'}</span></div>
      <div><span className="text-text-muted text-xs"> CONTRACTS </span><span className="num text-xs">{contracts.length}</span></div>
      <div><span className="text-text-muted text-xs"> STRIKES </span><span className="num text-xs">{strikes.length}</span></div>
      <div className="ml-auto flex items-center gap-2"><span className="text-text-muted text-[10px]">VISIBLE</span><select aria-label="Strike visibility" value={range} onChange={event => setRange(Number(event.target.value))} className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-secondary"><option value={0}>ALL STRIKES ({strikes.length})</option>{[5, 10, 20, 40].map(value => <option key={value} value={value}>+/-{value} ATM</option>)}</select></div>
    </div>
    <div className={cn('px-4 py-2 border-b border-border text-[10px] font-mono', stale || contracts.length === 0 ? 'text-amber bg-amber/5' : 'text-text-muted')}>
      symbol {chainSymbol} · source={sourceValue || '--'} · status={status}{completeChain ? ' · complete_chain=true' : ''}{fetchedAt !== '--' ? ` · fetched=${String(fetchedAt)}` : ''}{selectedExpiry ? ` · selected_expiry=${selectedExpiry}` : ''}
    </div>
    {mismatch && <div className="px-4 py-2 bg-down/5 text-down text-xs border-b border-border">Backend returned {String(data?.underlying)} while UI selected {chainSymbol}. Wrong-symbol rows are hidden.</div>}
    {contracts.length === 0 ? <div className="flex-1 overflow-auto p-4"><div className="card p-4"><div className="panel-title">Option Chain</div><div className="mt-3 text-amber font-semibold">NO VERIFIED BROKER CHAIN ROWS</div><div className="mt-2 text-xs text-text-muted">{noDataReason}</div><div className="mt-3 text-xs text-text-muted">Safety: ANALYZER / PAPER · LIVE OFF. No synthetic prices, strikes, OI, IV or Greeks are generated.</div></div></div> : <div className="flex-1 overflow-auto">
      <table className="w-full border-collapse text-[10px]">
        <thead className="sticky top-0 z-10 bg-surface-1"><tr><th className="thead border-b border-border text-right px-2 py-2">CE OI</th><th className="thead border-b border-border text-right px-2 py-2">CE OI%</th><th className="thead border-b border-border text-right px-2 py-2">CE VOL%</th><th className="thead border-b border-border text-right px-2 py-2">CE LTP</th><th className="thead border-b border-border text-right px-2 py-2">CE IV</th><th className="thead border-b border-border text-right px-2 py-2">CE BID</th><th className="thead border-b border-border text-center bg-surface-2 px-3 py-2">STRIKE</th><th className="thead border-b border-border text-left px-2 py-2">PE ASK</th><th className="thead border-b border-border text-left px-2 py-2">PE IV</th><th className="thead border-b border-border text-left px-2 py-2">PE LTP</th><th className="thead border-b border-border text-left px-2 py-2">PE VOL%</th><th className="thead border-b border-border text-left px-2 py-2">PE OI%</th><th className="thead border-b border-border text-left px-2 py-2">PE OI</th></tr></thead>
        <tbody>{visible.map(strike => {
          const row = strikeMap.get(strike) || {}
          const ce = row.CE
          const pe = row.PE
          const isAtm = spot != null && strikes.length > 1 && Math.abs(strike - spot) < Math.abs(strikes[1] - strikes[0]) / 2
          return <tr key={strike} ref={isAtm ? atmRef : undefined} className={cn('trow', isAtm && 'atm-row')}>
            <td className="tcell text-right">{formatOI(ce?.oi)}</td><td className="tcell text-right">{pct(oiChangePct(ce))}</td><td className="tcell text-right">{pct(volumeChangePct(ce))}</td><td className="tcell text-right">{ce ? <PriceCell value={Number(ce.ltp || 0)} /> : '--'}</td><td className="tcell text-right">{num(ce?.iv) != null ? Number(ce!.iv).toFixed(2) : '--'}</td><td className="tcell text-right">{quotePrice(ce, 'bid') != null ? fmt(quotePrice(ce, 'bid')!, 2) : '--'}</td>
            <td className={cn('tcell text-center font-bold text-sm px-3', isAtm ? 'text-accent bg-surface-2' : 'text-text-primary bg-surface-1')}>{fmt(strike, 2)}{isAtm && <span className="ml-1 text-[9px] text-accent font-mono">ATM</span>}</td>
            <td className="tcell text-left">{quotePrice(pe, 'ask') != null ? fmt(quotePrice(pe, 'ask')!, 2) : '--'}</td><td className="tcell text-left">{num(pe?.iv) != null ? Number(pe!.iv).toFixed(2) : '--'}</td><td className="tcell text-left">{pe ? <PriceCell value={Number(pe.ltp || 0)} /> : '--'}</td><td className="tcell text-left">{pct(volumeChangePct(pe))}</td><td className="tcell text-left">{pct(oiChangePct(pe))}</td><td className="tcell text-left">{formatOI(pe?.oi)}</td>
          </tr>
        })}</tbody>
      </table>
      <div className="hidden">{contracts.map((contract, index) => <span key={index}>{buildup(contract)} {num(contract.delta) ?? '--'} {num(contract.gamma) ?? '--'} {num(contract.theta) ?? '--'} {num(contract.vega) ?? '--'}</span>)}</div>
    </div>}
  </div>
}

export default OptionChain
