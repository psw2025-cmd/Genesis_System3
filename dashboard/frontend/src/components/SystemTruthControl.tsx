import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

type Status = 'PASS' | 'BLOCKED' | 'PARTIAL'

type LayerRow = {
  layer: string
  status: Status
  evidence: string
  requiredForMoney: boolean
}

const CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']

function badge(status: Status) {
  const ok = status === 'PASS'
  const partial = status === 'PARTIAL'
  return (
    <span style={{
      display: 'inline-flex',
      padding: '4px 9px',
      borderRadius: 999,
      fontSize: 11,
      fontWeight: 900,
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
  if (Array.isArray(x)) {
    if (x.some(looksLikeCandidate)) return x.filter(looksLikeCandidate)
    return x.flatMap(v => collectCandidateRows(v, depth + 1))
  }
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
  for (const key of ['positions', 'holdings', 'rows', 'data']) {
    if (Array.isArray(x[key])) return x[key].length
  }
  return collectCandidateRows(x).length
}

function hasCePe(x: any): boolean {
  const stack: any[] = [x]
  let seen = 0
  while (stack.length && seen < 1500) {
    seen += 1
    const item = stack.pop()
    if (Array.isArray(item)) {
      for (const child of item.slice(0, 100)) stack.push(child)
    } else if (item && typeof item === 'object') {
      const side = String(item.option_side || item.option_type || item.signal_type || item.side || item.direction || item.action || item.instrument_type || '').toUpperCase()
      if (side.includes('CE') || side.includes('PE') || side.includes('CALL') || side.includes('PUT')) return true
      for (const key of ['rankings', 'predictions', 'candidates', 'signals', 'latest', 'data', 'scanner', 'market_wide', 'by_segment', 'segments', 'top_ce', 'top_pe']) {
        if (item[key]) stack.push(item[key])
      }
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
  return source === 'dhan' && !x.blocked && x.stale !== true && spot > 0 && contracts > 0 && ['OK', 'MARKET_OPEN', 'MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT'].includes(status)
}

function safeNoTradeChain(x: any): boolean {
  if (!x || typeof x !== 'object') return false
  return String(x.data_source || x.source || '').toLowerCase() === 'dhan' && String(x.status || '').toUpperCase() === 'NO_DHAN_DATA'
}

export function SystemTruthControl() {
  const [data, setData] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [lastRun, setLastRun] = useState('')
  const [error, setError] = useState('')

  async function run() {
    setLoading(true)
    setError('')
    try {
      const entries = await Promise.all([
        ['health', axios.get(`${API_BASE}/api/health`)],
        ['state', axios.get(`${API_BASE}/api/state`)],
        ['broker', axios.get(`${API_BASE}/api/broker/dhan/status`)],
        ['funds', axios.get(`${API_BASE}/api/broker/funds`)],
        ['holdings', axios.get(`${API_BASE}/api/broker/holdings`)],
        ['positions', axios.get(`${API_BASE}/api/broker/positions/live`)],
        ['gain', axios.get(`${API_BASE}/api/gain_rank`)],
        ['scanner', axios.get(`${API_BASE}/api/scanner/top_contract_gainers?top_n=5`)],
        ['pnl', axios.get(`${API_BASE}/api/pnl`)],
        ['trades', axios.get(`${API_BASE}/api/trades/today`)],
        ['gates', axios.get(`${API_BASE}/api/auto_gates`)],
        ...CHAIN_SYMBOLS.map(sym => [`chain_${sym}`, axios.get(`${API_BASE}/api/chain/${sym}`)] as any),
      ].map(async ([key, promise]: any) => {
        try {
          const res = await promise
          return [key, { ok: true, status: res.status, data: res.data }]
        } catch (err: any) {
          return [key, { ok: false, status: err?.response?.status || 0, error: err?.message || String(err) }]
        }
      }))
      setData(Object.fromEntries(entries))
      setLastRun(new Date().toLocaleString())
    } catch (err: any) {
      setError(err?.message || String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { run() }, [])

  const rows: LayerRow[] = useMemo(() => {
    const broker = data.broker?.data || {}
    const funds = data.funds?.data || {}
    const state = data.state?.data || {}
    const gain = data.gain?.data || {}
    const scanner = data.scanner?.data || {}
    const trades = data.trades?.data || {}
    const gates = data.gates?.data || {}
    const chains = CHAIN_SYMBOLS.map(sym => ({ sym, payload: data[`chain_${sym}`]?.data, ok: data[`chain_${sym}`]?.ok }))
    const chainOkCount = chains.filter(x => x.ok && chainPass(x.payload)).length
    const chainSafeBlocks = chains.filter(x => x.ok && safeNoTradeChain(x.payload)).length
    const liveFlag = state.live_trading_enabled ?? state.liveTradingEnabled ?? broker.live_trading_enabled ?? false
    const orderAllowed = state.order_placement_allowed ?? broker.order_placement_allowed ?? false
    const gainRows = collectCandidateRows(gain)
    const scannerRows = collectCandidateRows(scanner)
    const gainCount = gainRows.length + scannerRows.length
    const tradeCount = countList(trades)
    const gateOk = Boolean(data.gates?.ok)
    const cePeOk = hasCePe(gain) || hasCePe(scanner)

    return [
      {
        layer: 'Backend/API route health',
        status: data.health?.ok && data.state?.ok ? 'PASS' : 'BLOCKED',
        evidence: `health=${data.health?.status || 0}, state=${data.state?.status || 0}`,
        requiredForMoney: true,
      },
      {
        layer: 'Broker read-only connection',
        status: broker.connected === true ? 'PASS' : 'BLOCKED',
        evidence: `connected=${broker.connected === true}, broker=${broker.broker || 'dhan'}, order_allowed=${broker.order_placement_allowed === true}`,
        requiredForMoney: true,
      },
      {
        layer: 'Funds / margin truth',
        status: data.funds?.ok && !funds.error ? 'PASS' : 'BLOCKED',
        evidence: `available=${funds.available_balance ?? funds.normalized?.available_balance ?? '-'}, used=${funds.used_margin ?? funds.normalized?.used_margin ?? '-'}, source=${funds.source || '-'}`,
        requiredForMoney: true,
      },
      {
        layer: 'Holdings and live positions read path',
        status: data.holdings?.ok && data.positions?.ok ? 'PASS' : 'BLOCKED',
        evidence: `holdings=${countList(data.holdings?.data)}, positions=${countList(data.positions?.data)}`,
        requiredForMoney: true,
      },
      {
        layer: 'Dhan option-chain availability',
        status: chainOkCount === CHAIN_SYMBOLS.length ? 'PASS' : chainSafeBlocks > 0 ? 'PARTIAL' : 'BLOCKED',
        evidence: `ready=${chainOkCount}/${CHAIN_SYMBOLS.length}, safe_no_trade=${chainSafeBlocks}/${CHAIN_SYMBOLS.length}`,
        requiredForMoney: true,
      },
      {
        layer: 'Universe / ranking candidates',
        status: gainCount > 0 ? 'PASS' : 'BLOCKED',
        evidence: `candidate_rows=${gainCount}, gain=${gainRows.length}, scanner=${scannerRows.length}`,
        requiredForMoney: true,
      },
      {
        layer: 'CE / PE decision evidence',
        status: cePeOk ? 'PASS' : 'BLOCKED',
        evidence: cePeOk ? 'CE/PE field found in ranker/scanner payload' : 'No CE/PE side found in model/ranker/scanner payload',
        requiredForMoney: true,
      },
      {
        layer: 'Paper/analyzer lifecycle',
        status: data.trades?.ok ? (tradeCount > 0 ? 'PASS' : 'PARTIAL') : 'BLOCKED',
        evidence: `today_trade_rows=${tradeCount}, endpoint=${data.trades?.status || 0}`,
        requiredForMoney: false,
      },
      {
        layer: 'Risk gates and automation status',
        status: gateOk ? 'PASS' : 'BLOCKED',
        evidence: `auto_gates_http=${data.gates?.status || 0}, status=${gates.status || '-'}`,
        requiredForMoney: true,
      },
      {
        layer: 'Live-money safety lock',
        status: liveFlag === true || orderAllowed === true ? 'BLOCKED' : 'PASS',
        evidence: `live_flag=${String(liveFlag)}, order_allowed=${String(orderAllowed)}`,
        requiredForMoney: true,
      },
      {
        layer: 'Dashboard operator truth',
        status: 'PASS',
        evidence: 'This panel is generated from live backend endpoints and blocks money-readiness when upstream/downstream proof is missing.',
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
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>System Truth Control</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
            Full upstream/downstream trading chain. This is the operator money-readiness view.
          </div>
        </div>
        <button onClick={run} disabled={loading} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface-2)', color: 'var(--text-primary)', cursor: 'pointer' }}>
          {loading ? 'Checking...' : 'Recheck All Layers'}
        </button>
      </div>

      {error && <div style={{ border: '1px solid rgba(239,68,68,.4)', color: 'var(--down)', padding: 10, borderRadius: 8, marginBottom: 12 }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(160px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card">{badge(infraOk ? 'PASS' : 'BLOCKED')}<div style={{ marginTop: 8, fontSize: 12 }}>Infrastructure / broker read path</div></div>
        <div className="card">{badge(moneyReady ? 'PASS' : 'BLOCKED')}<div style={{ marginTop: 8, fontSize: 12 }}>Money readiness</div></div>
        <div className="card"><div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Last run</div><div style={{ fontWeight: 800, marginTop: 6 }}>{lastRun || '-'}</div></div>
      </div>

      <div style={{ border: `1px solid ${moneyReady ? 'rgba(16,185,129,.45)' : 'rgba(239,68,68,.45)'}`, background: moneyReady ? 'rgba(16,185,129,.08)' : 'rgba(239,68,68,.08)', padding: 14, borderRadius: 10, marginBottom: 16 }}>
        <div style={{ fontWeight: 900, fontSize: 16 }}>{moneyReady ? 'MONEY_READY_PROOF_GREEN' : 'MONEY_READY_BLOCKED'}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
          {moneyReady ? 'All required layers are passing. A separate manual live gate is still required before broker order execution.' : 'At least one required upstream/downstream layer is missing proof. Live broker order execution must remain disabled.'}
        </div>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr>
            <th className="thead">Layer</th>
            <th className="thead">Status</th>
            <th className="thead">Required for money</th>
            <th className="thead">Evidence</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.layer}>
              <td className="tcell"><b>{row.layer}</b></td>
              <td className="tcell">{badge(row.status)}</td>
              <td className="tcell">{row.requiredForMoney ? 'YES' : 'NO'}</td>
              <td className="tcell">{row.evidence}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
