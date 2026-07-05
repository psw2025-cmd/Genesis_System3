import { useStore } from '../store'
import { fmtCr, signClass } from '../lib/utils'
import { cn } from '../lib/utils'
import { AuthUnlock } from './AuthUnlock'

function KPI({ label, value, sub, color }: {
  label: string; value: string | number; sub?: string; color?: string
}) {
  return (
    <div className="card p-4 flex flex-col gap-1">
      <span className="text-xs text-text-muted uppercase tracking-wider">{label}</span>
      <span className={cn('num text-2xl font-bold', color ?? 'text-text-primary')}>{value}</span>
      {sub && <span className="text-xs text-text-muted">{sub}</span>}
    </div>
  )
}

function GateRow({ label, status, note }: { label: string; status: string; note?: string }) {
  // status must always be a plain string by the time it gets here (see
  // displayGates below) — this coercion is a second line of defense, not
  // the fix: a non-string status (e.g. a nested gate object) previously
  // reached `.toUpperCase()` here directly and crashed the entire Overview
  // tab to a blank page on every load.
  const statusText = typeof status === 'string' ? status : 'PEND'
  const isPASS = statusText === 'PASS' || statusText === 'pass'
  const isPEND = statusText === 'PEND' || statusText === 'PENDING' || statusText === 'pending'
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
      <span className={cn(
        'pill text-[10px] w-14 justify-center',
        isPASS ? 'bg-up/10 text-up border border-up/20' :
        isPEND ? 'bg-amber/10 text-amber border border-amber/20' :
                 'bg-down/10 text-down border border-down/20'
      )}>{statusText.toUpperCase()}</span>
      <span className="text-sm text-text-primary flex-1">{label}</span>
      {note && <span className="text-xs text-text-muted font-mono truncate max-w-48">{note}</span>}
    </div>
  )
}

export function Overview() {
  const { health, paper, autoGates, apiStatus } = useStore()

  const brokerConn  = health?.broker?.connected
  const totalPnl    = paper?.pnl?.summary?.total_pnl ?? 0
  const openPos     = paper?.positions?.open_count ?? 0
  const cycleCount  = health?.cycle_count ?? 0

  // /api/auto_gates returns two shapes for the same data: raw `gates`
  // (keyed by gate_id, entries look like { pass: boolean, ... } — NO
  // `status` field) and `proof_gates` (an array already carrying a real
  // `status` string, human-readable `name`, and `note` per gate). This used
  // to read `gates` and reach for `val.status`, which never exists there —
  // `val?.status ?? val ?? 'PEND'` then fell through to `val` itself (the
  // whole gate object) as the "status", which crashed GateRow's
  // `.toUpperCase()` on every single gate, every load. `proof_gates` is the
  // shape actually meant for display; use it directly.
  const proofGates = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []

  // Static fallback gates when autoGates not loaded yet
  const staticGates = [
    { label: 'ML Accuracy (Spearman ρ)', status: 'PEND', note: 'Accumulating — need 10 trading days' },
    { label: 'Paper Lifecycle Proof', status: 'PEND', note: 'Market session required' },
    { label: 'Tick / Data Freshness', status: health?.data_source ? 'PASS' : 'PEND', note: `source: ${health?.data_source ?? 'checking...'}` },
    { label: 'Broker Connection', status: brokerConn ? 'PASS' : 'FAIL', note: brokerConn ? 'Dhan connected' : 'Dhan disconnected' },
    { label: 'Live Trading Gate', status: 'FAIL', note: 'OFF — hardcoded safety' },
    { label: 'Paper Mode Active', status: 'PASS', note: 'CLOUD_PAPER_ENGINE=0, analyzer mode' },
  ]

  const displayGates = proofGates.length > 0
    ? proofGates.map((g: any) => ({
        label: typeof g?.name === 'string' ? g.name : String(g?.gate_id ?? 'Gate'),
        status: typeof g?.status === 'string' ? g.status : (g?.pass ? 'PASS' : 'PEND'),
        note: typeof g?.note === 'string' ? g.note : undefined,
      }))
    : staticGates

  const passCount = displayGates.filter(g =>
    g.status === 'PASS' || g.status === 'pass').length

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="card p-4 border border-down/30 bg-down/5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="text-xs text-text-muted uppercase tracking-wider">Analyzer / Paper Command Center</div>
            <div className="text-sm text-text-primary font-semibold">PAPER MODE ACTIVE - LIVE TRADING DISABLED</div>
          </div>
          <span className="pill text-[10px] bg-down/10 text-down border border-down/20">LIVE OFF</span>
        </div>
        <div className="mt-3 text-xs text-text-muted">
          Option Chain: available in the Trade tab with market-closed/cache/no-data states.
        </div>
        {apiStatus && (
          <div className="mt-2 text-xs text-text-muted">
            API status: <span className="font-mono text-amber">{apiStatus.status}</span> - {apiStatus.message}
          </div>
        )}
      </div>
      {apiStatus?.status === 'API_AUTH_REQUIRED' && <AuthUnlock />}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI label="Broker"         value={brokerConn ? 'CONNECTED' : 'OFFLINE'}
             color={brokerConn ? 'text-up' : 'text-down'} sub="Dhan read-only" />
        <KPI label="Paper P&L"      value={fmtCr(totalPnl)}
             color={signClass(totalPnl)} sub="Cloud sim" />
        <KPI label="Open Positions" value={openPos} sub="Paper only" />
        <KPI label="Cycles"         value={cycleCount} sub="Engine ticks" />
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-text-primary">Gate Matrix</h3>
          <div className="flex items-center gap-2">
            <span className="num text-xs text-text-muted">{passCount}/{displayGates.length} PASS</span>
            <div className="w-32 h-1.5 bg-surface-3 rounded-full overflow-hidden">
              <div className="h-full bg-up rounded-full"
                   style={{ width: `${(passCount/displayGates.length)*100}%` }} />
            </div>
          </div>
        </div>
        {displayGates.map((g, i) => (
          <GateRow key={i} label={g.label} status={g.status} note={g.note} />
        ))}
      </div>

      <div className="card p-4">
        <h3 className="text-sm font-semibold text-text-primary mb-3">System Health</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            ['Mode',         health?.mode        ?? '--'],
            ['QC Status',    health?.qc_status   ?? '--'],
            ['Data Source',  health?.data_source  ?? '--'],
            ['Market',       health?.market?.is_open ? 'OPEN' : 'CLOSED'],
            ['Live Allowed', String(health?.live_allowed ?? false)],
            ['Last Sync',    health?.last_sync   ?? '--'],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between py-1.5 border-b border-border">
              <span className="text-text-muted">{k}</span>
              <span className="num text-text-primary font-mono">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
