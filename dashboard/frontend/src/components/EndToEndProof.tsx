import { useMemo } from 'react'
import { useStore } from '../store'

const REQUIRED_CHAIN_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
const OPTIONAL_CHAIN_SYMBOLS = ['SENSEX', 'RELIANCE']

function badge(ok: boolean, label?: string, warn = false) {
  const tone = ok ? 'var(--up)' : warn ? 'var(--amber)' : 'var(--down)'
  const bg = ok ? 'rgba(16,185,129,.14)' : warn ? 'rgba(245,158,11,.14)' : 'rgba(239,68,68,.14)'
  const border = ok ? 'rgba(16,185,129,.35)' : warn ? 'rgba(245,158,11,.35)' : 'rgba(239,68,68,.35)'
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6, padding: '3px 8px', borderRadius: 999,
      fontSize: 11, fontWeight: 800, background: bg, color: tone, border: `1px solid ${border}`,
    }}>{ok ? 'PASS' : warn ? 'PARTIAL' : 'WAITING'}{label ? ` · ${label}` : ''}</span>
  )
}

function rowsOf(value: any): any[] {
  if (Array.isArray(value)) return value
  if (!value || typeof value !== 'object') return []
  for (const key of ['rows', 'positions', 'holdings', 'data', 'open_positions']) if (Array.isArray(value[key])) return value[key]
  return []
}

function candidatesOf(value: any, depth = 0): any[] {
  if (depth > 7 || value == null) return []
  if (Array.isArray(value)) return value.flatMap(item => candidatesOf(item, depth + 1))
  if (typeof value !== 'object') return []
  const side = String(value.option_side || value.option_type || value.signal_type || value.side || '').toUpperCase()
  const named = Boolean(value.underlying || value.symbol || value.ticker || value.trading_symbol)
  const scored = value.score != null || value.confidence != null || value.gain_pct != null || value.change_percent != null
  const self = named && (scored || /CE|PE|CALL|PUT/.test(side)) ? [value] : []
  const nested: any[] = []
  for (const key of ['rankings', 'predictions', 'candidates', 'signals', 'latest', 'data', 'scanner', 'market_wide', 'by_segment', 'segments', 'top_ce', 'top_pe']) {
    if (value[key] != null) nested.push(...candidatesOf(value[key], depth + 1))
  }
  return [...self, ...nested]
}

function chainTruth(value: any) {
  if (!value || typeof value !== 'object') return { ready: false, badSource: false, reason: 'NOT_LOADED' }
  const source = String(value.data_source || value.source || '').toLowerCase()
  const priority = String(value.source_priority || '').toLowerCase()
  const status = String(value.status || '').toUpperCase()
  const combined = `${source} ${priority} ${status}`
  const badSource = /(csv|fallback|synthetic|bhavcopy|yahoo|fake|mock)/i.test(combined)
  const contracts = Number(value.total_contracts || (Array.isArray(value.contracts) ? value.contracts.length : 0))
  const spot = Number(value.spot || 0)
  const dhanish = source === 'dhan' || source.startsWith('dhan_') || priority.startsWith('dhan') || priority.includes('worker_push')
  const marketClosedSnapshot = ['MARKET_CLOSED_DHAN_SNAPSHOT', 'EOD_SNAPSHOT', 'MARKET_CLOSED'].includes(status)
    || (value.snapshot === true && /DHAN|SNAPSHOT/.test(combined.toUpperCase()))
  const ready = !badSource && dhanish && !value.pendingProof && contracts > 0 && spot > 0
    && (marketClosedSnapshot || (['OK', 'MARKET_OPEN'].includes(status) && value.stale !== true))
  return {
    ready,
    badSource,
    reason: ready ? (marketClosedSnapshot ? 'VERIFIED_DHAN_SESSION_SNAPSHOT' : 'REAL_DHAN_CONFIRMED') : String(value.pending_reason || value.message || status || 'NOT_READY'),
  }
}

