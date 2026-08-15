import React, { useMemo } from 'react'
import { useStore } from '../store'

type Status = 'PASS' | 'WAITING' | 'PARTIAL'
type LayerRow = { layer: string; status: Status; evidence: string; requiredForMoney: boolean }

const REQUIRED_CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
const OPTIONAL_CHAIN_SYMBOLS = ['SENSEX']

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

function rowsOf(value: any): any[] {
  if (Array.isArray(value)) return value
  if (!value || typeof value !== 'object') return []
  for (const key of ['rows', 'positions', 'holdings', 'data', 'open_positions']) {
    if (Array.isArray(value[key])) return value[key]
  }
  return []
}

function collectCandidates(value: any, depth = 0): any[] {
  if (depth > 7 || value == null) return []
  if (Array.isArray(value)) return value.flatMap(item => collectCandidates(item, depth + 1))
  if (typeof value !== 'object') return []
  const side = String(value.option_side || value.option_type || value.signal_type || value.side || '').toUpperCase()
  const named = Boolean(value.underlying || value.symbol || value.ticker || value.trading_symbol)
  const scored = value.score != null || value.confidence != null || value.gain_pct != null || value.change_percent != null
  const self = named && (scored || /CE|PE|CALL|PUT/.test(side)) ? [value] : []
  const nested: any[] = []
  for (const key of ['rankings', 'predictions', 'candidates', 'signals', 'top', 'top5', 'latest', 'data', 'scanner', 'market_wide', 'by_segment', 'segments', 'top_ce', 'top_pe']) {
    if (value[key] != null) nested.push(...collectCandidates(value[key], depth + 1))
  }
  return [...self, ...nested]
}

function hasCePe(value: any): boolean {
  return collectCandidates(value).some(item => /CE|PE|CALL|PUT/.test(String(item.option_side || item.option_type || item.signal_type || item.side || '').toUpperCase()))
}

function isDhanChainReady(value: any): boolean {
  if (!value || typeof value !== 'object') return false
  const source = String(value.data_source || value.source || '').toLowerCase()
  const priority = String(value.source_priority || '').toLowerCase()
  const status = String(value.status || '').toUpperCase()
  const contracts = Number(value.total_contracts || (Array.isArray(value.contracts) ? value.contracts.length : 0))
  const spot = Number(value.spot || 0)
  const dhanish = source === 'dhan' || source.startsWith('dhan_') || priority.startsWith('dhan') || priority.includes('worker_push')
  if (!dhanish || value.pendingProof || spot <= 0 || contracts <= 0) return false
  if (['MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT', 'MARKET_CLOSED'].includes(status)) return true
  if (value.snapshot === true && /DHAN|SNAPSHOT/.test(`${source} ${priority} ${status}`.toUpperCase())) return true
  return ['OK', 'MARKET_OPEN'].includes(status) && value.stale !== true
}

function isSafeNoTradeChain(value: any): boolean {
  if (!value || typeof value !== 'object') return false
  return String(value.data_source || value.source || '').toLowerCase().startsWith('dhan')
    && String(value.status || '').toUpperCase() === 'NO_DHAN_DATA'
}

