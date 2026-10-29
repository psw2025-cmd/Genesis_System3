import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Activity, Brain, Database, Shield, Sparkles, TrendingUp, CheckCircle2 } from 'lucide-react'
import { API_BASE, API_HEADERS } from '../config'
import { useStore } from '../store'
import { fmt, asPct } from '../lib/utils'
import { brokerPermissionLabel } from '../lib/lifecycleTruth'
import { PendingLifecycleBanner } from './PendingLifecycleBanner'

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
  const response = await axios.get(`${API_BASE}${path}`, { headers: API_HEADERS, timeout: 4000 })
  return response.data?.data ?? response.data
}

function pct(value: any) {
  const n = Number(value)
  if (!Number.isFinite(n)) return null
  return Math.abs(n) <= 1 ? n * 100 : n
}

function Metric({
  label,
  value,
  sub,
  tone
}: {
  label: string
  value: string
  sub?: string
  tone?: 'up' | 'down' | 'warn' | 'accent'
}) {
  const colorClass = tone === 'up'
    ? 'text-emerald-400'
    : tone === 'down'
      ? 'text-rose-400'
      : tone === 'warn'
        ? 'text-amber-400'
        : tone === 'accent'
          ? 'text-sky-400'
          : 'text-slate-100'

  return (
    <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between min-w-0 shadow-sm">
      <div className="text-xs font-semibold text-slate-400 truncate">{label}</div>
      <div className={`font-mono text-lg sm:text-xl font-bold mt-1 tabular-nums ${colorClass}`}>{value}</div>
      {sub && <div className="text-[11px] text-slate-500 mt-1 truncate">{sub}</div>}
    </div>
  )
}

function Panel({ title, children, icon }: { title: string; children: React.ReactNode; icon?: React.ReactNode }) {
  return (
    <section className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md min-w-0">
      <div className="flex items-center gap-2 mb-3">
        {icon && <span className="text-sky-400">{icon}</span>}
        <h3 className="text-sm font-bold text-slate-200 tracking-wide">{title}</h3>
      </div>
      {children}
    </section>
  )
}

function StatusRow({ label, value, health }: { label: string; value: string; health?: number | null }) {
  const good = /active|healthy|connected|normal|pass|ready|ok/i.test(value)
  const bad = /fail|error|down|invalid|disabled by error/i.test(value)
  const toneClass = good ? 'text-emerald-400' : bad ? 'text-rose-400' : 'text-amber-400'

  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-800/80 text-xs">
      <span className="text-slate-300 font-medium">{label}</span>
      <div className="flex items-center gap-2 font-mono">
        <span className={`font-bold ${toneClass}`}>{value}</span>
        <span className="text-slate-500 min-w-[36px] text-right">{health == null ? '--' : `${health.toFixed(0)}%`}</span>
      </div>
    </div>
  )
}

