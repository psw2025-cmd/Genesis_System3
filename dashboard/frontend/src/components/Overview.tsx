import { Activity, Bot, Brain, Shield, TrendingUp, Wallet } from 'lucide-react'
import { useStore } from '../store'
import { asPct, cn, fmt, fmtCr, signClass } from '../lib/utils'
import { statusToneCss } from '../lib/statusTone'
import { AuthUnlock } from './AuthUnlock'
import { ContinuousClosureBoard } from './ContinuousClosureBoard'
import { HolographicIndexCards } from './HolographicIndexCards'
import { ModelVsMarketComparator } from './ModelVsMarketComparator'
import { NiftyIntradayChart, VolatilitySmileChart, PnlEquityCurveChart } from './LiveInteractiveCharts'

function Metric({ label, value, sub, tone, icon }: {
  label: string; value: string; sub?: string; tone?: 'up' | 'down' | 'warn' | 'accent'; icon?: React.ReactNode
}) {
  const color = tone === 'up' ? 'var(--up)' : tone === 'down' ? 'var(--down)' : tone === 'warn' ? 'var(--amber)' : tone === 'accent' ? 'var(--accent)' : 'var(--text-pri)'
  return (
    <div className="metric-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'center' }}>
        <div className="metric-label">{label}</div>
        <div style={{ color: 'var(--text-mut)' }}>{icon}</div>
      </div>
      <div className="metric-value" style={{ color }}>{value}</div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  )
}

function ChartPlaceholder({ title, value }: { title: string; value?: string; tone?: 'accent' | 'up' | 'down' }) {
  const hasSnapshot = Boolean(value && value !== '--')
  return (
    <div className="chart-shell" style={{ minHeight: 145, padding: 12 }}>
      <div className="panel-title">{title}</div>
      {value && <div className="num" style={{ marginTop: 6, color: 'var(--text-pri)', fontSize: '1rem', fontWeight: 750 }}>{value}</div>}
      <div style={{ marginTop: 28, color: 'var(--text-mut)', fontSize: '.64rem', borderTop: '1px dashed var(--border)', paddingTop: 12 }}>
        {hasSnapshot ? 'CURRENT SNAPSHOT AVAILABLE · INTRADAY HISTORY NOT WIRED' : 'SNAPSHOT UNAVAILABLE · INTRADAY HISTORY NOT WIRED'}
      </div>
    </div>
  )
}

function getStatusTone(value: string) {
  return statusToneCss(value)
}