export function EndToEndProof() {
  const {
    health, state, brokerConnected, brokerStatus, brokerFunds, brokerHoldings, brokerPositions,
    chain, gainRank, autoGates, paper, pnl, lastSync,
  } = useStore()

  const proof = useMemo(() => {
    const brokerOk = brokerStatus?.connected === true || brokerConnected === true || health?.broker?.connected === true
    const apiOk = Boolean(health || state)
    const token = brokerStatus?.token_proof || {}
    const tokenOk = brokerOk
      && String(token?.source || '').toUpperCase().includes('GCP_SECRET_MANAGER')
      && token?.token_value_exposed !== true
      && Number(token?.hours_remaining ?? 1) > 0
    const fundsOk = Boolean(brokerFunds) && brokerFunds?.success !== false && brokerFunds?.pendingProof !== true
    const holdingsOk = Boolean(brokerHoldings) && brokerHoldings?.success !== false && brokerHoldings?.pendingProof !== true
    const positionsOk = Boolean(brokerPositions) && brokerPositions?.success !== false && brokerPositions?.pendingProof !== true
    const requiredChains = REQUIRED_CHAIN_SYMBOLS.map(symbol => ({ symbol, data: chain?.[symbol], truth: chainTruth(chain?.[symbol]) }))
    const optionalChains = OPTIONAL_CHAIN_SYMBOLS.map(symbol => ({ symbol, data: chain?.[symbol], truth: chainTruth(chain?.[symbol]) }))
    const requiredReady = requiredChains.filter(item => item.truth.ready).length
    const badRequiredSource = requiredChains.some(item => item.truth.badSource)
    const candidates = candidatesOf(gainRank)
    const cePe = candidates.some(item => /CE|PE|CALL|PUT/.test(String(item.option_side || item.option_type || item.signal_type || item.side || '').toUpperCase()))
    const paperOk = paper != null || pnl != null
    const gatesOk = autoGates != null
    const liveOn = Boolean(state?.live_trading_enabled ?? health?.live_allowed ?? brokerStatus?.live_trading_enabled)
    const orderAllowed = Boolean(state?.order_placement_allowed ?? brokerStatus?.order_placement_allowed)
    const safetyOk = !liveOn && !orderAllowed

    const readiness = [
      { item: 'Current backend/API shared state', ok: apiOk, evidence: apiOk ? `health=${health ? 'present' : 'missing'}, state=${state ? 'present' : 'missing'}` : 'Shared API truth not loaded' },
      { item: 'Dhan broker connection', ok: brokerOk, evidence: `connected=${brokerOk}` },
      { item: 'Dynamic Dhan token/session', ok: tokenOk, evidence: `source=${token?.source || '-'}, version=${token?.secret_version || '-'}, hours=${token?.hours_remaining ?? '-'}` },
      { item: 'Real broker funds/margin', ok: fundsOk, evidence: `available=${brokerFunds?.available_balance ?? brokerFunds?.normalized?.available_balance ?? '-'}` },
      { item: 'Real broker holdings response', ok: holdingsOk, evidence: `rows=${rowsOf(brokerHoldings).length}; empty success is valid` },
      { item: 'Real broker positions response', ok: positionsOk, evidence: `rows=${rowsOf(brokerPositions).length}; empty success is valid` },
      { item: 'Required Dhan option chains', ok: requiredReady === REQUIRED_CHAIN_SYMBOLS.length, evidence: `${requiredReady}/${REQUIRED_CHAIN_SYMBOLS.length} ready` },
      { item: 'No non-Dhan source in required chains', ok: !badRequiredSource, evidence: badRequiredSource ? 'non-Dhan marker detected' : 'clean' },
      { item: 'Current CE / PE candidate evidence', ok: cePe, evidence: cePe ? `${candidates.length} candidate rows include CE/PE truth` : `candidate_rows=${candidates.length}; CE/PE not yet proven` },
      { item: 'Paper/analyzer read path', ok: paperOk, evidence: paperOk ? String(paper?.status || 'paper/pnl present') : 'not loaded' },
      { item: 'Gate/risk state visible', ok: gatesOk, evidence: gatesOk ? String(autoGates?.status || 'present') : 'not loaded' },
      { item: 'LIVE/order safety lock', ok: safetyOk, evidence: `live=${liveOn}, order_allowed=${orderAllowed}` },
    ]
    const overall = readiness.every(item => item.ok)
    return { brokerOk, tokenOk, requiredChains, optionalChains, requiredReady, candidates, cePe, readiness, overall, safetyOk }
  }, [health, state, brokerConnected, brokerStatus, brokerFunds, brokerHoldings, brokerPositions, chain, gainRank, autoGates, paper, pnl])

  return (
    <div data-testid="end-to-end-proof" style={{ height: '100%', overflow: 'auto', padding: 18, background: 'var(--surface)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>End-to-End Current Truth Proof</h2>
          <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
            Uses the dashboard's bounded shared read-only truth. No duplicate 3.5-second probe storm; valid market-closed Dhan snapshots are accepted.
          </div>
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: 11, textAlign: 'right' }}>Shared-store sync<br /><b style={{ color: 'var(--text-primary)' }}>{lastSync || 'waiting'}</b></div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(150px, 1fr))', gap: 12, marginBottom: 16 }}>
        <div className="card" style={{ padding: 12 }}>{badge(proof.overall, 'FULL E2E')}<div style={{ marginTop: 8, fontSize: 12 }}>Current shared proof</div></div>
        <div className="card" style={{ padding: 12 }}>{badge(proof.brokerOk, 'BROKER')}<div style={{ marginTop: 8, fontSize: 12 }}>Dhan connectivity</div></div>
        <div className="card" style={{ padding: 12 }}>{badge(proof.requiredReady === REQUIRED_CHAIN_SYMBOLS.length, '4 CHAINS')}<div style={{ marginTop: 8, fontSize: 12 }}>Required option chains</div></div>
        <div className="card" style={{ padding: 12 }}>{badge(proof.cePe, 'CE/PE', !proof.cePe)}<div style={{ marginTop: 8, fontSize: 12 }}>Decision evidence</div></div>
        <div className="card" style={{ padding: 12 }}>{badge(proof.safetyOk, 'SAFETY')}<div style={{ marginTop: 8, fontSize: 12 }}>LIVE/order lock</div></div>
      </div>

      <h3 style={{ fontSize: 16 }}>Current Readiness Truth Checklist</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, marginBottom: 18 }}>
        <thead><tr><th className="thead">Required evidence</th><th className="thead">Status</th><th className="thead">Current shared evidence</th></tr></thead>
        <tbody>
          {proof.readiness.map(row => <tr key={row.item}>
            <td className="tcell"><b>{row.item}</b></td>
            <td className="tcell">{badge(row.ok)}</td>
            <td className="tcell">{row.evidence}</td>
          </tr>)}
        </tbody>
      </table>

      <h3 style={{ fontSize: 16 }}>Required Dhan Option Chain Truth</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, marginBottom: 18 }}>
        <thead><tr><th className="thead">Symbol</th><th className="thead">Status</th><th className="thead">Source</th><th className="thead">API status</th><th className="thead">Spot</th><th className="thead">Contracts</th><th className="thead">Reason</th></tr></thead>
        <tbody>
          {proof.requiredChains.map(item => <tr key={item.symbol}>
            <td className="tcell"><b>{item.symbol}</b></td>
            <td className="tcell">{badge(item.truth.ready)}</td>
            <td className="tcell">{String(item.data?.data_source || item.data?.source || '-')}</td>
            <td className="tcell">{String(item.data?.status || '-')}</td>
            <td className="tcell">{String(item.data?.spot ?? '-')}</td>
            <td className="tcell">{String(item.data?.total_contracts ?? (Array.isArray(item.data?.contracts) ? item.data.contracts.length : '-'))}</td>
            <td className="tcell">{item.truth.reason}</td>
          </tr>)}
        </tbody>
      </table>

      <h3 style={{ fontSize: 16 }}>Optional Watchlist Truth</h3>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {proof.optionalChains.map(item => (
          <span key={item.symbol} className="pill" style={{ color: item.truth.ready ? 'var(--up)' : 'var(--text-muted)' }}>
            {item.symbol}: {item.truth.ready ? 'READY' : item.truth.reason}
          </span>
        ))}
      </div>

      <div style={{ marginTop: 16, color: 'var(--text-muted)', fontSize: 11, lineHeight: 1.5 }}>
        This panel proves current read-only dashboard state only. It does not enable real-money trading. Market-closed Dhan snapshots remain valid source evidence when they contain real contracts and spot values.
      </div>
    </div>
  )
}