export function GenesisTab() {
  const {
    health: sharedHealth, state: sharedState, brokerStatus, brokerConnected,
    gainRank, research, lastSync, pnl, paper,
  } = useStore()

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
        error: failed === paths.length ? 'Shared live dashboard truth active (optional brain modules standby)' : undefined,
      })
    } catch (error: any) {
      setData((current) => ({ ...current, loading: false, error: error?.response?.data?.detail || error?.message || 'Optional Genesis APIs standby' }))
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

  const permission = brokerPermissionLabel({
    brokerConnected,
    brokerStatus,
    health: effectiveHealth,
    state: sharedState,
  })
  const truthScore = pct(data.truth?.truth_score ?? data.truth?.score ?? effectiveHealth?.truth_score)
  const confidence = pct(data.brain?.confidence ?? data.brain?.prediction_confidence ?? sharedState?.signals?.confidence)
  const accuracy = pct(data.brain?.accuracy ?? data.brain?.accuracy_pct ?? data.hunger?.accuracy_pct ?? paper?.summary?.win_rate)
  const hitRate = pct(data.brain?.hit_rate ?? data.brain?.top_n_hit_rate)
  const drawdown = pct(data.brain?.max_drawdown ?? effectiveSystem?.max_drawdown ?? paper?.summary?.max_drawdown)
  const profitRaw = data.brain?.profit_factor ?? effectiveSystem?.profit_factor ?? paper?.summary?.profit_factor ?? 'N/A - NO_PREDICTION'
  const profitFactor = profitRaw == null || profitRaw === '' || profitRaw === 'N/A - NO_PREDICTION' ? null : Number(profitRaw)
  const profitDisplay = profitRaw === 'N/A - NO_PREDICTION' ? 'N/A - NO_PREDICTION' : showNum(profitFactor)
  const driftRaw = data.brain?.drift_psi ?? data.brain?.psi ?? data.truth?.drift_psi
  const drift = driftRaw == null || driftRaw === '' ? null : Number(driftRaw)
  const showPct = (value: number | null) => value == null || !Number.isFinite(value) ? 'N/A' : `${value.toFixed(1)}%`
  const showNum = (value: number | null, digits = 2) => value == null || !Number.isFinite(value) ? 'N/A - NO_PREDICTION' : value.toFixed(digits)

  const rankingRows = useMemo(() => {
    const rankings = gainRank?.latest?.rankings ?? gainRank?.rankings ?? gainRank?.latest?.predictions ?? []
    return Array.isArray(rankings) ? rankings : []
  }, [gainRank])
  const topRankedUnderlying = String(rankingRows[0]?.underlying ?? rankingRows[0]?.symbol ?? 'NIFTY').toUpperCase()
  const neutralRankEvidence = `RANK EVIDENCE · ${topRankedUnderlying}`
  const bias = String(data.brain?.directional_bias ?? data.brain?.bias ?? sharedState?.signals?.directional_bias ?? sharedState?.signals?.bias ?? neutralRankEvidence).toUpperCase()
  const regime = String(data.brain?.market_regime ?? data.brief?.market_regime ?? (marketOpen ? 'MARKET OPEN' : 'AFTER HOURS'))
  const biasTone = /bull|up|long/i.test(bias) ? 'up' : /bear|down|short/i.test(bias) ? 'down' : 'warn'

  const modules: Array<[string, string, number | null]> = [
    ['Shared Local Truth', sharedHealth || sharedState ? 'PRESENT' : 'PENDING', null],
    ['Dhan Broker', permission, null],
    ['Genesis Brain', 'PENDING', null],
    ['Data Truth', truthScore == null ? 'PENDING' : 'PRESENT', truthScore],
    ['System Health', effectiveHealth ? 'PRESENT' : 'PENDING', null],
    ['Never Die Monitor', data.monitor && !data.monitor?.error ? 'PRESENT' : 'PENDING', null],
    ['Research / Sources', research ? 'PRESENT' : 'PENDING', null],
  ]

  const evidenceLines = [
    `Broker permission: ${permission}. A read-only session is not a tradable connection.`,
    'Option-chain rows are market data. safe_no_trade stays PENDING, not ACTIVE.',
    'Model confidence, hit rate, and profit factor render only when the payload has them.',
    'Lifecycle proof is BLOCKED until scripts/run_paper_validation.py exists and the checklist passes.',
  ]

  return (
    <div className="workspace-shell" data-testid="genesis-brain-live">
      <PendingLifecycleBanner />
      {data.loading && (
        <div className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-xs font-mono mb-3">
          <span className="font-bold text-blue-400">BACKGROUND REFRESH</span>
          <span className="text-slate-400 ml-2">Optional Genesis modules are refreshing. Shared local/Dhan truth below stays visible and current.</span>
        </div>
      )}
      {/* Header Card */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md mb-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Brain size={22} />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-extrabold text-slate-100 tracking-wide">
                Genesis Brain / AI Decision Center
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Shared local/Dhan truth renders immediately; model-specific evidence refreshes independently
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
            <span className="px-2.5 py-1 rounded-lg border font-bold bg-amber-500/10 text-amber-400 border-amber-500/30">
              DHAN {permission}
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 font-bold">
              CANDIDATE ROWS {rankingRows.length}
            </span>
            <button
              onClick={load}
              disabled={data.loading}
              className="px-3 py-1 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 font-bold border border-blue-500/30 active:scale-95 transition-all"
            >
              {data.loading ? 'Refreshing…' : 'Refresh model evidence'}
            </button>
            <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold flex items-center gap-1.5">
              <Shield size={12} />
              <span>ANALYZER · LIVE OFF</span>
            </span>
          </div>
        </div>
        <div className="text-[11px] text-slate-500 font-mono mt-2 pt-2 border-t border-slate-800/80">
          Shared truth sync: {lastSync || 'PENDING'} · candidate rows are not trades or profit
        </div>
      </div>

      {/* Top 7 Metric Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-4">
        <Metric label="Market Regime" value={regime.toUpperCase()} sub={marketOpen ? 'Market open' : 'After-hours standby'} tone={marketOpen ? 'up' : 'accent'} />
        <Metric label="Prediction Confidence" value={showPct(confidence)} sub="Payload or PENDING" tone="accent" />
        <Metric label="Model Ensemble" value="PENDING" sub="Not a live-trade state" tone="warn" />
        <Metric label="Truth Score" value={truthScore == null ? 'PENDING' : `${truthScore.toFixed(0)}%`} sub="Payload or PENDING" tone="accent" />
        <Metric label="Drift Detection" value={showNum(drift, 3)} sub="Payload or PENDING" tone="warn" />
        <Metric label="Anomaly State" value="PENDING" sub="No fabricated normal state" tone="warn" />
        <Metric label="Retraining" value="PENDING" sub="Not claimed converged" tone="accent" />
      </div>

      {/* Main Analysis Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-4">
        {/* Panel 1: Why the Model / Evidence */}
        <Panel title="Why the Model / Evidence" icon={<Sparkles size={16} />}>
          <div className="text-lg font-extrabold font-mono text-emerald-400 tracking-wide mb-1">
            {bias}
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Directional conviction derived from institutional options flow & multi-timeframe ML features.
          </p>
          <div className="space-y-2">
            {evidenceLines.map((reason) => (
              <div key={reason} className="flex items-start gap-2 text-xs text-slate-300">
                <CheckCircle2 size={14} className="text-amber-400 shrink-0 mt-0.5" />
                <span>{reason}</span>
              </div>
            ))}
          </div>
        </Panel>

        {/* Panel 2: Scenario / Confidence */}
        <Panel title="Scenario / Confidence" icon={<Activity size={16} />}>
          <div className="space-y-3">
            <Metric label="Confidence" value={showPct(confidence)} sub="Payload or PENDING" tone="accent" />
            <Metric label="Accuracy (OOS)" value={showPct(accuracy)} sub="Payload or PENDING" tone="warn" />
            <Metric label="Hit Rate" value={showPct(hitRate)} sub="Payload or PENDING" tone="warn" />
          </div>
        </Panel>

        {/* Panel 3: Model Performance / Quality */}
        <Panel title="Model Performance / Quality" icon={<Brain size={16} />}>
          <div className="grid grid-cols-2 gap-2 mb-3">
            <Metric label="Profit Factor" value={profitDisplay} sub="Payload or PENDING" tone="warn" />
            <Metric label="Max Drawdown" value={drawdown == null ? 'PENDING' : `${Math.abs(drawdown).toFixed(2)}%`} sub="Payload or PENDING" tone="warn" />
            <Metric label="Truth Score" value={truthScore == null ? 'PENDING' : `${truthScore.toFixed(0)}%`} sub="Payload or PENDING" tone="accent" />
            <Metric label="Memory Events" value="PENDING" sub="Not invented" tone="accent" />
          </div>
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="text-xs font-semibold text-slate-300 mb-1">Model trajectory</div>
            <div className="text-[11px] text-amber-400 font-mono">PENDING — no fabricated conviction</div>
          </div>
        </Panel>

        {/* Panel 4: AI Agents / Modules */}
        <Panel title="AI Agents / Modules" icon={<Database size={16} />}>
          <div className="divide-y divide-slate-800/80">
            {modules.map(([label, status, healthVal]) => (
              <StatusRow key={label} label={label} value={String(status)} health={healthVal as number | null} />
            ))}
          </div>
        </Panel>
      </div>
    </div>
  )
}
export default GenesisTab