export function Overview() {
  const {
    health, state, paper, autoGates, apiStatus, pnl, gainRank, alerts,
    brokerStatus, brokerFunds, brokerHoldings, brokerPositions, chain, marketOpen,
  } = useStore()

  const spot = (symbol: string) => Number(chain?.[symbol]?.spot || 0)
  const change = (symbol: string) => {
    const row = chain?.[symbol]
    const raw = row?.change_pct ?? row?.pct_change ?? row?.spot_change_pct
    return raw == null ? null : Number(raw)
  }
  const rawTotalPnl = paper?.pnl?.summary?.total_pnl ?? pnl?.summary?.total_pnl ?? paper?.summary?.total_pnl
  const totalPnl = rawTotalPnl == null ? null : Number(rawTotalPnl)
  const winRate = asPct(paper?.summary?.win_rate ?? paper?.pnl?.summary?.win_rate)
  const rawConf = state?.signals?.confidence ?? state?.prediction?.confidence ?? state?.model?.confidence
  const hasModelEvidence = Boolean(
    state?.signals?.directional_bias
    || state?.signals?.bias
    || state?.signals?.last_signal
    || state?.prediction?.bias
    || state?.decision?.bias
  )
  // Do not present NO_TRADE + confidence 0 as a calibrated model score.
  const modelConfidence = hasModelEvidence ? asPct(rawConf) : null
  const drawdown = asPct(paper?.summary?.max_drawdown ?? paper?.pnl?.summary?.max_drawdown)
  const brokerConnected = Boolean(brokerStatus?.connected ?? health?.broker?.connected)
  const brokerResponded = Boolean(brokerStatus || brokerFunds || brokerHoldings || brokerPositions)
  const latency = Number(brokerStatus?.latency_ms ?? brokerStatus?.latency ?? health?.broker?.latency_ms ?? 0)
  const liveAllowed = Boolean(state?.live_trading_enabled ?? state?.live_allowed ?? health?.live_allowed)
  const mode = String(health?.mode ?? state?.mode ?? 'ANALYZER').toUpperCase()

  const signalStatus = String(state?.signals?.status || '').toUpperCase()
  const decision = String(
    state?.signals?.directional_bias
    ?? state?.signals?.bias
    ?? state?.prediction?.bias
    ?? state?.decision?.bias
    ?? (signalStatus === 'NO_TRADE'
      ? `NO_TRADE · ${state?.signals?.reason || 'no model evidence'}`
      : 'WAITING FOR MODEL EVIDENCE')
  ).toUpperCase()
  const regime = String(state?.signals?.market_regime ?? state?.market?.regime ?? 'Awaiting regime evidence')
  const decisionTone = decision.includes('BULL') || decision.includes('UP') ? 'var(--up)' : decision.includes('BEAR') || decision.includes('DOWN') ? 'var(--down)' : 'var(--amber)'
  const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? []
  const topRows = Array.isArray(rankings) ? rankings.slice(0, 6) : []
  const resolveSpot = (row: any) => {
    const direct = Number(row?.spot_price)
    if (Number.isFinite(direct) && direct > 0) return direct
    const u = String(row?.underlying || row?.symbol || '').toUpperCase()
    const fromChain = Number(chain?.[u]?.spot)
    if (Number.isFinite(fromChain) && fromChain > 0) return fromChain
    return null
  }
  const proofGates = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []
  const passCount = proofGates.filter((gate: any) => gate?.pass === true || String(gate?.status).toUpperCase() === 'PASS').length
  const failingGate = proofGates.find((gate: any) => !(gate?.pass === true || String(gate?.status).toUpperCase() === 'PASS'))
  const gatesReady = proofGates.length > 0 && passCount === proofGates.length
  const alertCount = Array.isArray(alerts) ? alerts.length : 0
  const rawHealth = String(health?.status ?? health?.qc_status ?? (health ? 'RESPONDED' : 'WAITING')).toUpperCase()
  // Fail-closed: never present READY/HEALTHY while a proof gate is open.
  const systemHealth = gatesReady
    ? rawHealth
    : (failingGate?.gate_id ? `NOT_READY · ${failingGate.gate_id}` : (proofGates.length ? 'NOT_READY' : rawHealth))
  const apiAuthNeeded = apiStatus?.status === 'API_AUTH_REQUIRED'

  const indexCard = (label: string, symbol: string) => {
    const p = spot(symbol)
    const c = change(symbol)
    const sub = c != null
      ? `${c >= 0 ? '+' : ''}${c.toFixed(2)}%`
      : p > 0
        ? 'Spot snapshot available · change unavailable'
        : 'Market snapshot unavailable'
    return <Metric label={label} value={p > 0 ? fmt(p, 2) : '--'} sub={sub} tone={c == null ? undefined : c >= 0 ? 'up' : 'down'} icon={<TrendingUp size={14} />} />
  }

  return (
    <div className="workspace-shell">
      {apiAuthNeeded && <div style={{ marginBottom: 10 }}><AuthUnlock /></div>}

      <HolographicIndexCards />
      <ModelVsMarketComparator />

      <ContinuousClosureBoard />

      <div className="workspace-grid" style={{ gridTemplateColumns: 'repeat(8, minmax(0, 1fr))' }}>
        {indexCard('NIFTY', 'NIFTY')}
        {indexCard('BANKNIFTY', 'BANKNIFTY')}
        {indexCard('MIDCPNIFTY', 'MIDCPNIFTY')}
        <Metric label="Total P&L (Paper)" value={totalPnl == null ? '--' : fmtCr(totalPnl)} sub={totalPnl == null ? 'Waiting for paper evidence' : 'Paper / analyzer truth'} tone={totalPnl == null ? undefined : totalPnl >= 0 ? 'up' : 'down'} icon={<Wallet size={14} />} />
        <Metric label="Win Rate" value={winRate == null ? '--' : `${winRate.toFixed(1)}%`} sub="From paper evidence" tone={winRate == null ? undefined : winRate >= 50 ? 'up' : 'warn'} icon={<Activity size={14} />} />
        <Metric label="Model Confidence" value={modelConfidence == null ? '--' : `${modelConfidence.toFixed(0)}%`} sub={hasModelEvidence ? 'Bound to current System3 model state' : 'No model evidence · not invented'} tone={modelConfidence == null ? undefined : 'accent'} icon={<Brain size={14} />} />
        <Metric label="System Health" value={systemHealth} sub={`${passCount}/${proofGates.length || 0} proof gates${failingGate ? ` · trip: ${failingGate.gate_id}` : ''}`} tone={gatesReady && (systemHealth.includes('PASS') || systemHealth.includes('HEALTH')) ? 'up' : 'warn'} icon={<Shield size={14} />} />
        <Metric label="Latency" value={latency > 0 ? `${latency.toFixed(0)}ms` : '--'} sub={brokerConnected ? 'Broker read-only' : brokerResponded ? 'API responded' : 'Waiting'} tone={latency > 0 && latency < 500 ? 'up' : latency > 0 ? 'warn' : undefined} icon={<Activity size={14} />} />
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: 'minmax(0, 3fr) minmax(275px, 1fr)', marginTop: 10 }}>
        <div className="card" style={{ padding: 13 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center', marginBottom: 10 }}>
            <div>
              <div className="panel-title" style={{ color: '#8ebcff' }}>AI Decision Center</div>
              <div style={{ color: 'var(--text-mut)', fontSize: '.6rem', marginTop: 3 }}>Read-only presentation of existing model/state evidence</div>
            </div>
            <span className="pill" style={{ color: liveAllowed ? 'var(--down)' : 'var(--up)', background: liveAllowed ? 'rgba(255,73,100,.08)' : 'rgba(24,215,130,.07)', border: `1px solid ${liveAllowed ? 'rgba(255,73,100,.22)' : 'rgba(24,215,130,.22)'}` }}>
              {liveAllowed ? 'LIVE FLAG DETECTED' : `${mode} · LIVE OFF`}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.05fr 1fr 1.2fr', gap: 8 }}>
            <div className="metric-card" style={{ minHeight: 126 }}>
              <div className="metric-label">Directional Bias</div>
              <div style={{ marginTop: 12, color: decisionTone, fontSize: '1.45rem', fontWeight: 850, letterSpacing: '.02em' }}>{decision}</div>
              <div className="metric-sub">Market regime: {regime}</div>
            </div>
            <div className="metric-card" style={{ minHeight: 126 }}>
              <div className="metric-label">Prediction Confidence</div>
              <div className="metric-value">{modelConfidence == null ? '--' : `${modelConfidence.toFixed(1)}%`}</div>
              <div className="progress-bar" style={{ marginTop: 13 }}>
                <div className="progress-fill" style={{ width: `${Math.min(100, Math.max(0, modelConfidence ?? 0))}%`, background: 'linear-gradient(90deg, var(--accent), var(--up))' }} />
              </div>
              <div className="metric-sub">{hasModelEvidence ? 'Bound to current System3 model state' : 'NO_TRADE / awaiting verified model evidence'}</div>
            </div>
            <div className="metric-card" style={{ minHeight: 126 }}>
              <div className="metric-label">Evidence & Safety</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 7, marginTop: 10 }}>
                {[
                  ['Broker', brokerConnected ? 'CONNECTED' : brokerResponded ? 'RESPONDED' : 'WAITING'],
                  ['Market', marketOpen ? 'OPEN' : 'CLOSED / POLL'],
                  ['Alerts', String(alertCount)],
                  ['Proof Gates', `${passCount}/${proofGates.length || 0}`],
                ].map(([label, value]) => (
                  <div key={label} style={{ padding: '7px 8px', border: '1px solid var(--border)', borderRadius: 7, background: 'rgba(4,13,23,.45)' }}>
                    <div className="metric-label">{label}</div>
                    <div className="num" style={{ marginTop: 4, color: getStatusTone(value), fontSize: '.68rem', fontWeight: 700 }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: 13 }}>
          <div className="panel-title">Broker & Account</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 10 }}>
            <Metric label="Broker" value="DHAN" sub={brokerConnected ? 'CONNECTED' : brokerResponded ? 'API RESPONDED' : 'WAITING'} tone={brokerConnected ? 'up' : 'warn'} />
            <Metric label="Mode" value="READ-ONLY" sub="No order authority from dashboard" tone="accent" />
            <Metric label="Available" value={brokerFunds?.normalized?.available_balance != null ? fmtCr(brokerFunds.normalized.available_balance) : brokerFunds?.available_balance != null ? fmtCr(brokerFunds.available_balance) : '--'} sub="From broker API only" />
            <Metric label="Paper P&L" value={totalPnl == null ? '--' : fmtCr(totalPnl)} sub={totalPnl == null ? 'Waiting for evidence' : 'Simulation evidence'} tone={totalPnl == null ? undefined : totalPnl >= 0 ? 'up' : 'down'} />
          </div>
        </div>
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr minmax(270px, .95fr)', marginTop: 10 }}>
        <NiftyIntradayChart spot={spot('NIFTY')} changePct={change('NIFTY')} title="NIFTY 50 Intraday Dynamics" />
        <VolatilitySmileChart spot={spot('NIFTY')} />
        <PnlEquityCurveChart totalPnl={totalPnl ?? 0} />
        <div className="card" style={{ padding: 12 }}>
          <div className="panel-title">Automation Status</div>
          <div style={{ marginTop: 9 }}>
            {[
              ['Data engine', health ? 'RESPONDED' : 'WAITING'],
              ['Broker monitor', brokerConnected ? 'CONNECTED' : brokerResponded ? 'RESPONDED' : 'WAITING'],
              ['Model state', state ? 'RESPONDED' : 'WAITING'],
              ['Execution authority', liveAllowed ? 'LIVE FLAG' : 'LOCKED'],
            ].map(([label, value]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ color: 'var(--text-sec)', fontSize: '.66rem' }}>{label}</span>
                <span className="num" style={{ color: getStatusTone(value), fontSize: '.58rem', fontWeight: 800 }}>{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: 'minmax(0, 3fr) minmax(280px, 1fr)', marginTop: 10 }}>
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '11px 13px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)' }}>
            <div className="panel-title">Top Contracts / Gain Rank</div>
            <span style={{ color: 'var(--text-mut)', fontSize: '.58rem' }}>No synthetic contracts displayed</span>
          </div>
          {topRows.length === 0 ? (
            <div style={{ padding: 26, textAlign: 'center', color: 'var(--text-mut)', fontSize: '.7rem' }}>Waiting for scanner / gain-rank rows</div>
          ) : (
            <table style={{ width: '100%' }}>
              <thead><tr>{['Underlying / Contract', 'Spot', 'Change', 'Score', 'Source'].map((h) => <th key={h} className="thead" style={{ textAlign: h === 'Underlying / Contract' ? 'left' : 'right' }}>{h}</th>)}</tr></thead>
              <tbody>
                {topRows.map((row: any, index: number) => {
                  const chg = Number(row?.change_pct ?? row?.gain_pct ?? 0)
                  const spotVal = resolveSpot(row)
                  const spotSource = row?.spot_price != null && Number(row.spot_price) > 0
                    ? (row?.data_source ?? gainRank?.data_source ?? 'SCANNER')
                    : spotVal != null
                      ? 'CHAIN_SNAPSHOT'
                      : (row?.data_source ?? gainRank?.data_source ?? 'SCANNER')
                  return (
                    <tr className="trow" key={`${row?.symbol ?? row?.underlying ?? 'row'}-${index}`}>
                      <td className="tcell" style={{ fontWeight: 700 }}>{row?.symbol ?? row?.contract ?? row?.underlying ?? '--'}</td>
                      <td className="tcell" style={{ textAlign: 'right' }}>{spotVal != null ? fmt(spotVal, 2) : '--'}</td>
                      <td className={cn('tcell', signClass(chg))} style={{ textAlign: 'right' }}>{Number.isFinite(chg) ? `${chg >= 0 ? '+' : ''}${chg.toFixed(2)}%` : '--'}</td>
                      <td className="tcell" style={{ textAlign: 'right', color: 'var(--amber)' }}>{row?.score ?? row?.confidence ?? row?.gain_pct ?? '--'}</td>
                      <td className="tcell" style={{ textAlign: 'right', color: 'var(--text-mut)' }}>{spotSource}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>

        <div className="card" style={{ padding: 13 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="panel-title">Risk Status</div>
            <span className="pill" style={{ color: liveAllowed ? 'var(--down)' : 'var(--up)', border: `1px solid ${liveAllowed ? 'rgba(255,73,100,.25)' : 'rgba(24,215,130,.22)'}`, background: liveAllowed ? 'rgba(255,73,100,.07)' : 'rgba(24,215,130,.06)' }}>
              {liveAllowed ? 'CHECK REQUIRED' : 'LIVE LOCKED'}
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 10 }}>
            <Metric label="Max Drawdown" value={drawdown == null ? '--' : `${Math.abs(drawdown).toFixed(2)}%`} sub="Paper evidence" tone={drawdown == null ? undefined : Math.abs(drawdown) < 10 ? 'up' : 'warn'} />
            <Metric label="Proof Gates" value={`${passCount}/${proofGates.length || 0}`} sub="Current gate matrix" tone={proofGates.length > 0 && passCount === proofGates.length ? 'up' : 'warn'} />
            <Metric label="Market" value={marketOpen ? 'OPEN' : 'CLOSED'} sub="Read-only data remains visible" tone={marketOpen ? 'up' : 'warn'} />
            <Metric label="Authority" value={liveAllowed ? 'REVIEW' : 'LOCKED'} sub="Live execution state" tone={liveAllowed ? 'down' : 'up'} />
          </div>
        </div>
      </div>

      <div style={{ marginTop: 10, padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 8, display: 'flex', justifyContent: 'space-between', color: 'var(--text-mut)', fontSize: '.57rem', background: 'rgba(5,14,25,.76)' }}>
        <span>ANALYZER MODE · PAPER MODE ONLY · LIVE EXECUTION DISABLED</span>
        <span>Data shown only when supported by current System3 APIs</span>
      </div>
    </div>
  )
}
