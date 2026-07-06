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

function DataRow({ label, status, note }: { label: string; status: string; note?: any }) {
  const s = String(status || 'WAITING')
  const good = s === 'LOADED' || s === 'PASS'
  const warn = s === 'STALE' || s === 'MARKET_SESSION_ONLY' || s === 'WAITING'
  return (
    <div className="flex items-center gap-3 py-2 border-b border-border last:border-0">
      <span className={cn(
        'pill text-[10px] w-32 justify-center',
        good ? 'bg-up/10 text-up border border-up/20' :
        warn ? 'bg-amber/10 text-amber border border-amber/20' :
               'bg-down/10 text-down border border-down/20'
      )}>{s}</span>
      <span className="text-sm text-text-primary flex-1">{label}</span>
      {note && <span className="text-xs text-text-muted font-mono truncate max-w-[28rem]">{String(note)}</span>}
    </div>
  )
}

function hasApiFailure(obj: any): boolean {
  if (!obj) return false
  const raw = obj.raw ?? obj.data ?? obj.normalized?.raw ?? obj.funds?.raw ?? obj
  const status = String(raw?.status ?? obj?.status ?? '').toLowerCase()
  const details = JSON.stringify(raw?.remarks ?? raw?.error ?? obj?.error ?? obj?.message ?? '').toLowerCase()
  return obj?.success === false || status === 'failure' || details.includes('invalid') || details.includes('token') || details.includes('unauthorized')
}

function loadedStatus(obj: any) {
  if (!obj) return 'WAITING'
  return hasApiFailure(obj) ? 'ERROR' : 'LOADED'
}

export function Overview() {
  const {
    health, state, paper, autoGates, apiStatus, pnl, gainRank, alerts,
    brokerStatus, brokerFunds, brokerHoldings, brokerPositions,
    chain, chainSymbol, marketOpen,
  } = useStore()

  const brokerConn  = brokerStatus?.connected ?? health?.broker?.connected
  const totalPnl    = paper?.pnl?.summary?.total_pnl ?? pnl?.summary?.total_pnl ?? 0
  const openPos     = paper?.positions?.open_count ?? 0
  const cycleCount  = health?.cycle_count ?? 0
  const chainData   = chain?.[chainSymbol]

  const dataCoverage = [
    { label: 'Health API', status: health ? 'LOADED' : 'WAITING', note: health?.last_sync ?? health?.data_source },
    { label: 'State API', status: state ? 'LOADED' : 'WAITING', note: state?.market?.reason ?? state?.status },
    { label: 'Broker Status API', status: loadedStatus(brokerStatus), note: brokerStatus?.status ?? brokerStatus?.message ?? brokerStatus?.token_status },
    { label: 'Funds API', status: loadedStatus(brokerFunds), note: brokerFunds?.error ?? brokerFunds?.message ?? brokerFunds?.normalized?.raw?.remarks?.error_message },
    { label: 'Holdings API', status: loadedStatus(brokerHoldings), note: brokerHoldings?.error ?? brokerHoldings?.message },
    { label: 'Positions API', status: loadedStatus(brokerPositions), note: brokerPositions?.error ?? brokerPositions?.message },
    { label: 'P&L API', status: pnl ? 'LOADED' : paper ? 'LOADED' : 'WAITING', note: `pnl=${totalPnl}` },
    { label: 'Gain Rank / Scanner', status: gainRank?.stale ? 'STALE' : gainRank ? 'LOADED' : 'WAITING', note: gainRank?.latest_date ?? gainRank?.latest?.date ?? gainRank?.message },
    { label: 'Auto Gates', status: autoGates ? 'LOADED' : 'WAITING', note: Array.isArray(autoGates?.proof_gates) ? `${autoGates.proof_gates.length} gates` : undefined },
    { label: 'Alerts', status: Array.isArray(alerts) ? 'LOADED' : 'WAITING', note: Array.isArray(alerts) ? `${alerts.length} recent` : undefined },
    { label: 'Option Chain', status: chainData?.contracts?.length ? 'LOADED' : marketOpen ? 'WAITING' : 'MARKET_SESSION_ONLY', note: chainData?.message ?? (marketOpen ? 'waiting for rows' : 'live rows unavailable outside session') },
  ]

  const proofGates = Array.isArray(autoGates?.proof_gates) ? autoGates.proof_gates : []

  const staticGates = [
    { label: 'ML Accuracy (Spearman rho)', status: 'PEND', note: 'Accumulating - need 10 trading days' },
    { label: 'Paper Lifecycle Proof', status: 'PEND', note: 'Market session required' },
    { label: 'Tick / Data Freshness', status: health?.data_source ? 'PASS' : 'PEND', note: `source: ${health?.data_source ?? 'checking...'}` },
    { label: 'Broker Connection', status: brokerConn ? 'PASS' : 'FAIL', note: brokerConn ? 'Dhan connected' : 'Dhan disconnected' },
    { label: 'Live Trading Gate', status: 'FAIL', note: 'OFF - hardcoded safety' },
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
          Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
        </div>
        {apiStatus && (
          <div className="mt-2 text-xs text-text-muted">
            API status: <span className="font-mono text-amber">{apiStatus.status}</span> - {apiStatus.message}
          </div>
        )}
      </div>
      {apiStatus?.status === 'API_AUTH_REQUIRED' && <AuthUnlock />}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI label="Broker"         value={brokerConn ? 'CONNECTED' : brokerStatus || brokerFunds || brokerHoldings || brokerPositions ? 'API RESPONDED' : 'OFFLINE'}
             color={brokerConn ? 'text-up' : brokerStatus || brokerFunds || brokerHoldings || brokerPositions ? 'text-amber' : 'text-down'} sub="Dhan read-only" />
        <KPI label="Paper P&L"      value={fmtCr(totalPnl)}
             color={signClass(totalPnl)} sub="Cloud sim" />
        <KPI label="Open Positions" value={openPos} sub="Paper only" />
        <KPI label="Cycles"         value={cycleCount} sub="Engine ticks" />
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-text-primary">Live Data Coverage</h3>
          <span className="text-xs text-text-muted">market closed must not hide read-only data</span>
        </div>
        {dataCoverage.map((r, i) => (
          <DataRow key={i} label={r.label} status={r.status} note={r.note} />
        ))}
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
            ['Market',       health?.market?.is_open ? 'OPEN' : 'CLOSED / DATA POLLING'],
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

