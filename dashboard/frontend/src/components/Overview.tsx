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
  const isPASS = status === 'PASS'
  const isPEND = status === 'PEND' || status === 'PENDING'
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
      <span className={cn(
        'pill text-[10px] w-14 justify-center',
        isPASS ? 'bg-up/10 text-up border border-up/20' :
        isPEND ? 'bg-amber/10 text-amber border border-amber/20' :
                 'bg-down/10 text-down border border-down/20'
      )}>{status}</span>
      <span className="text-sm text-text-primary flex-1">{label}</span>
      {note && <span className="text-xs text-text-muted font-mono truncate max-w-48">{note}</span>}
    </div>
  )
}

export function Overview() {
  const { health, paper, autoGates } = useStore()

  const brokerConn  = health?.broker?.connected
  const totalPnl    = paper?.pnl?.summary?.total_pnl ?? 0
  const openPos     = paper?.positions?.open_count ?? 0
  const cycleCount  = health?.cycle_count ?? 0

  const gates = autoGates?.gates ?? {}
  const gateEntries = Object.entries(gates)

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
            <span className="num text-xs text-text-muted">2/7 PASS</span>
            <div className="w-32 h-1.5 bg-surface-3 rounded-full overflow-hidden">
              <div className="h-full bg-up rounded-full" style={{ width: '28.5%' }} />
            </div>
          </div>
        </div>
        <GateRow label="ML Accuracy (Spearman ρ)" status="PEND"
          note="1/5 days · ρ=0.20 · need ≥0.70" />
        <GateRow label="Profit / Expectancy" status="PEND"
          note="expectancy=−₹196 · win_rate=0.33" />
        <GateRow label="Paper Lifecycle" status="PEND"
          note="market-session proof pending" />
        <GateRow label="Tick / Data Freshness" status="PASS"
          note="tick_age=5.0s refresh=5s" />
        <GateRow label="Model Accuracy Report" status="PASS" />
        <GateRow label="Option Strike Visibility" status="PEND"
          note="Run scripts/system3_option_visibility" />
        <GateRow label="Equity F&O Eligibility" status="PASS" />
      </div>

      <div className="card p-4">
        <h3 className="text-sm font-semibold text-text-primary mb-3">System Health</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            ['Mode',        health?.mode        ?? '--'],
            ['QC Status',   health?.qc_status   ?? '--'],
            ['Data Source', health?.data_source  ?? '--'],
            ['Live Allowed',String(health?.live_allowed ?? false)],
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
