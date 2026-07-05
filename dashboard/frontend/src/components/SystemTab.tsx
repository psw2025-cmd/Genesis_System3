import { useStore } from '../store'
import { cn } from '../lib/utils'

function Row({ label, value, ok }: { label: string; value: string; ok?: boolean }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-sm text-text-muted">{label}</span>
      <span className={cn('num text-sm font-mono font-medium',
        ok === true ? 'text-up' : ok === false ? 'text-down' : 'text-text-primary'
      )}>{value}</span>
    </div>
  )
}

export function SystemTab() {
  const { health, wsStatus, brokerConnected } = useStore()

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Connection Status</h3>
        <Row label="Broker (Dhan)" value={brokerConnected ? 'CONNECTED' : 'DISCONNECTED'} ok={brokerConnected} />
        <Row label="WebSocket"    value={wsStatus.toUpperCase()} ok={wsStatus === 'live'} />
        <Row label="Live Trading" value="DISABLED (hardcoded)"  ok={false} />
        <Row label="Mode"         value={health?.mode ?? '--'} />
        <Row label="Data Source"  value={health?.data_source ?? '--'} />
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Performance</h3>
        <Row label="Cycle Count"        value={String(health?.cycle_count ?? 0)} />
        <Row label="Cycle Duration"     value={(health?.performance_sla?.cycle_duration_sec ?? 0).toFixed(2) + 's'} />
        <Row label="SLA Pass"           value={String(health?.performance_sla?.sla_pass ?? false)}
          ok={health?.performance_sla?.sla_pass} />
        <Row label="QC Status"          value={health?.qc_status ?? '--'}
          ok={health?.qc_status === 'OK' || health?.qc_status === 'PASS'} />
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Safety</h3>
        <Row label="LIVE_TRADING_ENABLED" value="0 (hardcoded)" ok={false} />
        <Row label="Paper Mode"           value="ACTIVE" ok={true} />
        <Row label="Live Allowed"         value={String(health?.live_allowed ?? false)} ok={false} />
        {(health?.live_blockers ?? []).map((b: string, i: number) => (
          <Row key={i} label={`Blocker ${i+1}`} value={b} ok={false} />
        ))}
      </div>
    </div>
  )
}
