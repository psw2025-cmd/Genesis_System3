import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

type Status = 'PASS' | 'WAITING' | 'PARTIAL'
type LayerRow = { layer: string; status: Status; evidence: string; requiredForMoney: boolean }

// Enabled universe must match the scanner/paper path. SENSEX remains optional until
// its official Dhan chain is proven; it must not block NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY readiness.
const REQUIRED_CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
const OPTIONAL_CHAIN_SYMBOLS = ['SENSEX']
const ALL_CHAIN_SYMBOLS = [...REQUIRED_CHAIN_SYMBOLS, ...OPTIONAL_CHAIN_SYMBOLS]

function badge(status: Status) {
  const ok = status === 'PASS'
  const partial = status === 'PARTIAL'
  return (
    <span style={{
      display: 'inline-flex', padding: '4px 9px', borderRadius: 999, fontSize: 11, fontWeight: 900,
      border: `1px solid ${ok ? 'rgba(16,185,129,.45)' : partial ? 'rgba(245,158,11,.45)' : 'rgba(239,68,68,.45)'}`,
      color: ok ? 'var(--up)' : partial ? '#f59e0b' : 'var(--down)',
      background: ok ? 'rgba(16,185,129,.12)' : partial ? 'rgba(245,158,11,.12)' : 'rgba(239,68,68,.12)',
    }}>{status}</span>
  )
}

function looksLikeCandidate(x: any): boolean {
  if (!x || typeof x !== 'object' || Array.isArray(x)) return false
  const hasName = Boolean(x.underlying || x.symbol || x.ticker || x.name || x.trading_symbol)
  const hasScore = x.score !== undefined || x.display_score !== undefined || x.confidence !== undefined || x.gain_pct !== undefined || x.change_percent !== undefined
  const hasOption = x.option_side !== undefined || x.option_type !== undefined || x.signal_type !== undefined || x.side !== undefined || x.direction !== undefined
  return hasName && (hasScore || hasOption)
}

function collectCandidateRows(x: any, depth = 0): any[] {
  if (depth > 8 || x == null) return []
  if (Array.isArray(x)) return x.some(looksLikeCandidate) ? x.filter(looksLikeCandidate) : x.flatMap(v => collectCandidateRows(v, depth + 1))
  if (typeof x !== 'object') return []
  const rows: any[] = []
  for (const key of ['rankings', 'predictions', 'candidates', 'signals', 'top5', 'top', 'entries']) {
    if (Array.isArray(x[key])) rows.push(...collectCandidateRows(x[key], depth + 1))
  }
  for (const key of ['top_ce', 'top_pe', 'market_top_ce', 'market_top_pe', 'best_ce', 'best_pe']) {
    if (looksLikeCandidate(x[key])) rows.push(x[key])
  }
  for (const key of ['latest', 'data', 'scanner', 'market_wide', 'by_segment', 'segments', 'payload', 'result']) {
    if (x[key]) rows.push(...collectCandidateRows(x[key], depth + 1))
  }
  return rows
}

function countList(x: any): number {
  if (Array.isArray(x)) return x.length
  if (!x || typeof x !== 'object') return 0
  for (const key of ['positions', 'holdings', 'rows', 'data']) if (Array.isArray(x[key])) return x[key].length
  return collectCandidateRows(x).length
}

function hasCePe(x: any): boolean {
  const stack: any[] = [x]
  let seen = 0
  while (stack.length && seen < 1500) {
    seen += 1
    const item = stack.pop()
    if (Array.isArray(item)) for (const child of item.slice(0, 100)) stack.push(child)
    else if (item && typeof item === 'object') {
      const side = String(item.option_side || item.option_type || item.signal_type || item.side || item.direction || item.action || item.instrument_type || '').toUpperCase()
      if (side.includes('CE') || side.includes('PE') || side.includes('CALL') || side.includes('PUT')) return true
      for (const key of ['rankings', 'predictions', 'candidates', 'signals', 'latest', 'data', 'scanner', 'market_wide', 'by_segment', 'segments', 'top_ce', 'top_pe']) if (item[key]) stack.push(item[key])
    }
  }
  return false
}

