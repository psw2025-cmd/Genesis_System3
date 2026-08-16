import { useEffect, useMemo, useState } from 'react'
import { Activity, Clock3 } from 'lucide-react'
import { API_BASE, API_HEADERS } from '../config'
import { useStore } from '../store'
import { formatIstStamp, shortSha } from '../lib/formatLive'

type SemanticState = 'PASS' | 'PARTIAL' | 'BLOCKED' | 'NOT_PROVEN' | 'ERROR'

type ProgressLane = {
  name: string
  state: SemanticState
  detail: string
  source: string
  verifiedAt?: string
}

type RuntimeContracts = {
  instruments: any
  accuracy: any
  backtest: any
  ml: any
  agent: any
}

const EMPTY_CONTRACTS: RuntimeContracts = {
  instruments: null,
  accuracy: null,
  backtest: null,
  ml: null,
  agent: null,
}

const TONE: Record<SemanticState, { color: string; background: string; border: string }> = {
  PASS: { color: 'var(--up)', background: 'rgba(0,232,122,.08)', border: 'rgba(0,232,122,.24)' },
  PARTIAL: { color: 'var(--amber)', background: 'rgba(245,158,11,.08)', border: 'rgba(245,158,11,.24)' },
  BLOCKED: { color: 'var(--down)', background: 'rgba(255,77,106,.08)', border: 'rgba(255,77,106,.24)' },
  NOT_PROVEN: { color: 'var(--text-mut)', background: 'var(--surface-2)', border: 'var(--border)' },
  ERROR: { color: 'var(--down)', background: 'rgba(255,77,106,.08)', border: 'rgba(255,77,106,.24)' },
}

const BASE = API_BASE || window.location.origin

async function fetchContract(path: string) {
  const response = await fetch(BASE + path, {
    cache: 'no-store',
    credentials: 'include',
    headers: { Accept: 'application/json', ...API_HEADERS },
  })
  if (!response.ok) throw new Error(`${path} returned ${response.status}`)
  return response.json()
}

function settledValue(result: PromiseSettledResult<any>) {
  return result.status === 'fulfilled' ? result.value : null
}