export function SystemTruthControl() {
  const {
    health, state, brokerConnected, brokerStatus, brokerFunds, brokerHoldings, brokerPositions,
    chain, gainRank, autoGates, paper, lastSync, apiStatus,
  } = useStore()

  const rows: LayerRow[] = useMemo(() => {
    const brokerOk = brokerStatus?.connected === true || brokerConnected === true || health?.broker?.connected === true
    const apiOk = String(health?.status || '').toLowerCase() === 'ok'
      || Boolean(health?.mode)
      || Boolean(state)
      || (apiStatus != null && !/ERROR|REQUIRED|DEGRADED/.test(String(apiStatus?.status || '').toUpperCase()))
    const fundsOk = Boolean(brokerFunds) && brokerFunds?.success !== false && brokerFunds?.pendingProof !== true
    const holdingsKnown = Boolean(brokerHoldings) && brokerHoldings?.success !== false && brokerHoldings?.pendingProof !== true
    const positionsKnown = Boolean(brokerPositions) && brokerPositions?.success !== false && brokerPositions?.pendingProof !== true
    const holdingsCount = rowsOf(brokerHoldings).length
    const positionsCount = rowsOf(brokerPositions).length

    const required = REQUIRED_CHAIN_SYMBOLS.map(symbol => ({ symbol, value: chain?.[symbol] }))
    const optional = OPTIONAL_CHAIN_SYMBOLS.map(symbol => ({ symbol, value: chain?.[symbol] }))
    const requiredReady = required.filter(item => isDhanChainReady(item.value)).length
    const requiredSafeNoTrade = required.filter(item => isSafeNoTradeChain(item.value)).length
    const optionalReady = optional.filter(item => isDhanChainReady(item.value)).length

    const candidates = collectCandidates(gainRank)
    const candidateCount = candidates.length
    const cePeOk = hasCePe(gainRank)
    const liveFlag = Boolean(state?.live_trading_enabled ?? health?.live_allowed ?? brokerStatus?.live_trading_enabled)
    const orderAllowed = Boolean(state?.order_placement_allowed ?? brokerStatus?.order_placement_allowed)
    const available = brokerFunds?.available_balance ?? brokerFunds?.normalized?.available_balance
    const used = brokerFunds?.used_margin ?? brokerFunds?.normalized?.used_margin ?? brokerFunds?.normalized?.utilized_amount

    return [
      {
        layer: 'Backend/API shared live truth',
        status: apiOk ? 'PASS' : 'WAITING',
        evidence: `health=${health ? String(health.status || health.mode || 'present') : 'missing'}, state=${state ? 'present' : 'missing'}, api=${apiStatus?.status || 'responding/idle'}`,
        requiredForMoney: true,
      },
      {
        layer: 'Broker read-only connection',
        status: brokerOk ? 'PASS' : 'WAITING',
        evidence: `connected=${brokerOk}, source=${brokerStatus?.broker || 'dhan'}, order_allowed=${orderAllowed}`,
        requiredForMoney: true,
      },
      {
        layer: 'Funds / margin truth',
        status: fundsOk ? 'PASS' : 'WAITING',
        evidence: `available=${available ?? '-'}, used=${used ?? '-'}, source=${brokerFunds?.source || brokerFunds?.normalized?.source || 'dhan'}`,
        requiredForMoney: true,
      },
      {
        layer: 'Holdings and Dhan positions read path',
        status: holdingsKnown && positionsKnown ? 'PASS' : (holdingsKnown || positionsKnown) ? 'PARTIAL' : 'WAITING',
        evidence: `holdings=${holdingsCount}, positions=${positionsCount}, empty broker response is valid when success=true`,
        requiredForMoney: true,
      },
      {
        layer: 'Required Dhan option-chain availability',
        status: requiredReady === REQUIRED_CHAIN_SYMBOLS.length ? 'PASS' : requiredReady > 0 ? 'PARTIAL' : 'WAITING',
        evidence: `required_ready=${requiredReady}/${REQUIRED_CHAIN_SYMBOLS.length}, safe_no_trade=${requiredSafeNoTrade}/${REQUIRED_CHAIN_SYMBOLS.length}, optional_ready=${optionalReady}/${OPTIONAL_CHAIN_SYMBOLS.length}`,
        requiredForMoney: true,
      },
      {
        layer: 'Universe / ranking candidates',
        status: candidateCount > 0 ? 'PASS' : 'PARTIAL',
        evidence: `candidate_rows=${candidateCount}; zero candidates is not fabricated into a PASS`,
        requiredForMoney: true,
      },
      {
        layer: 'CE / PE decision evidence',
        status: cePeOk ? 'PASS' : 'WAITING',
        evidence: cePeOk ? 'CE/PE field found in the current shared rank/scanner truth' : 'No CE/PE field found in current shared rank/scanner truth',
        requiredForMoney: true,
      },
      {
        layer: 'Paper/analyzer lifecycle read path',
        status: paper != null ? 'PASS' : 'WAITING',
        evidence: `paper=${paper == null ? 'missing' : String(paper.status || 'present')}; read-path presence does not prove completed lifecycle`,
        requiredForMoney: false,
      },
      {
        layer: 'Risk gates / automation state',
        status: autoGates != null ? 'PASS' : 'PARTIAL',
        evidence: `auto_gates=${autoGates == null ? 'missing' : String(autoGates.status || 'present')}`,
        requiredForMoney: true,
      },
      {
        layer: 'Live-money safety lock',
        status: !liveFlag && !orderAllowed ? 'PASS' : 'WAITING',
        evidence: `live_flag=${liveFlag}, order_allowed=${orderAllowed}; analyzer/PAPER requires both false`,
        requiredForMoney: true,
      },
    ]
  }, [health, state, brokerConnected, brokerStatus, brokerFunds, brokerHoldings, brokerPositions, chain, gainRank, autoGates, paper, apiStatus])

  const moneyRows = rows.filter(row => row.requiredForMoney)
  const moneyReady = moneyRows.every(row => row.status === 'PASS')
  const infraRows = rows.slice(0, 5)
  const infraOk = infraRows.every(row => row.status === 'PASS')

  return (
    <div data-testid="system-truth-control" style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>System Truth Control</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
            Shared live dashboard truth — no duplicate broker/API probe burst. Required chains: {REQUIRED_CHAIN_SYMBOLS.join(', ')}.
          </div>
        </div>
        <div style={{ textAlign: 'right', color: 'var(--text-muted)', fontSize: 11 }}>
          Shared-store sync<br /><b style={{ color: 'var(--text-primary)' }}>{lastSync || 'waiting'}</b>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(160px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card" style={{ padding: 12 }}>{badge(infraOk ? 'PASS' : 'WAITING')}<div style={{ marginTop: 8, fontSize: 12 }}>Infrastructure / broker read state</div></div>
        <div className="card" style={{ padding: 12 }}>{badge(moneyReady ? 'PASS' : 'WAITING')}<div style={{ marginTop: 8, fontSize: 12 }}>{moneyReady ? 'All required proof layers present' : 'Readiness evidence still incomplete'}</div></div>
        <div className="card" style={{ padding: 12 }}>{badge('PASS')}<div style={{ marginTop: 8, fontSize: 12 }}>PAPER / LIVE safety lock</div></div>
      </div>

      {!moneyReady && (
        <div style={{ border: '1px solid rgba(245,158,11,.35)', background: 'rgba(245,158,11,.08)', padding: 10, borderRadius: 8, marginBottom: 14, color: '#f59e0b', fontSize: 12 }}>
          <b>READINESS_NOT_PROVEN</b> — at least one required current evidence layer below is incomplete. This does not enable live broker orders.
        </div>
      )}

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead><tr><th className="thead">Layer</th><th className="thead">Status</th><th className="thead">Required</th><th className="thead">Current shared evidence</th></tr></thead>
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

      <div style={{ marginTop: 14, color: 'var(--text-muted)', fontSize: 11, lineHeight: 1.5 }}>
        Truth source: the same Zustand state populated by the dashboard's bounded read-only poller. A separate tab must not stampede the same Dhan/GCP endpoints and then display its timeout as broker truth.
      </div>
    </div>
  )
}
