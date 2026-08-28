import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Activity, Brain, Database, Shield, Sparkles } from 'lucide-react'
import { API_BASE, API_HEADERS } from '../config'
import { useStore } from '../store'

type GenesisState = {
  brief?: any
  brain?: any
  lab?: any
  monitor?: any
  hunger?: any
  truth?: any
  health?: any
  system?: any
  final?: any
  loading: boolean
  error?: string
}

async function getData(path: string) {
  const response = await axios.get(`${API_BASE}${path}`, { headers: API_HEADERS, timeout: 5000 })
  return response.data?.data ?? response.data
}

function pct(value: any) {
  const n = Number(value)
  if (!Number.isFinite(n)) return null
  return Math.abs(n) <= 1 ? n * 100 : n
}

function Metric({ label, value, sub, tone }: { label: string; value: string; sub?: string; tone?: 'up' | 'down' | 'warn' | 'accent' }) {
  const color = tone === 'up' ? 'var(--up)' : tone === 'down' ? 'var(--down)' : tone === 'warn' ? 'var(--amber)' : tone === 'accent' ? 'var(--accent)' : 'var(--text-pri)'
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={{ color, fontSize: '1.02rem' }}>{value}</div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  )
}

function Panel({ title, children, icon }: { title: string; children: React.ReactNode; icon?: React.ReactNode }) {
  return (
    <section className="card" style={{ padding: 12, minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 10 }}>
        {icon && <span style={{ color: 'var(--accent)' }}>{icon}</span>}
        <div className="panel-title">{title}</div>
      </div>
      {children}
    </section>
  )
}

function StatusRow({ label, value, health }: { label: string; value: string; health?: number | null }) {
  const good = /active|healthy|connected|normal|pass|ready|ok/i.test(value)
  const bad = /fail|error|down|invalid|disabled by error/i.test(value)
  const tone = good ? 'var(--up)' : bad ? 'var(--down)' : 'var(--amber)'
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 10, alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ color: 'var(--text-sec)', fontSize: '.66rem' }}>{label}</span>
      <span className="num" style={{ color: tone, fontSize: '.57rem', fontWeight: 800 }}>{value}</span>
      <span className="num" style={{ color: 'var(--text-mut)', fontSize: '.54rem', minWidth: 34, textAlign: 'right' }}>{health == null ? '--' : `${health.toFixed(0)}%`}</span>
    </div>
  )
}