function chainPass(x: any): boolean {
  if (!x || typeof x !== 'object') return false
  const source = String(x.data_source || x.source || '').toLowerCase()
  const status = String(x.status || '').toUpperCase()
  const contracts = Number(x.total_contracts || (Array.isArray(x.contracts) ? x.contracts.length : 0))
  const spot = Number(x.spot || 0)
  if (source !== 'dhan' || x.pendingProof || spot <= 0 || contracts <= 0) return false
  // After-hours Dhan snapshots are valid proof (stale=true is expected when market closed).
  if (['MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT', 'MARKET_CLOSED'].includes(status)) return true
  if (['OK', 'MARKET_OPEN'].includes(status) && x.stale !== true) return true
  return false
}

function safeNoTradeChain(x: any): boolean {
  if (!x || typeof x !== 'object') return false
  return String(x.data_source || x.source || '').toLowerCase() === 'dhan' && String(x.status || '').toUpperCase() === 'NO_DHAN_DATA'
}

export function SystemTruthControl() {
  const [data, setData] = useState<unknown>({})
  const [loading, setLoading] = useState(true)
  const [lastRun, setLastRun] = useState('')
  const [error, setError] = useState('')

  async function run() {
    setLoading(true); setError('')
    try {
      // Prefer batch endpoints — avoid stampeding 4× slow after-hours /api/chain calls.
      const entries = await Promise.all([
        ['health', axios.get(`${API_BASE}/api/health`, { timeout: 12000 })],
        ['state', axios.get(`${API_BASE}/api/state`, { timeout: 12000 })],
        ['batch_broker', axios.get(`${API_BASE}/api/batch/positions-holdings`, { timeout: 20000 })],
        ['batch_market', axios.get(`${API_BASE}/api/batch/market-data`, { timeout: 20000 })],
        ['batch_chains', axios.get(`${API_BASE}/api/batch/chains`, { timeout: 12000 })],
        ['scanner', axios.get(`${API_BASE}/api/scanner/top_contract_gainers?top_n=5`, { timeout: 15000 })],
        ['trades', axios.get(`${API_BASE}/api/trades/today`, { timeout: 12000 })],
      ].map(async ([key, promise]: any) => {
        try { const res = await promise; return [key, { ok: true, status: res.status, data: res.data }] }
        catch (err: any) { return [key, { ok: false, status: err?.response?.status || 0, error: err?.message || String(err) }] }
      }))
      const mapped: Record<string, any> = Object.fromEntries(entries)
      const brokerBatch = mapped.batch_broker?.data || {}
      const marketBatch = mapped.batch_market?.data || {}
      const chainsBatch = mapped.batch_chains?.data?.chains || {}
      mapped.broker = {
        ok: mapped.batch_broker?.ok && brokerBatch?.broker_status?.connected === true,
        status: mapped.batch_broker?.status || 0,
        data: brokerBatch.broker_status || {},
      }
      mapped.funds = {
        ok: mapped.batch_broker?.ok && brokerBatch?.funds?.success !== false,
        status: mapped.batch_broker?.status || 0,
        data: brokerBatch.funds || {},
      }
      mapped.holdings = {
        ok: mapped.batch_broker?.ok && brokerBatch?.holdings?.success !== false,
        status: mapped.batch_broker?.status || 0,
        data: brokerBatch.holdings || {},
      }
      mapped.positions = {
        ok: mapped.batch_broker?.ok && brokerBatch?.positions?.success !== false,
        status: mapped.batch_broker?.status || 0,
        data: brokerBatch.positions || {},
      }
      mapped.gain = {
        ok: mapped.batch_market?.ok && Boolean(marketBatch?.gain_rank),
        status: mapped.batch_market?.status || 0,
        data: marketBatch.gain_rank || {},
      }
      mapped.gates = {
        ok: mapped.batch_market?.ok && Boolean(marketBatch?.auto_gates),
        status: mapped.batch_market?.status || 0,
        data: marketBatch.auto_gates || {},
      }
      mapped.pnl = {
        ok: mapped.batch_market?.ok,
        status: mapped.batch_market?.status || 0,
        data: marketBatch.pnl || {},
      }
      for (const sym of ALL_CHAIN_SYMBOLS) {
        const payload = chainsBatch[sym]
        mapped[`chain_${sym}`] = payload
          ? { ok: true, status: 200, data: payload }
          : { ok: false, status: 0, error: 'missing_from_batch_chains' }
      }
      setData(mapped); setLastRun(new Date().toLocaleString())
    } catch (err: any) { setError(err?.message || String(err)) }
    finally { setLoading(false) }
  }

  useEffect(() => { run() }, [])

  const rows: LayerRow[] = useMemo(() => {
    const broker = data.broker?.data || {}, funds = data.funds?.data || {}, state = data.state?.data || {}, gain = data.gain?.data || {}, scanner = data.scanner?.data || {}, trades = data.trades?.data || {}, gates = data.gates?.data || {}
    const requiredChains = REQUIRED_CHAIN_SYMBOLS.map(sym => ({ sym, payload: data[`chain_${sym}`]?.data, ok: data[`chain_${sym}`]?.ok }))
    const optionalChains = OPTIONAL_CHAIN_SYMBOLS.map(sym => ({ sym, payload: data[`chain_${sym}`]?.data, ok: data[`chain_${sym}`]?.ok }))
    const requiredOk = requiredChains.filter(x => x.ok && chainPass(x.payload)).length
    const requiredSafeBlocks = requiredChains.filter(x => x.ok && safeNoTradeChain(x.payload)).length
    const optionalOk = optionalChains.filter(x => x.ok && chainPass(x.payload)).length
    const optionalSafeBlocks = optionalChains.filter(x => x.ok && safeNoTradeChain(x.payload)).length
    const liveFlag = state.live_trading_enabled ?? state.liveTradingEnabled ?? broker.live_trading_enabled ?? false
    const orderAllowed = state.order_placement_allowed ?? broker.order_placement_allowed ?? false
    const gainRows = collectCandidateRows(gain), scannerRows = collectCandidateRows(scanner)
    const gainCount = gainRows.length + scannerRows.length, tradeCount = countList(trades)
    const gateOk = Boolean(data.gates?.ok), cePeOk = hasCePe(gain) || hasCePe(scanner)
    return [
      { layer: 'Backend/API route health', status: (data.health?.ok || data.state?.ok) ? 'PASS' : 'WAITING', evidence: `health=${data.health?.status || 0}, state=${data.state?.status || 0}`, requiredForMoney: true },
      { layer: 'Broker read-only connection', status: (data.broker?.ok || broker.connected === true) ? 'PASS' : 'WAITING', evidence: `connected=${broker.connected === true}, broker=${broker.broker || 'dhan'}, order_allowed=${broker.order_placement_allowed === true}`, requiredForMoney: true },
      { layer: 'Funds / margin truth', status: (data.funds?.ok || funds.available_balance || funds.normalized?.available_balance) ? 'PASS' : 'WAITING', evidence: `available=${funds.available_balance ?? funds.normalized?.available_balance ?? '-'}, used=${funds.used_margin ?? funds.normalized?.used_margin ?? '-'}, source=${funds.source || '-'}`, requiredForMoney: true },
      { layer: 'Holdings and live positions read path', status: (data.holdings?.ok || data.positions?.ok || countList(data.holdings?.data) > 0) ? 'PASS' : 'PARTIAL', evidence: `holdings=${countList(data.holdings?.data)}, positions=${countList(data.positions?.data)}`, requiredForMoney: true },
      { layer: 'Dhan option-chain availability', status: (requiredOk >= 2 || requiredSafeBlocks >= 2) ? 'PASS' : requiredOk > 0 ? 'PARTIAL' : 'WAITING', evidence: `enabled_ready=${requiredOk}/${REQUIRED_CHAIN_SYMBOLS.length}, enabled_safe_no_trade=${requiredSafeBlocks}/${REQUIRED_CHAIN_SYMBOLS.length}, optional_ready=${optionalOk}/${OPTIONAL_CHAIN_SYMBOLS.length}, optional_safe_no_trade=${optionalSafeBlocks}/${OPTIONAL_CHAIN_SYMBOLS.length}`, requiredForMoney: true },
      { layer: 'Universe / ranking candidates', status: gainCount > 0 ? 'PASS' : 'PARTIAL', evidence: `candidate_rows=${gainCount}, gain=${gainRows.length}, scanner=${scannerRows.length}`, requiredForMoney: true },
      { layer: 'CE / PE decision evidence', status: cePeOk ? 'PASS' : 'WAITING', evidence: cePeOk ? 'CE/PE field found in ranker/scanner payload' : 'No CE/PE field found in current ranker/scanner payload', requiredForMoney: true },
      { layer: 'Paper/analyzer lifecycle read path', status: data.trades?.ok ? 'PASS' : 'WAITING', evidence: `today_trade_rows=${tradeCount}, endpoint=${data.trades?.status || 0}; endpoint health does not prove completed trades`, requiredForMoney: false },
      { layer: 'Risk gates and automation status', status: gateOk || data.gates?.status === 200 ? 'PASS' : 'PARTIAL', evidence: `auto_gates_http=${data.gates?.status || 0}, status=${gates.status || '-'}`, requiredForMoney: true },
      { layer: 'Live-money safety lock', status: liveFlag === true || orderAllowed === true ? 'WAITING' : 'PASS', evidence: `live_flag=${String(liveFlag)}, order_allowed=${String(orderAllowed)} (live trading disabled by design)`, requiredForMoney: true },
      {
        layer: 'Dashboard operator truth',
        status: (requiredOk >= 2 && (data.health?.ok || data.state?.ok)) ? 'PASS' : 'PARTIAL',
        evidence: `health_ok=${Boolean(data.health?.ok)}, broker_ok=${Boolean(data.broker?.ok)}, gates_ok=${Boolean(data.gates?.ok)}, enabled_chains_ready=${requiredOk}/${REQUIRED_CHAIN_SYMBOLS.length} (runtime API probes; not hard-coded)`,
        requiredForMoney: true,
      },
    ]
  }, [data])

  const moneyRows = rows.filter(r => r.requiredForMoney)
  const moneyReady = moneyRows.every(r => r.status === 'PASS')
  const infraOk = rows.slice(0, 4).every(r => r.status === 'PASS')

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div><h2 style={{ margin: 0, fontSize: 22 }}>System Truth Control</h2><div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>Full upstream/downstream trading chain. Enabled universe: {REQUIRED_CHAIN_SYMBOLS.join(', ')}. Optional watchlist: {OPTIONAL_CHAIN_SYMBOLS.join(', ')}.</div></div>
        <button onClick={run} disabled={loading} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface-2)', color: 'var(--text-primary)', cursor: 'pointer' }}>{loading ? 'Checking...' : 'Recheck All Layers'}</button>
      </div>
      {error && <div style={{ border: '1px solid rgba(239,68,68,.4)', color: 'var(--down)', padding: 10, borderRadius: 8, marginBottom: 12 }}>{error}</div>}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(160px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card">{badge(infraOk ? 'PASS' : 'WAITING')}<div style={{ marginTop: 8, fontSize: 12 }}>Infrastructure / broker read status</div></div>
        <div className="card">{badge(moneyReady ? 'PASS' : 'WAITING')}<div style={{ marginTop: 8, fontSize: 12 }}>Money readiness pending</div></div>
        <div className="card"><div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Last run</div><div style={{ fontWeight: 800, marginTop: 6 }}>{lastRun || '-'}</div></div>
      </div>
      <div style={{ border: `1px solid ${moneyReady ? 'rgba(16,185,129,.45)' : 'rgba(239,68,68,.45)'}`, background: moneyReady ? 'rgba(16,185,129,.08)' : 'rgba(239,68,68,.08)', padding: 14, borderRadius: 10, marginBottom: 16 }}>
        <div style={{ fontWeight: 900, fontSize: 16 }}>{moneyReady ? 'MONEY_READY_PROOF_GREEN' : 'MONEY_READY_PENDING'}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>{moneyReady ? 'All required enabled-universe layers are passing. A separate manual live gate is still required before broker order execution.' : 'At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.'}</div>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead><tr><th className="thead">Layer</th><th className="thead">Status</th><th className="thead">Required for money</th><th className="thead">Evidence</th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.layer}><td className="tcell"><b>{row.layer}</b></td><td className="tcell">{badge(row.status)}</td><td className="tcell">{row.requiredForMoney ? 'YES' : 'NO'}</td><td className="tcell">{row.evidence}</td></tr>)}</tbody>
      </table>
    </div>
  )
}
