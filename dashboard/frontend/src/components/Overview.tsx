import { useStore } from '../store'
import { fmtCr, signClass } from '../lib/utils'
import { cn } from '../lib/utils'

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
  const isPASS = status === 'PASS' || status === 'pass'
  const isPEND = status === 'PEND' || status === 'PENDING' || status === 'pending'
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
      <span className={cn(
        'pill text-[10px] w-14 justify-center',
        isPASS ? 'bg-up/10 text-up border border-up/20' :
        isPEND ? 'bg-amber/10 text-amber border border-amber/20' :
                 'bg-down/10 text-down border border-down/20'
      )}>{status.toUpperCase()}</span>
      <span className="text-sm text-text-primary flex-1">{label}</span>
      {note && <span className="text-xs text-text-muted font-mono truncate max-w-48">{note}</span>}
    </div>
  )
}

export function Overview() {
  const { health, paper, autoGates, brokerStatus, brokerFunds } = useStore()

  const brokerConn  = health?.broker?.connected
  const totalPnl    = paper?.pnl?.summary?.total_pnl ?? 0
  const openPos     = paper?.positions?.open_count ?? 0
  const cycleCount  = health?.cycle_count ?? 0

  // Use dynamic gates from /api/auto_gates if available, else show static
  const gates = autoGates?.gates ?? {}
  const gateEntries = Object.entries(gates)

  // Static fallback gates when autoGates not loaded yet
  const staticGates = [
    { label: 'ML Accuracy (Spearman ρ)', status: 'PEND', note: 'Accumulating — need 10 trading days' },
    { label: 'Paper Lifecycle Proof', status: 'PEND', note: 'Market session required' },
    { label: 'Tick / Data Freshness', status: health?.data_source ? 'PASS' : 'PEND', note: `source: ${health?.data_source ?? 'checking...'}` },
    { label: 'Broker Connection', status: brokerConn ? 'PASS' : 'FAIL', note: brokerConn ? 'Dhan connected' : 'Dhan disconnected' },
    { label: 'Live Trading Gate', status: 'FAIL', note: 'OFF — hardcoded safety' },
    { label: 'Paper Mode Active', status: 'PASS', note: 'CLOUD_PAPER_ENGINE=0, analyzer mode' },
  ]

  const displayGates = gateEntries.length > 0
    ? gateEntries.map(([key, val]: [string, any]) => ({
        label: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        status: val?.status ?? val ?? 'PEND',
        note: val?.note ?? val?.detail ?? undefined,
      }))
    : staticGates

  const passCount = displayGates.filter(g =>
    g.status === 'PASS' || g.status === 'pass').length

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
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