export function GenesisTab() {
  const {
    health: sharedHealth, state: sharedState, brokerStatus, brokerConnected,
    gainRank, research, lastSync,
  } = useStore()
  // The layout must never disappear behind slow optional/legacy evidence endpoints.
  // Shared dashboard truth renders immediately; Genesis-specific modules refresh in background.
  const [data, setData] = useState<GenesisState>({ loading: false })

  const load = async () => {
    setData((current) => ({ ...current, loading: true, error: undefined }))
    const paths = [
      '/genesis-production-brief',
      '/autonomous-brain',
      '/hidden-secrets-lab',
      '/never-die-monitor',
      '/hunger-meter',
      '/data-truth-score',
      '/health',
      '/api/system_health',
      '/final-message',
    ] as const
    try {
      const settled = await Promise.allSettled(paths.map(getData))
      const value = (index: number) => settled[index].status === 'fulfilled'
        ? (settled[index] as PromiseFulfilledResult<any>).value
        : { error: String((settled[index] as PromiseRejectedResult).reason?.message || 'request failed') }
      const failed = settled.filter((result) => result.status === 'rejected').length
      setData({
        brief: value(0), brain: value(1), lab: value(2), monitor: value(3), hunger: value(4),
        truth: value(5), health: value(6), system: value(7), final: value(8), loading: false,
        error: failed === paths.length ? 'Optional Genesis module APIs unavailable; shared live dashboard truth remains active' : undefined,
      })
    } catch (error: any) {
      setData((current) => ({ ...current, loading: false, error: error?.response?.data?.detail || error?.message || 'Optional Genesis APIs unavailable' }))
    }
  }

  useEffect(() => { load() }, [])

  const effectiveHealth = data.health && !data.health?.error ? data.health : sharedHealth
  const effectiveSystem = data.system && !data.system?.error ? data.system : sharedState
  const marketOpen = effectiveHealth?.market_status === 'open'
    || Boolean(effectiveHealth?.market?.is_open)
    || Boolean(sharedState?.market?.is_open)
  const liveAllowed = Boolean(sharedState?.live_trading_enabled ?? effectiveHealth?.live_allowed ?? effectiveHealth?.live_trading_enabled)
  const brokerOk = brokerStatus?.connected === true || brokerConnected === true || effectiveHealth?.broker?.connected === true
  const truthScore = pct(data.truth?.truth_score ?? data.truth?.score ?? effectiveHealth?.truth_score)
  const confidence = pct(data.brain?.confidence ?? data.brain?.prediction_confidence ?? data.final?.confidence)
  const accuracy = pct(data.brain?.accuracy ?? data.brain?.accuracy_pct ?? data.hunger?.accuracy_pct)
  const hitRate = pct(data.brain?.hit_rate ?? data.brain?.top_n_hit_rate)
  const drawdown = pct(data.brain?.max_drawdown ?? effectiveSystem?.max_drawdown)
  const profitFactor = Number(data.brain?.profit_factor ?? effectiveSystem?.profit_factor)
  const drift = Number(data.brain?.drift_psi ?? data.brain?.psi ?? data.truth?.drift_psi)
  const rankingRows = useMemo(() => {
    const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? gainRank?.latest?.predictions ?? []
    return Array.isArray(rankings) ? rankings : []
  }, [gainRank])
  const topRankedUnderlying = String(rankingRows[0]?.underlying ?? rankingRows[0]?.symbol ?? '').toUpperCase()
  const neutralRankEvidence = topRankedUnderlying ? `RANK EVIDENCE · ${topRankedUnderlying}` : 'WAITING FOR MODEL EVIDENCE'
  const bias = String(data.brain?.directional_bias ?? data.brain?.bias ?? data.final?.bias ?? neutralRankEvidence).toUpperCase()
  const regime = String(data.brain?.market_regime ?? data.brief?.market_regime ?? (marketOpen ? 'MARKET OPEN' : 'AFTER HOURS'))
  const biasTone = /bull|up|long/i.test(bias) ? 'var(--up)' : /bear|down|short/i.test(bias) ? 'var(--down)' : 'var(--amber)'
  const researchSources = Array.isArray(research?.sources) ? research.sources : []
  const sources = Array.isArray(data.brief?.sources) ? data.brief.sources : researchSources
  const reasons = Array.isArray(data.brain?.reasons) ? data.brain.reasons
    : Array.isArray(data.brief?.market_open_must_show) ? data.brief.market_open_must_show
    : []
  const decisions = Array.isArray(data.brain?.decision_audit) ? data.brain.decision_audit
    : Array.isArray(data.final?.audit) ? data.final.audit
    : []
  const candidateCount = rankingRows.length

  const modules = [
    ['Shared GCP Truth', sharedHealth || sharedState ? 'ACTIVE' : 'WAITING', sharedHealth || sharedState ? 100 : null],
    ['Dhan Broker', brokerOk ? 'CONNECTED' : 'WAITING', brokerOk ? 100 : null],
    ['Genesis Brain', data.brain?.status ?? (data.brain && !data.brain?.error ? 'ACTIVE' : 'WAITING'), pct(data.brain?.health_pct ?? data.brain?.health)],
    ['Data Truth', data.truth?.status ?? (data.truth && !data.truth?.error ? 'ACTIVE' : 'WAITING'), truthScore],
    ['System Health', effectiveSystem?.status ?? effectiveHealth?.status ?? (effectiveHealth ? 'ACTIVE' : 'WAITING'), pct(effectiveSystem?.health_pct)],
    ['Never Die Monitor', data.monitor?.status ?? (data.monitor && !data.monitor?.error ? 'ACTIVE' : 'WAITING'), pct(data.monitor?.health_pct)],
    ['Research / Sources', sources.length ? 'ACTIVE' : 'WAITING', sources.length ? 100 : null],
  ] as const

  return (
    <div className="workspace-shell" data-testid="genesis-brain-live">
      {data.loading && (
        <div className="card" style={{ padding: '8px 12px', marginBottom: 9, borderColor: 'rgba(59,140,255,.28)', background: 'rgba(59,140,255,.05)' }}>
          <span style={{ color: '#78b6ff', fontSize: '.62rem', fontWeight: 800 }}>BACKGROUND REFRESH</span>
          <span style={{ color: 'var(--text-mut)', fontSize: '.6rem', marginLeft: 10 }}>Optional Genesis modules are refreshing. Shared GCP/Dhan truth below stays visible and current.</span>
        </div>
      )}
      {data.error && (
        <div className="card" style={{ padding: '9px 12px', marginBottom: 9, borderColor: 'rgba(245,165,36,.34)', background: 'linear-gradient(90deg, rgba(245,165,36,.07), rgba(7,18,31,.9))' }}>
          <span style={{ color: 'var(--amber)', fontSize: '.62rem', fontWeight: 800 }}>OPTIONAL MODULES DEGRADED</span>
          <span style={{ color: 'var(--text-mut)', fontSize: '.6rem', marginLeft: 10 }}>{data.error}. Shared broker/market truth remains visible; unavailable model-only values stay WAITING/--.</span>
        </div>
      )}

      <div className="card" style={{ padding: 12, marginBottom: 9 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: 11, alignItems: 'center' }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, display: 'grid', placeItems: 'center', color: '#78b6ff', background: 'linear-gradient(135deg, rgba(59,140,255,.20), rgba(168,85,247,.10))', border: '1px solid rgba(59,140,255,.35)' }}><Brain size={20} /></div>
            <div>
              <div className="workspace-title" style={{ fontSize: '1.05rem' }}>Genesis Brain / AI Decision Center</div>
              <div style={{ marginTop: 3, color: 'var(--text-mut)', fontSize: '.6rem' }}>Shared GCP/Dhan truth renders immediately; model-specific evidence refreshes independently</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 7, alignItems: 'center', flexWrap: 'wrap' }}>
            <span className="pill" style={{ color: brokerOk ? 'var(--up)' : 'var(--amber)' }}>DHAN {brokerOk ? 'CONNECTED' : 'WAITING'}</span>
            <span className="pill">CANDIDATES {candidateCount}</span>
            <button className="soft-btn" onClick={load} disabled={data.loading}>{data.loading ? 'Refreshing…' : 'Refresh model evidence'}</button>
            <span className="pill" style={{ color: liveAllowed ? 'var(--down)' : 'var(--up)', border: `1px solid ${liveAllowed ? 'rgba(255,73,100,.24)' : 'rgba(24,215,130,.24)'}`, background: liveAllowed ? 'rgba(255,73,100,.06)' : 'rgba(24,215,130,.06)' }}>
              <Shield size={11} /> {liveAllowed ? 'LIVE FLAG REVIEW' : 'ANALYZER · LIVE OFF'}
            </span>
          </div>
        </div>
        <div style={{ color: 'var(--text-mut)', fontSize: '.55rem', marginTop: 7 }}>Shared truth sync: {lastSync || 'waiting'}</div>
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: 'repeat(7, minmax(0, 1fr))', marginBottom: 9 }}>
        <Metric label="Market Regime" value={regime.toUpperCase()} sub={marketOpen ? 'Market open' : 'Read-only after hours'} tone={marketOpen ? 'up' : 'warn'} />
        <Metric label="Prediction Confidence" value={confidence == null ? '--' : `${confidence.toFixed(1)}%`} sub="Model field only" tone={confidence == null ? 'warn' : 'accent'} />
        <Metric label="Model Ensemble" value={String(data.brain?.ensemble_status ?? data.brain?.status ?? 'WAITING').toUpperCase()} sub="Optional brain service" tone={data.brain && !data.brain?.error ? 'up' : 'warn'} />
        <Metric label="Truth Score" value={truthScore == null ? '--' : `${truthScore.toFixed(0)}%`} sub="Model/data truth evidence" tone={truthScore == null ? 'warn' : truthScore >= 90 ? 'up' : 'warn'} />
        <Metric label="Drift Detection" value={Number.isFinite(drift) ? drift.toFixed(3) : '--'} sub="PSI / model field" tone={Number.isFinite(drift) && drift < .2 ? 'up' : 'warn'} />
        <Metric label="Anomaly State" value={String(data.brain?.anomaly_status ?? data.truth?.anomaly_status ?? 'WAITING').toUpperCase()} sub="Existing evidence only" tone="warn" />
        <Metric label="Retraining" value={String(data.brain?.retraining_recommendation ?? data.hunger?.retraining_recommendation ?? 'WAITING').toUpperCase()} sub="No UI auto-promotion" tone="warn" />
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: 'minmax(280px, 1.05fr) minmax(250px, .8fr) minmax(0, 1.75fr) minmax(265px, 1fr)', alignItems: 'stretch' }}>
        <Panel title="Why the Model / Evidence" icon={<Sparkles size={14} />}>
          <div style={{ color: biasTone, fontSize: '1.2rem', fontWeight: 850 }}>{bias}</div>
          <div style={{ marginTop: 5, color: 'var(--text-mut)', fontSize: '.62rem' }}>Directional bias is displayed only when supplied; otherwise current durable rank evidence is shown neutrally.</div>
          <div style={{ display: 'grid', gap: 7, marginTop: 12 }}>
            {(reasons.length ? reasons.slice(0, 6) : ['No verified reason list supplied by the current model response.']).map((reason: any, index: number) => (
              <div key={index} style={{ display: 'flex', gap: 8, color: 'var(--text-sec)', fontSize: '.64rem', lineHeight: 1.45 }}><span style={{ color: 'var(--up)', fontWeight: 900 }}>✓</span><span>{String(reason?.reason ?? reason)}</span></div>
            ))}
          </div>
        </Panel>

        <Panel title="Scenario / Confidence" icon={<Activity size={14} />}>
          <div style={{ display: 'grid', gap: 8 }}>
            <Metric label="Confidence" value={confidence == null ? '--' : `${confidence.toFixed(1)}%`} sub="Current model" tone={confidence == null ? 'warn' : 'accent'} />
            <Metric label="Accuracy" value={accuracy == null ? '--' : `${accuracy.toFixed(1)}%`} sub="Only if API supplies it" tone={accuracy == null ? 'warn' : 'up'} />
            <Metric label="Hit Rate" value={hitRate == null ? '--' : `${hitRate.toFixed(1)}%`} sub="Only if API supplies it" tone={hitRate == null ? 'warn' : 'up'} />
          </div>
        </Panel>

        <Panel title="Model Performance / Quality" icon={<Brain size={14} />}>
          <div className="workspace-grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))' }}>
            <Metric label="Accuracy" value={accuracy == null ? '--' : `${accuracy.toFixed(1)}%`} sub="Model evidence" tone={accuracy == null ? 'warn' : 'up'} />
            <Metric label="Hit Rate" value={hitRate == null ? '--' : `${hitRate.toFixed(1)}%`} sub="Model evidence" tone={hitRate == null ? 'warn' : 'up'} />
            <Metric label="Profit Factor" value={Number.isFinite(profitFactor) ? profitFactor.toFixed(2) : '--'} sub="Evidence field" tone={Number.isFinite(profitFactor) && profitFactor > 1 ? 'up' : 'warn'} />
            <Metric label="Max Drawdown" value={drawdown == null ? '--' : `${Math.abs(drawdown).toFixed(2)}%`} sub="Evidence field" tone={drawdown == null ? 'warn' : Math.abs(drawdown) < 10 ? 'up' : 'warn'} />
            <Metric label="Truth Score" value={truthScore == null ? '--' : `${truthScore.toFixed(0)}%`} sub="Data quality" tone={truthScore == null ? 'warn' : truthScore >= 90 ? 'up' : 'warn'} />
            <Metric label="Memory Events" value={String(data.brain?.memory_events ?? '--')} sub="Brain state" />
          </div>
          <div className="chart-shell" style={{ minHeight: 105, marginTop: 9, padding: 10 }}>
            <div className="panel-title">Model Confidence History</div>
            <div className="chart-empty">Historical curve binds when the API exposes a series</div>
          </div>
        </Panel>

        <Panel title="AI Agents / Modules" icon={<Database size={14} />}>
          <div style={{ display: 'grid' }}>
            {modules.map(([label, status, health]) => <StatusRow key={label} label={label} value={String(status)} health={health as number | null} />)}
          </div>
        </Panel>
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: '1fr 1fr 1.55fr', marginTop: 9 }}>
        <Panel title="Forecast Distribution" icon={<Activity size={14} />}>
          <div className="chart-shell" style={{ minHeight: 145 }}><div className="chart-empty">No verified forecast-distribution series returned</div></div>
        </Panel>
        <Panel title="Confidence History & Bands" icon={<Activity size={14} />}>
          <div className="chart-shell" style={{ minHeight: 145 }}><div className="chart-empty">No verified confidence-band series returned</div></div>
        </Panel>
        <Panel title="Decision Audit Trail" icon={<Shield size={14} />}>
          {decisions.length === 0 ? (
            <div style={{ color: 'var(--text-mut)', fontSize: '.66rem', padding: '16px 0' }}>No decision-audit rows supplied by current Genesis API.</div>
          ) : (
            <table style={{ width: '100%' }}>
              <thead><tr>{['Time', 'Decision', 'Confidence', 'Reason'].map((heading) => <th key={heading} className="thead" style={{ textAlign: heading === 'Time' ? 'left' : 'right' }}>{heading}</th>)}</tr></thead>
              <tbody>{decisions.slice(0, 8).map((row: any, index: number) => <tr className="trow" key={index}><td className="tcell">{row?.time ?? row?.timestamp ?? '--'}</td><td className="tcell" style={{ textAlign: 'right' }}>{row?.decision ?? row?.bias ?? '--'}</td><td className="tcell" style={{ textAlign: 'right' }}>{row?.confidence ?? '--'}</td><td className="tcell" style={{ textAlign: 'right', color: 'var(--text-mut)' }}>{row?.reason ?? '--'}</td></tr>)}</tbody>
            </table>
          )}
        </Panel>
      </div>

      <div className="workspace-grid" style={{ gridTemplateColumns: '1.25fr .9fr', marginTop: 9 }}>
        <Panel title="Agent Orchestration / Command Console" icon={<Brain size={14} />}>
          <div style={{ color: 'var(--text-mut)', fontSize: '.64rem', lineHeight: 1.55 }}>Visual orchestration console only. This dashboard does not send execution or order mutations.</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
            {['Analyze NIFTY', 'Review model health', 'Check data truth', 'Explain current bias', 'Review risk evidence'].map((label) => <button key={label} className="soft-btn" disabled style={{ opacity: .7, cursor: 'default' }}>{label}</button>)}
          </div>
          <div style={{ marginTop: 9, height: 42, border: '1px solid var(--border)', borderRadius: 8, display: 'flex', alignItems: 'center', padding: '0 12px', color: 'var(--text-mut)', background: 'rgba(4,13,23,.55)', fontSize: '.64rem' }}>Read-only console · no mutation authority</div>
        </Panel>

        <Panel title="Research / Evidence Sources" icon={<Database size={14} />}>
          {sources.length === 0 ? <div style={{ color: 'var(--text-mut)', fontSize: '.65rem' }}>No source list returned.</div> : <div style={{ display: 'grid', gap: 7 }}>{sources.slice(0, 6).map((source: any, index: number) => <div key={index} style={{ padding: '8px 9px', border: '1px solid var(--border)', borderRadius: 7, background: 'rgba(4,13,23,.5)' }}><div style={{ color: 'var(--text-pri)', fontSize: '.64rem', fontWeight: 750 }}>{source?.name ?? source?.source ?? 'Source'}</div><div style={{ color: 'var(--text-mut)', fontSize: '.55rem', marginTop: 3 }}>{source?.use ?? source?.purpose ?? source?.url ?? '--'}</div></div>)}</div>}
        </Panel>
      </div>

      <div style={{ marginTop: 9, padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 8, display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', color: 'var(--text-mut)', fontSize: '.56rem', background: 'rgba(5,14,25,.76)' }}>
        <span>ANALYZER MODE · PAPER MODE ONLY · LIVE EXECUTION DISABLED</span>
        <span>Shared live truth stays visible while optional model evidence refreshes</span>
      </div>
    </div>
  )
}
