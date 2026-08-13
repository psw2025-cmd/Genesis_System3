import { useMemo, useStore } from '../store'
import { useMemo, cn } from '../lib/utils'
import { useMemo, AuthUnlock } from './AuthUnlock'

function Row({ label, value, ok }: { label: string; value: string; ok?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5 border-b border-border last:border-0">
      <span className="text-sm text-text-muted">{label}</span>
      <span className={cn(
        'num text-sm font-mono font-medium text-right break-words',
        ok === true ? 'text-up' : ok === false ? 'text-down' : 'text-text-primary',
      )}>{value}</span>
    </div>
  )
}

function fmtIst(value: unknown) {
  if (!value) return 'PENDING PROOF'
  const parsed = new Date(String(value))
  if (Number.isNaN(parsed.getTime())) return String(value)
  return parsed.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}

export function SystemTab() {
  const {
    health,
    wsStatus,
    brokerConnected,
    brokerStatus,
    apiStatus,
    marketOpen,
    state,
  } = useStore()

  const proof = brokerStatus?.token_proof || {}
  const reload = brokerStatus?.token_reload || {}
  const rotation = brokerStatus?.canonical_rotation || {}
  const hoursRemaining = proof?.hours_remaining == null ? null : Number(proof.hours_remaining)
  const tokenHealthy = proof?.expired === false && hoursRemaining != null && hoursRemaining > 0
  const tokenSourceProven = proof?.source === 'GCP_SECRET_MANAGER_DYNAMIC'
  const tokenExposureProvenSafe = proof?.token_value_exposed === false
  const orderLockProven = brokerStatus?.order_placement_allowed === false
  const liveFlagProvenOff = brokerStatus?.live_trading_enabled === false
  const liveOff = !Boolean(
    state?.live_trading_enabled
      || state?.liveTradingEnabled
      || brokerStatus?.live_trading_enabled
      || brokerStatus?.order_placement_allowed,
  )
  const authStyleError = apiStatus?.status === 'API_AUTH_REQUIRED'
    || /auth|API authentication|X-API-Key|session unlock/i.test(String(apiStatus?.message || ''))

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Connection Truth</h3>
        <Row label="Broker (Dhan)" value={brokerConnected ? 'CONNECTED' : (brokerStatus?.error || 'NOT PROVEN')} ok={brokerConnected ? true : brokerStatus ? false : undefined} />
        <Row label="Broker Latency" value={brokerStatus?.latency_ms != null ? `${brokerStatus.latency_ms} ms` : 'PENDING PROOF'} />
        <Row label="WebSocket" value={wsStatus.toUpperCase()} ok={wsStatus === 'live' ? true : wsStatus === 'error' ? false : undefined} />
        <Row label="Mode" value={health?.mode ?? 'PENDING PROOF'} />
        <Row label="Data Source" value={health?.data_source ?? 'PENDING PROOF'} />
        <Row label="Market State" value={marketOpen ? 'OPEN' : 'CLOSED / OFFLINE'} />
        <Row label="Public Read API" value={authStyleError ? 'CONTRACT ERROR' : (apiStatus?.status ?? 'AVAILABLE / WAITING')} ok={authStyleError ? false : apiStatus ? undefined : true} />
      </div>

      {authStyleError && <AuthUnlock />}

      <div className="card p-5" data-testid="system-token-truth-card">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <h3 className="text-sm font-semibold text-text-primary">Dhan Token & Connection Truth</h3>
            <p className="text-xs text-text-muted mt-1">Read-only broker provenance from the existing broker status contract. No token value is rendered.</p>
          </div>
          <span className={cn('text-xs font-semibold', brokerConnected ? 'text-up' : 'text-down')}>
            {brokerConnected ? 'CONNECTED' : 'DEGRADED / UNPROVEN'}
          </span>
        </div>
        <Row label="Token Source" value={proof?.source || 'PENDING PROOF'} ok={proof?.source ? tokenSourceProven : undefined} />
        <Row label="Secret Version" value={proof?.secret_version ? `VERSION ${proof.secret_version}` : 'PENDING PROOF'} ok={proof?.secret_version ? true : undefined} />
        <Row label="Token Loaded (IST)" value={fmtIst(proof?.loaded_at_utc)} />
        <Row label="Token Expiry (IST)" value={fmtIst(proof?.expires_at_utc)} ok={proof?.expires_at_utc ? tokenHealthy : undefined} />
        <Row label="Token Time Left" value={hoursRemaining == null || Number.isNaN(hoursRemaining) ? 'PENDING PROOF' : `${hoursRemaining.toFixed(2)} h`} ok={hoursRemaining == null || Number.isNaN(hoursRemaining) ? undefined : tokenHealthy} />
        <Row label="Last Reload" value={proof?.last_reload_reason || 'NOT YET PROVEN'} ok={proof?.last_error_type ? false : proof?.last_reload_reason ? true : undefined} />
        <Row label="Reload Result" value={reload?.attempted ? (reload?.success ? 'RELOADED + VERIFIED' : 'ATTEMPT FAILED / PENDING') : 'NOT REQUIRED / NOT ATTEMPTED'} ok={reload?.attempted ? Boolean(reload?.success) : undefined} />
        <Row label="Canonical Rotation" value={rotation?.state || rotation?.status || proof?.rotation_job || 'PENDING PROOF'} ok={rotation?.success === true ? true : rotation?.success === false ? false : undefined} />
        <Row label="Rotation Schedule" value={proof?.rotation_schedule || 'PENDING PROOF'} />
        <Row label="Raw Token Exposure" value={tokenExposureProvenSafe ? 'PROVEN NO' : 'UNKNOWN'} ok={tokenExposureProvenSafe ? true : undefined} />
        <Row label="Order Authority" value={orderLockProven ? 'LOCKED' : brokerStatus ? 'NOT PROVEN LOCKED' : 'PENDING PROOF'} ok={orderLockProven ? true : brokerStatus ? false : undefined} />
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Runtime Performance</h3>
        <Row label="Cycle Count" value={health?.cycle_count == null ? 'PENDING PROOF' : String(health.cycle_count)} />
        <Row label="Cycle Duration" value={health?.performance_sla?.cycle_duration_sec == null ? 'PENDING PROOF' : `${Number(health.performance_sla.cycle_duration_sec).toFixed(2)}s`} />
        <Row label="SLA Result" value={health?.performance_sla?.sla_pass == null ? 'NOT PROVEN' : String(health.performance_sla.sla_pass)} ok={health?.performance_sla?.sla_pass == null ? undefined : Boolean(health.performance_sla.sla_pass)} />
        <Row label="QC Status" value={health?.qc_status ?? 'PENDING PROOF'} ok={health?.qc_status == null ? undefined : health.qc_status === 'OK' || health.qc_status === 'PASS'} />
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Safety Truth</h3>
        <Row label="Runtime LIVE Flag" value={liveFlagProvenOff ? 'OFF' : brokerStatus?.live_trading_enabled === true ? 'ON — BLOCK' : 'UNKNOWN'} ok={liveFlagProvenOff ? true : brokerStatus?.live_trading_enabled === true ? false : undefined} />
        <Row label="System LIVE State" value={liveOff ? 'OFF / LOCKED' : 'LIVE FLAG DETECTED'} ok={liveOff} />
        <Row label="Paper / Analyzer" value={String(health?.mode || '').toLowerCase().includes('analy') || String(health?.mode || '').toLowerCase().includes('paper') ? String(health?.mode).toUpperCase() : 'PENDING PROOF'} />
        <Row label="Live Allowed" value={health?.live_allowed == null ? 'NOT PROVEN' : String(health.live_allowed)} ok={health?.live_allowed == null ? undefined : health.live_allowed === false} />
        <Row label="Broker Data Visibility" value={authStyleError ? 'PUBLIC-READ CONTRACT ERROR' : 'READ-ONLY'} ok={authStyleError ? false : true} />
        {(health?.live_blockers ?? []).map((b: string, i: number) => (
          <Row key={i} label={`Blocker ${i + 1}`} value={b} ok={false} />
        ))}
      </div>
    </div>
  )
}