function numberOrNull(value: unknown): number | null {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function ProgressCard({ lane }: { lane: ProgressLane }) {
  const tone = TONE[lane.state]
  return (
    <article
      data-progress-lane={lane.name}
      style={{
        minWidth: 0,
        padding: 14,
        borderRadius: 10,
        background: 'var(--surface-2)',
        border: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        gap: 9,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
        <h3 style={{ margin: 0, fontSize: 13, color: 'var(--text-pri)' }}>{lane.name}</h3>
        <span
          style={{
            flexShrink: 0,
            padding: '3px 7px',
            borderRadius: 999,
            color: tone.color,
            background: tone.background,
            border: `1px solid ${tone.border}`,
            fontSize: 9,
            fontWeight: 900,
            letterSpacing: '.04em',
          }}
        >
          {lane.state}
        </span>
      </div>
      <p style={{ margin: 0, color: 'var(--text-sec)', fontSize: 11, lineHeight: 1.45 }}>{lane.detail}</p>
      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 3, color: 'var(--text-mut)', fontSize: 10 }}>
        <span>Source: {lane.source}</span>
        <span>Verified: {formatIstStamp(lane.verifiedAt)}</span>
      </div>
    </article>
  )
}

export function SystemProgressPanel() {
  const { deployInfo, brokerStatus, health, paper, pnl } = useStore()
  const [contracts, setContracts] = useState<RuntimeContracts>(EMPTY_CONTRACTS)
  const [checkedAt, setCheckedAt] = useState('')
  const [loading, setLoading] = useState(true)
  const [errorCount, setErrorCount] = useState(0)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      const results = await Promise.allSettled([
        fetchContract('/api/instruments/health'),
        fetchContract('/api/accuracy_trend'),
        fetchContract('/api/backtest/results'),
        fetchContract('/api/ml/performance'),
        fetchContract('/api/agent/status'),
      ])
      if (cancelled) return
      setContracts({
        instruments: settledValue(results[0]),
        accuracy: settledValue(results[1]),
        backtest: settledValue(results[2]),
        ml: settledValue(results[3]),
        agent: settledValue(results[4]),
      })
      setErrorCount(results.filter((result) => result.status === 'rejected').length)
      setCheckedAt(new Date().toISOString())
      setLoading(false)
    }

    void load()
    const timer = window.setInterval(load, 60_000)
    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [])

  const lanes = useMemo<ProgressLane[]>(() => {
    const liveOn = brokerStatus?.live_trading_enabled === true || brokerStatus?.order_placement_allowed === true
    const safetyProven = brokerStatus?.live_trading_enabled === false
      && brokerStatus?.order_placement_allowed === false
      && Boolean(deployInfo?.git_sha)
    const brokerConnected = brokerStatus?.connected === true
    const instrumentMeta = contracts.instruments?.meta || {}
    const instrumentFresh = contracts.instruments?.status === 'ok' && contracts.instruments?.stale === false
    const days = numberOrNull(contracts.accuracy?.days_available) ?? 0
    const rho = numberOrNull(contracts.accuracy?.avg_rho)
    const accuracyTrend = Array.isArray(contracts.accuracy?.trend) ? contracts.accuracy.trend : []
    const latestAccuracy = accuracyTrend[accuracyTrend.length - 1]
    const hitRate = numberOrNull(latestAccuracy?.hit_rate)
    const modelReady = contracts.ml?.model_proof_ready === true
      || contracts.ml?.performance?.model_proof_ready === true
    const walk = contracts.backtest?.costed_walkforward
    const walkTrades = numberOrNull(walk?.trade_count) ?? 0
    const walkNet = numberOrNull(walk?.total_net_pnl)
    const paperSummary = pnl?.summary || paper?.pnl?.summary || {}
    const paperTrades = numberOrNull(paperSummary?.total_trades) ?? 0
    const closedTrades = numberOrNull(paperSummary?.closed_trades ?? paperSummary?.closed_count) ?? 0
    const recon = String(paper?.reconciliation?.status || health?.reconciliation?.status || '').toUpperCase()

    return [
      {
        name: 'Runtime & safety',
        state: liveOn ? 'BLOCKED' : safetyProven ? 'PASS' : 'NOT_PROVEN',
        detail: liveOn
          ? 'A LIVE/order flag is on. Treat as a safety block.'
          : safetyProven
            ? `Serving ${shortSha(deployInfo?.git_sha)} in PAPER/ANALYZER; LIVE and order authority are off.`
            : 'Serving SHA or explicit LIVE/order lock is missing from the current contracts.',
        source: '/api/deploy/info + /api/broker/status',
        verifiedAt: checkedAt,
      },
      {
        name: 'Broker reliability',
        state: brokerConnected ? 'PASS' : brokerStatus ? 'BLOCKED' : 'NOT_PROVEN',
        detail: brokerConnected
          ? `Dhan read-only session connected${brokerStatus?.token_proof?.secret_version ? ` · SM v${brokerStatus.token_proof.secret_version}` : ''}.`
          : String(brokerStatus?.error || 'Broker status has not loaded.'),
        source: '/api/broker/status',
        verifiedAt: checkedAt,
      },
      {
        name: 'Data foundation',
        state: instrumentFresh ? 'PARTIAL' : contracts.instruments ? 'BLOCKED' : 'NOT_PROVEN',
        detail: instrumentFresh
          ? `${Number(contracts.instruments?.rows || 0).toLocaleString('en-IN')} instrument rows are fresh. Full cash/futures/history coverage remains NOT_PROVEN.`
          : contracts.instruments
            ? 'Instrument master is stale or unhealthy.'
            : 'Instrument health contract unavailable.',
        source: '/api/instruments/health',
        verifiedAt: instrumentMeta.synced_utc || checkedAt,
      },
      {
        name: 'Prediction validation',
        state: days >= 5 && rho != null && rho >= 0.7 ? 'PASS' : contracts.accuracy ? 'NOT_PROVEN' : 'ERROR',
        detail: contracts.accuracy
          ? `${days} validation day(s) · avg ρ ${rho == null ? 'N/A' : rho.toFixed(2)} · latest hit rate ${hitRate == null ? 'N/A' : `${(hitRate * 100).toFixed(1)}%`}. Target needs ≥5 days and ρ≥0.70.`
          : 'Accuracy trend contract unavailable.',
        source: '/api/accuracy_trend',
        verifiedAt: latestAccuracy?.date || checkedAt,
      },
      {
        name: 'ML model proof',
        state: modelReady ? 'PASS' : contracts.ml ? 'NOT_PROVEN' : 'ERROR',
        detail: modelReady
          ? 'At least one model has a current proof-ready record.'
          : 'No proof-ready model registry record. Heuristic fallback must not be labeled ML.',
        source: '/api/ml/performance',
        verifiedAt: contracts.ml?.generated_at_utc || checkedAt,
      },
      {
        name: 'Costed walk-forward',
        state: walkTrades > 0 ? 'PARTIAL' : contracts.backtest ? 'NOT_PROVEN' : 'ERROR',
        detail: walkTrades > 0
          ? `${walkTrades} proof trades; costs/slippage included; net P&L ${walkNet == null ? 'N/A' : `₹${walkNet.toLocaleString('en-IN')}`}. Pipeline proof only, not strategy promotion.`
          : 'No costed walk-forward trade sample is available.',
        source: '/api/backtest/results',
        verifiedAt: walk?.completed || checkedAt,
      },
      {
        name: 'Paper lifecycle',
        state: closedTrades > 0 && recon === 'OK' ? 'PASS' : paperTrades > 0 ? 'PARTIAL' : 'NOT_PROVEN',
        detail: closedTrades > 0 && recon === 'OK'
          ? `${closedTrades} closed paper trade(s) with reconciliation OK.`
          : paperTrades > 0
            ? `${paperTrades} paper trade(s), but closed-trade reconciliation is incomplete.`
            : 'No reconciled closed paper lifecycle rows are visible yet.',
        source: '/api/batch/market-data + /api/pnl',
        verifiedAt: checkedAt,
      },
      {
        name: 'Engineering coordination',
        state: 'NOT_PROVEN',
        detail: contracts.agent?.available
          ? 'Agent runtime responds, but current wave/owner/next dependency are absent. BACKEND_PROGRESS_CONTRACT_REQUIRED.'
          : 'No safe runtime progress contract. BACKEND_PROGRESS_CONTRACT_REQUIRED.',
        source: '/api/agent/status',
        verifiedAt: contracts.agent?.timestamp || checkedAt,
      },
    ]
  }, [brokerStatus, checkedAt, contracts, deployInfo, health, paper, pnl])

  return (
    <section
      className="elevated-panel"
      data-testid="system-progress-panel"
      aria-label="System implementation progress"
      style={{ padding: 16 }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={16} color="var(--accent)" aria-hidden />
            <h2 style={{ margin: 0, fontSize: 15, fontWeight: 700 }}>System implementation progress</h2>
          </div>
          <p style={{ margin: '5px 0 0', fontSize: 11, color: 'var(--text-mut)' }}>
            Runtime-derived truth only. PASS means the named contract is currently proven, not that System3 is money-ready.
          </p>
        </div>
        <span className="feed-badge feed-badge-mut" style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
          <Clock3 size={11} aria-hidden />
          {loading ? 'LOADING' : `${errorCount} contract error${errorCount === 1 ? '' : 's'}`}
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 230px), 1fr))', gap: 10 }}>
        {lanes.map((lane) => <ProgressCard key={lane.name} lane={lane} />)}
      </div>
    </section>
  )
}
